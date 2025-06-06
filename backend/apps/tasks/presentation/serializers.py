"""
DRF Serializers for Task presentation layer
"""
from rest_framework import serializers
from datetime import datetime
from ..application.dto import CreateTaskDTO, UpdateTaskDTO, TaskFilterDTO, BulkCompleteTasksDTO


class CreateTaskSerializer(serializers.Serializer):
    """Serializer for task creation"""
    title = serializers.CharField(max_length=200, min_length=3)
    description = serializers.CharField(allow_blank=True, default="")
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'urgent'],
        default='medium'
    )
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_title(self, value):
        """Validate title"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
    
    def validate_due_date(self, value):
        """Validate due date"""
        if value and value < datetime.now():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value
    
    def to_dto(self, user_id: str) -> CreateTaskDTO:
        """Convert to DTO"""
        return CreateTaskDTO(
            title=self.validated_data['title'],
            description=self.validated_data['description'],
            priority=self.validated_data['priority'],
            due_date=self.validated_data.get('due_date'),
            user_id=user_id
        )


class UpdateTaskSerializer(serializers.Serializer):
    """Serializer for task updates"""
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'urgent'],
        required=False
    )
    status = serializers.ChoiceField(
        choices=['pending', 'in_progress', 'completed', 'cancelled'],
        required=False
    )
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_title(self, value):
        """Validate title"""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        if value is not None and len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value.strip() if value else value
    
    def to_dto(self, task_id: str) -> UpdateTaskDTO:
        """Convert to DTO"""
        return UpdateTaskDTO(
            task_id=task_id,
            title=self.validated_data.get('title'),
            description=self.validated_data.get('description'),
            priority=self.validated_data.get('priority'),
            status=self.validated_data.get('status'),
            due_date=self.validated_data.get('due_date')
        )


class TaskSerializer(serializers.Serializer):
    """Serializer for task representation"""
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    priority = serializers.CharField()
    status = serializers.CharField()
    due_date = serializers.DateTimeField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    user_id = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    is_overdue = serializers.BooleanField()
    days_until_due = serializers.IntegerField(allow_null=True)


class TaskFilterSerializer(serializers.Serializer):
    """Serializer for task filtering"""
    status = serializers.ChoiceField(
        choices=['pending', 'in_progress', 'completed', 'cancelled'],
        required=False
    )
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'urgent'],
        required=False
    )
    overdue_only = serializers.BooleanField(default=False)
    due_date_from = serializers.DateTimeField(required=False)
    due_date_to = serializers.DateTimeField(required=False)
    search_term = serializers.CharField(required=False, allow_blank=True)
    
    def to_dto(self, user_id: str) -> TaskFilterDTO:
        """Convert to DTO"""
        return TaskFilterDTO(
            user_id=user_id,
            status=self.validated_data.get('status'),
            priority=self.validated_data.get('priority'),
            overdue_only=self.validated_data.get('overdue_only', False),
            due_date_from=self.validated_data.get('due_date_from'),
            due_date_to=self.validated_data.get('due_date_to'),
            search_term=self.validated_data.get('search_term')
        )


class BulkCompleteTasksSerializer(serializers.Serializer):
    """Serializer for bulk task completion"""
    task_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    
    def to_dto(self, user_id: str) -> BulkCompleteTasksDTO:
        """Convert to DTO"""
        return BulkCompleteTasksDTO(
            task_ids=[str(task_id) for task_id in self.validated_data['task_ids']],
            user_id=user_id
        )


class TaskStatisticsSerializer(serializers.Serializer):
    """Serializer for task statistics"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    high_priority_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class ProductivitySerializer(serializers.Serializer):
    """Serializer for productivity metrics"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_completion_time = serializers.FloatField()
    productivity_score = serializers.FloatField()


class TaskSuggestionSerializer(serializers.Serializer):
    """Serializer for task suggestions"""
    reason = serializers.CharField()
    suggestion = serializers.CharField()


class BulkCompleteResponseSerializer(serializers.Serializer):
    """Serializer for bulk complete response"""
    updated_count = serializers.IntegerField()
    auto_completed_count = serializers.IntegerField()
    auto_completed_tasks = TaskSerializer(many=True)