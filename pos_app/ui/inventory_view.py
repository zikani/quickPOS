from pos_app.ui.mock_pyqt import *
from pos_app.models.product import Product
from pos_app.models.category import Category

class InventoryView(QWidget):
    """Full inventory catalog screen allowing product creation, list filters, and manual adjustments."""
    def __init__(self, inventory_service, product_repo, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.product_repo = product_repo
        
        self.selected_product_id = None
        self.init_ui()
        self.refresh_categories()
        self.refresh_products_list()
        self.refresh_purchase_orders()

    def init_ui(self):
        # Base layout is top level vertical layout to host QTabWidget
        self.top_layout = QVBoxLayout(self)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        
        self.tab_widget = QTabWidget(self)
        self.top_layout.addWidget(self.tab_widget)
        
        # ================= TAB 1: PRODUCT CATALOG =================
        self.catalog_tab = QWidget(self)
        self.main_layout = QHBoxLayout(self.catalog_tab)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # ================= LEFT PANEL: Catalog List & Filter =================
        self.left_panel = QWidget(self.catalog_tab)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)

        # Top Controls Bar
        self.filter_box = QWidget(self.left_panel)
        self.filter_layout = QHBoxLayout(self.filter_box)
        self.filter_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_layout.setSpacing(10)

        self.search_input = QLineEdit(self.filter_box)
        self.search_input.setPlaceholderText("Filter by name, SKU or barcode...")
        self.search_input.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.search_input.textChanged.connect(self.on_filter_changed)
        self.filter_layout.addWidget(self.search_input, stretch=3)

        self.category_combo = QComboBox(self.filter_box)
        self.category_combo.setStyleSheet("padding: 5px;")
        self.category_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.filter_layout.addWidget(self.category_combo, stretch=2)

        self.btn_add_product = QPushButton("+ Add Product", self.filter_box)
        self.btn_add_product.setStyleSheet("background-color: #22c55e; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.btn_add_product.clicked.connect(self.on_add_product_clicked)
        self.filter_layout.addWidget(self.btn_add_product)

        self.left_layout.addWidget(self.filter_box)

        # Product Inventory Table List
        self.table_box = QGroupBox("Store Catalog Inventory", self.left_panel)
        self.table_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.table_layout = QVBoxLayout(self.table_box)
        self.table_layout.setContentsMargins(10, 15, 10, 10)

        self.products_table = QTableWidget(self.table_box)
        self.products_table.setStyleSheet("font-weight: normal;")
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["SKU", "Item Name", "Cost", "Sell Price", "Stock Qty", "Status"])
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.cellClicked.connect(self.on_product_row_clicked)
        self.table_layout.addWidget(self.products_table)

        self.left_layout.addWidget(self.table_box)
        self.main_layout.addWidget(self.left_panel, stretch=3)

        # ================= RIGHT PANEL: Adjustment Tools =================
        self.right_panel = QWidget(self.catalog_tab)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(15)

        # Selected Product Detail Header Card
        self.detail_card = QGroupBox("Active Product Adjustment", self.right_panel)
        self.detail_card.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.detail_layout = QVBoxLayout(self.detail_card)
        self.detail_layout.setContentsMargins(15, 20, 15, 15)
        self.detail_layout.setSpacing(10)

        self.lbl_selected_title = QLabel("Select an item to view details", self.detail_card)
        self.lbl_selected_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #475569;")
        self.detail_layout.addWidget(self.lbl_selected_title)

        self.lbl_selected_meta = QLabel("SKU: -\nBarcode: -", self.detail_card)
        self.lbl_selected_meta.setStyleSheet("font-weight: normal; color: #64748b; line-height: 1.4;")
        self.detail_layout.addWidget(self.lbl_selected_meta)

        self.right_layout.addWidget(self.detail_card)

        # Manual Adjustment Form Box
        self.adjust_box = QGroupBox("Stock Adjustment Logs", self.right_panel)
        self.adjust_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.adjust_form_layout = QFormLayout(self.adjust_box)
        self.adjust_form_layout.setContentsMargins(15, 20, 15, 15)
        self.adjust_form_layout.setSpacing(10)

        self.adjust_spin = QDoubleSpinBox(self.adjust_box)
        self.adjust_spin.setStyleSheet("font-weight: normal; padding: 4px;")
        self.adjust_spin.setRange(-99999.0, 99999.0)
        self.adjust_spin.setValue(0.0)
        self.adjust_form_layout.addRow("Change Qty:", self.adjust_spin)

        self.reason_combo = QComboBox(self.adjust_box)
        self.reason_combo.setStyleSheet("font-weight: normal; padding: 4px;")
        self.reason_combo.addItems([
            "Restock Goods",
            "Wastage / Damaged",
            "Stocktake Correction",
            "Theft Loss",
            "Customer Return"
        ])
        self.adjust_form_layout.addRow("Reason:", self.reason_combo)

        self.btn_submit_adjust = QPushButton("Apply Adjustment", self.adjust_box)
        self.btn_submit_adjust.setStyleSheet("background-color: #3b82f6; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_submit_adjust.setEnabled(False)
        self.btn_submit_adjust.clicked.connect(self.on_apply_adjust_clicked)
        self.adjust_form_layout.addRow(self.btn_submit_adjust)

        self.right_layout.addWidget(self.adjust_box)
        
        # Low Stock Watchlist widget
        self.alert_box = QGroupBox("Low Stock Warnings", self.right_panel)
        self.alert_box.setStyleSheet("font-weight: bold; color: #e11d48;")
        self.alert_layout = QVBoxLayout(self.alert_box)
        self.alert_layout.setContentsMargins(10, 15, 10, 10)

        self.alerts_list = QListWidget(self.alert_box)
        self.alerts_list.setStyleSheet("font-weight: normal; color: #1e293b;")
        self.alert_layout.addWidget(self.alerts_list)

        self.right_layout.addWidget(self.alert_box, stretch=1)
        
        self.main_layout.addWidget(self.right_panel, stretch=2)
        
        # Add Catalog tab
        self.tab_widget.addTab(self.catalog_tab, "Product Catalog Catalog")
        
        # ================= TAB 2: PROCUREMENT MANAGEMENT =================
        self.procurement_tab = QWidget(self)
        self.init_procurement_tab()
        self.tab_widget.addTab(self.procurement_tab, "Procurement & Purchase Orders")

    # ================= Functional Controllers & Data Loading =================

    def refresh_categories(self):
        """Populate categories dropdown list."""
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", None)
        
        categories = self.product_repo.list_categories()
        for cat in categories:
            self.category_combo.addItem(cat.name, cat.id)

    def refresh_products_list(self):
        """Query and populate main inventory list matching filters."""
        self.products_table.setRowCount(0)
        query = self.search_input.text().strip()
        products = self.product_repo.search_products(query)
        
        selected_category_id = self.category_combo.itemData(self.category_combo.currentIndex())
        
        filtered_products = []
        for p in products:
            if selected_category_id is not None and p.category_id != selected_category_id:
                continue
            filtered_products.append(p)
            
        self.products_list_cache = filtered_products
        self.products_table.setRowCount(len(filtered_products))
        
        # Load list details
        for index, prod in enumerate(filtered_products):
            self.products_table.setItem(index, 0, QTableWidgetItem(prod.sku))
            self.products_table.setItem(index, 1, QTableWidgetItem(prod.name))
            self.products_table.setItem(index, 2, QTableWidgetItem(f"${prod.cost_price:.2f}"))
            self.products_table.setItem(index, 3, QTableWidgetItem(f"${prod.sell_price:.2f}"))
            self.products_table.setItem(index, 4, QTableWidgetItem(f"{prod.stock_qty} {prod.unit}"))
            
            # Stock alert flags
            status_item = QTableWidgetItem()
            if prod.stock_qty <= prod.reorder_level:
                status_item.setText("Low Stock ⚠️")
                status_item.setTextAlignment(Qt.AlignCenter)
            else:
                status_item.setText("Healthy ✓")
                status_item.setTextAlignment(Qt.AlignCenter)
                
            self.products_table.setItem(index, 5, status_item)

        # Refresh the Alert list
        self.refresh_alerts_watchlist()

    def refresh_alerts_watchlist(self):
        """Generate automatic low-stock lists."""
        self.alerts_list.clear()
        low_stock_items = self.inventory_service.get_low_stock_products()
        
        for item in low_stock_items:
            self.alerts_list.addItem(f"{item.name} - Only {item.stock_qty} {item.unit} left!")

    def on_filter_changed(self, *args):
        self.refresh_products_list()

    def on_product_row_clicked(self, row, column):
        """Active item state selector."""
        if row < len(self.products_list_cache):
            prod = self.products_list_cache[row]
            self.selected_product_id = prod.id
            
            self.lbl_selected_title.setText(prod.name)
            self.lbl_selected_meta.setText(
                f"SKU: {prod.sku}\n"
                f"Barcode: {prod.barcode or 'N/A'}\n"
                f"Reorder Level: {prod.reorder_level} {prod.unit}\n"
                f"Current Stock: {prod.stock_qty} {prod.unit}"
            )
            
            self.btn_submit_adjust.setEnabled(True)
            self.adjust_spin.setValue(0.0)

    def on_apply_adjust_clicked(self):
        """Execute restock adjustment transaction logs."""
        if not self.selected_product_id:
            return
            
        change = self.adjust_spin.value()
        if change == 0.0:
            QMessageBox.warning(self, "Adjustment Info", "Change value cannot be zero.")
            return
            
        reason = self.reason_combo.currentText()
        success = self.inventory_service.adjust_stock(self.selected_product_id, change, reason)
        
        if success:
            QMessageBox.information(self, "Success", "Product stock counts updated successfully.")
            self.refresh_products_list()
            
            # Reset form focus
            self.adjust_spin.setValue(0.0)
            # Re-click active row to update details
            for index, p in enumerate(self.products_list_cache):
                if p.id == self.selected_product_id:
                    self.on_product_row_clicked(index, 0)
                    break
        else:
            QMessageBox.critical(self, "Adjustment Error", "Could not adjust stock in database.")

    def on_add_product_clicked(self):
        """Launch Product Catalog Dialog form."""
        categories = self.product_repo.list_categories()
        if not categories:
            # Seed Category fallback if empty
            cat = self.inventory_service.create_category("General Store Goods")
            categories = [cat]

        dialog = ProductFormDialog(categories, self)
        if dialog.exec() == QDialog.Accepted:
            sku, barcode, name, cat_id, cost, sell, stock, reorder, unit = dialog.get_product_data()
            try:
                self.inventory_service.create_product(
                    sku=sku,
                    barcode=barcode,
                    name=name,
                    category_id=cat_id,
                    cost_price=cost,
                    sell_price=sell,
                    stock_qty=stock,
                    reorder_level=reorder,
                    unit=unit
                )
                QMessageBox.information(self, "Success", "New product created and seeded in catalog!")
                self.refresh_products_list()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to save product: {str(e)}")


class ProductFormDialog(QDialog):
    """Product catalog creator and validation overlay form."""
    def __init__(self, categories: list, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.setWindowTitle("Create New Product")
        self.setMinimumSize(450, 400)
        
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.form_widget = QWidget(self)
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)

        # Fields
        self.sku_input = QLineEdit(self.form_widget)
        self.sku_input.setPlaceholderText("e.g. SKU-12948-AB")
        self.form_layout.addRow("SKU Code:", self.sku_input)

        self.barcode_input = QLineEdit(self.form_widget)
        self.barcode_input.setPlaceholderText("e.g. 501234567890")
        self.form_layout.addRow("Barcode / UPC:", self.barcode_input)

        self.name_input = QLineEdit(self.form_widget)
        self.name_input.setPlaceholderText("e.g. Diet Coca-Cola 330ml Can")
        self.form_layout.addRow("Item Name:", self.name_input)

        self.category_combo = QComboBox(self.form_widget)
        for cat in self.categories:
            self.category_combo.addItem(cat.name, cat.id)
        self.form_layout.addRow("Category Group:", self.category_combo)

        self.cost_spin = QDoubleSpinBox(self.form_widget)
        self.cost_spin.setRange(0.0, 99999.0)
        self.cost_spin.setValue(1.0)
        self.form_layout.addRow("Item Cost Price ($):", self.cost_spin)

        self.sell_spin = QDoubleSpinBox(self.form_widget)
        self.sell_spin.setRange(0.0, 99999.0)
        self.sell_spin.setValue(1.5)
        self.form_layout.addRow("Selling Price ($):", self.sell_spin)

        self.stock_spin = QDoubleSpinBox(self.form_widget)
        self.stock_spin.setRange(0.0, 99999.0)
        self.stock_spin.setValue(10.0)
        self.form_layout.addRow("Initial Stock:", self.stock_spin)

        self.reorder_spin = QDoubleSpinBox(self.form_widget)
        self.reorder_spin.setRange(0.0, 9999.0)
        self.reorder_spin.setValue(5.0)
        self.form_layout.addRow("Low-Stock Warning Trigger:", self.reorder_spin)

        self.unit_combo = QComboBox(self.form_widget)
        self.unit_combo.addItems(["pcs", "kg", "g", "litres", "box", "can", "pack"])
        self.form_layout.addRow("Unit Measurement:", self.unit_combo)

        self.layout.addWidget(self.form_widget)

        # Dialog Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet("background-color: #cbd5e1; color: #1e293b; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("Create and Seed", self)
        self.ok_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.btn_layout.addWidget(self.ok_btn)
        
        self.layout.addLayout(self.btn_layout)

    def on_ok_clicked(self):
        sku = self.sku_input.text().strip()
        name = self.name_input.text().strip()
        
        if not sku or not name:
            QMessageBox.warning(self, "Validation Error", "Product SKU and Name fields are required.")
            return
            
        self.accept()

    def get_product_data(self) -> tuple[str, str, str, int, float, float, float, float, str]:
        return (
            self.sku_input.text().strip(),
            self.barcode_input.text().strip() or None,
            self.name_input.text().strip(),
            self.category_combo.itemData(self.category_combo.currentIndex()),
            self.cost_spin.value(),
            self.sell_spin.value(),
            self.stock_spin.value(),
            self.reorder_spin.value(),
            self.unit_combo.currentText()
        )

    # ================= Procurement Tab Interface & Controller Implementations =================

    def init_procurement_tab(self):
        """Build the procurement dashboard interface for wholesale purchase orders."""
        self.proc_layout = QHBoxLayout(self.procurement_tab)
        self.proc_layout.setContentsMargins(15, 15, 15, 15)
        self.proc_layout.setSpacing(15)
        
        # LEFT PANEL: PO list table
        self.po_left = QWidget(self.procurement_tab)
        self.po_left_layout = QVBoxLayout(self.po_left)
        self.po_left_layout.setContentsMargins(0, 0, 0, 0)
        self.po_left_layout.setSpacing(10)
        
        # Top action toolbar
        self.po_toolbar = QHBoxLayout()
        self.btn_draft_po = QPushButton("+ New Purchase Order", self.po_left)
        self.btn_draft_po.setStyleSheet("background-color: #22c55e; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.btn_draft_po.clicked.connect(self.on_create_po_clicked)
        self.po_toolbar.addWidget(self.btn_draft_po)
        
        self.btn_refresh_po = QPushButton("Refresh Orders", self.po_left)
        self.btn_refresh_po.setStyleSheet("background-color: #3b82f6; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.btn_refresh_po.clicked.connect(self.refresh_purchase_orders)
        self.po_toolbar.addWidget(self.btn_refresh_po)
        self.po_toolbar.addStretch()
        self.po_left_layout.addLayout(self.po_toolbar)
        
        # POs Table
        self.po_box = QGroupBox("Wholesale Procurement Archive", self.po_left)
        self.po_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.po_table_layout = QVBoxLayout(self.po_box)
        self.po_table_layout.setContentsMargins(10, 15, 10, 10)
        
        self.po_table = QTableWidget(self.po_box)
        self.po_table.setStyleSheet("font-weight: normal;")
        self.po_table.setColumnCount(5)
        self.po_table.setHorizontalHeaderLabels(["PO ID", "Wholesale Supplier", "Order Date", "Status", "Items Count"])
        self.po_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.po_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.po_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.po_table.cellClicked.connect(self.on_po_row_clicked)
        self.po_table_layout.addWidget(self.po_table)
        
        self.po_left_layout.addWidget(self.po_box)
        self.proc_layout.addWidget(self.po_left, stretch=3)
        
        # RIGHT PANEL: Selected PO detail card and receive stock actions
        self.po_right = QGroupBox("Selected Purchase Order Details", self.procurement_tab)
        self.po_right.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.po_right_layout = QVBoxLayout(self.po_right)
        self.po_right_layout.setContentsMargins(15, 20, 15, 15)
        self.po_right_layout.setSpacing(12)
        
        self.lbl_po_meta = QLabel("Select an order from the list to manage and receipt stock.", self.po_right)
        self.lbl_po_meta.setStyleSheet("font-weight: normal; color: #475569; line-height: 1.4;")
        self.po_right_layout.addWidget(self.lbl_po_meta)
        
        # Selected PO Items list
        self.lbl_po_items_title = QLabel("Ordered Items:", self.po_right)
        self.lbl_po_items_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #334155; margin-top: 5px;")
        self.po_right_layout.addWidget(self.lbl_po_items_title)
        
        self.po_items_table = QTableWidget(self.po_right)
        self.po_items_table.setStyleSheet("font-weight: normal;")
        self.po_items_table.setColumnCount(3)
        self.po_items_table.setHorizontalHeaderLabels(["Product Item", "Qty", "Cost Price"])
        self.po_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.po_items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.po_right_layout.addWidget(self.po_items_table)
        
        # Action Buttons
        self.po_actions_layout = QHBoxLayout()
        self.po_actions_layout.setSpacing(10)
        
        self.btn_cancel_po = QPushButton("Cancel/Void PO", self.po_right)
        self.btn_cancel_po.setStyleSheet("background-color: #ef4444; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_cancel_po.setEnabled(False)
        self.btn_cancel_po.clicked.connect(self.on_cancel_po_clicked)
        self.po_actions_layout.addWidget(self.btn_cancel_po, stretch=1)
        
        self.btn_receive_po = QPushButton("Receive Stock", self.po_right)
        self.btn_receive_po.setStyleSheet("background-color: #16a34a; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_receive_po.setEnabled(False)
        self.btn_receive_po.clicked.connect(self.on_receive_po_clicked)
        self.po_actions_layout.addWidget(self.btn_receive_po, stretch=1)
        
        self.po_right_layout.addLayout(self.po_actions_layout)
        self.proc_layout.addWidget(self.po_right, stretch=2)
        
        self.selected_po_id = None
        self.po_list_cache = []

    def refresh_purchase_orders(self):
        """Load wholesale purchase orders from SQLite."""
        try:
            self.po_table.setRowCount(0)
            orders = self.inventory_service.get_purchase_orders()
            self.po_list_cache = orders
            
            self.po_table.setRowCount(len(orders))
            
            suppliers = {s.id: s.name for s in self.inventory_service.get_all_suppliers()}
            
            for index, po in enumerate(orders):
                supplier_name = suppliers.get(po.supplier_id, f"Supplier #{po.supplier_id}")
                items = self.inventory_service.get_purchase_order_items(po.id)
                total_items = sum(item.qty for item in items)
                
                self.po_table.setItem(index, 0, QTableWidgetItem(f"PO-{po.id}"))
                self.po_table.setItem(index, 1, QTableWidgetItem(supplier_name))
                self.po_table.setItem(index, 2, QTableWidgetItem(po.created_at.strftime("%Y-%m-%d %H:%M")))
                
                status_item = QTableWidgetItem(po.status)
                status_item.setTextAlignment(Qt.AlignCenter)
                self.po_table.setItem(index, 3, status_item)
                
                self.po_table.setItem(index, 4, QTableWidgetItem(f"{int(total_items)} units"))
        except Exception:
            pass

    def on_po_row_clicked(self, row, column):
        if row < len(self.po_list_cache):
            po = self.po_list_cache[row]
            self.selected_po_id = po.id
            
            suppliers = {s.id: s.name for s in self.inventory_service.get_all_suppliers()}
            supplier_name = suppliers.get(po.supplier_id, f"Supplier #{po.supplier_id}")
            
            self.lbl_po_meta.setText(
                f"<b>Order Reference:</b> PO-{po.id}<br/>"
                f"<b>Wholesale Supplier:</b> {supplier_name}<br/>"
                f"<b>Created on:</b> {po.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
                f"<b>Current Status:</b> {po.status}"
            )
            
            self.po_items_table.setRowCount(0)
            items = self.inventory_service.get_purchase_order_items(po.id)
            self.po_items_table.setRowCount(len(items))
            
            products = {p.id: p.name for p in self.product_repo.search_products("")}
            for index, item in enumerate(items):
                p_name = products.get(item.product_id, f"Product #{item.product_id}")
                self.po_items_table.setItem(index, 0, QTableWidgetItem(p_name))
                self.po_items_table.setItem(index, 1, QTableWidgetItem(f"{int(item.qty)}"))
                self.po_items_table.setItem(index, 2, QTableWidgetItem(f"${item.unit_cost:.2f}"))
                
            if po.status == "Pending":
                self.btn_receive_po.setEnabled(True)
                self.btn_cancel_po.setEnabled(True)
            else:
                self.btn_receive_po.setEnabled(False)
                self.btn_cancel_po.setEnabled(False)

    def on_create_po_clicked(self):
        dialog = DraftPurchaseOrderDialog(self.inventory_service, self.product_repo, self)
        if dialog.exec() == QDialog.Accepted:
            supplier_id, items_data = dialog.get_po_data()
            po = self.inventory_service.create_purchase_order(supplier_id, items_data)
            QMessageBox.information(self, "Purchase Order Created", f"New wholesale order PO-{po.id} submitted successfully in Pending status!")
            self.refresh_purchase_orders()

    def on_receive_po_clicked(self):
        if not self.selected_po_id:
            return
        res = QMessageBox.question(
            self,
            "Confirm Goods Received",
            f"Are you sure you want to receipt stock for PO-{self.selected_po_id}?\nThis will increment catalog stock and create inventory restock audit logs.",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            success = self.inventory_service.receive_purchase_order(self.selected_po_id)
            if success:
                QMessageBox.information(self, "Success", f"Stock from PO-{self.selected_po_id} successfully received and loaded into active store catalog!")
                self.refresh_purchase_orders()
                self.refresh_products_list() # Sync standard Product Catalog stock table
                self.on_po_row_clicked(self.po_table.currentRow(), 0)
            else:
                QMessageBox.critical(self, "Error", "An error occurred while updating inventory stock levels.")

    def on_cancel_po_clicked(self):
        if not self.selected_po_id:
            return
        res = QMessageBox.question(
            self,
            "Confirm Void",
            f"Are you absolutely sure you want to cancel and void PO-{self.selected_po_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            success = self.inventory_service.cancel_purchase_order(self.selected_po_id)
            if success:
                QMessageBox.information(self, "Cancelled", f"Purchase Order PO-{self.selected_po_id} voided successfully.")
                self.refresh_purchase_orders()
                self.on_po_row_clicked(self.po_table.currentRow(), 0)


class DraftPurchaseOrderDialog(QDialog):
    """Interactive wizard to draft purchase orders with dynamic wholesale item lines."""
    def __init__(self, inventory_service, product_repo, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.product_repo = product_repo
        self.setWindowTitle("Draft New Purchase Order")
        self.setMinimumSize(600, 450)
        
        self.init_ui()
        self.load_suppliers()
        self.add_blank_line() # start with 1 item line
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(12)
        
        # Form layout for Supplier selection
        self.form_box = QWidget(self)
        self.form_layout = QFormLayout(self.form_box)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        
        self.supplier_combo = QComboBox(self.form_box)
        self.supplier_combo.setStyleSheet("padding: 4px;")
        self.form_layout.addRow("Select Wholesale Supplier:", self.supplier_combo)
        self.layout.addWidget(self.form_box)
        
        # Items table
        self.table_box = QGroupBox("Purchase Order Items List", self)
        self.table_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.table_layout = QVBoxLayout(self.table_box)
        self.table_layout.setContentsMargins(10, 15, 10, 10)
        
        self.items_table = QTableWidget(self.table_box)
        self.items_table.setStyleSheet("font-weight: normal;")
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Product Item", "Qty Ordered", "Unit Cost ($)", "Action"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_layout.addWidget(self.items_table)
        
        # Toolbar
        self.tool_layout = QHBoxLayout()
        self.btn_add_line = QPushButton("+ Add Line Item", self.table_box)
        self.btn_add_line.setStyleSheet("background-color: #3b82f6; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.btn_add_line.clicked.connect(self.add_blank_line)
        self.tool_layout.addWidget(self.btn_add_line)
        self.tool_layout.addStretch()
        self.table_layout.addLayout(self.tool_layout)
        
        self.layout.addWidget(self.table_box)
        
        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet("background-color: #cbd5e1; color: #1e293b; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Submit Purchase Order", self)
        self.save_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.save_btn.clicked.connect(self.on_submit_clicked)
        self.btn_layout.addWidget(self.save_btn)
        
        self.layout.addLayout(self.btn_layout)
        
        self.products_cache = self.product_repo.search_products("")
        
    def load_suppliers(self):
        suppliers = self.inventory_service.get_all_suppliers()
        for sup in suppliers:
            self.supplier_combo.addItem(sup.name, sup.id)
            
    def add_blank_line(self):
        row_idx = self.items_table.rowCount()
        self.items_table.insertRow(row_idx)
        
        # Column 0: Product Combo
        prod_combo = QComboBox(self.items_table)
        prod_combo.setStyleSheet("font-weight: normal;")
        for p in self.products_cache:
            prod_combo.addItem(p.name, p.id)
        prod_combo.currentIndexChanged.connect(lambda idx, r=row_idx: self.on_product_selection_changed(r))
        self.items_table.setCellWidget(row_idx, 0, prod_combo)
        
        # Column 1: Qty Spin
        qty_spin = QSpinBox(self.items_table)
        qty_spin.setRange(1, 99999)
        qty_spin.setValue(10)
        qty_spin.setStyleSheet("font-weight: normal;")
        self.items_table.setCellWidget(row_idx, 1, qty_spin)
        
        # Column 2: Cost DoubleSpin
        cost_spin = QDoubleSpinBox(self.items_table)
        cost_spin.setRange(0.01, 99999.0)
        if self.products_cache:
            cost_spin.setValue(self.products_cache[0].cost_price)
        cost_spin.setStyleSheet("font-weight: normal;")
        self.items_table.setCellWidget(row_idx, 2, cost_spin)
        
        # Column 3: Remove Button
        remove_btn = QPushButton("Remove", self.items_table)
        remove_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; max-height: 22px; border-radius: 3px;")
        # Capture current row index cleanly using cell coordinate matching on trigger
        remove_btn.clicked.connect(lambda checked=False, btn=remove_btn: self.remove_line_by_widget(btn))
        self.items_table.setCellWidget(row_idx, 3, remove_btn)
        
    def on_product_selection_changed(self, row_idx):
        try:
            prod_combo = self.items_table.cellWidget(row_idx, 0)
            cost_spin = self.items_table.cellWidget(row_idx, 2)
            if prod_combo and cost_spin:
                p_id = prod_combo.itemData(prod_combo.currentIndex())
                for p in self.products_cache:
                    if p.id == p_id:
                        cost_spin.setValue(p.cost_price)
                        break
        except Exception:
            pass
            
    def remove_line_by_widget(self, widget):
        index = self.items_table.indexAt(widget.pos())
        if index.isValid():
            self.items_table.removeRow(index.row())
        
    def on_submit_clicked(self):
        if self.supplier_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation Error", "Please select a wholesale supplier.")
            return
            
        row_count = self.items_table.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "Validation Error", "Please add at least one line item to the purchase order.")
            return
            
        self.accept()
        
    def get_po_data(self) -> tuple[int, list[dict]]:
        supplier_id = self.supplier_combo.itemData(self.supplier_combo.currentIndex())
        items_data = []
        
        for idx in range(self.items_table.rowCount()):
            prod_combo = self.items_table.cellWidget(idx, 0)
            qty_spin = self.items_table.cellWidget(idx, 1)
            cost_spin = self.items_table.cellWidget(idx, 2)
            
            if prod_combo and qty_spin and cost_spin:
                p_id = prod_combo.itemData(prod_combo.currentIndex())
                qty = qty_spin.value()
                cost = cost_spin.value()
                items_data.append({
                    "product_id": p_id,
                    "qty": float(qty),
                    "unit_cost": cost
                })
                
        return supplier_id, items_data

