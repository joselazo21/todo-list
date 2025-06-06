"""
Tests for Tasks use cases
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from apps.tasks.application.use_cases import CreateTaskUseCase, UpdateTaskUseCase
from apps.tasks.application.dto import CreateTaskDTO, UpdateTaskDTO
from apps.tasks.domain.entities import Task, TaskPriority, TaskStatus
from apps.tasks.domain.repositories import TaskRepository


class TestCreateTaskUseCase:
    """Test CreateTaskUseCase"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repository = Mock(spec=TaskRepository)
        self.use_case = CreateTaskUseCase(self.mock_repository)
    
    def test_create_task_success(self):
        """Test successful task creation"""
        # Arrange
        dto = CreateTaskDTO(
            title="Test Task",
            description="Test Description",
            priority="high",
            due_date=datetime.now() + timedelta(days=1),
            user_id="usr_001"
        )
        
        # Mock repository responses
        self.mock_repository.find_by_user_id.return_value = []
        self.mock_repository.save.return_value = Task(
            id="tsk_001",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            due_date=dto.due_date,
            completed_at=None,
            user_id="usr_001",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        result = self.use_case.execute(dto)
        
        # Assert
        assert result.title == "Test Task"
        assert result.priority == "high"
        assert result.status == "pending"
        assert result.user_id == "usr_001"
        self.mock_repository.save.assert_called_once()
    
    def test_create_task_validation_error(self):
        """Test task creation with validation error"""
        # Arrange
        dto = CreateTaskDTO(
            title="AB",  # Too short
            description="Test Description",
            priority="high",
            due_date=None,
            user_id="usr_001"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation failed"):
            self.use_case.execute(dto)
    
    def test_create_task_business_rule_violation(self):
        """Test task creation with business rule violation"""
        # Arrange
        dto = CreateTaskDTO(
            title="Test Task",
            description="Test Description",
            priority="urgent",
            due_date=None,
            user_id="usr_001"
        )
        
        # Mock existing urgent tasks (business rule: max 3 urgent tasks)
        existing_urgent_tasks = [
            Task(
                id=f"task{i}",
                title=f"Urgent Task {i}",
                description="",
                priority=TaskPriority.URGENT,
                status=TaskStatus.PENDING,
                due_date=None,
                completed_at=None,
                user_id="usr_001"
            )
            for i in range(3)
        ]
        
        self.mock_repository.find_by_user_id.return_value = existing_urgent_tasks
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot have more than 3 urgent tasks"):
            self.use_case.execute(dto)


class TestUpdateTaskUseCase:
    """Test UpdateTaskUseCase"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repository = Mock(spec=TaskRepository)
        self.use_case = UpdateTaskUseCase(self.mock_repository)
    
    def test_update_task_success(self):
        """Test successful task update"""
        # Arrange
        existing_task = Task(
            id="tsk_001",
            title="Old Title",
            description="Old Description",
            priority=TaskPriority.LOW,
            status=TaskStatus.PENDING,
            due_date=None,
            completed_at=None,
            user_id="usr_001",
            created_at=datetime.now() - timedelta(hours=1),
            updated_at=datetime.now() - timedelta(hours=1)
        )
        
        dto = UpdateTaskDTO(
            task_id="tsk_001",
            title="New Title",
            priority="high",
            status="completed"
        )
        
        updated_task = Task(
            id="tsk_001",
            title="New Title",
            description="Old Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.COMPLETED,
            due_date=None,
            completed_at=datetime.now(),
            user_id="usr_001",
            created_at=existing_task.created_at,
            updated_at=datetime.now()
        )
        
        self.mock_repository.find_by_id.return_value = existing_task
        self.mock_repository.save.return_value = updated_task
        
        # Act
        result = self.use_case.execute(dto)
        
        # Assert
        assert result.title == "New Title"
        assert result.priority == "high"
        assert result.status == "completed"
        assert result.completed_at is not None
        self.mock_repository.save.assert_called_once()
    
    def test_update_nonexistent_task(self):
        """Test updating non-existent task"""
        # Arrange
        dto = UpdateTaskDTO(
            task_id="nonexistent",
            title="New Title"
        )
        
        self.mock_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            self.use_case.execute(dto)
    
    def test_update_task_business_rule_violation(self):
        """Test updating task with business rule violation"""
        # Arrange
        old_completed_task = Task(
            id="tsk_001",
            title="Old Title",
            description="Old Description",
            priority=TaskPriority.LOW,
            status=TaskStatus.COMPLETED,
            due_date=None,
            completed_at=datetime.now() - timedelta(days=2),  # Completed 2 days ago
            user_id="usr_001",
            created_at=datetime.now() - timedelta(days=3),
            updated_at=datetime.now() - timedelta(days=2)
        )
        
        dto = UpdateTaskDTO(
            task_id="tsk_001",
            status="pending"  # Trying to uncomplete old task
        )
        
        self.mock_repository.find_by_id.return_value = old_completed_task
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot uncomplete a task that was completed more than 24 hours ago"):
            self.use_case.execute(dto)