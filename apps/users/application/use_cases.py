"""
User use cases - Application layer orchestrating business logic
"""
from typing import List, Optional
from datetime import datetime

from ..domain.entities import User, UserStatus, UserFilter
from ..domain.repositories import UserRepository
from ..domain.services import UserDomainService, UserValidationService
from .dto import (
    CreateUserDTO, UpdateUserDTO, UserDTO, UserFilterDTO,
    ChangePasswordDTO, UserStatisticsDTO, SecurityRecommendationDTO,
    EmailVerificationDTO
)


class CreateUserUseCase:
    """Use case for creating a new user"""
    
    def __init__(self, user_repository: UserRepository, domain_service: UserDomainService):
        self._user_repository = user_repository
        self._domain_service = domain_service
        self._validation_service = UserValidationService()
    
    def execute(self, dto: CreateUserDTO) -> UserDTO:
        """Execute user creation"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
        
        # Additional business validation
        business_errors = self._validation_service.validate_user_creation(
            dto.name, dto.email, dto.password
        )
        if business_errors:
            raise ValueError(f"Business validation failed: {', '.join(business_errors)}")
        
        # Use domain service to register user
        user = self._domain_service.register_new_user(dto.name, dto.email, dto.password)
        
        return UserDTO.from_entity(user)


class UpdateUserUseCase:
    """Use case for updating an existing user"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self._validation_service = UserValidationService()
    
    def execute(self, dto: UpdateUserDTO) -> UserDTO:
        """Execute user update"""
        # Find existing user
        existing_user = self._user_repository.find_by_id(dto.user_id)
        if not existing_user:
            raise ValueError(f"User with ID {dto.user_id} not found")
        
        # Prepare update data
        update_data = {}
        if dto.name is not None:
            update_data['name'] = dto.name
        if dto.email is not None:
            update_data['email'] = dto.email
        if dto.status is not None:
            update_data['status'] = dto.status
        
        # Validate business rules
        validation_errors = self._validation_service.validate_user_update(existing_user, update_data)
        if validation_errors:
            raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
        
        # Apply updates
        if dto.name is not None:
            existing_user.name = dto.name.strip()
        
        if dto.status is not None:
            new_status = dto.to_status_enum()
            if new_status == UserStatus.ACTIVE:
                existing_user.activate()
            elif new_status == UserStatus.INACTIVE:
                existing_user.deactivate()
        
        existing_user.updated_at = datetime.now()
        
        # Save updated user
        saved_user = self._user_repository.save(existing_user)
        
        return UserDTO.from_entity(saved_user)


class GetUserUseCase:
    """Use case for retrieving a single user"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self, user_id: str) -> Optional[UserDTO]:
        """Execute user retrieval"""
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            return None
        
        return UserDTO.from_entity(user)


class GetUserByEmailUseCase:
    """Use case for retrieving a user by email"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self, email: str) -> Optional[UserDTO]:
        """Execute user retrieval by email"""
        user = self._user_repository.find_by_email(email.lower())
        
        if not user:
            return None
        
        return UserDTO.from_entity(user)


class ListUsersUseCase:
    """Use case for listing users with filtering"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self, dto: UserFilterDTO) -> List[UserDTO]:
        """Execute user listing with filters"""
        # Convert DTO to domain filter
        domain_filter = UserFilter(
            status=UserStatus(dto.status) if dto.status else None,
            is_email_verified=dto.is_email_verified,
            is_locked=dto.is_locked,
            search_term=dto.search_term,
            created_after=dto.created_after,
            created_before=dto.created_before
        )
        
        # Get filtered users
        users = self._user_repository.find_with_filter(domain_filter)
        
        # Convert to DTOs
        return [UserDTO.from_entity(user) for user in users]


class DeleteUserUseCase:
    """Use case for deleting a user"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self, user_id: str) -> bool:
        """Execute user deletion"""
        # Check if user exists
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Business rule: Cannot delete active users with tasks
        # This would require checking with task repository
        # For now, we'll just delete
        
        return self._user_repository.delete(user_id)


class ChangePasswordUseCase:
    """Use case for changing user password"""
    
    def __init__(self, user_repository: UserRepository, domain_service: UserDomainService):
        self._user_repository = user_repository
        self._domain_service = domain_service
    
    def execute(self, dto: ChangePasswordDTO) -> UserDTO:
        """Execute password change"""
        # Validate input
        validation_errors = dto.validate()
        if validation_errors:
            raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
        
        # Use domain service to change password
        user = self._domain_service.change_password(
            dto.user_id, dto.current_password, dto.new_password
        )
        
        return UserDTO.from_entity(user)


class VerifyEmailUseCase:
    """Use case for email verification"""
    
    def __init__(self, user_repository: UserRepository, domain_service: UserDomainService):
        self._user_repository = user_repository
        self._domain_service = domain_service
    
    def execute(self, dto: EmailVerificationDTO) -> UserDTO:
        """Execute email verification"""
        # Use domain service to verify email
        user = self._domain_service.verify_email_with_token(dto.user_id, dto.token)
        
        return UserDTO.from_entity(user)


class UnlockAccountUseCase:
    """Use case for unlocking user account"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self, user_id: str) -> UserDTO:
        """Execute account unlock"""
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.unlock_account()
        saved_user = self._user_repository.save(user)
        
        return UserDTO.from_entity(saved_user)


class GetUserStatisticsUseCase:
    """Use case for getting user statistics"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self) -> UserStatisticsDTO:
        """Execute statistics retrieval"""
        stats = self._user_repository.get_statistics()
        return UserStatisticsDTO.from_domain(stats)


class GetSecurityRecommendationsUseCase:
    """Use case for getting user security recommendations"""
    
    def __init__(self, user_repository: UserRepository, domain_service: UserDomainService):
        self._user_repository = user_repository
        self._domain_service = domain_service
    
    def execute(self, user_id: str) -> List[SecurityRecommendationDTO]:
        """Execute security recommendations retrieval"""
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        recommendations = self._domain_service.get_security_recommendations(user)
        
        return [
            SecurityRecommendationDTO(
                type=rec['type'],
                priority=rec['priority'],
                message=rec['message']
            )
            for rec in recommendations
        ]


class UnlockExpiredAccountsUseCase:
    """Use case for unlocking expired account locks"""
    
    def __init__(self, user_repository: UserRepository, domain_service: UserDomainService):
        self._user_repository = user_repository
        self._domain_service = domain_service
    
    def execute(self) -> List[UserDTO]:
        """Execute expired account unlocking"""
        unlocked_users = self._domain_service.unlock_expired_accounts()
        
        return [UserDTO.from_entity(user) for user in unlocked_users]