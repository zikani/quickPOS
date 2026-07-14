# QuickPOS User Manual

Welcome to the **QuickPOS Terminal** user manual. This guide provides instructions for operators, cashiers, and managers to handle checkout transactions, update inventory, and manage terminal settings.

---

## 1. Getting Started & User Authentication

Upon launching the application, you will see the primary **Access Terminal** login form. QuickPOS uses role-based access controls to secure sensitive terminal configurations and management actions.

### Logging In
1. Input your designated username into the username field.
2. Enter your secure password credential.
3. Click **Access Terminal** or press the `Enter` key.

### Default Accounts for Training/Evaluation:
* **Admin Role**: Username: `admin` | Password: `admin123` *(Has complete access)*
* **Cashier Role**: Username: `cashier` | Password: `cashier123` *(Restricted checkout operator views)*

---

## 2. Main POS Screen: Checkout & Checkout Sales

The **Checkout Screen** is the central workspace of the application. It is designed to be highly responsive and optimized for both keyboard entry and touch screen environments.

### 2.1 Navigating the Checkout Screen
* **Searching Products**: Enter terms into the **Product Search Bar** to instantly filter matching items.
* **Adding to Cart**: Double-click an item in the search results or press `Enter` to add it to the active shopping cart.
* **Modifying Quantities**: Adjust item counts or remove items directly within the active basket view.
* **Attaching Customers**: Search and select customers from the CRM dropdown to link transactions to buyer profiles.

---

## 3. Barcode Scanner Support (Keyboard Wedge)

QuickPOS has native, automatic support for hardware **USB Barcode Scanners** operating as "keyboard wedges." This allows you to scan any item's barcode from anywhere in the checkout interface, even if the search input is not active.

### How to Scan:
1. Ensure you are logged into your user session.
2. Position the scanner over the product barcode and press the trigger button.
3. The global listener automatically detects the barcode stream, locates the matching item, switches your view to the checkout workspace, adds the product to the basket, and triggers a success sound/visual alert.

---

## 4. Finalizing Transactions & Touch Numpad

When checking out, click **Pay** or press the pay shortcut to open the **Secure Payment Dialogue**.

### Using the Payment Interface:
1. **Choose Payment Mode**: Select payment methods including Cash, Card, Mobile Money, or Split options.
2. **Input Tender (Cash)**:
   - For keyboard entry, click inside the cash tender field and type the received amount.
   - For touch screens, use the **Touch Numpad** layout to enter amounts, use backspace (`⌫`), or clear (`C`) values.
   - Use the convenient **+5 Quick Add** button to quickly adjust received amounts.
3. **Change Calculation**: The system automatically calculates and displays the change amount to return to the customer.
4. **Complete Checkout**: Click **Authorize Payment** to save the sale, decrement stock counts, and print or save the purchase receipt as a PDF.

---

## 5. Inventory & Catalog Manager

Authorized users (Admin and Managers) can access the **Inventory Manager** via the sidebar navigation to track, restock, and manage stock catalogs.

- **Low-Stock Warnings**: Products falling below their threshold values automatically trigger visual highlights to warn operators.
- **Stock Movement Logs**: The system records an immutable audit trail for every stock change, noting whether it was due to a checkout sale, restocking, manual adjustment, or wastage.

---

## 6. Customers CRM

The **Customer CRM** tab allows you to manage customer contact lists, transaction summaries, and customer history.

- **Creating Customers**: Register customers by entering their full name, phone number, and email.
- **Loyalty Tracking**: Review earned loyalty metrics based on completed transactions.

---

## 7. System Maintenance & Database Backups

Access **System Settings** in the sidebar (Admin and Managers only) to perform system maintenance tasks:

* **Instant SQLite Backup**: Click **Create Database Backup** to generate a copy of the database. Backups are named with timestamps and stored securely.
* **Database Restoring**: Choose an earlier backup to restore previous configurations and transaction logs.
* **Store Metadata Configuration**: Customize the store's name, address, tax ID, and default tax rates for print receipt templates.
