from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    """User model with enhanced validation"""
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="User's full name (minimum 2 characters)"
    )
    email = models.EmailField(
        unique=True,
        help_text="User's email address (must be unique)"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    def clean(self):
        """Custom validation"""
        super().clean()
        if self.name and len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters long.'})

    @property
    def active_tasks_count(self):
        """Return count of active tasks"""
        return self.tasks.filter(completed=False).count()

    @property
    def completed_tasks_count(self):
        """Return count of completed tasks"""
        return self.tasks.filter(completed=True).count()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]


class TaskPriority(models.TextChoices):
    """Task priority choices"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class Task(BaseModel):
    """Enhanced Task model with priority and better validation"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Task owner"
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Task title (minimum 3 characters)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed task description"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Task completion status"
    )
    priority = models.CharField(
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        help_text="Task priority level"
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Task due date and time"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the task was completed"
    )

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.title} ({self.get_priority_display()})"

    def clean(self):
        """Custom validation"""
        super().clean()
        if self.due_date and self.due_date < timezone.now():
            if not self.pk:  # Only for new tasks
                raise ValidationError({'due_date': 'Due date cannot be in the past.'})
        
        if self.title and len(self.title.strip()) < 3:
            raise ValidationError({'title': 'Title must be at least 3 characters long.'})

    def save(self, *args, **kwargs):
        """Override save to handle completion timestamp"""
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.due_date or self.completed:
            return False
        return timezone.now() > self.due_date

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now()
        return delta.days

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-priority', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]