"""
Utility functions for the API
"""
import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def get_client_ip(request):
    """Get the client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_password_strength(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit.")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")
    
    return password


def is_safe_url(url, allowed_hosts=None):
    """
    Check if a URL is safe for redirects
    """
    if not url:
        return False
    
    # Basic URL validation
    if url.startswith('//') or url.startswith('http://') or url.startswith('https://'):
        return False
    
    return True


def generate_username_from_email(email):
    """Generate a unique username from email"""
    base_username = email.split('@')[0]
    # Remove any non-alphanumeric characters
    base_username = re.sub(r'[^a-zA-Z0-9]', '', base_username)
    return base_username[:30]  # Django username max length


def calculate_password_expiry(user):
    """Calculate when user's password expires"""
    # Password expires after 90 days
    if user.date_joined:
        return user.date_joined + timedelta(days=90)
    return timezone.now() + timedelta(days=90)


def is_password_expired(user):
    """Check if user's password has expired"""
    expiry_date = calculate_password_expiry(user)
    return timezone.now() > expiry_date


def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove any path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename


def mask_email(email):
    """Mask email address for logging/display"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours"
    else:
        days = seconds // 86400
        return f"{days} days"