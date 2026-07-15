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
  - `InventoryService`: Stock movement logs, inventory adjustments, and warning checks.
  - `CustomerService`: Customer profile creation and history logs.
  - `ReportService`: Periodical financial totals and performance summaries.
  - `BackupService`: Live SQLite database backup copies and restructures.
  - `ReceiptService`: Direct local file receipt outputs.
- **Role-Based Access Control (RBAC):**
  - Fully integrated session managers identifying `Admin`, `Manager`, and `Cashier` roles.
  - Preconfigured training credentials loaded into the seeded database.

### 🧪 Quality Assurance & CI/CD Portability (Complete)
- **Headless PyQt6 Compilation Shim (`ui/mock_pyqt.py`):**
  - Dynamically mocks all PyQt6 core, GUI, and widget classes in environments lacking an X11 server or native Qt graphics stack.
  - Enables flawless integration testing, code linting, and compilation inside remote developer containers and CI/CD automation pipelines.
- **Automated Tests:**
  - Automated unit tests covering core transactions, inventory decrements, and sales rollbacks (`pos_app/tests/`).

### 🖥️ Desktop UI Layout Structures (Complete)
- **Main Window Layout:**
  - Dynamic `QMainWindow` containing collapsible sidebar and a central workspace stack widget.
- **Dynamic Permission Menus:**
  - Filters sidebar navigation based on active roles (e.g. Cashier sees only POS and CRM tabs; Manager adds Inventory and Reports; Admin gains full System Settings access).
- **Profile Banners:**
  - Sidebar renders visual boxes identifying the logged-in user and their current privilege level.

---

## 2. Features Not Implemented / Stubbed in Python GUI

The following desktop frontend components are currently stubbed as placeholder views with standard PyQt labels inside the desktop application UI stack, pending high-fidelity graphical layout expansion:

- **High-Fidelity Tab Layouts:**
  - `pos_screen`: Missing interactive product lookup lists, dynamic cart grids, tax summary cards, and quick-add panels.
  - `inventory_screen`: Missing search/filter product tables, restock forms, and categorical sliders.
  - `customer_screen`: Missing customer profiles, input fields, and purchase histories.
  - `reports_screen`: Missing charts, export formats, and shift logs.
  - `settings_screen`: Missing backup/restore file-pickers and terminal key configuration.
- **Dialogs & Overlays:**
  - Payment details forms (split tender calculation, card reader handshakes).
  - Cashier shift reconciliation popups.
  - Product category management dialogs.
- **QSS Visual Themes:**
  - Dedicated External stylesheet files (`light_theme.qss` & `dark_theme.qss`) have not yet been written or loaded to style standard Qt Widgets.

---

## 3. Features to Add (Future Roadmap)

- **Cloud Synchronization & Database Migrations:**
  - Alembic migration scripts to upgrade database states.
  - Multi-warehouse support and automatic background synchronization to remote cloud PostgreSQL databases.
- **Direct ESC/POS Thermal Printer Support:**
  - Native driver handshakes using pyusb or serial ports to print physical 80mm thermal receipts directly.
- **Direct Barcode Camera Reader Integration:**
  - Interactive camera feed on the side panel using `pyzbar` to capture and translate product barcodes on machines without dedicated hardware scanner guns.
- **Automated DB Backup Scheduler:**
  - Background thread scheduler automatically performing zipped DB database backups to offline drives hourly.
