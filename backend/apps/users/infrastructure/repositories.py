"""
Django implementation of user repositories
"""
from typing import List, Optional
from django.db.models import Q, Count
from django.utils import timezone

from ..domain.entities import User, UserFilter, UserStatistics, UserStatus
from ..domain.repositories import UserRepository, UserQueryRepository
from .models import UserModel
from .mappers import UserMapper


class DjangoUserRepository(UserRepository):
    """Django implementation of UserRepository"""
    
    def __init__(self):
        self._mapper = UserMapper()
    
    def save(self, user: User) -> User:
        """Save a user and return the saved entity"""
        if user.id:
            # Update existing user
            try:
                model = UserModel.objects.get(id=user.id)
                self._mapper.update_model_from_entity(model, user)
            except UserModel.DoesNotExist:
                raise ValueError(f"User with ID {user.id} not found")
        else:
            # Create new user
            model = self._mapper.entity_to_model(user)
        
        model.save()
        return self._mapper.model_to_entity(model)
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find a user by their ID"""
        try:
            model = UserModel.objects.get(id=user_id)
            return self._mapper.model_to_entity(model)
        except UserModel.DoesNotExist:
            return None
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by their email address"""
        try:
            model = UserModel.objects.get(email=email.lower())
            return self._mapper.model_to_entity(model)
        except UserModel.DoesNotExist:
            return None
    
    def find_with_filter(self, user_filter: UserFilter) -> List[User]:
        """Find users with filtering criteria"""
        queryset = UserModel.objects.all()
        
        # Apply filters
        if user_filter.status:
            queryset = queryset.filter(status=user_filter.status.value)
        
        if user_filter.is_email_verified is not None:
            queryset = queryset.filter(is_email_verified=user_filter.is_email_verified)
        
        if user_filter.is_locked is not None:
            if user_filter.is_locked:
                queryset = queryset.filter(
                    account_locked_until__gt=timezone.now()
                )
            else:
                queryset = queryset.filter(
                    Q(account_locked_until__isnull=True) |
                    Q(account_locked_until__lte=timezone.now())
                )
        
        if user_filter.search_term:
            queryset = queryset.filter(
                Q(name__icontains=user_filter.search_term) |
                Q(email__icontains=user_filter.search_term)
            )
        
        if user_filter.created_after:
            queryset = queryset.filter(created_at__gte=user_filter.created_after)
        
        if user_filter.created_before:
            queryset = queryset.filter(created_at__lte=user_filter.created_before)
        
        # Order results
        queryset = queryset.order_by('-created_at')
        
        return [self._mapper.model_to_entity(model) for model in queryset]
    
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID, return True if deleted"""
        try:
            user = UserModel.objects.get(id=user_id)
            user.delete()
            return True
        except UserModel.DoesNotExist:
            return False
    
    def exists_by_email(self, email: str) -> bool:
        """Check if a user exists with the given email"""
        return UserModel.objects.filter(email=email.lower()).exists()
    
    def get_statistics(self) -> UserStatistics:
        """Get user statistics"""
        queryset = UserModel.objects.all()
        
        stats = queryset.aggregate(
            total_users=Count('id'),
            active_users=Count('id', filter=Q(status=UserModel.Status.ACTIVE)),
            inactive_users=Count('id', filter=Q(status=UserModel.Status.INACTIVE)),
            verified_users=Count('id', filter=Q(is_email_verified=True)),
        )
        
        # Calculate locked users
        locked_count = queryset.filter(
            account_locked_until__gt=timezone.now()
        ).count()
        
        users_with_tasks = 0
        
        return UserStatistics(
            total_users=stats['total_users'],
            active_users=stats['active_users'],
            inactive_users=stats['inactive_users'],
            verified_users=stats['verified_users'],
            locked_users=locked_count,
            users_with_tasks=users_with_tasks
        )
    
    def find_locked_users(self) -> List[User]:
        """Find all currently locked users"""
        models = UserModel.objects.filter(
            account_locked_until__gt=timezone.now()
        ).order_by('account_locked_until')
        
        return [self._mapper.model_to_entity(model) for model in models]
    
    def find_users_with_failed_attempts(self, min_attempts: int = 3) -> List[User]:
        """Find users with multiple failed login attempts"""
        models = UserModel.objects.filter(
            failed_login_attempts__gte=min_attempts
        ).order_by('-failed_login_attempts')
        
        return [self._mapper.model_to_entity(model) for model in models]


class DjangoUserQueryRepository(UserQueryRepository):
    """Django implementation for complex user queries"""
    
    def __init__(self):
        self._mapper = UserMapper()
    
    def get_recent_users(self, limit: int = 10) -> List[User]:
        """Get recently registered users"""
        models = UserModel.objects.order_by('-created_at')[:limit]
        
        return [self._mapper.model_to_entity(model) for model in models]
    
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return UserModel.objects.filter(
            status=UserModel.Status.ACTIVE,
            is_email_verified=True
        ).count()
    
    def search_users(self, search_term: str) -> List[User]:
        """Search users by name or email"""
        models = UserModel.objects.filter(
            Q(name__icontains=search_term) |
            Q(email__icontains=search_term)
        ).order_by('name')
        
        return [self._mapper.model_to_entity(model) for model in models]
    
    def get_users_by_registration_date(self, start_date, end_date) -> List[User]:
        """Get users registered within a date range"""
        models = UserModel.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('-created_at')
        
        return [self._mapper.model_to_entity(model) for model in models]