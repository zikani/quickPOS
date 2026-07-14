# QuickPOS Terminal

QuickPOS is a professional, standalone, production-grade **Point-of-Sale (POS) desktop application** engineered in Python utilizing the powerful **PyQt6** GUI framework. Featuring a robust modular backend, offline-first SQLite database layer with SQLAlchemy ORM, and comprehensive services, it is built to handle the rigorous daily workflows of retail businesses securely and efficiently.

---

## 🎨 System Highlights

- **Desktop First**: Engineered from the ground up for native desktop performance on Windows, macOS, and Linux.
- **Offline-First Persistence**: Powered by SQLite with robust ACID transactions and rollback capabilities, ensuring zero data loss on crashes.
- **Enterprise Architecture**: Designed with a layered Model-View-Service-Repository architecture separating UI widgets from databases.
- **Modular Design**: Features dedicated services for authentication, checkout sales, product/inventory control, supplier transactions, and analytics reporting.

---

## 🚀 Key Functional Modules

### 1. Authentication & Security
- Secure login screen with password hashing.
- Role-Based Access Control (RBAC) with preconfigured roles: **Admin**, **Manager**, and **Cashier**.
- Session-state isolation to prevent cross-account leakage.

### 2. POS Checkout Terminal
- Instant product searches by title, SKU, or barcode scans.
- Dynamic cart rendering including tax estimation and discounts.
- Flexible payments supporting Cash, Cards, and Split Payments.
- Cash change helper calculations and automated stock decrements upon checkout completion.
- Global keyboard-wedge barcode listener to instantly add products to the checkout basket.

### 3. Inventory & Category Management
- Multi-tier classification system with automated low-stock warnings.
- Precise tracking with historical logs for every manual adjustment or sales transaction.

### 4. Supplier & Purchasing CRM
- Complete supplier directories and order management.
- Dynamic purchase orders that update inventories automatically upon goods receipt.

### 5. Analytics & Multi-Format Reporting
- Periodic cash drawer reconciliation, sales summaries, and performance metrics.
- PDF receipt/invoice fallback generation.

---

## 🏗️ Layered Project Directory Structure

```text
pos_app/
├── main.py                      # Application bootstrap & entry point
├── pyproject.toml               # Poetry dependencies (or requirements.txt)
├── README.md                    # Main project documentation
├── build_executable.spec        # PyInstaller specification for single-file binaries
│
├── config/
│   └── settings.py              # Central application configuration & environment management
│
├── core/
│   ├── session.py               # Singleton state for the active user session
│   └── exceptions.py            # custom app-wide exception classes
│
├── database/
│   ├── base.py                  # SQLAlchemy engine, session factory, and Declarative Base
│   ├── init_db.py               # Database bootstrapping and seed script
│   └── backup.py                # Database backup & restore utility functions
│
├── models/                      # SQLAlchemy ORM Data Models
│   ├── user.py                  # Users, credentials, and access roles
│   ├── product.py               # Core products catalog
│   ├── category.py              # Dynamic item categorizations
│   ├── customer.py              # Customer relations and loyalty indicators
│   ├── supplier.py              # Wholesalers and supplier contacts
│   ├── sale.py                  # Sales headers (invoice_no, tax, totals)
│   ├── sale_item.py             # Sale item line details (unit price, quantities, discounts)
│   ├── payment.py               # Record of financial payments
│   └── audit_log.py             # System-wide immutable operations audit trail
│
├── repositories/                # Data-Access Layer (Encapsulated SQL queries)
│   ├── user_repository.py
│   ├── product_repository.py
│   ├── sale_repository.py
│   └── customer_repository.py
│
├── services/                    # Business Logic Layer (Processes and Workflows)
│   ├── auth_service.py          # Hashing verification & login validation
│   ├── sales_service.py         # Transaction rollbacks and checkout workflows
│   ├── inventory_service.py     # Stock decrements and movement logging
│   └── customer_service.py      # Customer lookups and CRM updates
│
├── ui/                          # GUI Presentation Layer (PyQt6 views)
│   ├── main_window.py           # Native QMainWindow sidebar template shell
│   └── mock_pyqt.py             # Fallback shim for headless development containers
│
├── utils/
│   └── security.py              # Multi-platform password hashing helpers
│
└── tests/                       # Complete verification suite
    └── unit/
        ├── test_inventory_service.py
        └── test_sales_service.py
```

---

## 🛠️ Local Development Setup

Follow these straightforward steps to run, develop, and test the QuickPOS application on your machine.

### Prerequisites
- Python 3.11 or higher
- `pip` or Python virtual environment package (`venv`)

### 1. Clone & Set Up Virtual Environment

```bash
# Clone the repository and navigate into the root directory
cd quickpos

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (cmd):
venv\Scripts\activate.bat
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

Install the required PyQt6, SQLAlchemy, and utility packages:

```bash
pip install -r requirements.txt
```

*(Alternatively, if your environment uses standard setup, install core packages: `pip install PyQt6 SQLAlchemy bcrypt`)*

### 3. Run the Desktop Application

Execute the central bootstrap script to initialize the SQLite database, seed mock products, and launch the GUI window:

```bash
python pos_app/main.py
```

---

## 🧪 Running the Verification Suite

We use **pytest** to verify application logic. Run the test suite to ensure the business services perform flawlessly:

```bash
# Install test requirements
pip install pytest pytest-qt

# Execute all test assertions
pytest pos_app/tests/
```

---

## 📦 Packaging Standalone Executables

QuickPOS includes a PyInstaller `.spec` configuration file to bundle the entire Python runtime, Qt libraries, and database layers into a standalone, double-clickable application executable.

```bash
# Install PyInstaller
pip install pyinstaller

# Build a performance-optimized single-file executable for your OS
pyinstaller pos_app/build_executable.spec
```

The compiled binaries will be outputted directly to the `/dist/` folder on successful completion.

---

## 📚 Supplementary Documentation

To explore specific areas of the system, consult the following comprehensive resources in the `/docs` folder:

- **[System Architecture Guide](./docs/architecture.md)**: Layered MVC breakdowns, thread models, and signal configurations.
- **[Database Schema Blueprint](./docs/database_schema.md)**: Tables, attributes, indices, and database relations diagrams.
- **[POS User Manual](./docs/user_manual.md)**: Operations guidebook for Admins, Managers, and Cashier terminals.
