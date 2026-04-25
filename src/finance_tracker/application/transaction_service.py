"""
Business logic for managing transactions.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from finance_tracker.application.dtos import AddTransactionDTO
from finance_tracker.domain.transaction import Transaction, TransactionType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from finance_tracker.infrastructure.transaction_repository import TransactionRepository


class TransactionService:
    """Handles transaction operations.
    
    This service coordinates between the presentation layer (CLI) 
    and the domain/infrastructure layers.
    """
    
    def __init__(self, repository: 'TransactionRepository') -> None:
        """Initialize service with repository.
        
        Args:
            repository: Transaction repository for data persistence
        """
        self.repository = repository
        logger.info("TransactionService initialized with %s", type(repository).__name__)
    
    def add_transaction(self, dto: AddTransactionDTO) -> Transaction:
        """Create and save a new transaction.
        
        Args:
            dto: Data transfer object with transaction details
            
        Returns:
            Created transaction object
            
        Raises:
            ValueError: If transaction data is invalid
        """
        logger.info("Adding transaction: %s - $%.2f (%s)", 
                   dto.description, dto.amount, dto.type_)
        
        transaction_type = TransactionType.from_string(dto.type_)
        
        transaction = Transaction(
            amount=dto.amount,
            transaction_type=transaction_type,
            description=dto.description,
            categories=dto.categories
        )
        
        self.repository.add(transaction)
        logger.debug("Transaction created with ID: %s", transaction.id)
        return transaction
    
    def get_all_transactions(self) -> list[Transaction]:
        """Get all transactions.
        
        Returns:
            List of all transactions
        """
        logger.debug("Fetching all transactions")
        transactions = self.repository.get_all()
        logger.info("Retrieved %d transactions", len(transactions))
        return transactions
    
    def remove_transaction(self, transaction_id: str) -> None:
        """Remove transaction by ID.
        
        Args:
            transaction_id: ID of transaction to remove
            
        Raises:
            Exception: If transaction cannot be removed
        """
        logger.info("Removing transaction: %s", transaction_id)
        self.repository.remove(transaction_id)
        logger.debug("Transaction %s removed", transaction_id)
    
    def get_filtered_transactions(
        self,
        after: datetime | None = None,
        before: datetime | None = None,
        category: str | None = None,
        transaction_type: str | None = None
    ) -> list[Transaction]:
        """Get transactions with filters.
        
        Args:
            after: Show transactions after this date
            before: Show transactions before this date  
            category: Filter by category name
            transaction_type: Filter by type ("income" or "expense")
            
        Returns:
            Filtered list of transactions
        """
        logger.debug("Filtering transactions: after=%s, before=%s, category=%s, type=%s",
                    after, before, category, transaction_type)
        
        transactions = self.repository.get_by_filters(after, before, category, transaction_type)
        logger.info("Found %d transactions with filters", len(transactions))
        return transactions
    
    def get_all_categories(self) -> list[str]:
        """Get all unique categories.
        
        Returns:
            Sorted list of unique category names
        """
        logger.debug("Fetching all categories")
        transactions = self.repository.get_all()
        categories = set()
        
        for transaction in transactions:
            categories.update(transaction.categories)
        
        result = sorted(categories)
        logger.info("Found %d unique categories: %s", len(result), result)
        return result
    
    def remove_category(self, category_name: str) -> None:
        """Remove category from all transactions.
        
        Args:
            category_name: Name of category to remove
        """
        logger.info("Removing category '%s' from all transactions", category_name)
        self.repository.remove_category(category_name)
        logger.debug("Category '%s' removed", category_name)
