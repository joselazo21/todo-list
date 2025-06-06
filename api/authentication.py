"""
Enhanced authentication views and utilities
"""
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
import logging

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .permissions import IsOwnerOrReadOnly
from .utils import get_client_ip

logger = logging.getLogger(__name__)


class LoginRateThrottle(UserRateThrottle):
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    scope = 'register'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with enhanced security"""
    
    def validate(self, attrs):
        # Get the request object
        request = self.context.get('request')
        client_ip = get_client_ip(request) if request else None
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email and password are required.')
        
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email} from IP: {client_ip}")
            raise serializers.ValidationError('Invalid credentials.')
        
        # Check if account is locked
        if user.is_account_locked:
            logger.warning(f"Login attempt on locked account: {email} from IP: {client_ip}")
            raise serializers.ValidationError('Account is temporarily locked due to multiple failed login attempts.')
        
        # Check if account is active
        if not user.is_active:
            logger.warning(f"Login attempt on inactive account: {email} from IP: {client_ip}")
            raise serializers.ValidationError('Account is disabled.')
        
        # Authenticate user
        user = authenticate(request=request, username=email, password=password)
        
        if user is None:
            # Increment failed login attempts
            try:
                user_obj = User.objects.get(email=email.lower())
                user_obj.increment_failed_login()
                logger.warning(f"Failed login attempt for {email} from IP: {client_ip}")
            except User.DoesNotExist:
                pass
            raise serializers.ValidationError('Invalid credentials.')
        
        # Reset failed login attempts on successful login
        user.reset_failed_login()
        
        # Update last login IP
        if client_ip:
            user.last_login_ip = client_ip
            user.save(update_fields=['last_login_ip'])
        
        # Log successful login
        logger.info(f"Successful login for {user.email} from IP: {client_ip}")
        
        # Get tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': user.name,
                'is_email_verified': user.is_email_verified,
            }
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view with rate limiting"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]
    permission_classes = [AllowAny]


class UserRegistrationView(generics.CreateAPIView):
    """Enhanced user registration with email verification"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Log registration
        client_ip = get_client_ip(self.request)
        logger.info(f"New user registered: {user.email} from IP: {client_ip}")
        
        # Send verification email (if email backend is configured)
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            self.send_verification_email(user)
    
    def send_verification_email(self, user):
        """Send email verification"""
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # In a real application, you would construct a proper verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
            
            subject = 'Verify your email address'
            message = f"""
            Hi {user.name},
            
            Please click the following link to verify your email address:
            {verification_url}
            
            If you didn't create an account, please ignore this email.
            
            Best regards,
            Todo List Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Verification email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.UpdateAPIView):
    """Change password for authenticated users"""
    serializer_class = PasswordChangeSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log password change
        client_ip = get_client_ip(request)
        logger.info(f"Password changed for user {user.email} from IP: {client_ip}")
        
        return Response({'message': 'Password changed successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def password_reset_request(request):
    """Request password reset"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email, is_active=True)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Send reset email
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            subject = 'Password Reset Request'
            message = f"""
            Hi {user.name},
            
            You requested a password reset. Click the following link to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            Todo List Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        
        # Log password reset request
        client_ip = get_client_ip(request)
        logger.info(f"Password reset requested for {email} from IP: {client_ip}")
        
    except User.DoesNotExist:
        # Don't reveal if email exists or not
        pass
    
    return Response({'message': 'If the email exists, a password reset link has been sent.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
        user = User.objects.get(pk=uid, is_active=True)
        
        if default_token_generator.check_token(user, serializer.validated_data['token']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Log password reset
            client_ip = get_client_ip(request)
            logger.info(f"Password reset completed for {user.email} from IP: {client_ip}")
            
            return Response({'message': 'Password reset successfully.'})
        else:
            return Response(
                {'error': 'Invalid or expired token.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def logout_view(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log logout
        client_ip = get_client_ip(request)
        logger.info(f"User {request.user.email} logged out from IP: {client_ip}")
        
        return Response({'message': 'Successfully logged out.'})
    except Exception as e:
        return Response(
            {'error': 'Invalid token.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify user email address"""
    uid = request.data.get('uid')
    token = request.data.get('token')
    
    if not uid or not token:
        return Response(
            {'error': 'UID and token are required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            
            logger.info(f"Email verified for user {user.email}")
            return Response({'message': 'Email verified successfully.'})
        else:
            return Response(
                {'error': 'Invalid or expired verification link.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid verification link.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )