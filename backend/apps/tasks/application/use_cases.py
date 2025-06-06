"""
Task use cases - Application layer orchestrating business logic
"""
from typing import List, Optional
from datetime import datetime

from ..domain.entities import Task, TaskPriority, TaskStatus, TaskFilter
from ..domain.repositories import TaskRepository
from ..domain.services import TaskDomainService, TaskValidationService
from .dto import (
    CreateTaskDTO, UpdateTaskDTO, TaskDTO, TaskFilterDTO, 
    BulkCompleteTasksDTO, TaskStatisticsDTO, ProductivityDTO,
    TaskSuggestionDTO
)


class CreateTaskUseCase:
    """Use case for creating a new task"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
        self._validation_service = TaskValidationService()
    
    def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        """Execute task creation"""
        # Create domain entity
        task = Task(
            id=None,
            title=dto.title.strip(),
            description=dto.description.strip(),
            priority=dto.to_priority_enum(),
            status=TaskStatus.PENDING,
            due_date=dto.due_date,
            completed_at=None,
            user_id=dto.user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Validate business rules
        existing_tasks = self._task_repository.find_by_user_id(dto.user_id)
        validation_errors = self._validation_service.validate_task_creation(task, existing_tasks)
        
        if validation_errors:
            raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
        
        # Save task
        saved_task = self._task_repository.save(task)
        
        return TaskDTO.from_entity(saved_task)


class UpdateTaskUseCase:
    """Use case for updating an existing task"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
        self._validation_service = TaskValidationService()
    
    def execute(self, dto: UpdateTaskDTO) -> TaskDTO:
        """Execute task update"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"UpdateTaskUseCase - DTO: {dto}")
        
        # Find existing task
        existing_task = self._task_repository.find_by_id(dto.task_id)
        if not existing_task:
            raise ValueError(f"Task with ID {dto.task_id} not found")
        
        logger.info(f"UpdateTaskUseCase - Found existing task: {existing_task.title}")
        
        # Create updated task (don't set status yet if it's changing)
        updated_task = Task(
            id=existing_task.id,
            title=dto.title if dto.title is not None else existing_task.title,
            description=dto.description if dto.description is not None else existing_task.description,
            priority=dto.to_priority_enum() if dto.priority is not None else existing_task.priority,
            status=existing_task.status,  # Keep original status initially
            due_date=dto.due_date if dto.due_date is not None else existing_task.due_date,
            completed_at=existing_task.completed_at,
            user_id=existing_task.user_id,
            created_at=existing_task.created_at,
            updated_at=datetime.now()
        )
        
        logger.info(f"UpdateTaskUseCase - Status change: {dto.status}, existing: {existing_task.status}")
        
        # Handle status changes
        if dto.status == 'completed' and existing_task.status != TaskStatus.COMPLETED:
            updated_task.mark_as_completed()
            logger.info("UpdateTaskUseCase - Marked as completed")
        elif dto.status == 'pending' and existing_task.status == TaskStatus.COMPLETED:
            updated_task.mark_as_pending()
            logger.info("UpdateTaskUseCase - Marked as pending")
        elif dto.status is not None and dto.status != existing_task.status.value:
            # For other status changes, set directly
            updated_task.status = dto.to_status_enum()
            logger.info(f"UpdateTaskUseCase - Status changed to: {dto.status}")
        
        # Validate business rules
        validation_errors = self._validation_service.validate_task_update(existing_task, updated_task)
        if validation_errors:
            logger.error(f"UpdateTaskUseCase - Validation errors: {validation_errors}")
            raise ValueError(f"Validation failed: {', '.join(validation_errors)}")
        
        # Save updated task
        saved_task = self._task_repository.save(updated_task)
        logger.info(f"UpdateTaskUseCase - Task saved successfully")
        
        return TaskDTO.from_entity(saved_task)


class GetTaskUseCase:
    """Use case for retrieving a single task"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def execute(self, task_id: str, user_id: str) -> Optional[TaskDTO]:
        """Execute task retrieval"""
        task = self._task_repository.find_by_id(task_id)
        
        if not task:
            return None
        
        # Authorization check
        if task.user_id != user_id:
            raise PermissionError("Access denied: Task belongs to another user")
        
        return TaskDTO.from_entity(task)


class ListTasksUseCase:
    """Use case for listing tasks with filtering"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def execute(self, dto: TaskFilterDTO) -> List[TaskDTO]:
        """Execute task listing with filters"""
        # Convert DTO to domain filter
        domain_filter = TaskFilter(
            user_id=dto.user_id,
            status=TaskStatus(dto.status) if dto.status else None,
            priority=TaskPriority(dto.priority) if dto.priority else None,
            overdue_only=dto.overdue_only,
            due_date_from=dto.due_date_from,
            due_date_to=dto.due_date_to,
            search_term=dto.search_term
        )
        
        # Get filtered tasks
        tasks = self._task_repository.find_with_filter(domain_filter)
        
        # Convert to DTOs
        return [TaskDTO.from_entity(task) for task in tasks]


class DeleteTaskUseCase:
    """Use case for deleting a task"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def execute(self, task_id: str, user_id: str) -> bool:
        """Execute task deletion"""
        # Check if task exists and belongs to user
        task = self._task_repository.find_by_id(task_id)
        
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        if task.user_id != user_id:
            raise PermissionError("Access denied: Task belongs to another user")
        
        # Delete task
        return self._task_repository.delete(task_id)


class BulkCompleteTasksUseCase:
    """Use case for bulk completing tasks"""
    
    def __init__(self, task_repository: TaskRepository, domain_service: TaskDomainService):
        self._task_repository = task_repository
        self._domain_service = domain_service
    
    def execute(self, dto: BulkCompleteTasksDTO) -> dict:
        """Execute bulk task completion"""
        if not dto.task_ids:
            raise ValueError("No task IDs provided")
        
        # Verify all tasks belong to the user
        updated_count = 0
        auto_completed_tasks = []
        
        for task_id in dto.task_ids:
            task = self._task_repository.find_by_id(task_id)
            
            if not task:
                continue  # Skip non-existent tasks
            
            if task.user_id != dto.user_id:
                continue  # Skip tasks that don't belong to user
            
            if not task.is_completed:
                task.mark_as_completed()
                saved_task = self._task_repository.save(task)
                updated_count += 1
                
                related_tasks = self._domain_service.auto_complete_related_tasks(saved_task)
                auto_completed_tasks.extend(related_tasks)
        
        return {
            'updated_count': updated_count,
            'auto_completed_count': len(auto_completed_tasks),
            'auto_completed_tasks': [TaskDTO.from_entity(task) for task in auto_completed_tasks]
        }


class GetTaskStatisticsUseCase:
    """Use case for getting task statistics"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def execute(self, user_id: Optional[str] = None) -> TaskStatisticsDTO:
        """Execute statistics retrieval"""
        stats = self._task_repository.get_statistics(user_id)
        return TaskStatisticsDTO.from_domain(stats)


class GetUserProductivityUseCase:
    """Use case for getting user productivity metrics"""
    
    def __init__(self, task_repository: TaskRepository, domain_service: TaskDomainService):
        self._task_repository = task_repository
        self._domain_service = domain_service
    
    def execute(self, user_id: str, days: int = 30) -> ProductivityDTO:
        """Execute productivity calculation"""
        productivity_data = self._domain_service.calculate_user_productivity(user_id, days)
        
        return ProductivityDTO(
            total_tasks=productivity_data['total_tasks'],
            completed_tasks=productivity_data['completed_tasks'],
            completion_rate=productivity_data['completion_rate'],
            average_completion_time=productivity_data['average_completion_time'],
            productivity_score=productivity_data['productivity_score']
        )


class GetTaskSuggestionsUseCase:
    """Use case for getting task improvement suggestions"""
    
    def __init__(self, task_repository: TaskRepository, domain_service: TaskDomainService):
        self._task_repository = task_repository
        self._domain_service = domain_service
    
    def execute(self, task_id: str, user_id: str) -> List[TaskSuggestionDTO]:
        """Execute suggestion generation"""
        task = self._task_repository.find_by_id(task_id)
        
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        if task.user_id != user_id:
            raise PermissionError("Access denied: Task belongs to another user")
        
        suggestions = self._domain_service.suggest_task_breakdown(task)
        
        return [
            TaskSuggestionDTO(reason=s['reason'], suggestion=s['suggestion'])
            for s in suggestions
        ]


class AutoPrioritizeTasksUseCase:
    """Use case for automatically prioritizing tasks based on deadlines"""
    
    def __init__(self, task_repository: TaskRepository, domain_service: TaskDomainService):
        self._task_repository = task_repository
        self._domain_service = domain_service
    
    def execute(self, user_id: str) -> List[TaskDTO]:
        """Execute automatic task prioritization"""
        user_tasks = self._task_repository.find_by_user_id(user_id)
        
        # Filter only pending tasks
        pending_tasks = [task for task in user_tasks if not task.is_completed]
        
        updated_tasks = self._domain_service.prioritize_tasks_by_deadline(pending_tasks)
        
        return [TaskDTO.from_entity(task) for task in updated_tasks]