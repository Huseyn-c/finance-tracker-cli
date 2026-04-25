# Finance Tracker CLI

> A command-line personal finance tracker built with Clean Architecture principles.

[![CI Pipeline](https://github.com/Huseyn-c/finance-tracker-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/Huseyn-c/finance-tracker-cli/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)](https://github.com/Huseyn-c/finance-tracker-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Track your income and expenses directly from the terminal. Organize transactions by category, filter by date or type, and persist data via SQLite or SQLAlchemy.

---

## ✨ Features

- 💰 **Transaction management** — add, list, and remove income/expense entries
- 🏷️ **Category system** — organize transactions with custom categories
- 🔍 **Smart filtering** — filter transactions by date range, type, or category
- 💾 **Dual persistence** — choose between SQLite (raw) or SQLAlchemy (ORM) backend
- 📋 **Structured logging** — all operations logged to `logs/finance_tracker.log`
- ✅ **91% test coverage** — robust pytest suite with CI/CD pipeline
- 🏗️ **Clean Architecture** — strict separation of concerns across 4 layers

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Huseyn-c/finance-tracker-cli.git
cd finance-tracker-cli

# Install dependencies
uv sync
```

### Usage

```bash
# Add an income transaction
uv run finance add 1500 "Monthly salary" --type income --category salary

# Add an expense
uv run finance add 50 "Coffee with friends" --type expense --category food

# List all transactions
uv run finance list

# Filter transactions
uv run finance list --type expense --category food
uv run finance list --after 2025-01-01 --before 2025-12-31

# Remove a transaction by ID
uv run finance remove TRANSACTION_ID

# Manage categories
uv run finance list-categories
uv run finance remove-category food
```

### Switching Backend

By default the app uses raw SQLite. To use SQLAlchemy ORM instead:

```bash
export FINANCE_TRACKER_BACKEND=sqlalchemy
uv run finance add 100 "Test" --type income
```

---

## 🏗️ Architecture

The project follows **Clean Architecture** with strict dependency rules — outer layers depend on inner layers, never the reverse.

```
┌──────────────┐   User input / output
│ Presentation │   (CLI using Typer)
└──────┬───────┘
       │ calls
┌──────▼───────┐   Use case coordination
│ Application  │   (TransactionService, DTOs)
└──────┬───────┘
       │ uses
┌──────▼───────┐   Pure business rules
│   Domain     │   (Transaction, TransactionType)
└──────┬───────┘
       │ implements ports
┌──────▼───────┐   External details
│Infrastructure│   (SQLite + SQLAlchemy repositories)
└──────────────┘
```

📖 **Full architecture documentation:** [`docs/howto_architecture.md`](docs/howto_architecture.md)

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.12 |
| **CLI Framework** | Typer |
| **Validation** | Pydantic |
| **Database** | SQLite, SQLAlchemy ORM |
| **Testing** | pytest, pytest-cov |
| **Code Quality** | Ruff (linter), Pyright (type checker) |
| **Package Management** | uv |
| **CI/CD** | GitHub Actions |

---

## 🧪 Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run linter
uv run ruff check .

# Run type checker
uv run pyright src
```

---

## 📂 Project Structure

```
finance-tracker-cli/
├── src/finance_tracker/
│   ├── cli/                  # Presentation layer (Typer commands)
│   ├── application/          # Application layer (services, DTOs)
│   ├── domain/               # Domain layer (entities, business rules)
│   └── infrastructure/       # Infrastructure (SQLite, SQLAlchemy)
├── tests/                    # Test suite (16 tests, 91% coverage)
├── docs/                     # Architecture documentation
├── .github/workflows/        # CI/CD pipeline
└── pyproject.toml            # Project configuration
```

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Huseyn Huseynov**
B.Sc. Software Engineering and Design @ Constructor University, Bremen
- GitHub: [@Huseyn-c](https://github.com/Huseyn-c)