from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Task endpoints
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    
    # User endpoints
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:pk>/tasks/', views.UserTasksView.as_view(), name='user-tasks'),
    
    # Statistics endpoints
    path('statistics/tasks/', views.task_statistics, name='task-statistics'),
    path('statistics/users/', views.user_statistics, name='user-statistics'),
    
    # Bulk operations
    path('tasks/bulk-complete/', views.bulk_complete_tasks, name='bulk-complete-tasks'),
    
    # Registro de usuarios
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    # Login de usuarios
    path('auth/login/', views.LoginView.as_view(), name='login'),
]