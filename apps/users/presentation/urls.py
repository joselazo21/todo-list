"""
URL configuration for Users app
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User CRUD operations
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<uuid:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # User actions
    path('<uuid:user_id>/change-password/', views.change_password, name='change-password'),
    path('<uuid:user_id>/verify-email/', views.verify_email, name='verify-email'),
    path('<uuid:user_id>/unlock/', views.unlock_account, name='unlock-account'),
    path('<uuid:user_id>/security-recommendations/', views.security_recommendations, name='security-recommendations'),
    
    # Statistics and admin operations
    path('statistics/', views.user_statistics, name='user-statistics'),
]