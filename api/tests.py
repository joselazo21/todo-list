from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
import uuid

from .models import User, Task, TaskPriority


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.user_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }

    def test_user_creation(self):
        """Test user creation with valid data"""
        user = User.objects.create(**self.user_data)
        self.assertEqual(user.name, 'John Doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertTrue(user.is_active)
        self.assertIsInstance(user.id, uuid.UUID)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create(**self.user_data)
        expected = f"{user.name} ({user.email})"
        self.assertEqual(str(user), expected)

    def test_user_email_uniqueness(self):
        """Test that email must be unique"""
        User.objects.create(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create(**self.user_data)

    def test_user_name_validation(self):
        """Test user name validation"""
        user = User(name='A', email='test@example.com')
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_properties(self):
        """Test user computed properties"""
        user = User.objects.create(**self.user_data)
        
        # Create some tasks
        Task.objects.create(
            user=user, title='Task 1', completed=False
        )
        Task.objects.create(
            user=user, title='Task 2', completed=True
        )
        
        self.assertEqual(user.active_tasks_count, 1)
        self.assertEqual(user.completed_tasks_count, 1)


class TaskModelTest(TestCase):
    """Test cases for Task model"""

    def setUp(self):
        self.user = User.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        self.task_data = {
            'user': self.user,
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': TaskPriority.MEDIUM
        }

    def test_task_creation(self):
        """Test task creation with valid data"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertIsInstance(task.id, uuid.UUID)

    def test_task_str_representation(self):
        """Test task string representation"""
        task = Task.objects.create(**self.task_data)
        expected = f"○ {task.title} ({task.get_priority_display()})"
        self.assertEqual(str(task), expected)

    def test_task_completion_timestamp(self):
        """Test that completed_at is set when task is completed"""
        task = Task.objects.create(**self.task_data)
        self.assertIsNone(task.completed_at)
        
        task.completed = True
        task.save()
        self.assertIsNotNone(task.completed_at)

    def test_task_overdue_property(self):
        """Test is_overdue property"""
        # Task with future due date
        future_date = timezone.now() + timedelta(days=1)
        task = Task.objects.create(
            **self.task_data,
            due_date=future_date
        )
        self.assertFalse(task.is_overdue)
        
        # Task with past due date
        past_date = timezone.now() - timedelta(days=1)
        task.due_date = past_date
        task.save()
        self.assertTrue(task.is_overdue)
        
        # Completed task should not be overdue
        task.completed = True
        task.save()
        self.assertFalse(task.is_overdue)

    def test_task_title_validation(self):
        """Test task title validation"""
        task = Task(
            user=self.user,
            title='AB',  # Too short
            priority=TaskPriority.MEDIUM
        )
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_due_date_validation(self):
        """Test due date validation for new tasks"""
        past_date = timezone.now() - timedelta(days=1)
        task = Task(
            user=self.user,
            title='Test Task',
            due_date=past_date,
            priority=TaskPriority.MEDIUM
        )
        with self.assertRaises(ValidationError):
            task.full_clean()


class TaskAPITest(APITestCase):
    """Test cases for Task API endpoints"""

    def setUp(self):
        self.user = User.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': TaskPriority.MEDIUM,
            'user': str(self.user.id)
        }

    def test_create_task(self):
        """Test creating a task via API"""
        url = reverse('api:task-list-create')
        response = self.client.post(url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_list_tasks(self):
        """Test listing tasks via API"""
        Task.objects.create(
            user=self.user,
            title='Task 1',
            priority=TaskPriority.HIGH
        )
        Task.objects.create(
            user=self.user,
            title='Task 2',
            priority=TaskPriority.LOW
        )
        
        url = reverse('api:task-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_tasks_by_priority(self):
        """Test filtering tasks by priority"""
        Task.objects.create(
            user=self.user,
            title='High Priority Task',
            priority=TaskPriority.HIGH
        )
        Task.objects.create(
            user=self.user,
            title='Low Priority Task',
            priority=TaskPriority.LOW
        )
        
        url = reverse('api:task-list-create')
        response = self.client.get(url, {'priority': TaskPriority.HIGH})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['priority'], 
            TaskPriority.HIGH
        )

    def test_search_tasks(self):
        """Test searching tasks"""
        Task.objects.create(
            user=self.user,
            title='Important Meeting',
            priority=TaskPriority.HIGH
        )
        Task.objects.create(
            user=self.user,
            title='Buy Groceries',
            priority=TaskPriority.LOW
        )
        
        url = reverse('api:task-list-create')
        response = self.client.get(url, {'search': 'meeting'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_task(self):
        """Test updating a task"""
        task = Task.objects.create(
            user=self.user,
            title='Original Title',
            priority=TaskPriority.LOW
        )
        
        url = reverse('api:task-detail', kwargs={'pk': task.id})
        update_data = {
            'title': 'Updated Title',
            'completed': True,
            'priority': TaskPriority.HIGH,
            'user': str(self.user.id)
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Title')
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)

    def test_delete_task(self):
        """Test deleting a task"""
        task = Task.objects.create(
            user=self.user,
            title='Task to Delete',
            priority=TaskPriority.MEDIUM
        )
        
        url = reverse('api:task-detail', kwargs={'pk': task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)


class UserAPITest(APITestCase):
    """Test cases for User API endpoints"""

    def setUp(self):
        self.user_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }

    def test_create_user(self):
        """Test creating a user via API"""
        url = reverse('api:user-list-create')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_list_users(self):
        """Test listing users via API"""
        User.objects.create(**self.user_data)
        User.objects.create(name='Jane Doe', email='jane@example.com')
        
        url = reverse('api:user-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_user_with_tasks(self):
        """Test getting user with their tasks"""
        user = User.objects.create(**self.user_data)
        Task.objects.create(
            user=user,
            title='Task 1',
            priority=TaskPriority.HIGH
        )
        Task.objects.create(
            user=user,
            title='Task 2',
            priority=TaskPriority.LOW
        )
        
        url = reverse('api:user-tasks', kwargs={'pk': user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tasks']), 2)


class StatisticsAPITest(APITestCase):
    """Test cases for Statistics API endpoints"""

    def setUp(self):
        self.user = User.objects.create(
            name='John Doe',
            email='john@example.com'
        )

    def test_task_statistics(self):
        """Test task statistics endpoint"""
        # Create some tasks
        Task.objects.create(
            user=self.user,
            title='Completed Task',
            completed=True,
            priority=TaskPriority.HIGH
        )
        Task.objects.create(
            user=self.user,
            title='Pending Task',
            completed=False,
            priority=TaskPriority.URGENT
        )
        
        url = reverse('api:task-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_tasks'], 2)
        self.assertEqual(data['completed_tasks'], 1)
        self.assertEqual(data['pending_tasks'], 1)
        self.assertEqual(data['high_priority_tasks'], 1)
        self.assertEqual(data['urgent_tasks'], 1)

    def test_user_statistics(self):
        """Test user statistics endpoint"""
        User.objects.create(name='Jane Doe', email='jane@example.com')
        
        url = reverse('api:user-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_users'], 2)
        self.assertEqual(data['active_users'], 2)


class BulkOperationsTest(APITestCase):
    """Test cases for bulk operations"""

    def setUp(self):
        self.user = User.objects.create(
            name='John Doe',
            email='john@example.com'
        )

    def test_bulk_complete_tasks(self):
        """Test bulk completing tasks"""
        task1 = Task.objects.create(
            user=self.user,
            title='Task 1',
            completed=False
        )
        task2 = Task.objects.create(
            user=self.user,
            title='Task 2',
            completed=False
        )
        
        url = reverse('api:bulk-complete-tasks')
        data = {'task_ids': [str(task1.id), str(task2.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        # Verify tasks are completed
        task1.refresh_from_db()
        task2.refresh_from_db()
        self.assertTrue(task1.completed)
        self.assertTrue(task2.completed)
