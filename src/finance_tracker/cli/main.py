"""Command-line interface for finance tracker."""

import logging
import os
from datetime import datetime

import typer

from finance_tracker.application.dtos import AddTransactionDTO
from finance_tracker.application.transaction_service import TransactionService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/finance_tracker.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

backend = os.getenv("FINANCE_TRACKER_BACKEND", "sqlite")

if backend == "sqlalchemy":
    from finance_tracker.infrastructure.sqlalchemy_repository import (
        SQLAlchemyTransactionRepository,
    )
    repo = SQLAlchemyTransactionRepository()
    logger.info("Using SQLAlchemy backend")
else:
    from finance_tracker.infrastructure.transaction_repository import SQLiteTransactionRepository
    repo = SQLiteTransactionRepository()
    logger.info("Using SQLite backend")

service = TransactionService(repo)

app = typer.Typer()

_CATEGORIES_OPTION = typer.Option([], "--category", "-c", help="Transaction categories")


def validate_input(amount: float, type: str) -> None:
    """Проверяет входные данные перед созданием транзакции"""
    if amount <= 0:
        logger.error("Invalid amount: %s", amount)
        raise ValueError("Amount must be positive number")
    
    if type not in ["income", "expense"]:
        logger.error("Invalid transaction type: %s", type)
        raise ValueError("Type must be 'income' or 'expense'")


@app.command()
def add(
    amount: float = typer.Argument(..., help="Transaction amount"),
    description: str = typer.Argument(..., help="Transaction description"), 
    type: str = typer.Option("expense", "--type", "-t", help="income or expense"),
    categories: list[str] = _CATEGORIES_OPTION
) -> None:
    """Add a new transaction to your records."""
    try:
        validate_input(amount, type)
        
        dto = AddTransactionDTO(
            amount=amount,
            type_=type, 
            description=description,
            categories=categories
        )
        
        transaction = service.add_transaction(dto)
        
        print(f"Added {transaction.transaction_type.value}: ${transaction.amount:.2f}")
        print(f"Description: {transaction.description}")
        if categories:
            print(f"Categories: {', '.join(categories)}")
        print(f"Date: {transaction.date.strftime('%Y-%m-%d %H:%M')}")
        print(f"ID: {transaction.id}")
        
        logger.info("Transaction added successfully: %s", transaction.id)
        
    except ValueError as e:
        logger.error("Validation error: %s", e)
        print(f"Error: {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        logger.error("Unexpected error adding transaction: %s", e)
        print(f"Unexpected error: {e}")
        raise typer.Exit(code=1) from e


@app.command(name="list")
def list_cmd(
    after: str = typer.Option(None, "--after", help="Show transactions after date (YYYY-MM-DD)"),
    before: str = typer.Option(None, "--before", help="Show transactions before date (YYYY-MM-DD)"),
    category: str = typer.Option(None, "--category", help="Filter by category"),
    type: str = typer.Option(None, "--type", help="Filter by type (income/expense)")
) -> None:
    """Show transactions with optional filters."""
    try:
        after_date = datetime.fromisoformat(after) if after else None
        before_date = datetime.fromisoformat(before) if before else None
        
        transactions = service.get_filtered_transactions(
            after=after_date,
            before=before_date,
            category=category,
            transaction_type=type
        )
        
        if not transactions:
            print("No transactions found.")
            logger.info("No transactions found with filters")
            return
        
        print(f"Transactions ({len(transactions)}):")
        print("-" * 50)
        
        for i, transaction in enumerate(transactions, 1):
            sign = "+" if transaction.transaction_type.value == "income" else "-"
            cat_str = f" [{', '.join(transaction.categories)}]" if transaction.categories else ""
            line = f"{i}. {sign}${transaction.amount:.2f} - {transaction.description}{cat_str}"
            print(line)
            print(f"   {transaction.date.strftime('%Y-%m-%d')} | ID: {transaction.id}")
            print()
            
        logger.info("Displayed %d transactions", len(transactions))
            
    except ValueError as e:
        logger.error("Invalid date format: %s", e)
        print(f"Invalid date format: {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        logger.error("Error listing transactions: %s", e)
        print(f"Unexpected error: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def remove(transaction_id: str = typer.Argument(..., help="Transaction ID to remove")) -> None:
    """Remove a transaction by its ID."""
    try:
        # Проверяем существует ли транзакция
        transactions = service.get_filtered_transactions()
        found = any(t.id == transaction_id for t in transactions)
        
        if not found:
            logger.warning("Transaction not found: %s", transaction_id)
            print(f"Error: Transaction {transaction_id} not found")
            raise typer.Exit(code=1)
            
        service.remove_transaction(transaction_id)
        print(f"Transaction {transaction_id} removed")
        logger.info("Transaction removed: %s", transaction_id)
        
    except Exception as e:
        logger.error("Error removing transaction: %s", e)
        print(f"Error removing transaction: {e}")
        raise typer.Exit(code=1) from e


@app.command(name="add-category")
def add_category(category: str = typer.Argument(..., help="Category name to add")) -> None:
    """Add a new category."""
    try:
        print(f"Category '{category}' added")
        logger.info("Category added: %s", category)
    except Exception as e:
        logger.error("Error adding category: %s", e)
        print(f"Error adding category: {e}")
        raise typer.Exit(code=1) from e


@app.command(name="list-categories")
def list_categories() -> None:
    """Show all available categories."""
    try:
        categories = service.get_all_categories()
        
        if not categories:
            print("No categories found. Add some transactions with categories.")
            logger.info("No categories found")
            return
        
        print("Available categories:")
        for category in categories:
            print(f"  - {category}")
            
        logger.info("Displayed %d categories", len(categories))
        
    except Exception as e:
        logger.error("Error listing categories: %s", e)
        print(f"Unexpected error: {e}")
        raise typer.Exit(code=1) from e


@app.command(name="remove-category")
def remove_category(category: str = typer.Argument(..., help="Category name to remove")) -> None:
    """Remove a category from all transactions."""
    try:
        service.remove_category(category)
        print(f"Category '{category}' removed from all transactions")
        logger.info("Category removed from all transactions: %s", category)
    except Exception as e:
        logger.error("Error removing category: %s", e)
        print(f"Error removing category: {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    app()
