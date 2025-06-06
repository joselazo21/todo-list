"""
Data Transfer Objects for Authentication application layer
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LoginRequestDTO:
    """DTO for login request"""
    email: str
    password: str
    ip_address: str
    user_agent: Optional[str] = None
    
    def validate(self) -> list[str]:
        """Validate login request data"""
        errors = []
        
        if not self.email:
            errors.append("Email is required")
        elif '@' not in self.email:
            errors.append("Valid email address is required")
        
        if not self.password:
            errors.append("Password is required")
        
        if not self.ip_address:
            errors.append("IP address is required")
        
        return errors


@dataclass
class LoginResponseDTO:
    """DTO for login response"""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    error_message: Optional[str] = None
    requires_verification: bool = False
    account_locked: bool = False
    expires_at: Optional[datetime] = None


@dataclass
class RefreshTokenRequestDTO:
    """DTO for token refresh request"""
    refresh_token: str
    
    def validate(self) -> list[str]:
        """Validate refresh token request"""
        errors = []
        
        if not self.refresh_token:
            errors.append("Refresh token is required")
        
        return errors


@dataclass
class RefreshTokenResponseDTO:
    """DTO for token refresh response"""
    success: bool
    access_token: Optional[str] = None
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class LogoutRequestDTO:
    """DTO for logout request"""
    user_id: str
    session_id: Optional[str] = None
    revoke_all_sessions: bool = False


@dataclass
class ValidateTokenRequestDTO:
    """DTO for token validation request"""
    token: str
    
    def validate(self) -> list[str]:
        """Validate token validation request"""
        errors = []
        
        if not self.token:
            errors.append("Token is required")
        
        return errors


@dataclass
class ValidateTokenResponseDTO:
    """DTO for token validation response"""
    valid: bool
    user_id: Optional[str] = None
    token_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class PasswordResetRequestDTO:
    """DTO for password reset request"""
    email: str
    
    def validate(self) -> list[str]:
        """Validate password reset request"""
        errors = []
        
        if not self.email:
            errors.append("Email is required")
        elif '@' not in self.email:
            errors.append("Valid email address is required")
        
        return errors


@dataclass
class PasswordResetResponseDTO:
    """DTO for password reset response"""
    success: bool
    message: str
    token: Optional[str] = None  # Only for testing, not returned in production


@dataclass
class ResetPasswordRequestDTO:
    """DTO for password reset confirmation"""
    token: str
    new_password: str
    
    def validate(self) -> list[str]:
        """Validate password reset confirmation"""
        errors = []
        
        if not self.token:
            errors.append("Reset token is required")
        
        if not self.new_password:
            errors.append("New password is required")
        elif len(self.new_password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        return errors


@dataclass
class SessionDTO:
    """DTO for session representation"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool
    is_current: bool = False


@dataclass
class SecurityEventDTO:
    """DTO for security event representation"""
    id: str
    user_id: Optional[str]
    event_type: str
    description: str
    ip_address: str
    user_agent: Optional[str]
    severity: str
    occurred_at: datetime
    metadata: Optional[dict] = None


@dataclass
class LoginAttemptDTO:
    """DTO for login attempt representation"""
    id: str
    user_id: Optional[str]
    email: str
    ip_address: str
    user_agent: Optional[str]
    success: bool
    failure_reason: Optional[str]
    attempted_at: datetime
    method: str