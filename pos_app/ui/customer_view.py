from pos_app.ui.mock_pyqt import *
from pos_app.models.customer import Customer
from pos_app.models.sale import Sale

class CustomerView(QWidget):
    """Customer Relationship Management (CRM) panel listing profiles, loyalty status, and history."""
    def __init__(self, customer_service, session_db, parent=None):
        super().__init__(parent)
        self.customer_service = customer_service
        self.session_db = session_db
        
        self.selected_customer_id = None
        self.init_ui()
        self.refresh_customer_list()

    def init_ui(self):
        # Horizontal Split: Left side search and list, Right side details & history
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # ================= LEFT SIDE: CRM List =================
        self.left_panel = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)

        # Filters Bar
        self.filter_box = QWidget(self.left_panel)
        self.filter_layout = QHBoxLayout(self.filter_box)
        self.filter_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_layout.setSpacing(10)

        self.search_input = QLineEdit(self.filter_box)
        self.search_input.setPlaceholderText("Search customers by name, phone or email...")
        self.search_input.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.search_input.textChanged.connect(self.refresh_customer_list)
        self.filter_layout.addWidget(self.search_input, stretch=3)

        self.btn_add_customer = QPushButton("+ Add Customer", self.filter_box)
        self.btn_add_customer.setStyleSheet("background-color: #22c55e; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.btn_add_customer.clicked.connect(self.on_add_customer_clicked)
        self.filter_layout.addWidget(self.btn_add_customer)

        self.left_layout.addWidget(self.filter_box)

        # Customer List Table
        self.list_box = QGroupBox("Loyalty Accounts Directory", self.left_panel)
        self.list_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.list_layout = QVBoxLayout(self.list_box)
        self.list_layout.setContentsMargins(10, 15, 10, 10)

        self.customers_table = QTableWidget(self.list_box)
        self.customers_table.setStyleSheet("font-weight: normal;")
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Phone Number", "Email Profile", "Loyalty Pts"])
        self.customers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.customers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.cellClicked.connect(self.on_customer_row_clicked)
        self.list_layout.addWidget(self.customers_table)

        self.left_layout.addWidget(self.list_box)
        self.main_layout.addWidget(self.left_panel, stretch=3)

        # ================= RIGHT SIDE: Customer Detail View =================
        self.right_panel = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(15)

        # Customer Meta Summary Card
        self.meta_card = QGroupBox("Active Profile Summary", self.right_panel)
        self.meta_card.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.meta_layout = QVBoxLayout(self.meta_card)
        self.meta_layout.setContentsMargins(15, 20, 15, 15)
        self.meta_layout.setSpacing(10)

        self.lbl_selected_name = QLabel("Select a customer profile to view metrics", self.meta_card)
        self.lbl_selected_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #475569;")
        self.meta_layout.addWidget(self.lbl_selected_name)

        self.lbl_selected_stats = QLabel("Phone: -\nEmail: -\nTotal Loyalty: -\nBalance: $0.00", self.meta_card)
        self.lbl_selected_stats.setStyleSheet("font-weight: normal; color: #64748b; line-height: 1.4;")
        self.meta_layout.addWidget(self.lbl_selected_stats)

        self.right_layout.addWidget(self.meta_card)

        # Purchase Transactions History Grid
        self.history_box = QGroupBox("Invoice Purchase History", self.right_panel)
        self.history_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.history_layout = QVBoxLayout(self.history_box)
        self.history_layout.setContentsMargins(10, 15, 10, 10)

        self.history_table = QTableWidget(self.history_box)
        self.history_table.setStyleSheet("font-weight: normal;")
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Invoice No", "Date", "Grand Total"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_layout.addWidget(self.history_table)

        self.right_layout.addWidget(self.history_box, stretch=1)
        self.main_layout.addWidget(self.right_panel, stretch=2)

    # ================= Functional Controllers =================

    def refresh_customer_list(self, *args):
        """Query CRM database and populate directory."""
        self.customers_table.setRowCount(0)
        query = self.search_input.text().strip()
        customers = self.customer_service.search_customers(query)
        self.customers_list_cache = customers
        
        self.customers_table.setRowCount(len(customers))
        for index, cust in enumerate(customers):
            self.customers_table.setItem(index, 0, QTableWidgetItem(cust.name))
            self.customers_table.setItem(index, 1, QTableWidgetItem(cust.phone or "N/A"))
            self.customers_table.setItem(index, 2, QTableWidgetItem(cust.email or "N/A"))
            self.customers_table.setItem(index, 3, QTableWidgetItem(f"{cust.loyalty_points} pts"))

    def on_customer_row_clicked(self, row, column):
        """Display customer card and transaction summaries."""
        if row < len(self.customers_list_cache):
            cust = self.customers_list_cache[row]
            self.selected_customer_id = cust.id
            
            self.lbl_selected_name.setText(cust.name)
            self.lbl_selected_stats.setText(
                f"Phone: {cust.phone or 'N/A'}\n"
                f"Email: {cust.email or 'N/A'}\n"
                f"Total Loyalty: {cust.loyalty_points} points\n"
                f"Account Balance: ${cust.balance:.2f}"
            )
            
            # Query Purchase History from DB
            self.refresh_purchase_history(cust.id)

    def refresh_purchase_history(self, customer_id: int):
        self.history_table.setRowCount(0)
        sales = self.session_db.query(Sale).filter(Sale.customer_id == customer_id).order_by(Sale.created_at.desc()).all()
        
        self.history_table.setRowCount(len(sales))
        for index, sale in enumerate(sales):
            self.history_table.setItem(index, 0, QTableWidgetItem(sale.invoice_no))
            
            # Format Date
            date_str = sale.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(sale.created_at, "strftime") else str(sale.created_at)
            self.history_table.setItem(index, 1, QTableWidgetItem(date_str))
            
            self.history_table.setItem(index, 2, QTableWidgetItem(f"${sale.grand_total:.2f}"))

    def on_add_customer_clicked(self):
        """Launch Customer registration overlay form."""
        dialog = CustomerFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name, phone, email = dialog.get_customer_data()
            try:
                self.customer_service.create_customer(name=name, phone=phone, email=email)
                QMessageBox.information(self, "Success", "Customer profile registered in directory!")
                self.refresh_customer_list()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to save customer: {str(e)}")


class CustomerFormDialog(QDialog):
    """Clean pop-up card to add customers with basic input checks."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Loyalty Customer")
        self.setMinimumSize(400, 250)
        
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.form_widget = QWidget(self)
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)

        self.name_input = QLineEdit(self.form_widget)
        self.name_input.setPlaceholderText("e.g. Jane Doe")
        self.form_layout.addRow("Full Name:", self.name_input)

        self.phone_input = QLineEdit(self.form_widget)
        self.phone_input.setPlaceholderText("e.g. +1 (555) 019-2834")
        self.form_layout.addRow("Phone Number:", self.phone_input)

        self.email_input = QLineEdit(self.form_widget)
        self.email_input.setPlaceholderText("e.g. jane.doe@example.com")
        self.form_layout.addRow("Email Address:", self.email_input)

        self.layout.addWidget(self.form_widget)

        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet("background-color: #cbd5e1; color: #1e293b; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("Register Customer", self)
        self.ok_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.btn_layout.addWidget(self.ok_btn)
        
        self.layout.addLayout(self.btn_layout)

    def on_ok_clicked(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Customer name is a required field.")
            return
        self.accept()

    def get_customer_data(self) -> tuple[str, str, str]:
        return (
            self.name_input.text().strip(),
            self.phone_input.text().strip() or None,
            self.email_input.text().strip() or None
        )
