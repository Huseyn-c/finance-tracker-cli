"""SQLAlchemy repository for transactions."""

import json
import logging
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from finance_tracker.domain.transaction import Transaction, TransactionType
from finance_tracker.infrastructure.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)

Base = declarative_base()


class TransactionModel(Base):
    """SQLAlchemy model for transaction table."""

    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    categories = Column(Text, default="[]")


class SQLAlchemyTransactionRepository(TransactionRepository):
    """Repository implementation using SQLAlchemy."""

    def __init__(self, db_url: str = "sqlite:///finance_alchemy.db") -> None:
        """Initialize repository with database URL."""
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.debug("SQLAlchemy repository initialized with URL: %s", db_url)

    def add(self, transaction: Transaction) -> None:
        """Save transaction to database."""
        logger.debug("Saving transaction to SQLAlchemy: %s", transaction.id)
        session = self.Session()
        try:
            model = TransactionModel(
                id=str(transaction.id),
                amount=transaction.amount,
                type=transaction.transaction_type.value,
                description=transaction.description,
                date=transaction.date,
                created_at=transaction.created_at,
                categories=json.dumps(transaction.categories)
            )
            session.add(model)
            session.commit()
            logger.debug("Transaction saved via SQLAlchemy: %s", transaction.id)
        except Exception as e:
            logger.error("Error saving transaction via SQLAlchemy: %s", e)
            raise
        finally:
            session.close()

    def get_all(self) -> list[Transaction]:
        """Get all transactions from database."""
        logger.debug("Fetching all transactions via SQLAlchemy")
        return self.get_by_filters()

    def remove(self, transaction_id: str) -> None:
        """Remove transaction by ID."""
        logger.debug("Removing transaction via SQLAlchemy: %s", transaction_id)
        session = self.Session()
        try:
            session.query(TransactionModel).filter_by(id=transaction_id).delete()
            session.commit()
            logger.debug("Transaction removed via SQLAlchemy: %s", transaction_id)
        except Exception as e:
            logger.error("Error removing transaction via SQLAlchemy: %s", e)
            raise
        finally:
            session.close()

    def get_by_filters(
        self,
        after: datetime | None = None,
        before: datetime | None = None,
        category: str | None = None,
        transaction_type: str | None = None
    ) -> list[Transaction]:
        """Get transactions with optional filters."""
        logger.debug(
            "Querying transactions via SQLAlchemy with filters: "
            "after=%s, before=%s, category=%s, type=%s",
            after, before, category, transaction_type
        )
        
        session = self.Session()
        try:
            query = session.query(TransactionModel)

            if after:
                query = query.filter(TransactionModel.date >= after)
            if before:
                query = query.filter(TransactionModel.date <= before)
            if transaction_type:
                query = query.filter(TransactionModel.type == transaction_type)

            models = query.order_by(TransactionModel.date.desc()).all()
            transactions = []

            for model in models:
                cat_list = json.loads(str(model.categories))

                if category and category not in cat_list:
                    continue

                if str(model.type) == "income":
                    tx_type = TransactionType.INCOME
                else:
                    tx_type = TransactionType.EXPENSE

                amount_val = float(str(model.amount))
                desc_val = str(model.description)
                model_id = str(model.id)
                model_date = datetime.fromisoformat(model.date.isoformat())
                model_created = datetime.fromisoformat(model.created_at.isoformat())

                transaction = Transaction(
                    amount=amount_val,
                    transaction_type=tx_type,
                    description=desc_val,
                    categories=cat_list
                )

                transaction.id = model_id
                transaction.date = model_date
                transaction.created_at = model_created

                transactions.append(transaction)

            logger.debug("Retrieved %d transactions via SQLAlchemy", len(transactions))
            return transactions

        except Exception as e:
            logger.error("Error querying transactions via SQLAlchemy: %s", e)
            raise
        finally:
            session.close()

    def remove_category(self, category_name: str) -> None:
        """Remove category from all transactions."""
        logger.debug(
            "Removing category '%s' from all transactions via SQLAlchemy", 
            category_name
        )
        session = self.Session()
        try:
            models = session.query(TransactionModel).all()
            updated_count = 0

            for model in models:
                cat_list = json.loads(str(model.categories))
                if category_name in cat_list:
                    new_cats = [c for c in cat_list if c != category_name]
                    session.query(TransactionModel).filter_by(id=model.id).update(
                        {"categories": json.dumps(new_cats)}
                    )
                    updated_count += 1

            session.commit()
            logger.info(
                "Removed category '%s' from %d transactions via SQLAlchemy", 
                category_name, updated_count
            )
        except Exception as e:
            logger.error("Error removing category via SQLAlchemy: %s", e)
            raise
        finally:
            session.close()
