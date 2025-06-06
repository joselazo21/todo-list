"""
Authentication repository interfaces - Abstract contracts for auth data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .entities import AuthToken, LoginAttempt, AuthSession, PasswordResetRequest, SecurityEvent


class AuthTokenRepository(ABC):
    """Abstract repository for authentication tokens"""
    
    @abstractmethod
    def save_token(self, token: AuthToken) -> AuthToken:
        """Save an authentication token"""
        pass
    
    @abstractmethod
    def find_token(self, token: str) -> Optional[AuthToken]:
        """Find a token by its value"""
        pass
    
    @abstractmethod
    def find_tokens_by_user(self, user_id: str) -> List[AuthToken]:
        """Find all tokens for a user"""
        pass
    
    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        pass
    
    @abstractmethod
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user"""
        pass
    
    @abstractmethod
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens"""
        pass


class LoginAttemptRepository(ABC):
    """Abstract repository for login attempts"""
    
    @abstractmethod
    def save_attempt(self, attempt: LoginAttempt) -> LoginAttempt:
        """Save a login attempt"""
        pass
    
    @abstractmethod
    def find_recent_attempts(self, email: str, minutes: int = 15) -> List[LoginAttempt]:
        """Find recent login attempts for an email"""
        pass
    
    @abstractmethod
    def find_attempts_by_ip(self, ip_address: str, minutes: int = 60) -> List[LoginAttempt]:
        """Find recent login attempts from an IP"""
        pass
    
    @abstractmethod
    def get_failed_attempts_count(self, email: str, minutes: int = 15) -> int:
        """Get count of failed attempts for email in time window"""
        pass


class AuthSessionRepository(ABC):
    """Abstract repository for authentication sessions"""
    
    @abstractmethod
    def save_session(self, session: AuthSession) -> AuthSession:
        """Save an authentication session"""
        pass
    
    @abstractmethod
    def find_session(self, session_id: str) -> Optional[AuthSession]:
        """Find a session by ID"""
        pass
    
    @abstractmethod
    def find_user_sessions(self, user_id: str) -> List[AuthSession]:
        """Find all active sessions for a user"""
        pass
    
    @abstractmethod
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a session"""
        pass
    
    @abstractmethod
    def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user"""
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        pass


class PasswordResetRepository(ABC):
    """Abstract repository for password reset requests"""
    
    @abstractmethod
    def save_request(self, request: PasswordResetRequest) -> PasswordResetRequest:
        """Save a password reset request"""
        pass
    
    @abstractmethod
    def find_request(self, token: str) -> Optional[PasswordResetRequest]:
        """Find a reset request by token"""
        pass
    
    @abstractmethod
    def find_user_requests(self, user_id: str) -> List[PasswordResetRequest]:
        """Find all reset requests for a user"""
        pass
    
    @abstractmethod
    def mark_request_used(self, token: str) -> bool:
        """Mark a reset request as used"""
        pass
    
    @abstractmethod
    def cleanup_expired_requests(self) -> int:
        """Remove expired reset requests"""
        pass


class SecurityEventRepository(ABC):
    """Abstract repository for security events"""
    
    @abstractmethod
    def save_event(self, event: SecurityEvent) -> SecurityEvent:
        """Save a security event"""
        pass
    
    @abstractmethod
    def find_user_events(self, user_id: str, limit: int = 50) -> List[SecurityEvent]:
        """Find security events for a user"""
        pass
    
    @abstractmethod
    def find_critical_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Find critical security events in time window"""
        pass
    
    @abstractmethod
    def find_events_by_ip(self, ip_address: str, hours: int = 24) -> List[SecurityEvent]:
        """Find security events from an IP address"""
        pass