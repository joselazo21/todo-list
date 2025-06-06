"""
Data Transfer Objects for Task application layer
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..domain.entities import Task, TaskPriority, TaskStatus


@dataclass
class CreateTaskDTO:
    """DTO for task creation"""
    title: str
    description: str
    priority: str
    due_date: Optional[datetime]
    user_id: str
    
    def to_priority_enum(self) -> TaskPriority:
        """Convert string priority to enum"""
        priority_map = {
            'low': TaskPriority.LOW,
            'medium': TaskPriority.MEDIUM,
            'high': TaskPriority.HIGH,
            'urgent': TaskPriority.URGENT
        }
        return priority_map.get(self.priority.lower(), TaskPriority.MEDIUM)


@dataclass
class UpdateTaskDTO:
    """DTO for task updates"""
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    
    def to_priority_enum(self) -> Optional[TaskPriority]:
        """Convert string priority to enum"""
        if not self.priority:
            return None
        
        priority_map = {
            'low': TaskPriority.LOW,
            'medium': TaskPriority.MEDIUM,
            'high': TaskPriority.HIGH,
            'urgent': TaskPriority.URGENT
        }
        return priority_map.get(self.priority.lower())
    
    def to_status_enum(self) -> Optional[TaskStatus]:
        """Convert string status to enum"""
        if not self.status:
            return None
        
        status_map = {
            'pending': TaskStatus.PENDING,
            'in_progress': TaskStatus.IN_PROGRESS,
            'completed': TaskStatus.COMPLETED,
            'cancelled': TaskStatus.CANCELLED
        }
        return status_map.get(self.status.lower())


@dataclass
class TaskDTO:
    """DTO for task representation"""
    id: str
    title: str
    description: str
    priority: str
    status: str
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_overdue: bool
    days_until_due: Optional[int]
    
    @classmethod
    def from_entity(cls, task: Task) -> 'TaskDTO':
        """Create DTO from domain entity"""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority.value,
            status=task.status.value,
            due_date=task.due_date,
            completed_at=task.completed_at,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_overdue=task.is_overdue(),
            days_until_due=task.days_until_due()
        )


@dataclass
class TaskFilterDTO:
    """DTO for task filtering"""
    user_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    overdue_only: bool = False
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    search_term: Optional[str] = None


@dataclass
class BulkCompleteTasksDTO:
    """DTO for bulk task completion"""
    task_ids: list[str]
    user_id: str  # For authorization


@dataclass
class TaskStatisticsDTO:
    """DTO for task statistics"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    high_priority_tasks: int
    completion_rate: float
    
    @classmethod
    def from_domain(cls, stats) -> 'TaskStatisticsDTO':
        """Create DTO from domain statistics"""
        return cls(
            total_tasks=stats.total_tasks,
            completed_tasks=stats.completed_tasks,
            pending_tasks=stats.pending_tasks,
            overdue_tasks=stats.overdue_tasks,
            high_priority_tasks=stats.high_priority_tasks,
            completion_rate=stats.completion_rate
        )


@dataclass
class ProductivityDTO:
    """DTO for user productivity metrics"""
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    average_completion_time: float
    productivity_score: float


@dataclass
class TaskSuggestionDTO:
    """DTO for task suggestions"""
    reason: str
    suggestion: str