"""
Authentication use cases - Application layer orchestrating auth business logic
"""
from typing import List, Optional
from datetime import datetime, timedelta

from ..domain.services import AuthenticationDomainService, AuthenticationValidationService
from ..domain.repositories import (
    AuthTokenRepository, LoginAttemptRepository, AuthSessionRepository, SecurityEventRepository
)
from ...users.domain.repositories import UserRepository
from ...users.domain.services import UserDomainService
from .dto import (
    LoginRequestDTO, LoginResponseDTO, RefreshTokenRequestDTO, RefreshTokenResponseDTO,
    LogoutRequestDTO, ValidateTokenRequestDTO, ValidateTokenResponseDTO,
    PasswordResetRequestDTO, PasswordResetResponseDTO, ResetPasswordRequestDTO,
    SessionDTO, SecurityEventDTO, LoginAttemptDTO
)


class LoginUseCase:
    """Use case for user authentication"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        user_domain_service: UserDomainService,
        auth_domain_service: AuthenticationDomainService
    ):
        self._user_repository = user_repository
        self._user_domain_service = user_domain_service
        self._auth_domain_service = auth_domain_service
        self._validation_service = AuthenticationValidationService()
    
    def execute(self, dto: LoginRequestDTO) -> LoginResponseDTO:
        """Execute user login"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            return LoginResponseDTO(
                success=False,
                error_message=f"Validation failed: {', '.join(validation_errors)}"
            )
        
        # Check rate limiting
        if self._auth_domain_service.is_ip_rate_limited(dto.ip_address):
            self._auth_domain_service.record_login_attempt(
                email=dto.email,
                ip_address=dto.ip_address,
                user_agent=dto.user_agent,
                success=False,
                failure_reason='ip_rate_limited'
            )
            return LoginResponseDTO(
                success=False,
                error_message="Too many login attempts from this IP address. Please try again later."
            )
        
        if self._auth_domain_service.is_email_rate_limited(dto.email):
            self._auth_domain_service.record_login_attempt(
                email=dto.email,
                ip_address=dto.ip_address,
                user_agent=dto.user_agent,
                success=False,
                failure_reason='email_rate_limited'
            )
            return LoginResponseDTO(
                success=False,
                error_message="Too many failed login attempts for this email. Please try again later."
            )
        
        try:
            # Authenticate user using domain service
            user = self._user_domain_service.authenticate_user(
                email=dto.email,
                password=dto.password,
                ip_address=dto.ip_address
            )
            
            if not user:
                # Record failed attempt
                self._auth_domain_service.record_login_attempt(
                    email=dto.email,
                    ip_address=dto.ip_address,
                    user_agent=dto.user_agent,
                    success=False,
                    failure_reason='invalid_credentials'
                )
                return LoginResponseDTO(
                    success=False,
                    error_message="Invalid email or password"
                )
            
            # Generate tokens
            access_token, refresh_token = self._auth_domain_service.generate_jwt_tokens(user.id)
            
            # Create session
            session = self._auth_domain_service.create_session(
                user_id=user.id,
                ip_address=dto.ip_address,
                user_agent=dto.user_agent
            )
            
            # Record successful attempt
            self._auth_domain_service.record_login_attempt(
                email=dto.email,
                ip_address=dto.ip_address,
                user_agent=dto.user_agent,
                success=True,
                user_id=user.id
            )
            
            return LoginResponseDTO(
                success=True,
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                session_id=session.session_id,
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
        except ValueError as e:
            error_message = str(e)
            failure_reason = 'account_locked' if 'locked' in error_message else 'account_inactive'
            
            # Record failed attempt
            self._auth_domain_service.record_login_attempt(
                email=dto.email,
                ip_address=dto.ip_address,
                user_agent=dto.user_agent,
                success=False,
                failure_reason=failure_reason
            )
            
            return LoginResponseDTO(
                success=False,
                error_message=error_message,
                account_locked='locked' in error_message,
                requires_verification='not verified' in error_message
            )


class RefreshTokenUseCase:
    """Use case for refreshing access tokens"""
    
    def __init__(self, auth_domain_service: AuthenticationDomainService):
        self._auth_domain_service = auth_domain_service
    
    def execute(self, dto: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        """Execute token refresh"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            return RefreshTokenResponseDTO(
                success=False,
                error_message=f"Validation failed: {', '.join(validation_errors)}"
            )
        
        # Refresh token
        new_access_token = self._auth_domain_service.refresh_access_token(dto.refresh_token)
        
        if not new_access_token:
            return RefreshTokenResponseDTO(
                success=False,
                error_message="Invalid or expired refresh token"
            )
        
        return RefreshTokenResponseDTO(
            success=True,
            access_token=new_access_token,
            expires_at=datetime.now() + timedelta(hours=1)
        )


class LogoutUseCase:
    """Use case for user logout"""
    
    def __init__(self, auth_domain_service: AuthenticationDomainService):
        self._auth_domain_service = auth_domain_service
    
    def execute(self, dto: LogoutRequestDTO) -> bool:
        """Execute user logout"""
        try:
            self._auth_domain_service.logout_user(
                user_id=dto.user_id,
                session_id=dto.session_id if not dto.revoke_all_sessions else None
            )
            return True
        except Exception:
            return False


class ValidateTokenUseCase:
    """Use case for token validation"""
    
    def __init__(self, auth_domain_service: AuthenticationDomainService):
        self._auth_domain_service = auth_domain_service
    
    def execute(self, dto: ValidateTokenRequestDTO) -> ValidateTokenResponseDTO:
        """Execute token validation"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            return ValidateTokenResponseDTO(
                valid=False,
                error_message=f"Validation failed: {', '.join(validation_errors)}"
            )
        
        # Validate token
        payload = self._auth_domain_service.validate_jwt_token(dto.token)
        
        if not payload:
            return ValidateTokenResponseDTO(
                valid=False,
                error_message="Invalid or expired token"
            )
        
        return ValidateTokenResponseDTO(
            valid=True,
            user_id=payload.get('user_id'),
            token_type=payload.get('token_type'),
            expires_at=datetime.fromtimestamp(payload.get('exp', 0))
        )


class PasswordResetRequestUseCase:
    """Use case for requesting password reset"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        auth_domain_service: AuthenticationDomainService
    ):
        self._user_repository = user_repository
        self._auth_domain_service = auth_domain_service
    
    def execute(self, dto: PasswordResetRequestDTO) -> PasswordResetResponseDTO:
        """Execute password reset request"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            return PasswordResetResponseDTO(
                success=False,
                message=f"Validation failed: {', '.join(validation_errors)}"
            )
        
        # Find user
        user = self._user_repository.find_by_email(dto.email)
        
        # Always return success for security (don't reveal if email exists)
        if not user:
            return PasswordResetResponseDTO(
                success=True,
                message="If the email address exists, a password reset link has been sent."
            )
        
        # Generate reset token
        token = self._auth_domain_service.generate_password_reset_token(user.id, user.email)
        
        # In a real implementation, you would send an email here
        # For now, we'll just return success
        
        return PasswordResetResponseDTO(
            success=True,
            message="If the email address exists, a password reset link has been sent.",
            token=token  # Only for testing - remove in production
        )


class ResetPasswordUseCase:
    """Use case for resetting password with token"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        user_domain_service: UserDomainService
    ):
        self._user_repository = user_repository
        self._user_domain_service = user_domain_service
    
    def execute(self, dto: ResetPasswordRequestDTO) -> bool:
        """Execute password reset"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
        
        # In a real implementation, you would validate the reset token here
        # For now, we'll assume the token is valid and extract user info
        
        # This is a simplified implementation
        # In reality, you'd look up the token in the password reset repository
        
        return True


class GetUserSessionsUseCase:
    """Use case for getting user sessions"""
    
    def __init__(self, session_repository: AuthSessionRepository):
        self._session_repository = session_repository
    
    def execute(self, user_id: str, current_session_id: Optional[str] = None) -> List[SessionDTO]:
        """Execute get user sessions"""
        sessions = self._session_repository.find_user_sessions(user_id)
        
        return [
            SessionDTO(
                session_id=session.session_id,
                user_id=session.user_id,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                created_at=session.created_at,
                last_activity=session.last_activity,
                expires_at=session.expires_at,
                is_active=session.is_active,
                is_current=session.session_id == current_session_id
            )
            for session in sessions
        ]


class GetSecurityEventsUseCase:
    """Use case for getting security events"""
    
    def __init__(self, security_repository: SecurityEventRepository):
        self._security_repository = security_repository
    
    def execute(self, user_id: str, limit: int = 50) -> List[SecurityEventDTO]:
        """Execute get security events"""
        events = self._security_repository.find_user_events(user_id, limit)
        
        return [
            SecurityEventDTO(
                id=event.id,
                user_id=event.user_id,
                event_type=event.event_type,
                description=event.description,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                severity=event.severity,
                occurred_at=event.occurred_at,
                metadata=event.metadata
            )
            for event in events
        ]


class CleanupExpiredDataUseCase:
    """Use case for cleaning up expired authentication data"""
    
    def __init__(self, auth_domain_service: AuthenticationDomainService):
        self._auth_domain_service = auth_domain_service
    
    def execute(self) -> dict:
        """Execute cleanup of expired data"""
        return self._auth_domain_service.cleanup_expired_data()