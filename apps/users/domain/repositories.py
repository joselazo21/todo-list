"""
User repository interfaces - Abstract contracts for data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import User, UserFilter, UserStatistics


class UserRepository(ABC):
    """Abstract repository for user persistence"""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user and return the saved entity"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find a user by their ID"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by their email address"""
        pass
    
    @abstractmethod
    def find_with_filter(self, user_filter: UserFilter) -> List[User]:
        """Find users with filtering criteria"""
        pass
    
    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID, return True if deleted"""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if a user exists with the given email"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> UserStatistics:
        """Get user statistics"""
        pass
    
    @abstractmethod
    def find_locked_users(self) -> List[User]:
        """Find all currently locked users"""
        pass
    
    @abstractmethod
    def find_users_with_failed_attempts(self, min_attempts: int = 3) -> List[User]:
        """Find users with multiple failed login attempts"""
        pass


class UserQueryRepository(ABC):
    """Separate repository for complex user queries and read operations"""
    
    @abstractmethod
    def get_recent_users(self, limit: int = 10) -> List[User]:
        """Get recently registered users"""
        pass
    
    @abstractmethod
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        pass
    
    @abstractmethod
    def search_users(self, search_term: str) -> List[User]:
        """Search users by name or email"""
        pass
    
    @abstractmethod
    def get_users_by_registration_date(self, start_date, end_date) -> List[User]:
        """Get users registered within a date range"""
        pass