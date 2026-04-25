"""
Tests for Stage 2 features.
"""

import tempfile
import pytest
import os
from datetime import datetime, timedelta

from finance_tracker.application.dtos import AddTransactionDTO
from finance_tracker.domain.transaction import TransactionType
from finance_tracker.infrastructure.transaction_repository import SQLiteTransactionRepository
from finance_tracker.application.transaction_service import TransactionService


def test_remove_transaction():
    """Test removing a transaction."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        service = TransactionService(repo)

        dto = AddTransactionDTO(
            amount=100.0, 
            type_="income",
            description="Test"
        )
        transaction = service.add_transaction(dto)
        
        assert len(service.get_all_transactions()) == 1
        
        service.remove_transaction(str(transaction.id))
        
        assert len(service.get_all_transactions()) == 0
        
    finally:
        os.unlink(db_path)


def test_filter_by_type():
    """Test filtering transactions by type."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        service = TransactionService(repo)

        # Add income transaction
        income_dto = AddTransactionDTO(
            amount=100.0, 
            type_="income",
            description="Income"
        )
        service.add_transaction(income_dto)
        
        # Add expense transaction
        expense_dto = AddTransactionDTO(
            amount=50.0, 
            type_="expense",
            description="Expense"
        )
        service.add_transaction(expense_dto)
        
        # Test income filter
        income_tx = service.get_filtered_transactions(transaction_type="income")
        assert len(income_tx) == 1
        assert income_tx[0].transaction_type == TransactionType.INCOME
        
        # Test expense filter
        expense_tx = service.get_filtered_transactions(transaction_type="expense")
        assert len(expense_tx) == 1
        assert expense_tx[0].transaction_type == TransactionType.EXPENSE
        
    finally:
        os.unlink(db_path)


def test_categories():
    """Test transaction categories."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        service = TransactionService(repo)

        dto = AddTransactionDTO(
            amount=100.0, 
            type_="income",
            description="Test",
            categories=["salary", "work"]
        )
        transaction = service.add_transaction(dto)
        
        assert transaction.categories == ["salary", "work"]
        
        categories = service.get_all_categories()
        assert "salary" in categories
        assert "work" in categories
        
    finally:
        os.unlink(db_path)


def test_date_filters():
    """Test filtering by date."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        service = TransactionService(repo)

        dto = AddTransactionDTO(
            amount=100.0, 
            type_="income",
            description="Test"
        )
        service.add_transaction(dto)
        
        # Should find transactions from today
        today = datetime.now().date()
        transactions = service.get_filtered_transactions(after=datetime(today.year, today.month, today.day))
        assert len(transactions) >= 1
        
    finally:
        os.unlink(db_path)