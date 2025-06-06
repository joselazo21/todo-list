"""
Models for users app - imports from infrastructure layer
"""
from .infrastructure.models import UserModel

# Make the model available at the app level
__all__ = ['UserModel']