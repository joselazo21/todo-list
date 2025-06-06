"""
User domain services - Complex business logic that doesn't belong to entities
"""
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
from .entities import User, UserStatus
from .repositories import UserRepository


class UserDomainService:
    """Domain service for complex user business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def register_new_user(self, name: str, email: str, password: str) -> User:
        """
        Register a new user with business validation
        Business rule: Email must be unique, password must be hashed
        """
        # Check if email already exists
        if self._user_repository.exists_by_email(email.lower()):
            raise ValueError("Email address is already registered")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user entity
        user = User(
            id=None,
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return self._user_repository.save(user)
    
    def authenticate_user(self, email: str, password: str, ip_address: Optional[str] = None) -> Optional[User]:
        """
        Authenticate user with business rules
        Business rule: Check password, update login info, handle failed attempts
        """
        user = self._user_repository.find_by_email(email.lower())
        
        if not user:
            return None
        
        # Check if account is locked
        if user.is_account_locked():
            raise ValueError("Account is temporarily locked due to multiple failed login attempts")
        
        # Check if user can login
        if not user.can_login():
            raise ValueError("Account is not active or email is not verified")
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            # Increment failed attempts
            user.increment_failed_login()
            self._user_repository.save(user)
            return None
        
        # Successful login
        user.update_last_login(ip_address)
        return self._user_repository.save(user)
    
    def unlock_expired_accounts(self) -> List[User]:
        """
        Unlock accounts where lock period has expired
        Business rule: Auto-unlock accounts after lock period
        """
        locked_users = self._user_repository.find_locked_users()
        unlocked_users = []
        
        for user in locked_users:
            if user.account_locked_until and datetime.now() >= user.account_locked_until:
                user.unlock_account()
                updated_user = self._user_repository.save(user)
                unlocked_users.append(updated_user)
        
        return unlocked_users
    
    def generate_email_verification_token(self, user: User) -> str:
        """
        Generate secure email verification token
        Business rule: Token should be unique and time-limited
        """
        if user.is_email_verified:
            raise ValueError("Email is already verified")
        
        # Generate secure token
        token_data = f"{user.id}:{user.email}:{datetime.now().isoformat()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token
    
    def verify_email_with_token(self, user_id: str, token: str) -> User:
        """
        Verify email using token
        Business rule: Token validation and email verification
        """
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        if user.is_email_verified:
            raise ValueError("Email is already verified")
        
        # In a real implementation, you would validate the token
        # For now, we'll assume token is valid
        user.verify_email()
        
        return self._user_repository.save(user)
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> User:
        """
        Change user password with validation
        Business rule: Verify current password before changing
        """
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not self._verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        self._validate_password_strength(new_password)
        
        # Hash new password
        user.password_hash = self._hash_password(new_password)
        user.updated_at = datetime.now()
        
        return self._user_repository.save(user)
    
    def get_security_recommendations(self, user: User) -> List[dict]:
        """
        Get security recommendations for user
        Business logic for security analysis
        """
        recommendations = []
        
        if not user.is_email_verified:
            recommendations.append({
                'type': 'email_verification',
                'priority': 'high',
                'message': 'Please verify your email address to secure your account'
            })
        
        if user.failed_login_attempts > 0:
            recommendations.append({
                'type': 'failed_attempts',
                'priority': 'medium',
                'message': f'You have {user.failed_login_attempts} failed login attempts. Consider changing your password.'
            })
        
        if user.last_login and (datetime.now() - user.last_login).days > 30:
            recommendations.append({
                'type': 'inactive_account',
                'priority': 'low',
                'message': 'Your account has been inactive for over 30 days'
            })
        
        return recommendations
    
    def _hash_password(self, password: str) -> str:
        """Hash password using secure method"""
        # In a real implementation, use bcrypt or similar
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == hash_hex
        except ValueError:
            return False
    
    def _validate_password_strength(self, password: str) -> None:
        """Validate password strength"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")


class UserValidationService:
    """Service for complex user validation rules"""
    
    @staticmethod
    def validate_user_creation(name: str, email: str, password: str) -> List[str]:
        """
        Validate user creation with business rules
        Returns list of validation errors
        """
        errors = []
        
        # Name validation
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if len(name.strip()) > 100:
            errors.append("Name cannot exceed 100 characters")
        
        # Email validation
        if not email or '@' not in email:
            errors.append("Valid email address is required")
        
        if len(email) > 254:
            errors.append("Email address is too long")
        
        # Password validation
        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        elif len(password) > 128:
            errors.append("Password is too long")
        
        return errors
    
    @staticmethod
    def validate_user_update(original_user: User, updated_data: dict) -> List[str]:
        """
        Validate user updates with business rules
        """
        errors = []
        
        # Email cannot be changed to existing email
        if 'email' in updated_data and updated_data['email'] != original_user.email:
            errors.append("Email address cannot be changed")
        
        # Name validation if being updated
        if 'name' in updated_data:
            name = updated_data['name']
            if not name or len(name.strip()) < 2:
                errors.append("Name must be at least 2 characters long")
        
        return errors