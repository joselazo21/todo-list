"""
Tests for Tasks domain layer
"""
import pytest
from datetime import datetime, timedelta
from apps.tasks.domain.entities import Task, TaskPriority, TaskStatus, TaskStatistics


class TestTaskEntity:
    """Test Task domain entity"""
    
    def test_task_creation(self):
        """Test task creation with valid data"""
        task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            due_date=datetime.now() + timedelta(days=1),
            completed_at=None,
            user_id="usr_001",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert task.title == "Test Task"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert not task.is_completed
    
    def test_task_validation_short_title(self):
        """Test task validation with short title"""
        with pytest.raises(ValueError, match="Task title must be at least 3 characters long"):
            Task(
                id="123",
                title="AB",
                description="Test Description",
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                due_date=None,
                completed_at=None,
                user_id="usr_001"
            )
    
    def test_task_validation_past_due_date(self):
        """Test task validation with past due date"""
        with pytest.raises(ValueError, match="Due date cannot be in the past"):
            Task(
                id=None,  # New task
                title="Test Task",
                description="Test Description",
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                due_date=datetime.now() - timedelta(days=1),
                completed_at=None,
                user_id="usr_001"
            )
    
    def test_mark_as_completed(self):
        """Test marking task as completed"""
        task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            due_date=None,
            completed_at=None,
            user_id="usr_001"
        )
        
        task.mark_as_completed()
        
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.is_completed
    
    def test_mark_completed_task_as_completed_raises_error(self):
        """Test marking already completed task as completed raises error"""
        task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.COMPLETED,
            due_date=None,
            completed_at=datetime.now(),
            user_id="usr_001"
        )
        
        with pytest.raises(ValueError, match="Task is already completed"):
            task.mark_as_completed()
    
    def test_is_overdue(self):
        """Test overdue detection"""
        # Overdue task
        overdue_task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            due_date=datetime.now() - timedelta(hours=1),
            completed_at=None,
            user_id="usr_001"
        )
        
        assert overdue_task.is_overdue()
        
        # Not overdue task
        future_task = Task(
            id="124",
            title="Test Task 2",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            due_date=datetime.now() + timedelta(hours=1),
            completed_at=None,
            user_id="usr_001"
        )
        
        assert not future_task.is_overdue()
        
        # Completed task is not overdue
        completed_task = Task(
            id="125",
            title="Test Task 3",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.COMPLETED,
            due_date=datetime.now() - timedelta(hours=1),
            completed_at=datetime.now(),
            user_id="usr_001"
        )
        
        assert not completed_task.is_overdue()
    
    def test_update_priority(self):
        """Test updating task priority"""
        task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.LOW,
            status=TaskStatus.PENDING,
            due_date=None,
            completed_at=None,
            user_id="usr_001"
        )
        
        task.update_priority(TaskPriority.URGENT)
        assert task.priority == TaskPriority.URGENT
    
    def test_update_priority_completed_task_raises_error(self):
        """Test updating priority of completed task raises error"""
        task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.LOW,
            status=TaskStatus.COMPLETED,
            due_date=None,
            completed_at=datetime.now(),
            user_id="usr_001"
        )
        
        with pytest.raises(ValueError, match="Cannot change priority of completed task"):
            task.update_priority(TaskPriority.URGENT)
    
    def test_is_high_priority(self):
        """Test high priority detection"""
        high_task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            due_date=None,
            completed_at=None,
            user_id="usr_001"
        )
        
        urgent_task = Task(
            id="124",
            title="Test Task 2",
            description="Test Description",
            priority=TaskPriority.URGENT,
            status=TaskStatus.PENDING,
            due_date=None,
            completed_at=None,
            user_id="usr_001"
        )
        
        low_task = Task(
            id="125",
            title="Test Task 3",
            description="Test Description",
            priority=TaskPriority.LOW,
            status=TaskStatus.PENDING,
            due_date=None,
            completed_at=None,
            user_id="usr_001"
        )
        
        assert high_task.is_high_priority()
        assert urgent_task.is_high_priority()
        assert not low_task.is_high_priority()


class TestTaskStatistics:
    """Test TaskStatistics value object"""
    
    def test_calculate_statistics(self):
        """Test statistics calculation"""
        tasks = [
            Task(
                id="1", title="Task 1", description="", priority=TaskPriority.HIGH,
                status=TaskStatus.COMPLETED, due_date=None, completed_at=datetime.now(),
                user_id="user1"
            ),
            Task(
                id="2", title="Task 2", description="", priority=TaskPriority.LOW,
                status=TaskStatus.PENDING, due_date=datetime.now() - timedelta(hours=1),
                completed_at=None, user_id="user1"
            ),
            Task(
                id="3", title="Task 3", description="", priority=TaskPriority.URGENT,
                status=TaskStatus.PENDING, due_date=None, completed_at=None,
                user_id="user1"
            ),
        ]
        
        stats = TaskStatistics.calculate(tasks)
        
        assert stats.total_tasks == 3
        assert stats.completed_tasks == 1
        assert stats.pending_tasks == 2
        assert stats.overdue_tasks == 1
        assert stats.high_priority_tasks == 2
        assert stats.completion_rate == pytest.approx(33.33, rel=1e-2)