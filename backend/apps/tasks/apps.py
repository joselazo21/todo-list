"""
Tasks app configuration
"""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    verbose_name = 'Tasks'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Configure dependency injection
        from apps.shared.infrastructure.dependency_injection import configure_dependencies
        configure_dependencies()