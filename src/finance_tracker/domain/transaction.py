"""
Core transaction business model.
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4


class TransactionType(Enum):
    """Types of financial transactions."""
    
    INCOME = "income"
    EXPENSE = "expense"
    
    @classmethod
    def from_string(cls, type_str: str) -> 'TransactionType':
        """Create TransactionType from string.
        
        Args:
            type_str: String representation of transaction type
            
        Returns:
            Corresponding TransactionType enum
            
        Raises:
            ValueError: If type_str is not 'income' or 'expense'
        """
        try:
            return cls(type_str.lower())
        except ValueError as e:
            error_msg = f"Invalid transaction type: {type_str}. Must be 'income' or 'expense'"
            raise ValueError(error_msg) from e


class Transaction:
    """Represents a single financial transaction.
    
    Attributes:
        id: Unique identifier
        amount: Transaction amount (positive)
        transaction_type: Type of transaction (income/expense)
        description: Transaction description
        date: Transaction date
        created_at: Creation timestamp
        categories: List of category names
    """
    
    def __init__(
        self, 
        amount: float, 
        transaction_type: TransactionType, 
        description: str, 
        categories: list[str] | None = None
    ) -> None:
        """Initialize a transaction with validated data.
        
        Args:
            amount: Positive transaction amount
            transaction_type: Type of transaction
            description: Transaction description
            categories: Optional list of categories
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.id = str(uuid4())
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description.strip()
        self.date = datetime.now()
        self.created_at = datetime.now()
        self.categories = categories or []
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        sign = "+" if self.transaction_type.value == "income" else "-"
        cat_str = f" [{', '.join(self.categories)}]" if self.categories else ""
        return f"{sign}${self.amount:.2f} - {self.description}{cat_str}"