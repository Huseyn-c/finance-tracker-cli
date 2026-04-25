"""
Tests for transaction functionality.
"""

import tempfile
import pytest
import os

from finance_tracker.domain.transaction import Transaction
from finance_tracker.application.dtos import AddTransactionDTO
from finance_tracker.domain.transaction import TransactionType
from finance_tracker.infrastructure.transaction_repository import SQLiteTransactionRepository
from finance_tracker.application.transaction_service import TransactionService


def test_create_transaction():
    """Test creating a transaction works correctly."""
    tx = Transaction(100.0, TransactionType.INCOME, "Salary")
    assert tx.amount == 100.0
    assert tx.transaction_type == TransactionType.INCOME


def test_transaction_validation():
    """Test that invalid transactions raise errors."""
    with pytest.raises(ValueError):
        Transaction(-50.0, TransactionType.EXPENSE, "Test")


def test_add_transaction():
    """Test the complete add transaction flow."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        service = TransactionService(repo)

        dto = AddTransactionDTO(
            amount=150.0, 
            type_="income",
            description="Bonus"
        )
        transaction = service.add_transaction(dto)
        
        assert transaction.amount == 150.0
        assert len(service.get_all_transactions()) == 1
        
    finally:
        os.unlink(db_path)


def test_persistence():
    """Test that data persists between sessions."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        service = TransactionService(repo)

        dto = AddTransactionDTO(
            amount=200.0, 
            type_="income",
            description="Salary"
        )
        service.add_transaction(dto)
        
        new_repo = SQLiteTransactionRepository(db_path)
        new_service = TransactionService(new_repo)
        transactions = new_service.get_all_transactions()
        
        assert len(transactions) == 1
        assert transactions[0].amount == 200.0
        
    finally:
        os.unlink(db_path)


def test_database_schema():
    """Test database setup and basic operations."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repo = SQLiteTransactionRepository(db_path)
        tx = Transaction(100.0, TransactionType.EXPENSE, "Test")
        repo.add(tx)
        
        transactions = repo.get_all()
        assert len(transactions) == 1
        
    finally:
        os.unlink(db_path)