"""
Task domain services - Complex business logic that doesn't belong to entities
"""
from typing import List, Optional
from datetime import datetime, timedelta
from .entities import Task, TaskPriority, TaskStatus, TaskStatistics
from .repositories import TaskRepository


class TaskDomainService:
    """Domain service for complex task business logic"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def prioritize_tasks_by_deadline(self, tasks: List[Task]) -> List[Task]:
        """
        Automatically prioritize tasks based on deadline proximity
        Business rule: Tasks due within 24 hours become HIGH priority
        Tasks due within 1 hour become URGENT priority
        """
        now = datetime.now()
        updated_tasks = []
        
        for task in tasks:
            if task.due_date and not task.is_completed:
                time_until_due = task.due_date - now
                
                if time_until_due <= timedelta(hours=1):
                    task.update_priority(TaskPriority.URGENT)
                elif time_until_due <= timedelta(hours=24):
                    task.update_priority(TaskPriority.HIGH)
                
                updated_tasks.append(self._task_repository.save(task))
            else:
                updated_tasks.append(task)
        
        return updated_tasks
    
    def calculate_user_productivity(self, user_id: str, days: int = 30) -> dict:
        """
        Calculate user productivity metrics
        Business logic for productivity analysis
        """
        user_tasks = self._task_repository.find_by_user_id(user_id)
        
        # Filter tasks from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tasks = [
            task for task in user_tasks 
            if task.created_at and task.created_at >= cutoff_date
        ]
        
        if not recent_tasks:
            return {
                'total_tasks': 0,
                'completion_rate': 0,
                'average_completion_time': 0,
                'productivity_score': 0
            }
        
        completed_tasks = [task for task in recent_tasks if task.is_completed]
        
        # Calculate average completion time
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                completion_time = (task.completed_at - task.created_at).total_seconds() / 3600  # hours
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        completion_rate = len(completed_tasks) / len(recent_tasks) * 100
        
        # Productivity score (0-100) based on completion rate and speed
        productivity_score = min(100, completion_rate * 0.7 + (100 - min(100, avg_completion_time)) * 0.3)
        
        return {
            'total_tasks': len(recent_tasks),
            'completed_tasks': len(completed_tasks),
            'completion_rate': completion_rate,
            'average_completion_time': avg_completion_time,
            'productivity_score': productivity_score
        }
    
    def suggest_task_breakdown(self, task: Task) -> List[dict]:
        """
        Suggest breaking down large tasks into smaller ones
        Business rule: Tasks with long descriptions might benefit from breakdown
        """
        suggestions = []
        
        if len(task.description) > 500:  # Long description
            suggestions.append({
                'reason': 'Long description detected',
                'suggestion': 'Consider breaking this task into smaller, more manageable subtasks'
            })
        
        if task.priority == TaskPriority.URGENT and not task.due_date:
            suggestions.append({
                'reason': 'Urgent task without deadline',
                'suggestion': 'Add a specific deadline to better manage this urgent task'
            })
        
        # Check for keywords that suggest complexity
        complex_keywords = ['implement', 'design', 'research', 'analyze', 'develop']
        if any(keyword in task.title.lower() or keyword in task.description.lower() 
               for keyword in complex_keywords):
            suggestions.append({
                'reason': 'Complex task detected',
                'suggestion': 'Consider breaking this into planning, execution, and review phases'
            })
        
        return suggestions
    
    def auto_complete_related_tasks(self, completed_task: Task) -> List[Task]:
        """
        Business rule: When certain tasks are completed, 
        automatically complete related tasks
        """
        if not completed_task.is_completed:
            return []
        
        # Find tasks with similar titles (potential duplicates or related tasks)
        all_user_tasks = self._task_repository.find_by_user_id(completed_task.user_id)
        
        related_tasks = []
        for task in all_user_tasks:
            if (task.id != completed_task.id and 
                not task.is_completed and
                self._are_tasks_related(completed_task, task)):
                
                task.mark_as_completed()
                updated_task = self._task_repository.save(task)
                related_tasks.append(updated_task)
        
        return related_tasks
    
    def _are_tasks_related(self, task1: Task, task2: Task) -> bool:
        """
        Determine if two tasks are related based on business rules
        """
        # Simple similarity check - in real world, this could be more sophisticated
        title_similarity = len(set(task1.title.lower().split()) & 
                                set(task2.title.lower().split())) / max(
                                    len(task1.title.split()), 
                                    len(task2.title.split())
                                )
        
        return title_similarity > 0.6  # 60% word similarity


class TaskValidationService:
    """Service for complex task validation rules"""
    
    @staticmethod
    def validate_task_creation(task: Task, existing_tasks: List[Task]) -> List[str]:
        """
        Validate task creation with business rules
        Returns list of validation errors
        """
        errors = []
        
        # Check for duplicate titles
        duplicate_titles = [
            existing_task for existing_task in existing_tasks
            if (existing_task.title.lower() == task.title.lower() and 
                existing_task.user_id == task.user_id and
                not existing_task.is_completed)
        ]
        
        if duplicate_titles:
            errors.append("A pending task with this title already exists")
        
        # Business rule: Cannot have more than 3 urgent tasks at once
        urgent_tasks = [
            existing_task for existing_task in existing_tasks
            if (existing_task.priority == TaskPriority.URGENT and
                existing_task.user_id == task.user_id and
                not existing_task.is_completed)
        ]
        
        if task.priority == TaskPriority.URGENT and len(urgent_tasks) >= 3:
            errors.append("Cannot have more than 3 urgent tasks at once")
        
        # Business rule: Tasks due within 1 hour must be high priority or urgent
        if task.due_date:
            time_until_due = task.due_date - datetime.now()
            if (time_until_due <= timedelta(hours=1) and 
                task.priority not in [TaskPriority.HIGH, TaskPriority.URGENT]):
                errors.append("Tasks due within 1 hour must be HIGH or URGENT priority")
        
        return errors
    
    @staticmethod
    def validate_task_update(original_task: Task, updated_task: Task) -> List[str]:
        """
        Validate task updates with business rules
        """
        errors = []
        
        # Cannot change user assignment
        if original_task.user_id != updated_task.user_id:
            errors.append("Cannot change task owner")
        
        # Cannot uncomplete a task that was completed more than 24 hours ago
        if (original_task.is_completed and 
            not updated_task.is_completed and
            original_task.completed_at and
            datetime.now() - original_task.completed_at > timedelta(hours=24)):
            errors.append("Cannot uncomplete a task that was completed more than 24 hours ago")
        
        return errors