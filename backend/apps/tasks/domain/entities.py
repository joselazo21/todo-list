"""
Task domain entities - Pure business logic without framework dependencies
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task domain entity with business logic"""
    id: Optional[str]
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate entity after initialization"""
        self._validate()
    
    def _validate(self):
        """Business validation rules"""
        if not self.title or len(self.title.strip()) < 3:
            raise ValueError("Task title must be at least 3 characters long")
        
        if self.due_date and self.due_date < datetime.now():
            if not self.id:  # Only for new tasks
                raise ValueError("Due date cannot be in the past")
    
    def mark_as_completed(self) -> None:
        """Mark task as completed - business rule"""
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Task is already completed")
        
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_as_pending(self) -> None:
        """Mark task as pending - business rule"""
        if self.status == TaskStatus.PENDING:
            raise ValueError("Task is already pending")
        
        self.status = TaskStatus.PENDING
        self.completed_at = None
    
    def update_priority(self, new_priority: TaskPriority) -> None:
        """Update task priority with business validation"""
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Cannot change priority of completed task")
        
        self.priority = new_priority
    
    def is_overdue(self) -> bool:
        """Check if task is overdue - business logic"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return datetime.now() > self.due_date
    
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now()
        return delta.days
    
    def is_high_priority(self) -> bool:
        """Check if task has high priority"""
        return self.priority in [TaskPriority.HIGH, TaskPriority.URGENT]
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED


@dataclass
class TaskFilter:
    """Value object for task filtering"""
    user_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    overdue_only: bool = False
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    search_term: Optional[str] = None


@dataclass
class TaskStatistics:
    """Value object for task statistics"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    high_priority_tasks: int
    completion_rate: float
    
    @classmethod
    def calculate(cls, tasks: list[Task]) -> 'TaskStatistics':
        """Calculate statistics from task list"""
        total = len(tasks)
        completed = sum(1 for task in tasks if task.is_completed)
        pending = total - completed
        overdue = sum(1 for task in tasks if task.is_overdue())
        high_priority = sum(1 for task in tasks if task.is_high_priority())
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return cls(
            total_tasks=total,
            completed_tasks=completed,
            pending_tasks=pending,
            overdue_tasks=overdue,
            high_priority_tasks=high_priority,
            completion_rate=completion_rate
        )