"""
Django models for Task infrastructure layer
"""
from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class TaskModel(models.Model):
    """Django model for Task persistence"""
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Task title (minimum 3 characters)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed task description"
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Task priority level"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Task status"
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
    user_id = models.UUIDField(
        help_text="Task owner ID"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks_task'  # Custom table name
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-priority', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['user_id', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        status_icon = "✓" if self.status == self.Status.COMPLETED else "○"
        return f"{status_icon} {self.title} ({self.get_priority_display()})"
    
    def clean(self):
        """Model validation"""
        super().clean()
        if self.due_date and self.due_date < timezone.now():
            if not self.pk:  # Only for new tasks
                raise ValidationError({'due_date': 'Due date cannot be in the past.'})
        
        if self.title and len(self.title.strip()) < 3:
            raise ValidationError({'title': 'Title must be at least 3 characters long.'})
    
    def save(self, *args, **kwargs):
        """Override save to handle completion timestamp"""
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.Status.COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.due_date or self.status == self.Status.COMPLETED:
            return False
        return timezone.now() > self.due_date
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now()
        return delta.days