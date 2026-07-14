# 💻 QuickPOS Terminal
> **Production-grade, standalone PyQt6 Point-of-Sale (POS) desktop application engineered for high-throughput retail operations.**

[![Language](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/UI-PyQt6-darkgreen?logo=qt&logoColor=white)](https://www.qt.io/)
[![Database ORM](https://img.shields.io/badge/ORM-SQLAlchemy-red?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Offline Engine](https://img.shields.io/badge/Offline--First-SQLite-blueviolet?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Packager](https://img.shields.io/badge/Bundled_with-PyInstaller-yellow)](https://pyinstaller.org/)

---

## 🎨 System Highlights & Architectural Pillars

*   **Desktop-First Architecture:** Crafted specifically for native performance on Windows, macOS, and Linux client machines.
*   **Offline-First & Fault-Tolerant:** Leverages an embedded, enterprise-configured SQLite layer backed by transaction-safe rollbacks to guarantee data integrity.
*   **Decoupled Design:** Implements a strict, layered **Model-View-Service-Repository** pattern that isolates database queries from UI layouts.
*   **Role-Based Views:** Dynamic navigation sidebar adapts menus based on authenticated roles.

---

## 🔑 Access Terminal & Role Permissions Matrix

The login form authorizes operators and immediately restructures the UI layouts based on the account's authority:

| Feature Tab | Cashier Operator | Store Manager | System Admin |
| :--- | :---: | :---: | :---: |
| **Checkout terminal** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Customer CRM** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Inventory Catalog** | ❌ Blocked | ✅ Yes | ✅ Yes |
| **Sales Reporting** | ❌ Blocked | ✅ Yes | ✅ Yes |
| **System Settings / Backups** | ❌ Blocked | ❌ Blocked | ✅ Yes |

### 🛠️ Default Training Accounts:
*   **Admin Role:** Username: `admin` | Password: `admin123` *(Full System Access)*
*   **Manager Role:** Username: `manager` | Password: `manager123` *(Sales/Inventory Access)*
*   **Cashier Role:** Username: `cashier` | Password: `cashier123` *(Checkout Terminal Access)*

---

## 🏗️ Layered Project Structure

```text
pos_app/
├── main.py                      # Application bootstrap & entry point
├── pyproject.toml               # Poetry dependencies (or requirements.txt)
├── README.md                    # Central documentation shell
├── build_executable.spec        # PyInstaller packaging configuration
│
├── config/
│   └── settings.py              # Central settings and system metadata
│
├── core/
│   ├── session.py               # Singleton state for user sessions
│   └── exceptions.py            # Custom POS exception types
│
├── database/
│   ├── base.py                  # Scoped sessions and engine setup
│   ├── init_db.py               # Database bootstrapping & seed data
│   └── backup.py                # Database backup & restore utilities
│
├── models/                      # SQLAlchemy Declarative Models
│   ├── user.py                  # User profiles and roles
│   ├── product.py               # Product metadata & inventory counts
│   ├── category.py              # Item categories
│   ├── customer.py              # CRM customer records & loyalty points
│   ├── supplier.py              # Supplier details
│   ├── sale.py                  # Sales transaction logs
│   ├── sale_item.py             # Sale item line details
│   ├── payment.py               # Transaction payments
│   └── audit_log.py             # Security audit logs
│
├── repositories/                # Encapsulated SQL Queries (Data-Access Layer)
│   ├── user_repository.py
│   ├── product_repository.py
│   ├── sale_repository.py
│   └── customer_repository.py
│
├── services/                    # Core Business Logic Layer
│   ├── auth_service.py          # Hashing & sign-in coordination
│   ├── sales_service.py         # Transaction commits & cart operations
│   ├── inventory_service.py     # Stock logs & level warning checks
│   └── customer_service.py      # Customer profile management
│
├── ui/                          # Presentation Layer (PyQt6 views)
│   ├── main_window.py           # Central shell sidebar layout
│   └── mock_pyqt.py             # Dev-container headless mockup shim
│
└── tests/                       # Automated Test Suites
    └── unit/
        ├── test_inventory_service.py
        └── test_sales_service.py
```

---

## 🛠️ Local Development Setup

Set up, run, and compile the native application on your local workstation in five minutes:

### Prerequisites
*   Python 3.11 or higher
*   Python `venv` virtual environment package

### 1. Initialize and Activate Virtual Environment
```bash
# Clone the repository and navigate to root directory
cd quickpos

# Create a virtual environment
python -m venv venv

# Activate the virtual environment:
# On macOS / Linux:
source venv/bin/activate
# On Windows (CMD):
venv\Scripts\activate.bat
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 2. Install Project Dependencies
```bash
pip install PyQt6 SQLAlchemy bcrypt
```

### 3. Run the Native POS Desktop Application
```bash
python pos_app/main.py
```

---

## 🧪 Running Automated Unit Tests
Verify all core services and checkout logic locally using `pytest`:

```bash
# Install testing tools
pip install pytest pytest-qt

# Execute testing assertions
pytest pos_app/tests/
```

---

## 📦 Bundling Standalone Binaries
Use `PyInstaller` to compile the Python source, Qt GUI assets, and SQLite engine into a single executable binary:

```bash
# Install bundle tools
pip install pyinstaller

# Build target binary
pyinstaller pos_app/build_executable.spec
```
The optimized single-file binary will be generated inside the `/dist/` output directory.

---

## 📚 Deep Dive Technical Guides

For comprehensive technical breakdowns, review the following files inside the `/docs` directory:
*   📄 **[System Architecture Guide](./docs/architecture.md):** In-depth analysis of the Service-Repository pattern, thread management, and signal interfaces.
*   📄 **[Database Schema Blueprint](./docs/database_schema.md):** Structured index tables, relational foreign keys, column specifications, and diagram mappings.
*   📄 **[POS Operator Manual](./docs/user_manual.md):** User instructions detailing checkout processes, touch-screen keypad usage, and stock alert workflows.
