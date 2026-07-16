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
        self.init_procurement_tab()
        self.refresh_categories()
        self.refresh_products_list()
        self.refresh_purchase_orders()

    def init_ui(self):
        # Base layout is top level vertical layout to host QTabWidget
        self.top_layout = QVBoxLayout(self)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        
        # Tab widget for catalog vs procurement
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setStyleSheet("font-size: 13px;")
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
        self.products_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
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
        self.lbl_selected_meta.setStyleSheet("color: #64748b; font-size: 12px;")
        self.detail_layout.addWidget(self.lbl_selected_meta)

        self.right_layout.addWidget(self.detail_card)

        # Stock Adjustment Form
        self.adjust_card = QGroupBox("Stock Adjustment", self.right_panel)
        self.adjust_card.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.adjust_layout = QFormLayout(self.adjust_card)
        self.adjust_layout.setContentsMargins(15, 20, 15, 15)
        self.adjust_layout.setSpacing(10)

        self.adjust_spin = QDoubleSpinBox(self.adjust_card)
        self.adjust_spin.setRange(-9999.0, 9999.0)
        self.adjust_spin.setValue(0.0)
        self.adjust_layout.addRow("Adjustment Qty (+/-):", self.adjust_spin)

        self.adjust_reason = QLineEdit(self.adjust_card)
        self.adjust_reason.setPlaceholderText("Reason (e.g. damage, restock)")
        self.adjust_layout.addRow("Reason:", self.adjust_reason)

        self.btn_adjust = QPushButton("Apply Adjustment", self.adjust_card)
        self.btn_adjust.setStyleSheet("background-color: #f59e0b; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_adjust.clicked.connect(self.on_adjust_stock_clicked)
        self.adjust_layout.addRow(self.btn_adjust)

        self.right_layout.addWidget(self.adjust_card)

        # Low Stock Alerts Panel
        self.alert_box = QGroupBox("Low Stock Alerts", self.right_panel)
        self.alert_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.alert_layout = QVBoxLayout(self.alert_box)
        self.alert_layout.setContentsMargins(15, 20, 15, 15)
        self.alert_layout.setSpacing(10)

        self.alerts_list = QLabel("No low stock items", self.alert_box)
        self.alerts_list.setStyleSheet("font-weight: normal; color: #1e293b;")
        self.alert_layout.addWidget(self.alerts_list)

        self.right_layout.addWidget(self.alert_box, stretch=1)
        
        self.main_layout.addWidget(self.right_panel, stretch=2)
        
        # Add Catalog tab
        self.tab_widget.addTab(self.catalog_tab, "Product Catalog Catalog")
        
        # ================= TAB 2: PROCUREMENT MANAGEMENT =================
        self.procurement_tab = QWidget(self)
        self.tab_widget.addTab(self.procurement_tab, "Procurement & Purchase Orders")

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
        self.po_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.po_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
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
        self.po_items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
        self.btn_receive_po.setStyleSheet("background-color: #22c55e; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_receive_po.setEnabled(False)
        self.btn_receive_po.clicked.connect(self.on_receive_po_clicked)
        self.po_actions_layout.addWidget(self.btn_receive_po, stretch=1)
        
        self.po_right_layout.addLayout(self.po_actions_layout)
        self.proc_layout.addWidget(self.po_right, stretch=2)

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
            
        # Update low stock alert panel
        low_stock_items = [p for p in filtered_products if p.stock_qty <= p.reorder_level]
        if low_stock_items:
            alert_text = "\n".join([f"• {p.name} ({p.stock_qty} {p.unit})" for p in low_stock_items[:5]])
            if len(low_stock_items) > 5:
                alert_text += f"\n... and {len(low_stock_items) - 5} more"
            self.alerts_list.setText(alert_text)
            self.alerts_list.setStyleSheet("font-weight: normal; color: #ef4444;")
        else:
            self.alerts_list.setText("No low stock items")
            self.alerts_list.setStyleSheet("font-weight: normal; color: #1e293b;")

    def on_filter_changed(self):
        """Handle search text or category filter changes."""
        self.refresh_products_list()

    def on_product_row_clicked(self, row, column):
        """Handle product selection from table."""
        if row < len(self.products_list_cache):
            prod = self.products_list_cache[row]
            self.selected_product_id = prod.id
            self.lbl_selected_title.setText(prod.name)
            self.lbl_selected_meta.setText(f"SKU: {prod.sku}\nBarcode: {prod.barcode or 'N/A'}\nCurrent Stock: {prod.stock_qty} {prod.unit}")

    def on_adjust_stock_clicked(self):
        """Process stock adjustment for selected product."""
        if not self.selected_product_id:
            QMessageBox.warning(self, "No Selection", "Please select a product from the catalog first.")
            return
            
        adjustment = self.adjust_spin.value()
        reason = self.adjust_reason.text().strip()
        
        if adjustment == 0:
            QMessageBox.warning(self, "Invalid Adjustment", "Adjustment quantity cannot be zero.")
            return
            
        if not reason:
            QMessageBox.warning(self, "Missing Reason", "Please provide a reason for this adjustment.")
            return
            
        try:
            self.inventory_service.adjust_stock(
                product_id=self.selected_product_id,
                quantity_change=adjustment,
                reason=reason
            )
            QMessageBox.information(self, "Success", "Stock adjustment recorded successfully!")
            self.refresh_products_list()
            self.adjust_spin.setValue(0.0)
            self.adjust_reason.clear()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to adjust stock: {str(e)}")

    def on_add_product_clicked(self):
        """Launch product creation dialog."""
        categories = self.product_repo.list_categories()
        if not categories:
            QMessageBox.warning(self, "No Categories", "Please create categories first before adding products.")
            return
            
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

    def refresh_purchase_orders(self):
        """Load wholesale purchase orders from SQLite."""
        try:
            self.po_table.setRowCount(0)
            orders = self.inventory_service.get_purchase_orders()
            self.po_list_cache = orders
            
            self.po_table.setRowCount(len(orders))
            
            suppliers = {s.id: s.name for s in self.inventory_service.get_all_suppliers()}
            
            for index, po in enumerate(orders):
                self.po_table.setItem(index, 0, QTableWidgetItem(str(po.id)))
                self.po_table.setItem(index, 1, QTableWidgetItem(suppliers.get(po.supplier_id, "Unknown")))
                self.po_table.setItem(index, 2, QTableWidgetItem(po.order_date.strftime("%Y-%m-%d")))
                self.po_table.setItem(index, 3, QTableWidgetItem(po.status))
                self.po_table.setItem(index, 4, QTableWidgetItem(str(len(po.items))))
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load purchase orders: {str(e)}")

    def on_po_row_clicked(self, row, column):
        """Handle PO selection."""
        if row < len(self.po_list_cache):
            po = self.po_list_cache[row]
            self.selected_po_id = po.id
            self.lbl_po_meta.setText(f"PO #{po.id} • {po.status} • {po.order_date.strftime('%Y-%m-%d')}")
            self.btn_cancel_po.setEnabled(po.status == "Pending")
            self.btn_receive_po.setEnabled(po.status == "Pending")
            
            # Load PO items
            self.po_items_table.setRowCount(len(po.items))
            for idx, item in enumerate(po.items):
                self.po_items_table.setItem(idx, 0, QTableWidgetItem(item.product_name))
                self.po_items_table.setItem(idx, 1, QTableWidgetItem(str(item.quantity)))
                self.po_items_table.setItem(idx, 2, QTableWidgetItem(f"${item.unit_cost:.2f}"))

    def on_create_po_clicked(self):
        """Launch PO creation dialog."""
        QMessageBox.information(self, "Feature", "Purchase Order creation dialog to be implemented.")

    def on_cancel_po_clicked(self):
        """Cancel/void selected PO."""
        if not self.selected_po_id:
            return
        res = QMessageBox.question(self, "Confirm Cancel", "Are you sure you want to void this purchase order?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            try:
                self.inventory_service.cancel_purchase_order(self.selected_po_id)
                QMessageBox.information(self, "Success", "Purchase order cancelled successfully.")
                self.refresh_purchase_orders()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to cancel PO: {str(e)}")

    def on_receive_po_clicked(self):
        """Receive stock from selected PO."""
        if not self.selected_po_id:
            return
        try:
            self.inventory_service.receive_purchase_order(self.selected_po_id)
            QMessageBox.information(self, "Success", "Stock received and inventory updated successfully.")
            self.refresh_purchase_orders()
            self.refresh_products_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to receive stock: {str(e)}")


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
