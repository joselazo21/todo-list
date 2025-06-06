from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from .models import Task, User, TaskPriority
from .utils import validate_password_strength


class UserSerializer(serializers.ModelSerializer):
    """Enhanced User serializer with computed fields"""
    active_tasks_count = serializers.ReadOnlyField()
    completed_tasks_count = serializers.ReadOnlyField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'is_active', 'created_at', 'updated_at',
            'active_tasks_count', 'completed_tasks_count', 'tasks_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_tasks_count(self, obj):
        """Get total tasks count"""
        return obj.tasks.count()

    def validate_name(self, value):
        """Validate name field"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip().title()

    def validate_email(self, value):
        """Validate email field"""
        return value.lower()


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for task lists"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'completed', 'priority', 'priority_display',
            'due_date', 'created_at', 'user_name', 'is_overdue', 'days_until_due'
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual tasks"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed', 'priority', 'priority_display',
            'due_date', 'completed_at', 'created_at', 'updated_at', 'user', 'user_name',
            'user_email', 'is_overdue', 'days_until_due'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']

    def validate_title(self, value):
        """Validate title field"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_due_date(self, value):
        """Validate due_date field"""
        if value and value < timezone.now():
            # Only validate for new tasks
            if not self.instance:
                raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_priority(self, value):
        """Validate priority field"""
        if value not in [choice[0] for choice in TaskPriority.choices]:
            raise serializers.ValidationError("Invalid priority value.")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        # If marking as completed, ensure completed_at is set
        if attrs.get('completed', False) and not attrs.get('completed_at'):
            attrs['completed_at'] = timezone.now()
        elif not attrs.get('completed', True):
            attrs['completed_at'] = None
        
        return attrs


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'user']

    def validate_title(self, value):
        """Validate title field"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_due_date(self, value):
        """Validate due_date field"""
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value


class UserTasksSerializer(serializers.ModelSerializer):
    """Serializer for user with their tasks"""
    tasks = TaskListSerializer(many=True, read_only=True)
    active_tasks_count = serializers.ReadOnlyField()
    completed_tasks_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'is_active', 'created_at',
            'active_tasks_count', 'completed_tasks_count', 'tasks'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def validate_name(self, value):
        """Validate name field"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip().title()

    def validate_email(self, value):
        """Validate email field"""
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Alias for backward compatibility
TaskSerializer = TaskDetailSerializer