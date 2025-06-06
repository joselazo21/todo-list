"""
Shared domain exceptions
"""


class DomainException(Exception):
    """Base exception for domain errors"""
    pass


class ValidationError(DomainException):
    """Raised when domain validation fails"""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found"""
    pass


class UnauthorizedError(DomainException):
    """Raised when user is not authorized"""
    pass


class AuthenticationError(DomainException):
    """Raised when authentication fails"""
    pass


class AccountLockedError(AuthenticationError):
    """Raised when account is locked"""
    pass


class EmailNotVerifiedError(AuthenticationError):
    """Raised when email is not verified"""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when token is expired"""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid"""
    pass