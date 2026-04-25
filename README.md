# Finance Tracker CLI

A command-line personal finance tracker that lets users log income and expenses with category organization.

## Stage 1: Architecture Design

### 1. Use Case Cards

#### Add Transaction
**Actor:** CLI User  
**Inputs:** amount, description, type (income/expense), categories, date (default today)  
**Happy Path:**
1. Validate amount > 0
2. Create `Transaction` entity
3. Persist via `TransactionRepository.add()`
4. Return "Transaction added successfully"
**Failure:** invalid amount → "Amount must be positive"

#### List Transactions
**Actor:** CLI User  
**Inputs:** --after, --before, --category, --type filters  
**Happy Path:**
1. Parse filter parameters
2. Retrieve transactions via `TransactionRepository.list()`
3. Format and display results
**Failure:** invalid date → "Invalid date format"

#### Remove Transaction
**Actor:** CLI User  
**Inputs:** transaction_id  
**Happy Path:**
1. Find transaction by ID
2. Remove via `TransactionRepository.remove()`
3. Return "Transaction removed"
**Failure:** not found → "Transaction not found"

#### Add Category
**Actor:** CLI User  
**Inputs:** name, description  
**Happy Path:**
1. Validate name uniqueness
2. Create `Category` entity
3. Persist via `CategoryRepository.add()`
4. Return "Category created"
**Failure:** duplicate name → "Category already exists"

#### List Categories
**Actor:** CLI User  
**Inputs:** none  
**Happy Path:**
1. Retrieve all via `CategoryRepository.list_all()`
2. Display category list
**Failure:** none

#### Remove Category
**Actor:** CLI User  
**Inputs:** category_id  
**Happy Path:**
1. Find category by ID
2. Remove via `CategoryRepository.remove()`
3. Return "Category removed"
**Failure:** not found → "Category not found"

### 2. Domain Model

+----------------+
|   Transaction  |
|----------------|
|id: UUID        |
|amount: float	 | # > 0
|type: TxType	 | # income/expense
|description: str|
|date: datetime  |
|created_at: dt  |
+----------------+
    ^ *
    | belongs-to
+----------------+
|    Category    |
|----------------|
|id: UUID        |
|name: str	     |
|description: str|
+----------------+


**Invariants:** `amount > 0`, `type in {income, expense}`, `categories ≥ 0`

### 3. Layered Architecture
┌──────────────┐ User input / output
│ Presentation │ (CLI using Typer)
└──────┬───────┘
│ calls
┌──────▼───────┐ Orchestrates use cases
│ Application │ (TransactionService, CategoryService)
└──────┬───────┘
│ uses
┌──────▼───────┐ Pure business rules & entities
│ Domain │ (Transaction, Category)
└──────┬───────┘
│ implements ports
┌──────▼───────┐ External details
│Infrastructure│ (SQLite repositories)
└──────────────┘

**Dependency rule:** arrows only point inward.

**Responsibilities:**
- **Presentation:** CLI argument parsing, output formatting
- **Application:** Use case coordination, service logic
- **Domain:** Business entities and validation rules
- **Infrastructure:** SQLite database operations

### 4. Ports / Interfaces

```python
class TransactionRepository(Protocol):
    def add(self, tx: Transaction) -> None: ...
    def get(self, tx_id: UUID) -> Transaction | None: ...
    def list(self, *, after: date | None = None, 
             before: date | None = None,
             category: str | None = None,
             type: str | None = None) -> list[Transaction]: ...
    def remove(self, tx_id: UUID) -> bool: ...

class CategoryRepository(Protocol):
    def add(self, category: Category) -> None: ...
    def get(self, cat_id: UUID) -> Category | None: ...
    def get_by_name(self, name: str) -> Category | None: ...
    def list_all(self) -> list[Category]: ...
    def remove(self, cat_id: UUID) -> bool: ...

### 5. End-to-end feature flow

```
CLI (Presentation layer)
└─ command `add()` collects from user:
      amount=1500.00, type=income, categories=['salary'], description='Monthly salary'
   ↓
Application layer
└─ `TransactionService.add_transaction()`
      • validates amount > 0
      • builds Domain entity: Transaction(...)
      • enforces business rules
      • calls `TransactionRepository.add(transaction)`
        ↓
Infrastructure layer
└─ `SQLiteTransactionRepository.add()`
      • maps entity → database model
      • INSERT INTO transactions ...
      • returns success
   ↑
Application layer
└─ constructs success response
   ↑
CLI
└─ prints "Transaction added successfully"
```
# Updated: Sat Nov 15 00:23:56 CET 2025
 
