"""
Infrastructure implementations of authentication repositories
"""
from typing import Optional, List
from datetime import datetime, timedelta
from django.core.cache import cache
from django.contrib.auth import get_user_model

from ..domain.repositories import (
    AuthTokenRepository, LoginAttemptRepository, AuthSessionRepository,
    PasswordResetRepository, SecurityEventRepository
)
from ..domain.entities import (
    AuthToken, LoginAttempt, AuthSession, PasswordResetRequest, SecurityEvent
)

User = get_user_model()


class CacheAuthTokenRepository(AuthTokenRepository):
    """Cache-based implementation of AuthTokenRepository"""
    
    def save_token(self, token: AuthToken) -> AuthToken:
        """Save token to cache"""
        cache_key = f"auth_token:{token.token}"
        cache.set(cache_key, token, timeout=int((token.expires_at - datetime.now()).total_seconds()))
        
        # Also track user tokens
        user_tokens_key = f"user_tokens:{token.user_id}"
        user_tokens = cache.get(user_tokens_key, [])
        if token.token not in user_tokens:
            user_tokens.append(token.token)
            cache.set(user_tokens_key, user_tokens, timeout=86400 * 7)  # 7 days
        
        return token
    
    def find_token(self, token: str) -> Optional[AuthToken]:
        """Find token in cache"""
        cache_key = f"auth_token:{token}"
        return cache.get(cache_key)
    
    def find_tokens_by_user(self, user_id: str) -> List[AuthToken]:
        """Find all tokens for a user"""
        # This is a simplified implementation
        # In a real scenario, you'd need to track user tokens
        user_tokens_key = f"user_tokens:{user_id}"
        token_list = cache.get(user_tokens_key, [])
        
        tokens = []
        for token_str in token_list:
            token = self.find_token(token_str)
            if token and token.is_valid():
                tokens.append(token)
        
        return tokens
    
    def revoke_token(self, token: str) -> bool:
        """Revoke token by removing from cache"""
        cache_key = f"auth_token:{token}"
        cache.delete(cache_key)
        return True
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user"""
        user_tokens_key = f"user_tokens:{user_id}"
        token_list = cache.get(user_tokens_key, [])
        
        revoked_count = 0
        for token_str in token_list:
            if self.revoke_token(token_str):
                revoked_count += 1
        
        # Clear user tokens list
        cache.delete(user_tokens_key)
        
        return revoked_count
    
    def cleanup_expired_tokens(self) -> int:
        """Cleanup expired tokens (handled automatically by cache TTL)"""
        return 0


class CacheLoginAttemptRepository(LoginAttemptRepository):
    """Cache-based implementation of LoginAttemptRepository"""
    
    def save_attempt(self, attempt: LoginAttempt) -> LoginAttempt:
        """Save login attempt to cache"""
        attempt_id = f"attempt_{datetime.now().timestamp()}"
        attempt.id = attempt_id
        
        # Store by IP
        ip_key = f"login_attempts_ip:{attempt.ip_address}"
        ip_attempts = cache.get(ip_key, [])
        ip_attempts.append(attempt)
        cache.set(ip_key, ip_attempts, timeout=3600)  # 1 hour
        
        # Store by email
        email_key = f"login_attempts_email:{attempt.email}"
        email_attempts = cache.get(email_key, [])
        email_attempts.append(attempt)
        cache.set(email_key, email_attempts, timeout=3600)  # 1 hour
        
        return attempt
    
    def find_recent_attempts(self, email: str, minutes: int = 15) -> List[LoginAttempt]:
        """Find recent login attempts for an email"""
        return self.find_attempts_by_email(email, minutes)
    
    def find_attempts_by_ip(self, ip_address: str, window_minutes: int) -> List[LoginAttempt]:
        """Find login attempts by IP address within time window"""
        cache_key = f"login_attempts_ip:{ip_address}"
        attempts = cache.get(cache_key, [])
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        return [a for a in attempts if a.attempted_at >= cutoff_time]
    
    def find_attempts_by_email(self, email: str, window_minutes: int) -> List[LoginAttempt]:
        """Find login attempts by email within time window"""
        cache_key = f"login_attempts_email:{email}"
        attempts = cache.get(cache_key, [])
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        return [a for a in attempts if a.attempted_at >= cutoff_time]
    
    def get_failed_attempts_count(self, email: str, window_minutes: int) -> int:
        """Get count of failed attempts for email"""
        attempts = self.find_attempts_by_email(email, window_minutes)
        return len([a for a in attempts if not a.success])


class CacheAuthSessionRepository(AuthSessionRepository):
    """Cache-based implementation of AuthSessionRepository"""
    
    def save_session(self, session: AuthSession) -> AuthSession:
        """Save session to cache"""
        cache_key = f"auth_session:{session.session_id}"
        timeout = int((session.expires_at - datetime.now()).total_seconds())
        cache.set(cache_key, session, timeout=timeout)
        
        # Also track user sessions
        user_sessions_key = f"user_sessions:{session.user_id}"
        user_sessions = cache.get(user_sessions_key, [])
        if session.session_id not in user_sessions:
            user_sessions.append(session.session_id)
            cache.set(user_sessions_key, user_sessions, timeout=86400)  # 24 hours
        
        return session
    
    def find_session(self, session_id: str) -> Optional[AuthSession]:
        """Find session by ID"""
        cache_key = f"auth_session:{session_id}"
        return cache.get(cache_key)
    
    def find_user_sessions(self, user_id: str) -> List[AuthSession]:
        """Find all sessions for a user"""
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = cache.get(user_sessions_key, [])
        
        sessions = []
        for session_id in session_ids:
            session = self.find_session(session_id)
            if session and session.is_valid():
                sessions.append(session)
        
        return sessions
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a specific session"""
        cache_key = f"auth_session:{session_id}"
        session = cache.get(cache_key)
        if session:
            session.is_active = False
            cache.set(cache_key, session, timeout=60)  # Keep for a minute for cleanup
        return True
    
    def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user"""
        sessions = self.find_user_sessions(user_id)
        for session in sessions:
            self.terminate_session(session.session_id)
        
        # Clear user sessions list
        user_sessions_key = f"user_sessions:{user_id}"
        cache.delete(user_sessions_key)
        
        return len(sessions)
    
    def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions (handled automatically by cache TTL)"""
        return 0


class CachePasswordResetRepository(PasswordResetRepository):
    """Cache-based implementation of PasswordResetRepository"""
    
    def save_request(self, request: PasswordResetRequest) -> PasswordResetRequest:
        """Save password reset request to cache"""
        cache_key = f"password_reset:{request.token}"
        timeout = int((request.expires_at - datetime.now()).total_seconds())
        cache.set(cache_key, request, timeout=timeout)
        return request
    
    def find_request(self, token: str) -> Optional[PasswordResetRequest]:
        """Find password reset request by token"""
        cache_key = f"password_reset:{token}"
        return cache.get(cache_key)
    
    def find_user_requests(self, user_id: str) -> List[PasswordResetRequest]:
        """Find all reset requests for a user"""
        # This is a simplified implementation
        # In a real scenario, you'd need better indexing
        return []
    
    def mark_request_used(self, token: str) -> bool:
        """Mark a reset request as used"""
        return self.consume_request(token)
    
    def cleanup_expired_requests(self) -> int:
        """Remove expired reset requests (handled automatically by cache TTL)"""
        return 0
    
    def consume_request(self, token: str) -> bool:
        """Consume (delete) password reset request"""
        cache_key = f"password_reset:{token}"
        cache.delete(cache_key)
        return True


class CacheSecurityEventRepository(SecurityEventRepository):
    """Cache-based implementation of SecurityEventRepository"""
    
    def save_event(self, event: SecurityEvent) -> SecurityEvent:
        """Save security event to cache"""
        event_id = f"event_{datetime.now().timestamp()}"
        event.id = event_id
        
        # Store individual event
        cache_key = f"security_event:{event_id}"
        cache.set(cache_key, event, timeout=86400 * 30)  # 30 days
        
        # Add to user events list
        if event.user_id:
            user_events_key = f"user_security_events:{event.user_id}"
            user_events = cache.get(user_events_key, [])
            user_events.append(event_id)
            # Keep only last 100 events
            if len(user_events) > 100:
                user_events = user_events[-100:]
            cache.set(user_events_key, user_events, timeout=86400 * 30)
        
        return event
    
    def find_user_events(self, user_id: str, limit: int = 50) -> List[SecurityEvent]:
        """Find security events for a user"""
        user_events_key = f"user_security_events:{user_id}"
        event_ids = cache.get(user_events_key, [])
        
        events = []
        for event_id in event_ids[-limit:]:  # Get last N events
            cache_key = f"security_event:{event_id}"
            event = cache.get(cache_key)
            if event:
                events.append(event)
        
        return sorted(events, key=lambda e: e.occurred_at, reverse=True)
    
    def find_critical_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Find critical security events in time window"""
        # This is a simplified implementation
        # In a real scenario, you'd need better indexing
        return []
    
    def find_events_by_ip(self, ip_address: str, hours: int = 24) -> List[SecurityEvent]:
        """Find security events from an IP address"""
        # This is a simplified implementation
        # In a real scenario, you'd need better indexing
        return []
    
    def find_events_by_type(self, event_type: str, limit: int = 50) -> List[SecurityEvent]:
        """Find security events by type"""
        # This is a simplified implementation
        # In a real scenario, you'd need better indexing
        return []