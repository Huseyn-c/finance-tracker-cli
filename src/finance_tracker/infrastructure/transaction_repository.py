"""
SQLite database operations for transactions.
"""

import ast
import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime

from finance_tracker.domain.transaction import Transaction, TransactionType

logger = logging.getLogger(__name__)


class TransactionRepository(ABC):
    """Interface for transaction storage."""
    
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        """Save a transaction to storage."""
        pass
    
    @abstractmethod
    def get_all(self) -> list[Transaction]:
        """Get all transactions from storage."""
        pass
    
    @abstractmethod
    def remove(self, transaction_id: str) -> None:
        """Remove transaction by ID."""
        pass
    
    @abstractmethod
    def get_by_filters(
        self,
        after: datetime | None = None,
        before: datetime | None = None,
        category: str | None = None,
        transaction_type: str | None = None
    ) -> list[Transaction]:
        """Get transactions with filters."""
        pass
    
    @abstractmethod
    def remove_category(self, category_name: str) -> None:
        """Remove category from all transactions."""
        pass


class SQLiteTransactionRepository(TransactionRepository):
    """Stores transactions in SQLite database."""
    
    def __init__(self, db_path: str = "finance.db") -> None:
        """Initialize with database path."""
        self.db_path = db_path
        self._create_tables()
        logger.debug("SQLite repository initialized with database: %s", db_path)
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    categories TEXT DEFAULT '[]'
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date 
                ON transactions(date)
            """)
        logger.debug("Database tables created/verified")
    
    def add(self, transaction: Transaction) -> None:
        """Save a transaction to the database."""
        logger.debug("Saving transaction to SQLite: %s", transaction.id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(transaction.id),
                    transaction.amount,
                    transaction.transaction_type.value,
                    transaction.description,
                    transaction.date.isoformat(),
                    transaction.created_at.isoformat(),
                    str(transaction.categories)
                )
            )
        logger.debug("Transaction saved: %s", transaction.id)
    
    def get_all(self) -> list[Transaction]:
        """Get all transactions from database."""
        logger.debug("Fetching all transactions from SQLite")
        return self.get_by_filters()
    
    def remove(self, transaction_id: str) -> None:
        """Remove transaction by ID."""
        logger.debug("Removing transaction from SQLite: %s", transaction_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        logger.debug("Transaction removed: %s", transaction_id)
    
    def get_by_filters(
        self,
        after: datetime | None = None,
        before: datetime | None = None,
        category: str | None = None,
        transaction_type: str | None = None
    ) -> list[Transaction]:
        """Get transactions with filters."""
        logger.debug(
            "Querying transactions with filters: "
            "after=%s, before=%s, category=%s, type=%s",
            after, before, category, transaction_type
        )
        
        query = (
            "SELECT id, amount, type, description, date, created_at, categories "
            "FROM transactions WHERE 1=1"
        )
        params = []
        
        if after:
            query += " AND date >= ?"
            params.append(after.isoformat())
        
        if before:
            query += " AND date <= ?"
            params.append(before.isoformat())
        
        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY date DESC"
        
        transactions = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                (transaction_id, amount, type_str, description, 
                 date_str, created_str, categories_str) = row
                
                if type_str == "income":
                    tx_type = TransactionType.INCOME
                else:
                    tx_type = TransactionType.EXPENSE
                
                # Parse categories from string safely
                categories = (ast.literal_eval(categories_str) 
                            if categories_str else [])
                
                # Skip if category filter doesn't match
                if category and category not in categories:
                    continue
                
                transaction = Transaction(
                    amount=amount,
                    transaction_type=tx_type,
                    description=description,
                    categories=categories
                )
                
                transaction.id = transaction_id
                transaction.date = datetime.fromisoformat(date_str)
                transaction.created_at = datetime.fromisoformat(created_str)
                
                transactions.append(transaction)
        
        logger.debug("Retrieved %d transactions from SQLite", len(transactions))
        return transactions
    
    def remove_category(self, category_name: str) -> None:
        """Remove category from all transactions."""
        logger.debug(
            "Removing category '%s' from all transactions in SQLite", 
            category_name
        )
        transactions = self.get_all()
        updated_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for transaction in transactions:
                if category_name in transaction.categories:
                    updated_categories = [
                        c for c in transaction.categories 
                        if c != category_name
                    ]
                    conn.execute(
                        "UPDATE transactions SET categories = ? WHERE id = ?",
                        (str(updated_categories), str(transaction.id))
                    )
                    updated_count += 1
        
        logger.info(
            "Removed category '%s' from %d transactions", 
            category_name, updated_count
        )
