"""
URL configuration for Authentication API endpoints
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('token/refresh/', views.refresh_token, name='refresh_token_compat'),  # Compatibility route
    path('validate/', views.validate_token, name='validate_token'),
    
    # Password reset endpoints
    path('password-reset/request/', views.request_password_reset, name='request_password_reset'),
    path('password-reset/confirm/', views.reset_password, name='reset_password'),
    
    # Session and security endpoints
    path('sessions/', views.get_sessions, name='get_sessions'),
    path('security-events/', views.get_security_events, name='get_security_events'),
]