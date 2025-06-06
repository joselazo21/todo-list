"""
DRF Serializers for User presentation layer
"""
from rest_framework import serializers
from datetime import datetime
from ..application.dto import CreateUserDTO, UpdateUserDTO, UserFilterDTO, ChangePasswordDTO, EmailVerificationDTO


class CreateUserSerializer(serializers.Serializer):
    """Serializer for user creation"""
    name = serializers.CharField(max_length=100, min_length=2)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    
    def validate_name(self, value):
        """Validate name"""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()
    
    def validate_email(self, value):
        """Validate email"""
        return value.lower().strip()
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        return value
    
    def to_dto(self) -> CreateUserDTO:
        """Convert to DTO"""
        return CreateUserDTO(
            name=self.validated_data['name'],
            email=self.validated_data['email'],
            password=self.validated_data['password']
        )


class UpdateUserSerializer(serializers.Serializer):
    """Serializer for user updates"""
    name = serializers.CharField(max_length=100, min_length=2, required=False)
    email = serializers.EmailField(required=False)
    status = serializers.ChoiceField(
        choices=['active', 'inactive', 'suspended', 'pending_verification'],
        required=False
    )
    
    def validate_name(self, value):
        """Validate name"""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip() if value else value
    
    def validate_email(self, value):
        """Validate email"""
        if value is not None:
            return value.lower().strip()
        return value
    
    def to_dto(self, user_id: str) -> UpdateUserDTO:
        """Convert to DTO"""
        return UpdateUserDTO(
            user_id=user_id,
            name=self.validated_data.get('name'),
            email=self.validated_data.get('email'),
            status=self.validated_data.get('status')
        )


class UserSerializer(serializers.Serializer):
    """Serializer for user representation"""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    status = serializers.CharField()
    is_email_verified = serializers.BooleanField()
    last_login_ip = serializers.IPAddressField(allow_null=True)
    failed_login_attempts = serializers.IntegerField()
    account_locked_until = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    last_login = serializers.DateTimeField(allow_null=True)
    is_active = serializers.BooleanField()
    is_account_locked = serializers.BooleanField()
    security_level = serializers.CharField()


class UserFilterSerializer(serializers.Serializer):
    """Serializer for user filtering"""
    status = serializers.ChoiceField(
        choices=['active', 'inactive', 'suspended', 'pending_verification'],
        required=False
    )
    is_email_verified = serializers.BooleanField(required=False)
    is_locked = serializers.BooleanField(required=False)
    search_term = serializers.CharField(required=False, allow_blank=True)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)
    
    def to_dto(self) -> UserFilterDTO:
        """Convert to DTO"""
        return UserFilterDTO(
            status=self.validated_data.get('status'),
            is_email_verified=self.validated_data.get('is_email_verified'),
            is_locked=self.validated_data.get('is_locked'),
            search_term=self.validated_data.get('search_term'),
            created_after=self.validated_data.get('created_after'),
            created_before=self.validated_data.get('created_before')
        )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        return value
    
    def to_dto(self, user_id: str) -> ChangePasswordDTO:
        """Convert to DTO"""
        return ChangePasswordDTO(
            user_id=user_id,
            current_password=self.validated_data['current_password'],
            new_password=self.validated_data['new_password']
        )


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField()
    
    def to_dto(self, user_id: str) -> EmailVerificationDTO:
        """Convert to DTO"""
        return EmailVerificationDTO(
            user_id=user_id,
            token=self.validated_data['token']
        )


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    locked_users = serializers.IntegerField()
    users_with_tasks = serializers.IntegerField()
    verification_rate = serializers.FloatField()
    activity_rate = serializers.FloatField()


class SecurityRecommendationSerializer(serializers.Serializer):
    """Serializer for security recommendations"""
    type = serializers.CharField()
    priority = serializers.CharField()
    message = serializers.CharField()