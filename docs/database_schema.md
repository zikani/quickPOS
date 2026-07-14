# Database Schema Blueprint

QuickPOS uses an embedded, transactional, offline-first **SQLite** database managed with the powerful **SQLAlchemy Object-Relational Mapper (ORM)**. This document provides the complete schema definitions, data types, foreign keys, constraints, and relationships of the database tables.

---

## 1. Schema Diagram Overview

The following relationship map shows how tables are connected through foreign key references:

```text
    ┌───────────────┐
    │  categories   │◀──────┐ (Parent/Child relation)
    └───────┬───────┘       │
            │               │
            ▼ 1             │
    ┌───────────────┐ 1     │
    │   products    │◀──────┘
    └───────┬───────┘
            │ 1
            ├───────────────────────┐
            │                       │
            ▼ N                     ▼ N
    ┌───────────────┐       ┌───────────────────────┐
    │  sale_items   │       │ purchase_order_items  │
    └───────┬───────┘       └───────────┬───────────┘
            │ N                         │ N
            ▼ 1                         ▼ 1
    ┌───────────────┐       ┌───────────────────────┐
    │     sales     │       │    purchase_orders    │
    └───────┬───────┘       └───────────┬───────────┘
            │                           │
            │ 1                         │ 1
            ▼ N                         ▼ N
    ┌───────────────┐       ┌───────────────────────┐
    │   payments    │       │       suppliers       │
    └───────────────┘       └───────────────────────┘
```

---

## 2. Table Specifications

### 2.1 Table: `users`
Stores user credentials, access levels, and active status indicators.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Unique user record identifier |
| `username` | String(50) | Unique, Indexed, Not Null | Unique username for terminal access |
| `password_hash` | String(255) | Not Null | Securely hashed password credential |
| `role` | String(20) | Not Null | User authority role: `Admin`, `Manager`, `Cashier` |
| `full_name` | String(100) | Not Null | Full display name of the user |
| `is_active` | Boolean | Default: True | Access active indicator |
| `created_at` | DateTime | Default: UTC Now | Account creation timestamp |

---

### 2.2 Table: `categories`
Organizes products into nested hierarchies.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Category identifier |
| `name` | String(100) | Not Null | Display name of category |
| `parent_id` | Integer | Foreign Key (`categories.id`), Nullable | Reference to parent category (for sub-categories) |

---

### 2.3 Table: `products`
The inventory items available for checkout sales or supplier purchase orders.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Product identifier |
| `sku` | String(50) | Unique, Indexed, Not Null | Stock Keeping Unit code |
| `barcode` | String(50) | Unique, Indexed, Nullable | Barcode scan identifier |
| `name` | String(150) | Not Null | Display name of the product |
| `category_id` | Integer | Foreign Key (`categories.id`), Nullable | Organizes product into category |
| `cost_price` | Decimal(10,2) | Not Null, >= 0 | Cost to buy product |
| `sell_price` | Decimal(10,2) | Not Null, >= 0 | Sale retail price to consumer |
| `tax_rate` | Decimal(5,2) | Default: 0.00 | Tax percentage applied to sales (e.g. 15.00) |
| `stock_qty` | Decimal(10,2) | Default: 0.00 | Current quantity in inventory stock |
| `reorder_level`| Decimal(10,2) | Default: 5.00 | Threshold for low-stock alerts |
| `unit` | String(20) | Default: 'pcs' | Measurement unit (pcs, kg, pack, liters) |
| `image_path` | String(255) | Nullable | File path reference to product icon/photo |

---

### 2.4 Table: `customers`
Tracks client contact detail information, transaction histories, and balance sheets.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Customer identifier |
| `name` | String(100) | Not Null | Customer's full name |
| `phone` | String(30) | Nullable, Indexed | Direct phone number |
| `email` | String(100) | Nullable | Contact email address |
| `loyalty_points`| Integer | Default: 0 | Earned customer loyalty metrics |
| `balance` | Decimal(10,2) | Default: 0.00 | Credit or account balance outstanding |

---

### 2.5 Table: `suppliers`
Wholesale supplier directory records for inventory restock orders.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Supplier identifier |
| `name` | String(100) | Not Null | Wholesaler/Supplier business name |
| `contact` | String(100) | Nullable | Contact representative name |
| `email` | String(100) | Nullable | Business communication email |
| `address` | String(255) | Nullable | Physical warehouse shipping address |

---

### 2.6 Table: `sales`
The central checkout transaction record header.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Unique transaction identifier |
| `invoice_no` | String(50) | Unique, Indexed, Not Null | Standardized invoice receipt number |
| `customer_id` | Integer | Foreign Key (`customers.id`), Nullable | Reference to buyer CRM record |
| `cashier_id` | Integer | Foreign Key (`users.id`), Not Null | Reference to cashier checkout login |
| `subtotal` | Decimal(10,2) | Not Null | Sum price before taxes and discounts |
| `tax_total` | Decimal(10,2) | Not Null | Combined calculated taxes of all line items |
| `discount_total`| Decimal(10,2)| Not Null | Cumulative cart-level discounts applied |
| `grand_total` | Decimal(10,2) | Not Null | Total customer payment amount |
| `status` | String(20) | Not Null | Transaction status: `COMPLETED`, `VOIDED`, `REFUNDED` |
| `created_at` | DateTime | Default: UTC Now | Transaction date-time timestamp |

---

### 2.7 Table: `sale_items`
Detailed checkout line items for completed transactions.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Record identifier |
| `sale_id` | Integer | Foreign Key (`sales.id`), Not Null | Parent sales transaction record |
| `product_id` | Integer | Foreign Key (`products.id`), Not Null | Transacted catalog item |
| `qty` | Decimal(10,2) | Not Null, > 0 | Sold quantity |
| `unit_price` | Decimal(10,2) | Not Null | Unit retail price at time of sale |
| `discount` | Decimal(10,2) | Default: 0.00 | Unit discount deduction |
| `tax` | Decimal(10,2) | Default: 0.00 | Calculated tax total for this line item |
| `line_total` | Decimal(10,2) | Not Null | Final net line total after discount and taxes |

---

### 2.8 Table: `payments`
Tracks individual financial payouts mapping to specific transactions.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Payment transaction ID |
| `sale_id` | Integer | Foreign Key (`sales.id`), Not Null | Associated sales invoice |
| `method` | String(30) | Not Null | Method: `CASH`, `CARD`, `MOBILE_MONEY`, `SPLIT` |
| `amount` | Decimal(10,2) | Not Null | Amount paid |
| `reference` | String(100) | Nullable | Receipt confirmation code or slip reference |

---

### 2.9 Table: `inventory_logs`
Chronological movement trail tracking stock quantity adjustments.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Log identifier |
| `product_id` | Integer | Foreign Key (`products.id`), Not Null | Associated catalog product |
| `change_qty` | Decimal(10,2) | Not Null | Quantity adjusted (+ for stock-in, - for sales/wastage) |
| `reason` | String(100) | Not Null | Reason: `SALE`, `STOCK_IN`, `WASTAGE`, `ADJUSTMENT` |
| `user_id` | Integer | Foreign Key (`users.id`), Not Null | Manager/Cashier logging the action |
| `created_at` | DateTime | Default: UTC Now | Adjustment event timestamp |

---

### 2.10 Table: `purchase_orders`
Tracks restock orders submitted to wholesalers.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Restock transaction identifier |
| `supplier_id` | Integer | Foreign Key (`suppliers.id`), Not Null | Supplier catalog contact reference |
| `status` | String(20) | Not Null | Order Status: `DRAFT`, `ORDERED`, `RECEIVED`, `CANCELLED` |
| `created_at` | DateTime | Default: UTC Now | Purchase order timestamp |

---

### 2.11 Table: `purchase_order_items`
Contains the individual quantities and wholesale prices of ordered items.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Item line identifier |
| `po_id` | Integer | Foreign Key (`purchase_orders.id`), Not Null| Associated purchase order |
| `product_id` | Integer | Foreign Key (`products.id`), Not Null | Product being restocked |
| `qty` | Decimal(10,2) | Not Null | Quantity ordered from wholesaler |
| `unit_cost` | Decimal(10,2) | Not Null | Unit cost quoted by wholesaler |

---

### 2.12 Table: `audit_logs`
System-wide security ledger tracking actions performed by authenticated users.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Audit record identifier |
| `user_id` | Integer | Foreign Key (`users.id`), Not Null | Associated user login account |
| `action` | String(100) | Not Null | Action logged (e.g. `LOGIN`, `VOID_SALE`, `DELETE_ITEM`) |
| `entity` | String(50) | Not Null | Targeted table name (e.g. `sales`, `products`) |
| `entity_id` | Integer | Nullable | ID of targeted record |
| `timestamp` | DateTime | Default: UTC Now | Immutable event logging date-time |

---

### 2.13 Table: `settings`
Key-Value application properties and store metadata.

| Field | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `key` | String(100) | Primary Key | Parameter key (e.g., `store_name`, `tax_id`) |
| `value` | Text | Nullable | Configured parameter value |
