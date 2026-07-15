from pos_app.ui.mock_pyqt import *
from pos_app.core.session import session
from pos_app.models.product import Product
from pos_app.models.customer import Customer
import datetime

class POSView(QWidget):
    """Interactive POS Checkout terminal screen with search, cart, totals, and payment processing."""
    def __init__(self, sales_service, product_repo, customer_service, parent=None):
        super().__init__(parent)
        self.sales_service = sales_service
        self.product_repo = product_repo
        self.customer_service = customer_service
        
        # State variables
        self.cart_items = [] # list of dict: {'product_id': int, 'name': str, 'price': float, 'qty': int, 'tax_rate': float}
        self.parked_carts = [] # list of parked cart_items
        self.selected_customer_id = None
        
        self.init_ui()
        self.refresh_products()
        self.refresh_customers()

    def init_ui(self):
        # Base horizontal layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # ================= LEFT SIDE: Products & Quick Add =================
        self.left_panel = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)

        # Search Bar Group
        self.search_box = QGroupBox("Product Lookup", self.left_panel)
        self.search_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.search_layout = QHBoxLayout(self.search_box)
        self.search_layout.setContentsMargins(10, 15, 10, 10)
        
        self.search_input = QLineEdit(self.search_box)
        self.search_input.setPlaceholderText("Scan barcode or type name/SKU...")
        self.search_input.setStyleSheet("font-weight: normal; padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.search_input.returnPressed.connect(self.on_search_triggered)
        self.search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Search", self.search_box)
        self.search_btn.setStyleSheet("background-color: #3b82f6; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.search_btn.clicked.connect(self.on_search_triggered)
        self.search_layout.addWidget(self.search_btn)

        self.camera_scan_btn = QPushButton("📷 Scan with Camera", self.search_box)
        self.camera_scan_btn.setStyleSheet("background-color: #ec4899; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px;")
        self.camera_scan_btn.clicked.connect(self.on_camera_scan_clicked)
        self.search_layout.addWidget(self.camera_scan_btn)
        
        self.left_layout.addWidget(self.search_box)

        # Products Table Results
        self.results_box = QGroupBox("Available Catalog", self.left_panel)
        self.results_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.results_layout = QVBoxLayout(self.results_box)
        self.results_layout.setContentsMargins(10, 15, 10, 10)

        self.products_table = QTableWidget(self.results_box)
        self.products_table.setStyleSheet("font-weight: normal;")
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Name", "SKU", "Price", "Action"])
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.cellDoubleClicked.connect(self.on_product_double_clicked)
        self.results_layout.addWidget(self.products_table)
        
        self.left_layout.addWidget(self.results_box)

        # Quick Add Grid panel
        self.quick_add_box = QGroupBox("Quick Action Items", self.left_panel)
        self.quick_add_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.quick_layout = QGridLayout(self.quick_add_box)
        self.quick_layout.setContentsMargins(10, 15, 10, 10)
        self.quick_layout.setSpacing(10)

        # Populate a few standard items for instantaneous touch addition
        quick_items = [
            ("Fresh Banana", "SKU-BANANA"),
            ("Organic Milk", "SKU-MILK"),
            ("Whole Wheat Bread", "SKU-BREAD"),
            ("Mineral Water", "SKU-WATER")
        ]
        
        for index, (name, sku) in enumerate(quick_items):
            row = index // 2
            col = index % 2
            btn = QPushButton(name, self.quick_add_box)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5f9;
                    color: #1e293b;
                    font-weight: 500;
                    padding: 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            # Connect using closure
            btn.clicked.connect(lambda checked=False, s=sku: self.add_by_sku(s))
            self.quick_layout.addWidget(btn, row, col)

        self.left_layout.addWidget(self.quick_add_box)
        self.main_layout.addWidget(self.left_panel, stretch=3)

        # ================= RIGHT SIDE: Cart, Customer & Checkouts =================
        self.right_panel = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(10)

        # Customer & Loyalty Lookup
        self.cust_box = QGroupBox("Attach Customer Account", self.right_panel)
        self.cust_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.cust_layout = QHBoxLayout(self.cust_box)
        self.cust_layout.setContentsMargins(10, 15, 10, 10)

        self.customer_combo = QComboBox(self.cust_box)
        self.customer_combo.setStyleSheet("font-weight: normal; padding: 4px;")
        self.customer_combo.currentIndexChanged.connect(self.on_customer_selected)
        self.cust_layout.addWidget(self.customer_combo, stretch=3)
        
        self.right_layout.addWidget(self.cust_box)

        # Active Cart Grid Table
        self.cart_box = QGroupBox("Shopping Cart", self.right_panel)
        self.cart_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.cart_layout = QVBoxLayout(self.cart_box)
        self.cart_layout.setContentsMargins(10, 15, 10, 10)

        self.cart_table = QTableWidget(self.cart_box)
        self.cart_table.setStyleSheet("font-weight: normal;")
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_layout.addWidget(self.cart_table)
        
        self.right_layout.addWidget(self.cart_box, stretch=2)

        # Totals Summary Card
        self.totals_card = QFrame(self.right_panel)
        self.totals_card.setFrameShape(QFrame.StyledPanel)
        self.totals_card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 8px;
                color: white;
                padding: 12px;
            }
        """)
        self.totals_layout = QVBoxLayout(self.totals_card)
        
        self.lbl_subtotal = QLabel("Subtotal: $0.00", self.totals_card)
        self.lbl_subtotal.setStyleSheet("font-size: 14px; font-weight: 500;")
        self.totals_layout.addWidget(self.lbl_subtotal)
        
        self.lbl_tax = QLabel("Tax (Included): $0.00", self.totals_card)
        self.lbl_tax.setStyleSheet("font-size: 13px; color: #94a3b8;")
        self.totals_layout.addWidget(self.lbl_tax)
        
        self.lbl_total = QLabel("Total: $0.00", self.totals_card)
        self.lbl_total.setStyleSheet("font-size: 22px; font-weight: bold; color: #3b82f6; margin-top: 5px;")
        self.totals_layout.addWidget(self.lbl_total)

        self.right_layout.addWidget(self.totals_card)

        # Bottom Actions Bar
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)

        self.btn_park = QPushButton("Hold Sale", self.right_panel)
        self.btn_park.setStyleSheet("background-color: #64748b; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_park.clicked.connect(self.on_hold_clicked)
        self.actions_layout.addWidget(self.btn_park)

        self.btn_resume = QPushButton("Resume", self.right_panel)
        self.btn_resume.setStyleSheet("background-color: #475569; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_resume.clicked.connect(self.on_resume_clicked)
        self.actions_layout.addWidget(self.btn_resume)

        self.btn_void = QPushButton("Clear Cart", self.right_panel)
        self.btn_void.setStyleSheet("background-color: #ef4444; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_void.clicked.connect(self.on_clear_cart_clicked)
        self.actions_layout.addWidget(self.btn_void)

        self.right_layout.addLayout(self.actions_layout)

        self.btn_checkout = QPushButton("Pay & Complete Checkout", self.right_panel)
        self.btn_checkout.setStyleSheet("background-color: #22c55e; color: white; padding: 14px; font-size: 15px; font-weight: bold; border-radius: 6px; margin-top: 5px;")
        self.btn_checkout.clicked.connect(self.on_checkout_clicked)
        self.right_layout.addWidget(self.btn_checkout)

        self.main_layout.addWidget(self.right_panel, stretch=2)

    # ================= Functional Controllers & Event Handlers =================

    def refresh_products(self, query=""):
        """Load database items into the product selector list."""
        self.products_table.setRowCount(0)
        products = self.product_repo.search_products(query)
        self.products_list_cache = products
        
        self.products_table.setRowCount(len(products))
        for index, prod in enumerate(products):
            self.products_table.setItem(index, 0, QTableWidgetItem(prod.name))
            self.products_table.setItem(index, 1, QTableWidgetItem(prod.sku))
            self.products_table.setItem(index, 2, QTableWidgetItem(f"${prod.sell_price:.2f}"))
            
            add_btn = QPushButton("Add", self.products_table)
            add_btn.setStyleSheet("background-color: #3b82f6; color: white; max-height: 22px; font-weight: bold; border-radius: 3px;")
            add_btn.clicked.connect(lambda checked=False, p_id=prod.id: self.add_by_id(p_id))
            self.products_table.setCellWidget(index, 3, add_btn)

    def refresh_customers(self):
        """Populate loyalty customer drop-down selector."""
        self.customer_combo.clear()
        self.customer_combo.addItem("Walk-in Customer", None)
        
        customers = self.customer_service.search_customers("")
        for cust in customers:
            self.customer_combo.addItem(f"{cust.name} ({cust.loyalty_points} pts)", cust.id)

    def on_search_triggered(self):
        """Handle search queries or direct barcode matching."""
        query = self.search_input.text().strip()
        if not query:
            self.refresh_products()
            return
            
        # Try direct barcode check
        match = self.product_repo.get_by_barcode(query)
        if match:
            self.add_by_id(match.id)
            self.search_input.clear()
            self.refresh_products()
            return
            
        self.refresh_products(query)

    def on_camera_scan_clicked(self):
        """Open the real-time webcam frame camera dialog to scan physical barcodes."""
        try:
            import cv2
            from pyzbar import pyzbar
        except ImportError:
            QMessageBox.critical(
                self,
                "Driver Error",
                "Camera barcode scanning requires OpenCV (cv2) and Pyzbar libraries!\n"
                "Please run: pip install opencv-python pyzbar"
            )
            return

        dialog = CameraScannerDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.barcode:
            barcode_str = dialog.barcode
            # Find and add product matching decoded barcode
            match = self.product_repo.get_by_barcode(barcode_str)
            if match:
                self.add_by_id(match.id)
                QMessageBox.information(self, "Item Scanned", f"Successfully scanned and added:\n{match.name}")
            else:
                QMessageBox.warning(self, "Scan Result", f"Scanned barcode: {barcode_str}\nHowever, no catalog item matches this barcode.")

    def add_by_sku(self, sku: str):
        prod = self.product_repo.get_by_sku(sku)
        if prod:
            self.add_by_id(prod.id)

    def add_by_id(self, product_id: int):
        prod = self.product_repo.get_by_id(product_id)
        if not prod:
            return
            
        # Check if item already exists in the cart
        for item in self.cart_items:
            if item['product_id'] == prod.id:
                item['qty'] += 1
                self.update_cart_ui()
                return
                
        self.cart_items.append({
            'product_id': prod.id,
            'name': prod.name,
            'price': prod.sell_price,
            'qty': 1,
            'tax_rate': prod.tax_rate
        })
        self.update_cart_ui()

    def on_product_double_clicked(self, row, column):
        if row < len(self.products_list_cache):
            prod = self.products_list_cache[row]
            self.add_by_id(prod.id)

    def on_customer_selected(self, index):
        if index >= 0:
            self.selected_customer_id = self.customer_combo.itemData(index)

    def update_cart_ui(self):
        """Redraw cart list widget and refresh pricing summaries."""
        self.cart_table.setRowCount(0)
        self.cart_table.setRowCount(len(self.cart_items))
        
        subtotal = 0.0
        tax_total = 0.0
        
        for index, item in enumerate(self.cart_items):
            line_total = item['price'] * item['qty']
            subtotal += line_total
            tax_total += line_total * item['tax_rate']
            
            self.cart_table.setItem(index, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(index, 1, QTableWidgetItem(f"${item['price']:.2f}"))
            
            # Interactive spinbox for Qty
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            qty_layout.setSpacing(4)
            
            minus_btn = QPushButton("-", qty_widget)
            minus_btn.setStyleSheet("max-width: 20px; max-height: 20px; font-weight: bold; background-color: #cbd5e1;")
            minus_btn.clicked.connect(lambda checked=False, i=index: self.adjust_qty(i, -1))
            qty_layout.addWidget(minus_btn)
            
            lbl_qty = QLabel(str(item['qty']), qty_widget)
            lbl_qty.setAlignment(Qt.AlignCenter)
            qty_layout.addWidget(lbl_qty)
            
            plus_btn = QPushButton("+", qty_widget)
            plus_btn.setStyleSheet("max-width: 20px; max-height: 20px; font-weight: bold; background-color: #cbd5e1;")
            plus_btn.clicked.connect(lambda checked=False, i=index: self.adjust_qty(i, 1))
            qty_layout.addWidget(plus_btn)
            
            self.cart_table.setCellWidget(index, 2, qty_widget)
            self.cart_table.setItem(index, 3, QTableWidgetItem(f"${line_total:.2f}"))
            
        grand_total = subtotal # Tax is included in item rates in standard config
        
        self.lbl_subtotal.setText(f"Subtotal: ${subtotal:.2f}")
        self.lbl_tax.setText(f"Tax (Included): ${tax_total:.2f}")
        self.lbl_total.setText(f"Total: ${grand_total:.2f}")

    def adjust_qty(self, index: int, delta: int):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['qty'] += delta
            if self.cart_items[index]['qty'] <= 0:
                self.cart_items.pop(index)
            self.update_cart_ui()

    def on_hold_clicked(self):
        """Park the current active cart in memory for multi-tasking."""
        if not self.cart_items:
            QMessageBox.warning(self, "Hold Sale", "Cannot park an empty shopping cart.")
            return
            
        self.parked_carts.append(list(self.cart_items))
        self.cart_items.clear()
        self.update_cart_ui()
        QMessageBox.information(self, "Hold Sale", "Active sale parked successfully.")

    def on_resume_clicked(self):
        """Retrieve and restore the last parked shopping cart."""
        if not self.parked_carts:
            QMessageBox.warning(self, "Resume Sale", "No parked transactions are currently available.")
            return
            
        self.cart_items = self.parked_carts.pop()
        self.update_cart_ui()

    def on_clear_cart_clicked(self):
        """Clear cart list cleanly."""
        if not self.cart_items:
            return
        res = QMessageBox.question(self, "Confirm Clear", "Are you sure you want to void this transaction?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.cart_items.clear()
            self.update_cart_ui()

    def on_checkout_clicked(self):
        """Prompt checkout flow validation."""
        if not self.cart_items:
            QMessageBox.warning(self, "Checkout Error", "Shopping cart is empty. Add items first!")
            return
            
        subtotal = sum(i['price'] * i['qty'] for i in self.cart_items)
        
        # Launch checkout payment processing modal
        dialog = PaymentDialog(subtotal, self)
        if dialog.exec() == QDialog.Accepted:
            method, ref = dialog.get_payment_details()
            
            # Format arguments matching SalesService.process_checkout
            cart_payload = [{'product_id': i['product_id'], 'qty': i['qty']} for i in self.cart_items]
            payment_payload = [{'method': method, 'amount': subtotal, 'reference': ref}]
            
            try:
                sale = self.sales_service.process_checkout(
                    cart_items=cart_payload,
                    payments=payment_payload,
                    customer_id=self.selected_customer_id
                )
                
                # Execute direct physical printing via USB/Serial thermal receipt printer driver
                from pos_app.services.receipt_service import ReceiptService
                receipt_service = ReceiptService(self.sales_service.session_db)
                printed = receipt_service.print_to_physical_printer(sale.id)
                
                print_msg = "\n(Receipt printed automatically to physical thermal printer)" if printed else "\n(Physical printer offline, receipt printed to logging console)"
                
                # Show receipt confirmation dialog
                QMessageBox.information(
                    self, 
                    "Transaction Succeeded", 
                    f"Sale completed successfully!\nInvoice No: {sale.invoice_no}\nTotal: ${sale.grand_total:.2f}{print_msg}\n\nStock adjusted and loyalty points issued!"
                )
                
                # Reset Terminal State
                self.cart_items.clear()
                self.update_cart_ui()
                self.refresh_products()
                self.refresh_customers()
                
            except Exception as e:
                QMessageBox.critical(self, "Checkout Failed", f"Database error processing sale: {str(e)}")


class PaymentDialog(QDialog):
    """Clean layout capturing tender payments, change calculation, and reference keys."""
    def __init__(self, amount_due: float, parent=None):
        super().__init__(parent)
        self.amount_due = amount_due
        self.setWindowTitle("Process Payment")
        self.setMinimumSize(400, 300)
        
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Subtitle
        self.lbl_due = QLabel(f"Amount Due: ${self.amount_due:.2f}", self)
        self.lbl_due.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b; text-align: center;")
        self.layout.addWidget(self.lbl_due)
        
        # Input Form
        self.form = QWidget(self)
        self.form_layout = QFormLayout(self.form)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        
        # Payment Method Dropdown
        self.method_combo = QComboBox(self.form)
        self.method_combo.addItems(["Cash", "Credit Card", "Mobile Money", "Debit Card"])
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        self.form_layout.addRow("Tender Mode:", self.method_combo)
        
        # Amount Tendered Input
        self.tendered_input = QLineEdit(self.form)
        self.tendered_input.setText(f"{self.amount_due:.2f}")
        self.tendered_input.textChanged.connect(self.calculate_change)
        self.form_layout.addRow("Amount Tendered:", self.tendered_input)
        
        # Reference Field
        self.ref_input = QLineEdit(self.form)
        self.ref_input.setPlaceholderText("Optional transaction ID / approval code")
        self.form_layout.addRow("Reference Key:", self.ref_input)
        
        self.layout.addWidget(self.form)
        
        # Change label
        self.lbl_change = QLabel("Change Due: $0.00", self)
        self.lbl_change.setStyleSheet("font-size: 15px; font-weight: 500; color: #16a34a;")
        self.layout.addWidget(self.lbl_change)
        
        # Dialog Button Box
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet("background-color: #cbd5e1; color: #1e293b; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("Finalize Payment", self)
        self.ok_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.ok_btn.clicked.connect(self.accept)
        self.btn_layout.addWidget(self.ok_btn)
        
        self.layout.addLayout(self.btn_layout)
        
    def calculate_change(self):
        try:
            tendered = float(self.tendered_input.text() or 0.0)
            change = max(0.0, tendered - self.amount_due)
            self.lbl_change.setText(f"Change Due: ${change:.2f}")
        except ValueError:
            self.lbl_change.setText("Change Due: $0.00")
            
    def on_method_changed(self, index):
        method = self.method_combo.currentText()
        if method != "Cash":
            # Cards are exact tender usually
            self.tendered_input.setText(f"{self.amount_due:.2f}")
            self.tendered_input.setEnabled(False)
        else:
            self.tendered_input.setEnabled(True)
        self.calculate_change()

    def get_payment_details(self) -> tuple[str, str]:
        return self.method_combo.currentText(), self.ref_input.text().strip()


class CameraThread(QThread):
    barcode_scanned = pyqtSignal(str)
    frame_updated = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        try:
            import cv2
            from pyzbar import pyzbar
        except ImportError:
            return

        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            
            # Grayscale conversions improve reader threshold accuracy
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = pyzbar.decode(gray)
            for b in barcodes:
                data_str = b.data.decode('utf-8')
                if data_str:
                    self.barcode_scanned.emit(data_str)
                    self.running = False
                    break
            
            self.frame_updated.emit(frame)
            self.msleep(30)
            
        cap.release()

    def stop(self):
        self.running = False
        self.wait()


class CameraScannerDialog(QDialog):
    """Real-time camera dialog rendering raw OpenCV feeds and decoding barcodes with pyzbar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Camera Barcode Reader")
        self.setMinimumSize(500, 400)
        self.barcode = None
        
        self.layout = QVBoxLayout(self)
        self.lbl_feed = QLabel("Initializing webcam feed...", self)
        self.lbl_feed.setAlignment(Qt.AlignCenter)
        self.lbl_feed.setStyleSheet("background-color: black; color: white; border-radius: 6px;")
        self.layout.addWidget(self.lbl_feed, stretch=1)
        
        self.cancel_btn = QPushButton("Cancel Scan", self)
        self.cancel_btn.setStyleSheet("background-color: #ef4444; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.cancel_btn.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_btn)
        
        self.thread = CameraThread(self)
        self.thread.barcode_scanned.connect(self.on_barcode_scanned)
        self.thread.frame_updated.connect(self.on_frame_updated)
        self.thread.start()
        
    def on_frame_updated(self, frame):
        try:
            import cv2
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.lbl_feed.setPixmap(QPixmap.fromImage(q_img).scaled(self.lbl_feed.width(), self.lbl_feed.height(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception:
            pass
            
    def on_barcode_scanned(self, barcode):
        self.barcode = barcode
        self.accept()
        
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
        
    def reject(self):
        self.thread.stop()
        super().reject()

