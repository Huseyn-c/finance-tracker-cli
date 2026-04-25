# Architecture Documentation

This document describes the architecture of the Finance Tracker CLI project, which follows **Clean Architecture** principles with strict separation of concerns across four layers.

---

## 1. Use Cases

The application supports the following user actions:

### Add Transaction
- **Actor:** CLI User
- **Inputs:** amount, description, type (income/expense), categories, date (defaults to today)
- **Flow:**
  1. Validate that `amount > 0`
  2. Create a `Transaction` domain entity
  3. Persist via `TransactionRepository.add()`
  4. Return success confirmation
- **Failure:** invalid amount → "Amount must be positive"

### List Transactions
- **Actor:** CLI User
- **Inputs:** `--after`, `--before`, `--category`, `--type` filters (all optional)
- **Flow:**
  1. Parse and validate filter parameters
  2. Retrieve transactions via `TransactionRepository.get_by_filters()`
  3. Format and display the results
- **Failure:** invalid date format → "Invalid date format"

### Remove Transaction
- **Actor:** CLI User
- **Inputs:** `transaction_id`
- **Flow:**
  1. Verify the transaction exists
  2. Remove via `TransactionRepository.remove()`
  3. Return success confirmation
- **Failure:** transaction not found → "Transaction not found"

### Manage Categories
- **List categories:** retrieve all unique categories from existing transactions
- **Remove category:** remove a category name from all transactions that contain it

---

## 2. Domain Model

```
+--------------------+
|    Transaction     |
+--------------------+
| id: str (UUID)     |
| amount: float      |
| transaction_type:  |
|   TransactionType  |
| description: str   |
| date: datetime     |
| created_at: dt     |
| categories: list   |
+--------------------+
```

**Invariants:**
- `amount > 0`
- `transaction_type ∈ {income, expense}`
- `categories` is a list (can be empty)

**Value Objects:**
- `TransactionType` — Enum with values `INCOME` and `EXPENSE`

---

## 3. Layered Architecture

```
┌──────────────┐   User input / output
│ Presentation │   (CLI using Typer)
└──────┬───────┘
       │ calls
┌──────▼───────┐   Use case coordination
│ Application  │   (TransactionService, DTOs)
└──────┬───────┘
       │ uses
┌──────▼───────┐   Pure business rules & entities
│   Domain     │   (Transaction, TransactionType)
└──────┬───────┘
       │ implements ports
┌──────▼───────┐   External details
│Infrastructure│   (SQLite + SQLAlchemy repositories)
└──────────────┘
```

**Dependency rule:** arrows only point inward — outer layers depend on inner layers, never the reverse.

### Layer Responsibilities

| Layer | Responsibility | Examples |
|-------|---------------|----------|
| **Presentation** | CLI argument parsing, output formatting | `cli/main.py` |
| **Application** | Use case coordination, service logic, DTOs | `application/transaction_service.py`, `application/dtos.py` |
| **Domain** | Business entities and validation rules (zero I/O) | `domain/transaction.py` |
| **Infrastructure** | Database operations, external integrations | `infrastructure/transaction_repository.py`, `infrastructure/sqlalchemy_repository.py` |

---

## 4. Ports & Interfaces

The Application layer depends on abstract interfaces, not concrete implementations. This enables testability and backend swapping.

```python
class TransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> None: ...

    @abstractmethod
    def get_all(self) -> list[Transaction]: ...

    @abstractmethod
    def remove(self, transaction_id: str) -> None: ...

    @abstractmethod
    def get_by_filters(
        self,
        after: datetime | None = None,
        before: datetime | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
    ) -> list[Transaction]: ...

    @abstractmethod
    def remove_category(self, category_name: str) -> None: ...
```

The repository has two concrete implementations:
- `SQLiteTransactionRepository` — uses raw SQLite via Python's `sqlite3` module
- `SQLAlchemyTransactionRepository` — uses SQLAlchemy ORM

The active backend is selected at runtime via the `FINANCE_TRACKER_BACKEND` environment variable.

---

## 5. End-to-End Feature Flow

Example: adding a new transaction via the CLI.

```
CLI (Presentation layer)
└─ command `add()` collects user input:
   amount=1500.00, type=income, categories=['salary'], description='Monthly salary'
   ↓
Application layer
└─ TransactionService.add_transaction(dto):
   • Pydantic DTO validates input (amount > 0, valid type, etc.)
   • Builds domain entity: Transaction(...)
   • Enforces business invariants
   • Calls TransactionRepository.add(transaction)
   ↓
Infrastructure layer
└─ SQLiteTransactionRepository.add():
   • Maps domain entity → database row
   • Executes INSERT INTO transactions ...
   • Returns success
   ↑
Application layer
└─ Returns the created Transaction back to CLI
   ↑
CLI
└─ Prints: "Added income: $1500.00 - Monthly salary"
```

---

## 6. Key Design Decisions

- **Repository Pattern** — abstracts data access behind an interface, allowing multiple backends without changing application code
- **DTOs (Pydantic models)** — validate input data at the boundary between CLI and Application layers
- **Dependency Inversion** — high-level modules (services) depend on abstractions (`TransactionRepository` ABC), not on concrete implementations
- **Type Safety** — full type hints across the codebase, verified by Pyright in CI