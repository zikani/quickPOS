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

    def init_ui(self):
        # Base horizontal layout: Left side list, Right side manual restock tools
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # ================= LEFT PANEL: Catalog List & Filter =================
        self.left_panel = QWidget(self)
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
        self.right_panel = QWidget(self)
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
