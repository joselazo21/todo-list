"""
Authentication domain services - Complex business logic for auth
"""
from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import hashlib
import jwt
from django.conf import settings

from .entities import (
    AuthToken, TokenType, LoginAttempt, AuthSession, PasswordResetRequest,
    SecurityEvent, AuthenticationResult, AuthenticationMethod
)
from .repositories import (
    AuthTokenRepository, LoginAttemptRepository, AuthSessionRepository,
    PasswordResetRepository, SecurityEventRepository
)


class AuthenticationDomainService:
    """Domain service for authentication business logic"""
    
    def __init__(
        self,
        token_repository: AuthTokenRepository,
        attempt_repository: LoginAttemptRepository,
        session_repository: AuthSessionRepository,
        security_repository: SecurityEventRepository
    ):
        self._token_repository = token_repository
        self._attempt_repository = attempt_repository
        self._session_repository = session_repository
        self._security_repository = security_repository
    
    def generate_jwt_tokens(self, user_id: str) -> tuple[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.now()
        
        # Generate access token
        access_payload = {
            'user_id': user_id,
            'token_type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=1),
            'jti': secrets.token_hex(16)
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Generate refresh token
        refresh_payload = {
            'user_id': user_id,
            'token_type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=7),
            'jti': secrets.token_hex(16)
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Store tokens in repository
        access_token_entity = AuthToken(
            token=access_token,
            token_type=TokenType.ACCESS,
            user_id=user_id,
            expires_at=now + timedelta(hours=1),
            created_at=now
        )
        
        refresh_token_entity = AuthToken(
            token=refresh_token,
            token_type=TokenType.REFRESH,
            user_id=user_id,
            expires_at=now + timedelta(days=7),
            created_at=now
        )
        
        self._token_repository.save_token(access_token_entity)
        self._token_repository.save_token(refresh_token_entity)
        
        return access_token, refresh_token
    
    def validate_jwt_token(self, token: str) -> Optional[dict]:
        """Validate JWT token and return payload"""
        try:
            # Check if token exists in repository
            token_entity = self._token_repository.find_token(token)
            if not token_entity or not token_entity.is_valid():
                return None
            
            # Decode JWT
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            # Mark token as revoked
            self._token_repository.revoke_token(token)
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token using refresh token"""
        # Validate refresh token
        payload = self.validate_jwt_token(refresh_token)
        if not payload or payload.get('token_type') != 'refresh':
            return None
        
        user_id = payload['user_id']
        
        # Generate new access token
        now = datetime.now()
        access_payload = {
            'user_id': user_id,
            'token_type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=1),
            'jti': secrets.token_hex(16)
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Store new access token
        access_token_entity = AuthToken(
            token=access_token,
            token_type=TokenType.ACCESS,
            user_id=user_id,
            expires_at=now + timedelta(hours=1),
            created_at=now
        )
        
        self._token_repository.save_token(access_token_entity)
        
        return access_token
    
    def record_login_attempt(
        self,
        email: str,
        ip_address: str,
        user_agent: Optional[str],
        success: bool,
        user_id: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> LoginAttempt:
        """Record a login attempt"""
        attempt = LoginAttempt(
            id=None,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            attempted_at=datetime.now(),
            method=AuthenticationMethod.PASSWORD
        )
        
        saved_attempt = self._attempt_repository.save_attempt(attempt)
        
        # Record security event if suspicious
        if attempt.is_suspicious():
            self._record_security_event(
                user_id=user_id,
                event_type='suspicious_login',
                description=f'Suspicious login attempt: {failure_reason}',
                ip_address=ip_address,
                user_agent=user_agent,
                severity='medium'
            )
        
        return saved_attempt
    
    def is_ip_rate_limited(self, ip_address: str, max_attempts: int = 10, window_minutes: int = 15) -> bool:
        """Check if IP address is rate limited"""
        attempts = self._attempt_repository.find_attempts_by_ip(ip_address, window_minutes)
        failed_attempts = [a for a in attempts if not a.success]
        
        return len(failed_attempts) >= max_attempts
    
    def is_email_rate_limited(self, email: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Check if email is rate limited"""
        failed_count = self._attempt_repository.get_failed_attempts_count(email, window_minutes)
        return failed_count >= max_attempts
    
    def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        duration_hours: int = 24
    ) -> AuthSession:
        """Create a new authentication session"""
        session = AuthSession(
            session_id=secrets.token_urlsafe(32),
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=duration_hours)
        )
        
        return self._session_repository.save_session(session)
    
    def validate_session(self, session_id: str) -> Optional[AuthSession]:
        """Validate and update session"""
        session = self._session_repository.find_session(session_id)
        
        if not session or not session.is_valid():
            return None
        
        # Update last activity
        session.update_activity()
        return self._session_repository.save_session(session)
    
    def logout_user(self, user_id: str, session_id: Optional[str] = None) -> None:
        """Logout user by terminating sessions and revoking tokens"""
        if session_id:
            # Terminate specific session
            self._session_repository.terminate_session(session_id)
        else:
            # Terminate all sessions
            self._session_repository.terminate_all_user_sessions(user_id)
        
        # Revoke all tokens
        self._token_repository.revoke_all_user_tokens(user_id)
        
        # Record security event
        self._record_security_event(
            user_id=user_id,
            event_type='user_logout',
            description='User logged out',
            ip_address='unknown',
            severity='low'
        )
    
    def generate_password_reset_token(self, user_id: str, email: str) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        
        reset_request = PasswordResetRequest(
            id=None,
            user_id=user_id,
            email=email,
            token=token,
            requested_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        # Save request (this would be implemented in infrastructure)
        # self._reset_repository.save_request(reset_request)
        
        return token
    
    def _record_security_event(
        self,
        user_id: Optional[str],
        event_type: str,
        description: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        severity: str = 'low',
        metadata: Optional[dict] = None
    ) -> SecurityEvent:
        """Record a security event"""
        event = SecurityEvent(
            id=None,
            user_id=user_id,
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            occurred_at=datetime.now(),
            metadata=metadata
        )
        
        return self._security_repository.save_event(event)
    
    def cleanup_expired_data(self) -> dict:
        """Cleanup expired tokens, sessions, and reset requests"""
        expired_tokens = self._token_repository.cleanup_expired_tokens()
        expired_sessions = self._session_repository.cleanup_expired_sessions()
        
        return {
            'expired_tokens': expired_tokens,
            'expired_sessions': expired_sessions
        }


class AuthenticationValidationService:
    """Service for authentication validation rules"""
    
    @staticmethod
    def validate_login_request(email: str, password: str, ip_address: str) -> List[str]:
        """Validate login request"""
        errors = []
        
        if not email:
            errors.append("Email is required")
        elif '@' not in email:
            errors.append("Valid email address is required")
        
        if not password:
            errors.append("Password is required")
        
        if not ip_address:
            errors.append("IP address is required")
        
        return errors
    
    @staticmethod
    def validate_token_request(token: str) -> List[str]:
        """Validate token request"""
        errors = []
        
        if not token:
            errors.append("Token is required")
        elif len(token) < 10:
            errors.append("Invalid token format")
        
        return errors