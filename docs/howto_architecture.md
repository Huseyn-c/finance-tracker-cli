## From Feature List to Architecture

**Important:** This guide is a recommendation, not a requirement. You can modify the steps as you want. The main goal is to get a clear picture of the system which you'll implement.

---

### 1. Write **Use‑Case Cards**

For every CLI command or user action, capture only the essentials.

| Field                | What to write                               |
| -------------------- | ------------------------------------------- |
| **Name**             | Short verb phrase (e.g. *Add Transaction*)  |
| **Actor**            | Who triggers it (CLI user, scheduler)       |
| **Inputs**           | Parameters or prompts                       |
| **Happy‑path steps** | 3–7 numbered steps                          |
| **Outputs**          | What comes back (e.g. confirmation message) |
| **Failure cases**    | Validations, error messages                 |

> **Example Card**
> **Name:** Add Transaction
> **Actor:** CLI User
> **Inputs:** amount, date (default today), type (income/expense), categories, note
> **Happy Path:**
>
> 1. Validate amount > 0
> 2. Create `Transaction` entity
> 3. Persist via `TransactionRepository.add()`
> 4. Return “Transaction #27 added”
>    **Failure:** invalid amount → “Amount must be positive”.

Create one card per command—nothing more.

That's a simplified version of user scenario. You can read more on the topic [here](https://www.interaction-design.org/literature/topics/user-scenarios) (side note: I'm sure there are better resources; though, it's your responsibility to find them).

---

### 2. **Sketch the Domain Model**

Draw a quick box‑and‑arrow diagram (whiteboard or ASCII).

```
+----------------+
|  Transaction   |
|----------------|
| id: int        |
| amount: float  |
| date: date     |
| type: TxType   |
| note: str?     |
+----------------+
        ^ *
        | belongs‑to
+----------------+
|   Category     |
|----------------|
| id: int        |
| name: str      |
| limit: float?  |
+----------------+
```

Write invariants beside the boxes: `amount > 0`, `categories ≥ 1`.

Note: You can structure the DB differently

Resource: I found this [tutorial](https://youtu.be/FLtqAi7WNBY) helpful.

---

### 3. **Layered Architecture** (Recommended)

We pick a classic 4‑layer stack to keep things simple and testable.

```
┌──────────────┐  User input / output
│ Presentation │  (CLI using Typer)
└──────┬───────┘
       │ calls
┌──────▼───────┐  Orchestrates use cases
│ Application  │  (Services, DTOs)
└──────┬───────┘
       │ uses
┌──────▼───────┐  Pure business rules & entities
│   Domain     │
└──────┬───────┘
       │ implements ports
┌──────▼───────┐  External details (DB, API)
│Infrastructure│  (SQLite adapter, logging)
└──────────────┘
```

**Dependency rule:** arrows *only* point inward—outer layers import inner layers, never the reverse.

**Responsibilities**

* **Presentation:** parse CLI args, format output. No business logic.
* **Application:** coordinate a use case; depends on Domain and Ports.
* **Domain:** entities, value objects, rules. Zero I/O.
* **Infrastructure:** concrete adapters (SQLite, file system). Implements Port interfaces defined above.

---

### 4. Define **Ports / Interfaces**

Create abstractions the Domain/Application layers rely on. Keep them tiny.

```python
class TransactionRepository(Protocol):
    def add(self, tx: Transaction) -> None: ...
    def by_id(self, tx_id: int) -> Transaction | None: ...
    def list(self, *, after: date | None = None, before: date | None = None) -> list[Transaction]: ...
```

Concrete implementations live in *Infrastructure* (e.g. `SqliteTransactionRepository`). Switch databases by wiring a different adapter—no domain code changes.

---

### 5. End-to-end feature flow

```
CLI (Presentation layer)
└─ command `add()` collects from user:
      amount=120.00, type=expense, categories=['groceries'], note='weekly'
   ↓
Application layer
└─ `AddTransactionService.handle(AddTxCmdDTO)`
      • validates DTO
      • builds Domain entity: Transaction(...)
      • enforces invariant amount>0 (Domain call)
      • calls `TransactionRepo.add(transaction)`
        ↓
Infrastructure layer
└─ `SQLiteTransactionRepo.add()`
      • maps entity → ORM model
      • INSERT INTO transactions ... (SQL)
      • returns generated ID = 42
   ↑
Application layer
└─ constructs `AddTxResultDTO(id=42)`
   ↑
CLI
└─ prints “✅ Transaction #42 added.”
```

