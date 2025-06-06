"""
Tests for Users domain layer
"""
import pytest
from datetime import datetime, timedelta
from apps.users.domain.entities import User, UserStatus


class TestUserEntity:
    """Test User domain entity"""
    
    def test_user_creation(self):
        """Test user creation with valid data"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip="192.168.1.1",
            failed_login_attempts=0,
            account_locked_until=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert user.name == "Carlos Rodriguez"
        assert user.email == "carlos.rodriguez@company.com"
        assert user.status == UserStatus.ACTIVE
        assert user.is_active()
        assert not user.is_account_locked()
    
    def test_user_validation_short_name(self):
        """Test user validation with short name"""
        with pytest.raises(ValueError, match="User name must be at least 2 characters long"):
            User(
                id="123",
                name="A",
                email="carlos.rodriguez@company.com",
                password_hash="hashed_password",
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                last_login_ip=None,
                failed_login_attempts=0,
                account_locked_until=None
            )
    
    def test_user_validation_invalid_email(self):
        """Test user validation with invalid email"""
        with pytest.raises(ValueError, match="Valid email address is required"):
            User(
                id="123",
                name="Carlos Rodriguez",
                email="invalid-email",
                password_hash="hashed_password",
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                last_login_ip=None,
                failed_login_attempts=0,
                account_locked_until=None
            )
    
    def test_lock_account(self):
        """Test account locking"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        user.lock_account(30)
        
        assert user.is_account_locked()
        assert user.status == UserStatus.SUSPENDED
        assert user.account_locked_until is not None
    
    def test_lock_already_locked_account_raises_error(self):
        """Test locking already locked account raises error"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.SUSPENDED,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=datetime.now() + timedelta(minutes=30)
        )
        
        with pytest.raises(ValueError, match="Account is already locked"):
            user.lock_account(30)
    
    def test_unlock_account(self):
        """Test account unlocking"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.SUSPENDED,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=3,
            account_locked_until=datetime.now() + timedelta(minutes=30)
        )
        
        user.unlock_account()
        
        assert not user.is_account_locked()
        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None
        assert user.status == UserStatus.ACTIVE
    
    def test_increment_failed_login(self):
        """Test incrementing failed login attempts"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        for i in range(4):
            user.increment_failed_login()
            assert not user.is_account_locked()
        
        user.increment_failed_login()
        assert user.is_account_locked()
        assert user.failed_login_attempts == 5
    
    def test_verify_email(self):
        """Test email verification"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.PENDING_VERIFICATION,
            is_email_verified=False,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        user.verify_email()
        
        assert user.is_email_verified
        assert user.status == UserStatus.ACTIVE
    
    def test_verify_already_verified_email_raises_error(self):
        """Test verifying already verified email raises error"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        with pytest.raises(ValueError, match="Email is already verified"):
            user.verify_email()
    
    def test_activate_user(self):
        """Test user activation"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.INACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        user.activate()
        
        assert user.status == UserStatus.ACTIVE
        assert user.is_active()
    
    def test_activate_user_without_verified_email_raises_error(self):
        """Test activating user without verified email raises error"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.INACTIVE,
            is_email_verified=False,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        with pytest.raises(ValueError, match="Cannot activate user with unverified email"):
            user.activate()
    
    def test_deactivate_user(self):
        """Test user deactivation"""
        user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        user.deactivate()
        
        assert user.status == UserStatus.INACTIVE
        assert not user.is_active()
    
    def test_can_login(self):
        """Test login capability check"""
        active_user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        assert active_user.can_login()
        
        inactive_user = User(
            id="124",
            name="Maria Gonzalez",
            email="maria.gonzalez@company.com",
            password_hash="hashed_password",
            status=UserStatus.INACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        assert not inactive_user.can_login()
        
        locked_user = User(
            id="125",
            name="Roberto Silva",
            email="roberto.silva@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=datetime.now() + timedelta(minutes=30)
        )
        
        assert not locked_user.can_login()
    
    def test_get_security_level(self):
        """Test security level assessment"""
        normal_user = User(
            id="123",
            name="Carlos Rodriguez",
            email="carlos.rodriguez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        assert normal_user.get_security_level() == "NORMAL"
        
        locked_user = User(
            id="124",
            name="Maria Gonzalez",
            email="maria.gonzalez@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=datetime.now() + timedelta(minutes=30)
        )
        
        assert locked_user.get_security_level() == "LOCKED"
        
        high_risk_user = User(
            id="125",
            name="Roberto Silva",
            email="roberto.silva@company.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            last_login_ip=None,
            failed_login_attempts=4,
            account_locked_until=None
        )
        
        assert high_risk_user.get_security_level() == "HIGH_RISK"
        
        unverified_user = User(
            id="126",
            name="Ana Martinez",
            email="ana.martinez@company.com",
            password_hash="hashed_password",
            status=UserStatus.PENDING_VERIFICATION,
            is_email_verified=False,
            last_login_ip=None,
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        assert unverified_user.get_security_level() == "UNVERIFIED"