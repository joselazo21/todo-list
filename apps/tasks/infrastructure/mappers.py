"""
Mappers between domain entities and Django models
"""
from ..domain.entities import Task, TaskPriority, TaskStatus
from .models import TaskModel


class TaskMapper:
    """Mapper between Task entity and TaskModel"""
    
    def model_to_entity(self, model: TaskModel) -> Task:
        """Convert Django model to domain entity"""
        return Task(
            id=str(model.id),
            title=model.title,
            description=model.description,
            priority=TaskPriority(model.priority),
            status=TaskStatus(model.status),
            due_date=model.due_date,
            completed_at=model.completed_at,
            user_id=str(model.user_id),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def entity_to_model(self, entity: Task) -> TaskModel:
        """Convert domain entity to Django model"""
        model = TaskModel(
            title=entity.title,
            description=entity.description,
            priority=entity.priority.value,
            status=entity.status.value,
            due_date=entity.due_date,
            completed_at=entity.completed_at,
            user_id=entity.user_id,
        )
        
        if entity.id:
            model.id = entity.id
        
        return model
    
    def update_model_from_entity(self, model: TaskModel, entity: Task) -> None:
        """
        Update existing Django model with entity data.
        
        The user_id and created_at fields are preserved, and updated_at
        is automatically handled by Django's auto_now functionality.
        """
        model.title = entity.title
        model.description = entity.description
        model.priority = entity.priority.value
        model.status = entity.status.value
        model.due_date = entity.due_date
        model.completed_at = entity.completed_at