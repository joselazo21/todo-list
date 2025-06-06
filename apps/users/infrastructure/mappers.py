"""
Mappers between domain entities and Django models
"""
from ..domain.entities import User, UserStatus
from .models import UserModel


class UserMapper:
    """Mapper between User entity and UserModel"""
    
    def model_to_entity(self, model: UserModel) -> User:
        """Convert Django model to domain entity"""
        return User(
            id=str(model.id),
            name=model.name,
            email=model.email,
            password_hash=model.password,
            status=UserStatus(model.status),
            is_email_verified=model.is_email_verified,
            last_login_ip=model.last_login_ip,
            failed_login_attempts=model.failed_login_attempts,
            account_locked_until=model.account_locked_until,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    def entity_to_model(self, entity: User) -> UserModel:
        """Convert domain entity to Django model"""
        model = UserModel(
            name=entity.name,
            email=entity.email,
            password=entity.password_hash,
            status=entity.status.value,
            is_email_verified=entity.is_email_verified,
            last_login_ip=entity.last_login_ip,
            failed_login_attempts=entity.failed_login_attempts,
            account_locked_until=entity.account_locked_until,
            last_login=entity.last_login,
            is_active=entity.status == UserStatus.ACTIVE
        )
        
        if entity.id:
            model.id = entity.id
        
        return model
    
    def update_model_from_entity(self, model: UserModel, entity: User) -> None:
        """
        Update existing Django model with entity data.
        
        The created_at field is preserved and updated_at is automatically
        handled by Django's auto_now functionality.
        """
        model.name = entity.name
        model.email = entity.email
        model.password = entity.password_hash
        model.status = entity.status.value
        model.is_email_verified = entity.is_email_verified
        model.last_login_ip = entity.last_login_ip
        model.failed_login_attempts = entity.failed_login_attempts
        model.account_locked_until = entity.account_locked_until
        model.last_login = entity.last_login
        model.is_active = entity.status == UserStatus.ACTIVE