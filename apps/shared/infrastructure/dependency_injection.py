"""
Dependency Injection Container for Clean Architecture
"""
from typing import Dict, Any, Callable, TypeVar, Type
from abc import ABC, abstractmethod

T = TypeVar('T')


class DIContainer:
    """Simple Dependency Injection Container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        key = self._get_key(interface)
        self._factories[key] = lambda: implementation()
        self._singletons[key] = None
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a transient service (new instance each time)"""
        key = self._get_key(interface)
        self._factories[key] = lambda: implementation()
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance"""
        key = self._get_key(interface)
        self._services[key] = instance
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function"""
        key = self._get_key(interface)
        self._factories[key] = factory
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance"""
        key = self._get_key(interface)
        
        # Check if we have a direct instance
        if key in self._services:
            return self._services[key]
        
        # Check if it's a singleton
        if key in self._singletons:
            if self._singletons[key] is None:
                self._singletons[key] = self._factories[key]()
            return self._singletons[key]
        
        # Create new instance
        if key in self._factories:
            return self._factories[key]()
        
        raise ValueError(f"Service {interface.__name__} not registered")
    
    def _get_key(self, interface: Type) -> str:
        """Get string key for interface"""
        return f"{interface.__module__}.{interface.__name__}"


# Global container instance
container = DIContainer()


def configure_dependencies():
    """Configure all dependencies for the application"""
    # Tasks domain
    from apps.tasks.domain.repositories import TaskRepository
    from apps.tasks.infrastructure.repositories import DjangoTaskRepository
    from apps.tasks.domain.services import TaskDomainService
    from apps.tasks.application.use_cases import (
        CreateTaskUseCase, UpdateTaskUseCase, GetTaskUseCase,
        ListTasksUseCase, DeleteTaskUseCase, BulkCompleteTasksUseCase
    )
    
    # Users domain
    from apps.users.domain.repositories import UserRepository
    from apps.users.infrastructure.repositories import DjangoUserRepository
    from apps.users.domain.services import UserDomainService
    from apps.users.application.use_cases import (
        CreateUserUseCase, UpdateUserUseCase, GetUserUseCase,
        ListUsersUseCase, ChangePasswordUseCase
    )
    
    from apps.authentication.domain.services import AuthenticationDomainService
    from apps.authentication.application.use_cases import (
        LoginUseCase, RefreshTokenUseCase, LogoutUseCase, ValidateTokenUseCase
    )
    
    # Register Task repositories
    container.register_singleton(TaskRepository, DjangoTaskRepository)
    
    # Register User repositories
    container.register_singleton(UserRepository, DjangoUserRepository)
    
    # Register Task domain services
    container.register_factory(
        TaskDomainService,
        lambda: TaskDomainService(container.get(TaskRepository))
    )
    
    # Register User domain services
    container.register_factory(
        UserDomainService,
        lambda: UserDomainService(container.get(UserRepository))
    )
    
    # Register Task use cases
    container.register_factory(
        CreateTaskUseCase,
        lambda: CreateTaskUseCase(container.get(TaskRepository))
    )
    
    container.register_factory(
        UpdateTaskUseCase,
        lambda: UpdateTaskUseCase(container.get(TaskRepository))
    )
    
    container.register_factory(
        GetTaskUseCase,
        lambda: GetTaskUseCase(container.get(TaskRepository))
    )
    
    container.register_factory(
        ListTasksUseCase,
        lambda: ListTasksUseCase(container.get(TaskRepository))
    )
    
    container.register_factory(
        DeleteTaskUseCase,
        lambda: DeleteTaskUseCase(container.get(TaskRepository))
    )
    
    container.register_factory(
        BulkCompleteTasksUseCase,
        lambda: BulkCompleteTasksUseCase(
            container.get(TaskRepository),
            container.get(TaskDomainService)
        )
    )
    
    # Register User use cases
    container.register_factory(
        CreateUserUseCase,
        lambda: CreateUserUseCase(
            container.get(UserRepository),
            container.get(UserDomainService)
        )
    )
    
    container.register_factory(
        UpdateUserUseCase,
        lambda: UpdateUserUseCase(container.get(UserRepository))
    )
    
    container.register_factory(
        GetUserUseCase,
        lambda: GetUserUseCase(container.get(UserRepository))
    )
    
    container.register_factory(
        ListUsersUseCase,
        lambda: ListUsersUseCase(container.get(UserRepository))
    )
    
    container.register_factory(
        ChangePasswordUseCase,
        lambda: ChangePasswordUseCase(
            container.get(UserRepository),
            container.get(UserDomainService)
        )
    )


# Decorator for dependency injection
def inject(interface: Type[T]) -> Callable:
    """Decorator to inject dependencies"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            service = container.get(interface)
            return func(service, *args, **kwargs)
        return wrapper
    return decorator