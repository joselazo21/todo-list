"""
Django implementation of task repositories
"""
from typing import List, Optional
from django.db.models import Q, Count, Case, When
from django.utils import timezone

from ..domain.entities import Task, TaskPriority, TaskStatus, TaskFilter, TaskStatistics
from ..domain.repositories import TaskRepository, TaskQueryRepository
from .models import TaskModel
from .mappers import TaskMapper


class DjangoTaskRepository(TaskRepository):
    """Django implementation of TaskRepository"""
    
    def __init__(self):
        self._mapper = TaskMapper()
    
    def save(self, task: Task) -> Task:
        """Save a task and return the saved entity"""
        if task.id:
            # Update existing task
            try:
                model = TaskModel.objects.get(id=task.id)
                self._mapper.update_model_from_entity(model, task)
            except TaskModel.DoesNotExist:
                raise ValueError(f"Task with ID {task.id} not found")
        else:
            # Create new task
            model = self._mapper.entity_to_model(task)
        
        model.save()
        return self._mapper.model_to_entity(model)
    
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by its ID"""
        try:
            model = TaskModel.objects.get(id=task_id)
            return self._mapper.model_to_entity(model)
        except TaskModel.DoesNotExist:
            return None
    
    def find_by_user_id(self, user_id: str) -> List[Task]:
        """Find all tasks for a specific user"""
        models = TaskModel.objects.filter(user_id=user_id).order_by('-created_at')
        return [self._mapper.model_to_entity(model) for model in models]
    
    def find_with_filter(self, task_filter: TaskFilter) -> List[Task]:
        """Find tasks with filtering criteria"""
        queryset = TaskModel.objects.all()
        
        # Apply filters
        if task_filter.user_id:
            queryset = queryset.filter(user_id=task_filter.user_id)
        
        if task_filter.status:
            queryset = queryset.filter(status=task_filter.status.value)
        
        if task_filter.priority:
            queryset = queryset.filter(priority=task_filter.priority.value)
        
        if task_filter.overdue_only:
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=[TaskModel.Status.PENDING, TaskModel.Status.IN_PROGRESS]
            )
        
        if task_filter.due_date_from:
            queryset = queryset.filter(due_date__gte=task_filter.due_date_from)
        
        if task_filter.due_date_to:
            queryset = queryset.filter(due_date__lte=task_filter.due_date_to)
        
        if task_filter.search_term:
            queryset = queryset.filter(
                Q(title__icontains=task_filter.search_term) |
                Q(description__icontains=task_filter.search_term)
            )
        
        # Order results
        queryset = queryset.order_by('-priority', 'due_date', '-created_at')
        
        return [self._mapper.model_to_entity(model) for model in queryset]
    
    def delete(self, task_id: str) -> bool:
        """Delete a task by ID, return True if deleted"""
        try:
            task = TaskModel.objects.get(id=task_id)
            task.delete()
            return True
        except TaskModel.DoesNotExist:
            return False
    
    def bulk_update_status(self, task_ids: List[str], status: str) -> int:
        """Bulk update task status, return number of updated tasks"""
        updated_count = TaskModel.objects.filter(
            id__in=task_ids,
            status__in=[TaskModel.Status.PENDING, TaskModel.Status.IN_PROGRESS]
        ).update(
            status=status,
            completed_at=timezone.now() if status == TaskModel.Status.COMPLETED else None
        )
        
        return updated_count
    
    def get_statistics(self, user_id: Optional[str] = None) -> TaskStatistics:
        """Get task statistics, optionally filtered by user"""
        queryset = TaskModel.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        stats = queryset.aggregate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(status=TaskModel.Status.COMPLETED)),
            pending_tasks=Count('id', filter=Q(status__in=[
                TaskModel.Status.PENDING, 
                TaskModel.Status.IN_PROGRESS
            ])),
            high_priority_tasks=Count('id', filter=Q(priority__in=[
                TaskModel.Priority.HIGH, 
                TaskModel.Priority.URGENT
            ])),
        )
        
        # Calculate overdue tasks
        overdue_count = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=[TaskModel.Status.PENDING, TaskModel.Status.IN_PROGRESS]
        ).count()
        
        stats['overdue_tasks'] = overdue_count
        stats['completion_rate'] = (
            (stats['completed_tasks'] / stats['total_tasks'] * 100) 
            if stats['total_tasks'] > 0 else 0
        )
        
        return TaskStatistics(
            total_tasks=stats['total_tasks'],
            completed_tasks=stats['completed_tasks'],
            pending_tasks=stats['pending_tasks'],
            overdue_tasks=stats['overdue_tasks'],
            high_priority_tasks=stats['high_priority_tasks'],
            completion_rate=stats['completion_rate']
        )
    
    def exists(self, task_id: str) -> bool:
        """Check if a task exists"""
        return TaskModel.objects.filter(id=task_id).exists()


class DjangoTaskQueryRepository(TaskQueryRepository):
    """Django implementation for complex task queries"""
    
    def __init__(self):
        self._mapper = TaskMapper()
    
    def get_overdue_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        """Get all overdue tasks"""
        queryset = TaskModel.objects.filter(
            due_date__lt=timezone.now(),
            status__in=[TaskModel.Status.PENDING, TaskModel.Status.IN_PROGRESS]
        )
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        queryset = queryset.order_by('due_date')
        
        return [self._mapper.model_to_entity(model) for model in queryset]
    
    def get_tasks_by_priority(self, priority: str, user_id: Optional[str] = None) -> List[Task]:
        """Get tasks filtered by priority"""
        queryset = TaskModel.objects.filter(priority=priority)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        queryset = queryset.order_by('due_date', '-created_at')
        
        return [self._mapper.model_to_entity(model) for model in queryset]
    
    def get_recent_tasks(self, user_id: str, limit: int = 10) -> List[Task]:
        """Get recently created tasks for a user"""
        models = TaskModel.objects.filter(
            user_id=user_id
        ).order_by('-created_at')[:limit]
        
        return [self._mapper.model_to_entity(model) for model in models]
    
    def search_tasks(self, search_term: str, user_id: Optional[str] = None) -> List[Task]:
        """Search tasks by title or description"""
        queryset = TaskModel.objects.filter(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term)
        )
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        queryset = queryset.order_by('-created_at')
        
        return [self._mapper.model_to_entity(model) for model in queryset]