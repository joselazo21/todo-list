from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Case, When, BooleanField
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters_rf
import logging

from .models import Task, User, TaskPriority
from .serializers import (
    TaskDetailSerializer, TaskListSerializer, TaskCreateSerializer,
    UserSerializer, UserTasksSerializer
)

logger = logging.getLogger(__name__)


class TaskFilter(filters_rf.FilterSet):
    """Custom filter for tasks"""
    completed = filters_rf.BooleanFilter()
    priority = filters_rf.ChoiceFilter(choices=TaskPriority.choices)
    overdue = filters_rf.BooleanFilter(method='filter_overdue')
    due_date_from = filters_rf.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = filters_rf.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    
    class Meta:
        model = Task
        fields = ['completed', 'priority', 'user']

    def filter_overdue(self, queryset, name, value):
        """Filter overdue tasks"""
        from django.utils import timezone
        if value:
            return queryset.filter(
                due_date__lt=timezone.now(),
                completed=False
            )
        return queryset


class TaskListCreateView(generics.ListCreateAPIView):
    """
    List all tasks or create a new task.
    Supports filtering, searching, and ordering.
    """
    queryset = Task.objects.select_related('user').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description', 'user__name']
    ordering_fields = ['created_at', 'due_date', 'priority', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskListSerializer

    def perform_create(self, serializer):
        """Log task creation"""
        task = serializer.save()
        logger.info(f"Task created: {task.title} for user {task.user.name}")


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a task instance.
    """
    queryset = Task.objects.select_related('user').all()
    serializer_class = TaskDetailSerializer

    def perform_update(self, serializer):
        """Log task updates"""
        task = serializer.save()
        logger.info(f"Task updated: {task.title}")

    def perform_destroy(self, instance):
        """Log task deletion"""
        logger.info(f"Task deleted: {instance.title}")
        super().perform_destroy(instance)


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user.
    """
    queryset = User.objects.annotate(
        tasks_count=Count('tasks')
    ).all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'email', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        """Log user creation"""
        user = serializer.save()
        logger.info(f"User created: {user.name} ({user.email})")


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user instance.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        """Log user updates"""
        user = serializer.save()
        logger.info(f"User updated: {user.name}")

    def perform_destroy(self, instance):
        """Log user deletion"""
        logger.info(f"User deleted: {instance.name}")
        super().perform_destroy(instance)


class UserTasksView(generics.RetrieveAPIView):
    """
    Get a user with all their tasks.
    """
    queryset = User.objects.prefetch_related('tasks').all()
    serializer_class = UserTasksSerializer


@api_view(['GET'])
def task_statistics(request):
    """
    Get task statistics.
    """
    try:
        stats = Task.objects.aggregate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(completed=True)),
            pending_tasks=Count('id', filter=Q(completed=False)),
            high_priority_tasks=Count('id', filter=Q(priority=TaskPriority.HIGH)),
            urgent_tasks=Count('id', filter=Q(priority=TaskPriority.URGENT)),
        )
        
        # Calculate overdue tasks
        from django.utils import timezone
        overdue_count = Task.objects.filter(
            due_date__lt=timezone.now(),
            completed=False
        ).count()
        
        stats['overdue_tasks'] = overdue_count
        stats['completion_rate'] = (
            (stats['completed_tasks'] / stats['total_tasks'] * 100) 
            if stats['total_tasks'] > 0 else 0
        )
        
        return Response(stats)
    except Exception as e:
        logger.error(f"Error getting task statistics: {str(e)}")
        return Response(
            {'error': 'Unable to fetch statistics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def user_statistics(request):
    """
    Get user statistics.
    """
    try:
        stats = User.objects.aggregate(
            total_users=Count('id'),
            active_users=Count('id', filter=Q(is_active=True)),
        )
        
        # Users with tasks
        users_with_tasks = User.objects.annotate(
            task_count=Count('tasks')
        ).filter(task_count__gt=0).count()
        
        stats['users_with_tasks'] = users_with_tasks
        
        return Response(stats)
    except Exception as e:
        logger.error(f"Error getting user statistics: {str(e)}")
        return Response(
            {'error': 'Unable to fetch statistics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def bulk_complete_tasks(request):
    """
    Mark multiple tasks as completed.
    """
    task_ids = request.data.get('task_ids', [])
    
    if not task_ids:
        return Response(
            {'error': 'task_ids is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from django.utils import timezone
        updated_count = Task.objects.filter(
            id__in=task_ids,
            completed=False
        ).update(
            completed=True,
            completed_at=timezone.now()
        )
        
        logger.info(f"Bulk completed {updated_count} tasks")
        return Response({
            'message': f'{updated_count} tasks marked as completed',
            'updated_count': updated_count
        })
    except Exception as e:
        logger.error(f"Error in bulk complete: {str(e)}")
        return Response(
            {'error': 'Unable to complete tasks'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Backward compatibility aliases
TaskListCreate = TaskListCreateView
TaskDetail = TaskDetailView
UserListCreate = UserListCreateView
UserDetail = UserDetailView