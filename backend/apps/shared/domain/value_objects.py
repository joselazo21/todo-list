"""
Shared domain value objects
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
import uuid


@dataclass(frozen=True)
class EntityId:
    """Value object for entity identifiers"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Entity ID cannot be empty")
    
    @classmethod
    def generate(cls) -> 'EntityId':
        """Generate a new UUID-based entity ID"""
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Email:
    """Value object for email addresses"""
    value: str
    
    def __post_init__(self):
        if not self.value or '@' not in self.value:
            raise ValueError("Invalid email address")
        
        if len(self.value) > 254:
            raise ValueError("Email address is too long")
    
    @property
    def domain(self) -> str:
        """Get email domain"""
        return self.value.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get email local part"""
        return self.value.split('@')[0]
    
    def __str__(self) -> str:
        return self.value.lower()


@dataclass(frozen=True)
class IPAddress:
    """Value object for IP addresses"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("IP address cannot be empty")
        # Basic validation - in real app, use ipaddress module
        parts = self.value.split('.')
        if len(parts) != 4:
            raise ValueError("Invalid IP address format")
    
    def __str__(self) -> str:
        return self.value


@dataclass
class AuditInfo:
    """Value object for audit information"""
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    @classmethod
    def create_new(cls, user_id: Optional[str] = None) -> 'AuditInfo':
        """Create audit info for new entity"""
        now = datetime.now()
        return cls(
            created_at=now,
            updated_at=now,
            created_by=user_id,
            updated_by=user_id
        )
    
    def update(self, user_id: Optional[str] = None) -> 'AuditInfo':
        """Update audit info"""
        return AuditInfo(
            created_at=self.created_at,
            updated_at=datetime.now(),
            created_by=self.created_by,
            updated_by=user_id
        )


@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts"""
    amount: float
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money amounts"""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        
        return Money(result_amount, self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass
class Pagination:
    """Value object for pagination"""
    page: int
    page_size: int
    total_items: int
    
    def __post_init__(self):
        if self.page < 1:
            raise ValueError("Page must be greater than 0")
        
        if self.page_size < 1:
            raise ValueError("Page size must be greater than 0")
        
        if self.total_items < 0:
            raise ValueError("Total items cannot be negative")
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        if self.total_items == 0:
            return 0
        return (self.total_items - 1) // self.page_size + 1
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1


@dataclass
class SearchCriteria:
    """Value object for search criteria"""
    query: str
    filters: dict
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    pagination: Optional[Pagination] = None
    
    def __post_init__(self):
        if self.sort_order not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
    
    def add_filter(self, key: str, value: Any) -> 'SearchCriteria':
        """Add a filter to the search criteria"""
        new_filters = self.filters.copy()
        new_filters[key] = value
        
        return SearchCriteria(
            query=self.query,
            filters=new_filters,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            pagination=self.pagination
        )