"""
URL configuration for Tasks app
"""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task CRUD operations
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<uuid:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    
    # Bulk operations
    path('bulk-complete/', views.bulk_complete_tasks, name='bulk-complete-tasks'),
    
    # Statistics and analytics
    path('statistics/', views.task_statistics, name='task-statistics'),
    path('productivity/', views.user_productivity, name='user-productivity'),
    
    path('<uuid:task_id>/suggestions/', views.task_suggestions, name='task-suggestions'),
    path('auto-prioritize/', views.auto_prioritize_tasks, name='auto-prioritize-tasks'),
]