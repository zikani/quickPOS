# System Architecture Guide

This document outlines the software design patterns, structural layers, data flow patterns, and architectural principles implemented across the **QuickPOS Terminal** codebase.

---

## 1. Architectural Blueprint: Layered Design

QuickPOS implements a highly modular **Model-View-Service-Repository** design pattern. Direct communication between the GUI widgets and the database is strictly forbidden. Communication flows sequentially through the defined layers:

```text
┌──────────────────────────────────────────────┐
│             UI / VIEW LAYER                  │
│       (PyQt6 QMainWindow / QWidgets)         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼  Calls Business APIs
┌──────────────────────────────────────────────┐
│           BUSINESS SERVICE LAYER             │
│   (Services: Auth, Sales, Inventory, etc.)   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼  Invokes Data Access Methods
┌──────────────────────────────────────────────┐
│            REPOSITORY LAYER                  │
│   (Repositories: Users, Products, Sales)     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼  Queries Database ORMs
┌──────────────────────────────────────────────┐
│         DATABASE MODELS & ENGINE             │
│    (SQLAlchemy ORM / SQLite Persistence)     │
└──────────────────────────────────────────────┘
```

### Description of System Layers

1. **Presentation Layer (`pos_app/ui/`)**: Built entirely with **PyQt6**. It contains views, custom widgets, and main dashboard shells. Views never handle raw business logic or SQL; instead, they capture user events, pass request parameters to Services, and render the resulting state.
2. **Business Logic Layer (`pos_app/services/`)**: The core cognitive engine of the system. Services coordinate complex workflows, handle password hashes, compute tax rules, manage transaction scope (rollback or commit), and validate transaction parameters.
3. **Data Access Layer (`pos_app/repositories/`)**: Encapsulates raw SQLAlchemy queries and CRUD statements. By isolating table reads/writes to single repositories, the application supports smooth scaling and enables future migrations (e.g., from SQLite to PostgreSQL) without rewriting core logic.
4. **Database & ORM Layer (`pos_app/models/`, `pos_app/database/`)**: Comprises the declarative models describing database columns and foreign key relations. Configures SQLite settings, manages schema setup, and runs initial database seeds.

---

## 2. Dynamic Data Flows & Sequence

### Example flow: POS Checkout Transaction
1. **Barcode Scanned**: The global barcode event listener or a search bar triggers a search.
2. **Retrieve Product**: The Checkout View invokes `SalesService.add_item_to_cart(product_id)`.
3. **Fetch & Verify Stock**: `SalesService` requests stock limits from `InventoryRepository` through `ProductRepository` and verifies the current item is in stock.
4. **Finalize Cart Payment**: When checking out, `POSMainWindow` opens the payment dialogue, captures cash tender, and calls `SalesService.checkout(cart_items, customer_id, cashier_id, payment_details)`.
5. **Database Transaction Safeguard**:
   - `SalesService` starts a scoped database transaction.
   - It saves a `Sale` log record.
   - Saves multiple individual `SaleItem` records.
   - Decrements stock counts in the `Product` table.
   - Generates an `InventoryLog` tracking stock exit reason.
   - **Commit or Rollback**: If any individual save or DB query fails, the transaction is immediately rolled back completely via `session.rollback()`, ensuring inventory and transaction logs never become desynchronized. If all succeed, the transaction commits.
6. **Trigger UI Refresh**: The checkout service returns success; UI slots trigger basket clearing and display a dynamic success notification.

---

## 3. Signal-Slot & Event-Driven Communication

To avoid tight couplings where child widgets depend on other sibling components, QuickPOS leverages **PyQt6 Signals and Slots**:
- Sibling widgets do not share direct reference pointers.
- When an event occurs (e.g., a product is added to the cart, or a transaction succeeds), the source widget emits a custom PyQt6 signal (e.g., `cartUpdated = pyqtSignal()`).
- The parent window handles coordination, connecting signals to updates on other views.
- This creates clean, decoupled, and reusable user interface components.

---

## 4. Thread Safety & UI Responsiveness

PyQt6 runs on a single main UI thread. Blocking this thread with resource-intensive tasks (such as generating bulk reports, backing up files, or print handshakes) causes visual lag and application freezes. QuickPOS ensures a smooth experience by:

- **QThread and QThreadPool Workers**: All resource-intensive tasks run in background worker threads.
- **Background DB Sessions**: Worker threads instantiate their own thread-safe database sessions to avoid race conditions.
- **Signals for Thread Synchronization**: Workers pass results back to the main GUI thread using PyQt6 signals, safely driving visual updates.

---

## 5. Portability & Headless Execution Shims

In containerized, headless development servers, or continuous integration environments (CI/CD workflows), native Qt GUI environments are unavailable. To ensure compiling, linting, and unit testing remain fully operational:

- **`pos_app/ui/mock_pyqt.py`**: Intercepts PyQt imports when native Qt frameworks are missing.
- It provides elegant, standard-conforming class stubs for `QApplication`, `QMainWindow`, `QWidget`, and related system libraries.
- This permits robust backend testing of services, repositories, database persistence, and validations on remote servers, while guaranteeing cross-platform executable builds with PyInstaller.
