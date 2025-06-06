"""
Authentication domain entities - Pure business logic for auth
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class TokenType(Enum):
    """Token type enumeration"""
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class AuthenticationMethod(Enum):
    """Authentication method enumeration"""
    PASSWORD = "password"
    JWT = "jwt"
    SOCIAL = "social"
    TWO_FACTOR = "two_factor"


@dataclass
class AuthToken:
    """Authentication token entity"""
    token: str
    token_type: TokenType
    user_id: str
    expires_at: datetime
    created_at: datetime
    is_revoked: bool = False
    metadata: Optional[dict] = None
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now() >= self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)"""
        return not self.is_expired() and not self.is_revoked
    
    def revoke(self) -> None:
        """Revoke the token"""
        self.is_revoked = True
    
    def time_until_expiry(self) -> timedelta:
        """Get time until token expires"""
        return self.expires_at - datetime.now()


@dataclass
class LoginAttempt:
    """Login attempt tracking entity"""
    id: Optional[str]
    user_id: Optional[str]
    email: str
    ip_address: str
    user_agent: Optional[str]
    success: bool
    failure_reason: Optional[str]
    attempted_at: datetime
    method: AuthenticationMethod
    
    def is_suspicious(self) -> bool:
        """Check if login attempt is suspicious"""
        # Business rule: Multiple failures from same IP in short time
        return not self.success and self.failure_reason in [
            'invalid_credentials', 'account_locked', 'too_many_attempts'
        ]


@dataclass
class AuthSession:
    """User authentication session entity"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() >= self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return self.is_active and not self.is_expired()
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def terminate(self) -> None:
        """Terminate the session"""
        self.is_active = False
    
    def extend_session(self, minutes: int = 60) -> None:
        """Extend session expiry time"""
        self.expires_at = datetime.now() + timedelta(minutes=minutes)
        self.update_activity()


@dataclass
class PasswordResetRequest:
    """Password reset request entity"""
    id: Optional[str]
    user_id: str
    email: str
    token: str
    requested_at: datetime
    expires_at: datetime
    used_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if reset request is expired"""
        return datetime.now() >= self.expires_at
    
    def is_used(self) -> bool:
        """Check if reset request has been used"""
        return self.used_at is not None
    
    def is_valid(self) -> bool:
        """Check if reset request is valid"""
        return not self.is_expired() and not self.is_used()
    
    def mark_as_used(self) -> None:
        """Mark reset request as used"""
        self.used_at = datetime.now()


@dataclass
class AuthenticationResult:
    """Result of authentication attempt"""
    success: bool
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    error_message: Optional[str] = None
    requires_verification: bool = False
    account_locked: bool = False
    
    @classmethod
    def success_result(cls, user_id: str, access_token: str, refresh_token: str) -> 'AuthenticationResult':
        """Create successful authentication result"""
        return cls(
            success=True,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @classmethod
    def failure_result(cls, error_message: str, **kwargs) -> 'AuthenticationResult':
        """Create failed authentication result"""
        return cls(
            success=False,
            error_message=error_message,
            **kwargs
        )


@dataclass
class SecurityEvent:
    """Security event tracking entity"""
    id: Optional[str]
    user_id: Optional[str]
    event_type: str
    description: str
    ip_address: str
    user_agent: Optional[str]
    severity: str  # low, medium, high, critical
    occurred_at: datetime
    metadata: Optional[dict] = None
    
    def is_critical(self) -> bool:
        """Check if security event is critical"""
        return self.severity == 'critical'
    
    def is_high_severity(self) -> bool:
        """Check if security event is high severity"""
        return self.severity in ['high', 'critical']