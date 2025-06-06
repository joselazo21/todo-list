"""
Task repository interfaces - Abstract contracts for data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Task, TaskFilter, TaskStatistics


class TaskRepository(ABC):
    """Abstract repository for task persistence"""
    
    @abstractmethod
    def save(self, task: Task) -> Task:
        """Save a task and return the saved entity"""
        pass
    
    @abstractmethod
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by its ID"""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[Task]:
        """Find all tasks for a specific user"""
        pass
    
    @abstractmethod
    def find_with_filter(self, task_filter: TaskFilter) -> List[Task]:
        """Find tasks with filtering criteria"""
        pass
    
    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """Delete a task by ID, return True if deleted"""
        pass
    
    @abstractmethod
    def bulk_update_status(self, task_ids: List[str], status: str) -> int:
        """Bulk update task status, return number of updated tasks"""
        pass
    
    @abstractmethod
    def get_statistics(self, user_id: Optional[str] = None) -> TaskStatistics:
        """Get task statistics, optionally filtered by user"""
        pass
    
    @abstractmethod
    def exists(self, task_id: str) -> bool:
        """Check if a task exists"""
        pass


class TaskQueryRepository(ABC):
    """Separate repository for complex queries and read operations"""
    
    @abstractmethod
    def get_overdue_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        """Get all overdue tasks"""
        pass
    
    @abstractmethod
    def get_tasks_by_priority(self, priority: str, user_id: Optional[str] = None) -> List[Task]:
        """Get tasks filtered by priority"""
        pass
    
    @abstractmethod
    def get_recent_tasks(self, user_id: str, limit: int = 10) -> List[Task]:
        """Get recently created tasks for a user"""
        pass
    
    @abstractmethod
    def search_tasks(self, search_term: str, user_id: Optional[str] = None) -> List[Task]:
        """Search tasks by title or description"""
        pass