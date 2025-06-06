"""
Views for Authentication API endpoints
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model

from .serializers import (
    LoginSerializer, LoginResponseSerializer,
    RefreshTokenSerializer, RefreshTokenResponseSerializer,
    RegisterSerializer, RegisterResponseSerializer,
    LogoutSerializer, PasswordResetRequestSerializer,
    PasswordResetResponseSerializer, ResetPasswordSerializer,
    ValidateTokenSerializer, ValidateTokenResponseSerializer,
    SessionSerializer, SecurityEventSerializer
)
from ..application.use_cases import (
    LoginUseCase, RefreshTokenUseCase, LogoutUseCase,
    ValidateTokenUseCase, PasswordResetRequestUseCase,
    ResetPasswordUseCase, GetUserSessionsUseCase,
    GetSecurityEventsUseCase
)
from ..application.dto import (
    LoginRequestDTO, RefreshTokenRequestDTO, LogoutRequestDTO,
    ValidateTokenRequestDTO, PasswordResetRequestDTO,
    ResetPasswordRequestDTO
)
from ...users.application.use_cases import CreateUserUseCase, GetUserUseCase
from ...users.application.dto import CreateUserDTO
from ...shared.infrastructure.dependency_injection import get_dependency


User = get_user_model()


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@extend_schema(
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(RegisterResponseSerializer, description="User registered successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Create user using use case
            create_user_use_case = get_dependency(CreateUserUseCase)
            dto = CreateUserDTO(
                name=serializer.validated_data['name'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            user = create_user_use_case.execute(dto)
            
            response_data = {
                'user_id': str(user.id),
                'email': user.email,
                'name': user.name,
                'message': 'User registered successfully'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Registration failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(LoginResponseSerializer, description="Login successful"),
        400: OpenApiResponse(description="Invalid credentials"),
        429: OpenApiResponse(description="Too many attempts"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Authenticate user and return JWT tokens"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Execute login use case
            login_use_case = get_dependency(LoginUseCase)
            dto = LoginRequestDTO(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            result = login_use_case.execute(dto)
            
            if result.success:
                # Get user information
                user_use_case = get_dependency(GetUserUseCase)
                user_dto = user_use_case.execute(result.user_id)
                
                response_data = {
                    'access_token': result.access_token,
                    'refresh_token': result.refresh_token,
                    'access': result.access_token,  # Frontend compatibility
                    'refresh': result.refresh_token,  # Frontend compatibility
                    'user_id': result.user_id,
                    'expires_at': result.expires_at,
                    'user': {
                        'id': user_dto.id,
                        'name': user_dto.name,
                        'email': user_dto.email
                    } if user_dto else None
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS if 'too many' in result.error_message.lower() else status.HTTP_400_BAD_REQUEST
                return Response(
                    {'error': result.error_message},
                    status=status_code
                )
                
        except Exception as e:
            return Response(
                {'error': 'Login failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=RefreshTokenSerializer,
    responses={
        200: OpenApiResponse(RefreshTokenResponseSerializer, description="Token refreshed successfully"),
        400: OpenApiResponse(description="Invalid refresh token"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token using refresh token"""
    serializer = RefreshTokenSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Execute refresh token use case
            refresh_use_case = get_dependency(RefreshTokenUseCase)
            dto = RefreshTokenRequestDTO(
                refresh_token=serializer.validated_data['refresh_token']
            )
            
            result = refresh_use_case.execute(dto)
            
            if result.success:
                response_data = {
                    'access_token': result.access_token,
                    'access': result.access_token,  # Frontend compatibility
                    'expires_at': result.expires_at
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': 'Token refresh failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LogoutSerializer,
    responses={
        200: OpenApiResponse(description="Logout successful"),
        400: OpenApiResponse(description="Logout failed"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user and invalidate tokens"""
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Execute logout use case
            logout_use_case = get_dependency(LogoutUseCase)
            dto = LogoutRequestDTO(
                user_id=str(request.user.id),
                revoke_all_sessions=serializer.validated_data.get('revoke_all_sessions', False)
            )
            
            success = logout_use_case.execute(dto)
            
            if success:
                return Response(
                    {'message': 'Logout successful'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Logout failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': 'Logout failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ValidateTokenSerializer,
    responses={
        200: OpenApiResponse(ValidateTokenResponseSerializer, description="Token validation result"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_token(request):
    """Validate JWT token"""
    serializer = ValidateTokenSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Execute validate token use case
            validate_use_case = get_dependency(ValidateTokenUseCase)
            dto = ValidateTokenRequestDTO(
                token=serializer.validated_data['token']
            )
            
            result = validate_use_case.execute(dto)
            
            response_data = {
                'valid': result.valid,
                'user_id': result.user_id,
                'token_type': result.token_type,
                'expires_at': result.expires_at
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'valid': False, 'error': 'Token validation failed'},
                status=status.HTTP_200_OK
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(PasswordResetResponseSerializer, description="Password reset email sent"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request password reset"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Execute password reset request use case
            reset_request_use_case = get_dependency(PasswordResetRequestUseCase)
            dto = PasswordResetRequestDTO(
                email=serializer.validated_data['email']
            )
            
            result = reset_request_use_case.execute(dto)
            
            response_data = {
                'message': result.message
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': 'Password reset request failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password reset successful"),
        400: OpenApiResponse(description="Invalid token or password"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password with token"""
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Execute reset password use case
            reset_use_case = get_dependency(ResetPasswordUseCase)
            dto = ResetPasswordRequestDTO(
                token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password']
            )
            
            success = reset_use_case.execute(dto)
            
            if success:
                return Response(
                    {'message': 'Password reset successful'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Password reset failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Password reset failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: OpenApiResponse(SessionSerializer(many=True), description="User sessions"),
    },
    tags=['Authentication']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sessions(request):
    """Get user sessions"""
    try:
        # Execute get sessions use case
        sessions_use_case = get_dependency(GetUserSessionsUseCase)
        sessions = sessions_use_case.execute(
            user_id=str(request.user.id),
            current_session_id=request.session.session_key
        )
        
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve sessions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={
        200: OpenApiResponse(SecurityEventSerializer(many=True), description="Security events"),
    },
    tags=['Authentication']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_security_events(request):
    """Get user security events"""
    try:
        # Execute get security events use case
        events_use_case = get_dependency(GetSecurityEventsUseCase)
        events = events_use_case.execute(
            user_id=str(request.user.id),
            limit=int(request.GET.get('limit', 50))
        )
        
        serializer = SecurityEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve security events'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )