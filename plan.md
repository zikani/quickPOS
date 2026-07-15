# 🗺️ QuickPOS Development Plan

This document maps out the system's architecture, identifies the features currently implemented in the modular backend and native UI shells, and lists the items slated for future releases.

---

## 1. Features Implemented

### 📦 Backend, Core, and Database Layer (Complete)
- **Database Engine (SQLAlchemy ORM):**
  - Robust offline-first, transaction-safe SQLite database structure.
  - Comprehensive schemas supporting relationships (Categories, Products, Users, Customers, Suppliers, Sales, Sale Items, Payments, Inventory Logs, Purchase Orders, and Security Audit Logs).
- **Service-Oriented Business Logic:**
  - `AuthService`: Secure password hash validations and user session coordination.
  - `SalesService`: Multi-step database transaction operations with automated rollbacks on failure.
  - `InventoryService`: Stock movement logs, inventory adjustments, and warning checks. Also integrates robust APIs to draft wholesale Purchase Orders, void orders, and receive items.
  - `CustomerService`: Customer profile creation and history logs.
  - `ReportService`: Periodical financial totals and performance summaries, including daily sales over time and category-wise sales breakup statistics.
  - `BackupService`: Live SQLite database backup copies and restructures.
  - `ReceiptService`: Direct local file receipt outputs, and compiles raw ESC/POS binary templates.
- **Role-Based Access Control (RBAC):**
  - Fully integrated session managers identifying `Admin`, `Manager`, and `Cashier` roles.
  - Preconfigured training credentials loaded into the seeded database.

### 🔌 Hardware & Local Integrations (Complete)
- **Direct ESC/POS Thermal Printer Support:**
  - Native USB driver handshakes (Class 7 printers via endpoints) and serial print queues (`/dev/usb/lp0` fallbacks) compiling and sending raw ESC/POS binary templates directly.
- **Direct Camera Barcode Reader Integration:**
  - Interactive webcam reader dialog that spins up a real-time thread to capture, grayscalize, and decode physical barcodes instantly using OpenCV and `pyzbar`.
- **Automated DB Backup Scheduler Thread:**
  - High-reliability background daemon thread (`BackupScheduler`) executing hot SQLite snapshots hourly, with safe termination procedures on window close.

### 🖥️ High-Fidelity Desktop UI Views (Complete)
- **Checkout Terminal (`pos_screen`):**
  - High-fidelity visual split-pane design. Left side includes search bars, a camera scanner trigger, and interactive product grids. Right side includes a transaction cart table, tax calculations, and a payment processing panel.
- **Inventory & Procurement Manager (`inventory_screen`):**
  - Dual-tab workflow. Tab 1 handles the Product Catalog with search filters, automatic low-stock alerting widgets, and instant adjust dialogs. Tab 2 exposes a wholesale procurement archive where users can draft purchase orders using multi-line item builders and receive goods.
- **Customer CRM Profile Portal (`customer_screen`):**
  - Visual panel to create new profiles and review client list details with dynamic loyalty indicators.
- **Interactive Reports Dashboard (`reports_screen`):**
  - Dynamic analytical charts (Sales Over Time and Product Category Breakdowns) custom-drawn via headless PyQt painting engines, shift summaries, and physical exporter drivers producing standard PDF summaries (via ReportLab) and Excel spreadsheets (via OpenPyXL).
- **System Settings Configuration (`settings_screen`):**
  - Displays backup archive lists, lets users run manual DB backups or file restorations, and provides customizable tax settings.
- **Main Window Layout & RBAC:**
  - Collapsible elegant navigation menus with automatic tab-access filtering and real-time user-privilege headers.

### 🧪 Quality Assurance & CI/CD Portability (Complete)
- **Headless PyQt6 Compilation Shim (`ui/mock_pyqt.py`):**
  - Dynamically mocks all PyQt6 core, GUI, and widget classes in environments lacking an X11 server or native Qt graphics stack.
  - Enables flawless integration testing, code linting, and compilation inside remote developer containers and CI/CD automation pipelines.
- **Automated Tests:**
  - Automated unit tests covering core transactions, inventory decrements, and sales rollbacks (`pos_app/tests/`).

---

## 2. Features to Add (Future Roadmap)

- **Cloud Synchronization & Database Migrations:**
  - Alembic migration scripts to upgrade database states.
  - Multi-warehouse support and automatic background synchronization to remote cloud PostgreSQL databases.

