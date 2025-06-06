"""
Serializers for Authentication API endpoints
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Basic validation - actual authentication will be handled in the view
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user_id = serializers.CharField()
    expires_at = serializers.DateTimeField()


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    refresh_token = serializers.CharField(required=False)
    refresh = serializers.CharField(required=False)  # For frontend compatibility
    
    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token') or attrs.get('refresh')
        if not refresh_token:
            raise serializers.ValidationError('Must include refresh_token or refresh.')
        # Normalize to refresh_token
        attrs['refresh_token'] = refresh_token
        return attrs


class RefreshTokenResponseSerializer(serializers.Serializer):
    """Serializer for token refresh response"""
    access_token = serializers.CharField()
    expires_at = serializers.DateTimeField()


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    name = serializers.CharField(max_length=255, min_length=2)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_password(self, value):
        """Validate password using Django's password validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        from ...users.infrastructure.models import UserModel
        if UserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class RegisterResponseSerializer(serializers.Serializer):
    """Serializer for registration response"""
    user_id = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField()
    message = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout"""
    revoke_all_sessions = serializers.BooleanField(default=False)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()


class PasswordResetResponseSerializer(serializers.Serializer):
    """Serializer for password reset response"""
    message = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_new_password(self, value):
        """Validate new password using Django's password validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class ValidateTokenSerializer(serializers.Serializer):
    """Serializer for token validation"""
    token = serializers.CharField()


class ValidateTokenResponseSerializer(serializers.Serializer):
    """Serializer for token validation response"""
    valid = serializers.BooleanField()
    user_id = serializers.CharField(required=False)
    token_type = serializers.CharField(required=False)
    expires_at = serializers.DateTimeField(required=False)


class SessionSerializer(serializers.Serializer):
    """Serializer for session representation"""
    session_id = serializers.CharField()
    ip_address = serializers.IPAddressField()
    user_agent = serializers.CharField(required=False)
    created_at = serializers.DateTimeField()
    last_activity = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    is_current = serializers.BooleanField()


class SecurityEventSerializer(serializers.Serializer):
    """Serializer for security event representation"""
    id = serializers.CharField()
    event_type = serializers.CharField()
    description = serializers.CharField()
    ip_address = serializers.IPAddressField()
    user_agent = serializers.CharField(required=False)
    severity = serializers.CharField()
    occurred_at = serializers.DateTimeField()
    metadata = serializers.JSONField(required=False)