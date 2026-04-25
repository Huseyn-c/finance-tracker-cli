"""Tests for SQLAlchemy repository."""

import os
import tempfile
from datetime import datetime

import pytest

from finance_tracker.domain.transaction import Transaction, TransactionType
from finance_tracker.infrastructure.sqlalchemy_repository import (
    SQLAlchemyTransactionRepository
)


@pytest.fixture
def sqlalchemy_repo():
    """Create SQLAlchemy repository with temporary database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_url = f"sqlite:///{f.name}"
        repo = SQLAlchemyTransactionRepository(db_url)
        yield repo
        # Cleanup
        try:
            os.unlink(f.name)
        except:
            pass


class TestSQLAlchemyRepository:
    """Test SQLAlchemy repository functionality."""
    
    def test_add_transaction(self, sqlalchemy_repo):
        """Test adding transaction to SQLAlchemy repository."""
        transaction = Transaction(
            amount=100.0,
            transaction_type=TransactionType.INCOME,
            description="Test income",
            categories=["work", "salary"]
        )
        
        sqlalchemy_repo.add(transaction)
        
        transactions = sqlalchemy_repo.get_all()
        assert len(transactions) == 1
        assert transactions[0].amount == 100.0
        assert transactions[0].description == "Test income"
    
    def test_remove_transaction(self, sqlalchemy_repo):
        """Test removing transaction from SQLAlchemy repository."""
        transaction = Transaction(
            amount=50.0,
            transaction_type=TransactionType.EXPENSE,
            description="Test expense",
            categories=["food"]
        )
        
        sqlalchemy_repo.add(transaction)
        transaction_id = transaction.id
        
        # Verify transaction exists
        transactions = sqlalchemy_repo.get_all()
        assert len(transactions) == 1
        
        # Remove transaction
        sqlalchemy_repo.remove(transaction_id)
        
        # Verify transaction removed
        transactions = sqlalchemy_repo.get_all()
        assert len(transactions) == 0
    
    def test_filter_by_type(self, sqlalchemy_repo):
        """Test filtering transactions by type."""
        # Add income transaction
        income_transaction = Transaction(
            amount=100.0,
            transaction_type=TransactionType.INCOME,
            description="Salary",
            categories=["work"]
        )
        sqlalchemy_repo.add(income_transaction)
        
        # Add expense transaction  
        expense_transaction = Transaction(
            amount=50.0,
            transaction_type=TransactionType.EXPENSE,
            description="Lunch",
            categories=["food"]
        )
        sqlalchemy_repo.add(expense_transaction)
        
        # Test income filter
        income_transactions = sqlalchemy_repo.get_by_filters(
            transaction_type="income"
        )
        assert len(income_transactions) == 1
        assert income_transactions[0].transaction_type == TransactionType.INCOME
        
        # Test expense filter
        expense_transactions = sqlalchemy_repo.get_by_filters(
            transaction_type="expense"
        )
        assert len(expense_transactions) == 1
        assert expense_transactions[0].transaction_type == TransactionType.EXPENSE
    
    def test_filter_by_category(self, sqlalchemy_repo):
        """Test filtering transactions by category."""
        # Add transaction with food category
        food_transaction = Transaction(
            amount=30.0,
            transaction_type=TransactionType.EXPENSE,
            description="Groceries",
            categories=["food", "shopping"]
        )
        sqlalchemy_repo.add(food_transaction)
        
        # Add transaction with different category
        other_transaction = Transaction(
            amount=80.0,
            transaction_type=TransactionType.EXPENSE,
            description="Electricity",
            categories=["utilities"]
        )
        sqlalchemy_repo.add(other_transaction)
        
        # Test food category filter
        food_transactions = sqlalchemy_repo.get_by_filters(category="food")
        assert len(food_transactions) == 1
        assert "food" in food_transactions[0].categories
        
        # Test utilities category filter
        utilities_transactions = sqlalchemy_repo.get_by_filters(category="utilities")
        assert len(utilities_transactions) == 1
        assert "utilities" in utilities_transactions[0].categories
    
    def test_filter_by_date(self, sqlalchemy_repo):
        """Test filtering transactions by date."""
        # Create transaction with specific date
        test_date = datetime(2024, 1, 15)
        transaction = Transaction(
            amount=100.0,
            transaction_type=TransactionType.INCOME,
            description="Test",
            categories=["test"]
        )
        transaction.date = test_date
        sqlalchemy_repo.add(transaction)
        
        # Test after filter
        after_transactions = sqlalchemy_repo.get_by_filters(
            after=datetime(2024, 1, 1)
        )
        assert len(after_transactions) == 1
        
        # Test before filter
        before_transactions = sqlalchemy_repo.get_by_filters(
            before=datetime(2024, 1, 31)
        )
        assert len(before_transactions) == 1
        
        # Test date range
        range_transactions = sqlalchemy_repo.get_by_filters(
            after=datetime(2024, 1, 1),
            before=datetime(2024, 1, 31)
        )
        assert len(range_transactions) == 1
    
    def test_remove_category(self, sqlalchemy_repo):
        """Test removing category from all transactions."""
        # Add transactions with test category
        transaction1 = Transaction(
            amount=10.0,
            transaction_type=TransactionType.EXPENSE,
            description="Lunch",
            categories=["food", "test"]
        )
        transaction2 = Transaction(
            amount=20.0,
            transaction_type=TransactionType.EXPENSE, 
            description="Dinner",
            categories=["food", "test", "restaurant"]
        )
        
        sqlalchemy_repo.add(transaction1)
        sqlalchemy_repo.add(transaction2)
        
        # Remove test category
        sqlalchemy_repo.remove_category("test")
        
        # Verify category removed from all transactions
        transactions = sqlalchemy_repo.get_all()
        for transaction in transactions:
            assert "test" not in transaction.categories
            assert "food" in transaction.categories
    
    def test_get_all_categories(self, sqlalchemy_repo):
        """Test getting all unique categories."""
        # Add transactions with various categories
        transaction1 = Transaction(
            amount=10.0,
            transaction_type=TransactionType.EXPENSE,
            description="Lunch",
            categories=["food", "restaurant"]
        )
        transaction2 = Transaction(
            amount=100.0,
            transaction_type=TransactionType.INCOME,
            description="Salary",
            categories=["work", "salary"]
        )
        transaction3 = Transaction(
            amount=30.0,
            transaction_type=TransactionType.EXPENSE,
            description="Groceries",
            categories=["food", "shopping"]
        )
        
        sqlalchemy_repo.add(transaction1)
        sqlalchemy_repo.add(transaction2)
        sqlalchemy_repo.add(transaction3)
        
        # Get all categories through transactions
        transactions = sqlalchemy_repo.get_all()
        all_categories = set()
        for transaction in transactions:
            all_categories.update(transaction.categories)
        
        # Should have all unique categories
        expected_categories = {"food", "restaurant", "work", "salary", "shopping"}
        assert all_categories == expected_categories