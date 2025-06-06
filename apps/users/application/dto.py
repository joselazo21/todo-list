"""
Data Transfer Objects for User application layer
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..domain.entities import User, UserStatus


@dataclass
class CreateUserDTO:
    """DTO for user creation"""
    name: str
    email: str
    password: str
    
    def validate(self) -> list[str]:
        """Validate DTO data"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if not self.email or '@' not in self.email:
            errors.append("Valid email address is required")
        
        if not self.password or len(self.password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        return errors


@dataclass
class UpdateUserDTO:
    """DTO for user updates"""
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    
    def to_status_enum(self) -> Optional[UserStatus]:
        """Convert string status to enum"""
        if not self.status:
            return None
        
        status_map = {
            'active': UserStatus.ACTIVE,
            'inactive': UserStatus.INACTIVE,
            'suspended': UserStatus.SUSPENDED,
            'pending_verification': UserStatus.PENDING_VERIFICATION
        }
        return status_map.get(self.status.lower())


@dataclass
class UserDTO:
    """DTO for user representation"""
    id: str
    name: str
    email: str
    status: str
    is_email_verified: bool
    last_login_ip: Optional[str]
    failed_login_attempts: int
    account_locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    is_account_locked: bool
    security_level: str
    
    @classmethod
    def from_entity(cls, user: User) -> 'UserDTO':
        """Create DTO from domain entity"""
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            status=user.status.value,
            is_email_verified=user.is_email_verified,
            last_login_ip=user.last_login_ip,
            failed_login_attempts=user.failed_login_attempts,
            account_locked_until=user.account_locked_until,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            is_active=user.is_active(),
            is_account_locked=user.is_account_locked(),
            security_level=user.get_security_level()
        )


@dataclass
class UserFilterDTO:
    """DTO for user filtering"""
    status: Optional[str] = None
    is_email_verified: Optional[bool] = None
    is_locked: Optional[bool] = None
    search_term: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class ChangePasswordDTO:
    """DTO for password change"""
    user_id: str
    current_password: str
    new_password: str
    
    def validate(self) -> list[str]:
        """Validate password change data"""
        errors = []
        
        if not self.current_password:
            errors.append("Current password is required")
        
        if not self.new_password or len(self.new_password) < 8:
            errors.append("New password must be at least 8 characters long")
        
        if self.current_password == self.new_password:
            errors.append("New password must be different from current password")
        
        return errors


@dataclass
class UserStatisticsDTO:
    """DTO for user statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    verified_users: int
    locked_users: int
    users_with_tasks: int
    verification_rate: float
    activity_rate: float
    
    @classmethod
    def from_domain(cls, stats) -> 'UserStatisticsDTO':
        """Create DTO from domain statistics"""
        return cls(
            total_users=stats.total_users,
            active_users=stats.active_users,
            inactive_users=stats.inactive_users,
            verified_users=stats.verified_users,
            locked_users=stats.locked_users,
            users_with_tasks=stats.users_with_tasks,
            verification_rate=stats.verification_rate,
            activity_rate=stats.activity_rate
        )


@dataclass
class SecurityRecommendationDTO:
    """DTO for security recommendations"""
    type: str
    priority: str
    message: str


@dataclass
class EmailVerificationDTO:
    """DTO for email verification"""
    user_id: str
    token: str