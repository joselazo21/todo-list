"""
Django models for User infrastructure layer
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class UserModel(AbstractUser):
    """Django model for User persistence"""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        SUSPENDED = 'suspended', 'Suspended'
        PENDING_VERIFICATION = 'pending_verification', 'Pending Verification'
    
    # Override default fields
    username = None
    first_name = None
    last_name = None
    
    # Custom fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="User's full name (minimum 2 characters)"
    )
    email = models.EmailField(
        unique=True,
        help_text="User's email address (must be unique)"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_VERIFICATION,
        help_text="User account status"
    )
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email has been verified"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP address of last login"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this timestamp"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['account_locked_until']),
            models.Index(fields=['is_email_verified']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def clean(self):
        """Model validation"""
        super().clean()
        if self.name and len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters long.'})
    
    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    @property
    def active_tasks_count(self):
        """Return count of active tasks"""
        # This would require importing Task model
        # For now, return 0
        return 0
    
    @property
    def completed_tasks_count(self):
        """Return count of completed tasks"""
        # This would require importing Task model
        # For now, return 0
        return 0