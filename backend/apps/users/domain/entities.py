"""
User domain entities - Pure business logic without framework dependencies
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class UserStatus(Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class User:
    """User domain entity with business logic"""
    id: Optional[str]
    name: str
    email: str
    password_hash: str
    status: UserStatus
    is_email_verified: bool
    last_login_ip: Optional[str]
    failed_login_attempts: int
    account_locked_until: Optional[datetime]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate entity after initialization"""
        self._validate()
    
    def _validate(self):
        """Business validation rules"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("User name must be at least 2 characters long")
        
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email address is required")
        
        if not self.password_hash:
            raise ValueError("Password hash is required")
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock the account for specified duration - business rule"""
        if self.is_account_locked():
            raise ValueError("Account is already locked")
        
        self.account_locked_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.status = UserStatus.SUSPENDED
    
    def unlock_account(self) -> None:
        """Unlock the account - business rule"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        if self.status == UserStatus.SUSPENDED:
            self.status = UserStatus.ACTIVE
    
    def increment_failed_login(self, max_attempts: int = 5) -> None:
        """Increment failed login attempts - business rule"""
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
    
    def reset_failed_login(self) -> None:
        """Reset failed login attempts on successful login"""
        if self.failed_login_attempts > 0:
            self.failed_login_attempts = 0
    
    def verify_email(self) -> None:
        """Verify user email - business rule"""
        if self.is_email_verified:
            raise ValueError("Email is already verified")
        
        self.is_email_verified = True
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
    
    def update_last_login(self, ip_address: Optional[str] = None) -> None:
        """Update last login information"""
        self.last_login = datetime.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.reset_failed_login()
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        if self.status == UserStatus.INACTIVE:
            raise ValueError("User is already inactive")
        
        self.status = UserStatus.INACTIVE
    
    def activate(self) -> None:
        """Activate user account"""
        if self.status == UserStatus.ACTIVE:
            raise ValueError("User is already active")
        
        self.status = UserStatus.ACTIVE
        self.unlock_account()
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if not self.account_locked_until:
            return False
        return datetime.now() < self.account_locked_until
    
    def is_active(self) -> bool:
        """Check if user is active and can login"""
        return (self.status == UserStatus.ACTIVE and 
                not self.is_account_locked())
    
    def can_login(self) -> bool:
        """Check if user can login"""
        return self.is_active()
    
    def get_security_level(self) -> str:
        """Get user security level based on account status"""
        if self.is_account_locked():
            return "LOCKED"
        elif self.failed_login_attempts >= 3:
            return "HIGH_RISK"
        elif not self.is_email_verified:
            return "UNVERIFIED"
        else:
            return "NORMAL"


@dataclass
class UserFilter:
    """Value object for user filtering"""
    status: Optional[UserStatus] = None
    is_email_verified: Optional[bool] = None
    is_locked: Optional[bool] = None
    search_term: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class UserStatistics:
    """Value object for user statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    verified_users: int
    locked_users: int
    users_with_tasks: int
    
    @property
    def verification_rate(self) -> float:
        """Calculate email verification rate"""
        return (self.verified_users / self.total_users * 100) if self.total_users > 0 else 0
    
    @property
    def activity_rate(self) -> float:
        """Calculate user activity rate"""
        return (self.active_users / self.total_users * 100) if self.total_users > 0 else 0