from pos_app.ui.mock_pyqt import *
from pos_app.ui.icon_helper import get_icon

class ReportsView(QWidget):
    """Admin dashboard presenting aggregated metrics, cashier performance, and bestseller summaries."""
    def __init__(self, report_service, parent=None):
        super().__init__(parent)
        self.report_service = report_service
        
        self.init_ui()
        self.refresh_dashboard()

    def init_ui(self):
        # Master vertical layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # ================= TOP PANEL: Key Metrics Cards (Grid) =================
        self.metrics_container = QWidget(self)
        self.metrics_layout = QHBoxLayout(self.metrics_container)
        self.metrics_layout.setContentsMargins(0, 0, 0, 0)
        self.metrics_layout.setSpacing(12)

        # Card 1: Total Sales Revenue
        self.card_rev = QFrame(self.metrics_container)
        self.card_rev.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_rev.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px;")
        self.rev_layout = QVBoxLayout(self.card_rev)
        self.lbl_rev_title = QLabel("Gross Revenue", self.card_rev)
        self.lbl_rev_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.lbl_rev_val = QLabel("$0.00", self.card_rev)
        self.lbl_rev_val.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: bold; margin-top: 4px;")
        self.rev_layout.addWidget(self.lbl_rev_title)
        self.rev_layout.addWidget(self.lbl_rev_val)
        self.metrics_layout.addWidget(self.card_rev)

        # Card 2: Transactions Count
        self.card_tx = QFrame(self.metrics_container)
        self.card_tx.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_tx.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px;")
        self.tx_layout = QVBoxLayout(self.card_tx)
        self.lbl_tx_title = QLabel("Sales Transactions", self.card_tx)
        self.lbl_tx_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.lbl_tx_val = QLabel("0 sales", self.card_tx)
        self.lbl_tx_val.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: bold; margin-top: 4px;")
        self.tx_layout.addWidget(self.lbl_tx_title)
        self.tx_layout.addWidget(self.lbl_tx_val)
        self.metrics_layout.addWidget(self.card_tx)

        # Card 3: Discounts Issued
        self.card_disc = QFrame(self.metrics_container)
        self.card_disc.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_disc.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px;")
        self.disc_layout = QVBoxLayout(self.card_disc)
        self.lbl_disc_title = QLabel("Total Discounts", self.card_disc)
        self.lbl_disc_title.setStyleSheet("color: #e11d48; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.lbl_disc_val = QLabel("$0.00", self.card_disc)
        self.lbl_disc_val.setStyleSheet("color: #ef4444; font-size: 20px; font-weight: bold; margin-top: 4px;")
        self.disc_layout.addWidget(self.lbl_disc_title)
        self.disc_layout.addWidget(self.lbl_disc_val)
        self.metrics_layout.addWidget(self.card_disc)

        # Card 4: Net Profit
        self.card_prof = QFrame(self.metrics_container)
        self.card_prof.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_prof.setStyleSheet("background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px;")
        self.prof_layout = QVBoxLayout(self.card_prof)
        self.lbl_prof_title = QLabel("Net Business Profit", self.card_prof)
        self.lbl_prof_title.setStyleSheet("color: #16a34a; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.lbl_prof_val = QLabel("$0.00", self.card_prof)
        self.lbl_prof_val.setStyleSheet("color: #15803d; font-size: 20px; font-weight: bold; margin-top: 4px;")
        self.prof_layout.addWidget(self.lbl_prof_title)
        self.prof_layout.addWidget(self.lbl_prof_val)
        self.metrics_layout.addWidget(self.card_prof)

        self.main_layout.addWidget(self.metrics_container)

        # ================= MIDDLE PANEL: Interactive Visual Charts =================
        self.charts_container = QWidget(self)
        self.charts_layout = QHBoxLayout(self.charts_container)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_layout.setSpacing(15)
        
        from pos_app.ui.chart_widgets import SalesOverTimeChart, CategoryBreakdownChart
        self.sales_chart = SalesOverTimeChart(self.charts_container)
        self.sales_chart.setMinimumHeight(240)
        self.category_chart = CategoryBreakdownChart(self.charts_container)
        self.category_chart.setMinimumHeight(240)
        
        self.charts_layout.addWidget(self.sales_chart, stretch=1)
        self.charts_layout.addWidget(self.category_chart, stretch=1)
        self.main_layout.addWidget(self.charts_container)

        # ================= BOTTOM PANEL: Split Tables (Cashiers & Products) =================
        self.tables_container = QWidget(self)
        self.tables_layout = QHBoxLayout(self.tables_container)
        self.tables_layout.setContentsMargins(0, 0, 0, 0)
        self.tables_layout.setSpacing(15)

        # Left Table: Cashier performance ranking
        self.cashier_box = QGroupBox("Cashier Shift Breakdown", self.tables_container)
        self.cashier_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.cashier_layout = QVBoxLayout(self.cashier_box)
        self.cashier_layout.setContentsMargins(10, 15, 10, 10)

        self.cashier_table = QTableWidget(self.cashier_box)
        self.cashier_table.setStyleSheet("font-weight: normal;")
        self.cashier_table.setColumnCount(3)
        self.cashier_table.setHorizontalHeaderLabels(["Operator Name", "Ticket count", "Revenue Value"])
        self.cashier_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cashier_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cashier_layout.addWidget(self.cashier_table)
        
        self.tables_layout.addWidget(self.cashier_box)

        # Right Table: Bestsellers summary
        self.product_box = QGroupBox("Best-Selling Catalog Items", self.tables_container)
        self.product_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.product_layout = QVBoxLayout(self.product_box)
        self.product_layout.setContentsMargins(10, 15, 10, 10)

        self.bestsellers_table = QTableWidget(self.product_box)
        self.bestsellers_table.setStyleSheet("font-weight: normal;")
        self.bestsellers_table.setColumnCount(3)
        self.bestsellers_table.setHorizontalHeaderLabels(["Product Name", "Units Sold", "Total sales"])
        self.bestsellers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bestsellers_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_layout.addWidget(self.bestsellers_table)

        self.tables_layout.addWidget(self.product_box)
        self.main_layout.addWidget(self.tables_container, stretch=1)

        # ================= FOOTER PANEL: Operations Actions =================
        self.footer_box = QWidget(self)
        self.footer_layout = QHBoxLayout(self.footer_box)
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(10)

        self.btn_refresh = QPushButton("Refresh Data", self.footer_box)
        self.btn_refresh.setIcon(get_icon("sync"))
        self.btn_refresh.setStyleSheet("background-color: #475569; color: white; padding: 10px 18px; font-weight: bold; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.refresh_dashboard)
        self.footer_layout.addWidget(self.btn_refresh)

        self.footer_layout.addStretch()

        self.btn_export_pdf = QPushButton("Export PDF Summary", self.footer_box)
        self.btn_export_pdf.setIcon(get_icon("receipt"))
        self.btn_export_pdf.setStyleSheet("background-color: #3b82f6; color: white; padding: 10px 18px; font-weight: bold; border-radius: 4px;")
        self.btn_export_pdf.clicked.connect(self.on_export_pdf_clicked)
        self.footer_layout.addWidget(self.btn_export_pdf)

        self.btn_export_excel = QPushButton("Export Excel Sheets", self.footer_box)
        self.btn_export_excel.setIcon(get_icon("table_dine_in"))
        self.btn_export_excel.setStyleSheet("background-color: #16a34a; color: white; padding: 10px 18px; font-weight: bold; border-radius: 4px;")
        self.btn_export_excel.clicked.connect(self.on_export_excel_clicked)
        self.footer_layout.addWidget(self.btn_export_excel)

        self.main_layout.addWidget(self.footer_box)

    # ================= Functional Controllers =================

    def refresh_dashboard(self):
        """Query SQLAlchemy analytics metrics and load tables."""
        # 1. Sales Summary
        summary = self.report_service.get_sales_summary()
        self.lbl_rev_val.setText(f"${summary['total_revenue']:.2f}")
        self.lbl_tx_val.setText(f"{summary['transaction_count']} tickets")
        self.lbl_disc_val.setText(f"${summary['total_discount']:.2f}")
        self.lbl_prof_val.setText(f"${summary['net_profit']:.2f} ({summary['profit_margin_pct']:.1f}%)")

        # 2. Update Charts with live data
        sales_data = self.report_service.get_sales_over_time()
        self.sales_chart.setData(sales_data)
        
        cat_data = self.report_service.get_category_breakup()
        self.category_chart.setData(cat_data)

        # 3. Cashier Performances Table
        self.cashier_table.setRowCount(0)
        cashiers = self.report_service.get_cashier_performance()
        self.cashier_table.setRowCount(len(cashiers))
        for index, row in enumerate(cashiers):
            self.cashier_table.setItem(index, 0, QTableWidgetItem(row['name']))
            self.cashier_table.setItem(index, 1, QTableWidgetItem(f"{row['sales_count']} sales"))
            self.cashier_table.setItem(index, 2, QTableWidgetItem(f"${row['revenue_total']:.2f}"))

        # 4. Best Selling Products Table
        self.bestsellers_table.setRowCount(0)
        bestsellers = self.report_service.get_top_selling_products(limit=8)
        self.bestsellers_table.setRowCount(len(bestsellers))
        for index, row in enumerate(bestsellers):
            self.bestsellers_table.setItem(index, 0, QTableWidgetItem(row['name']))
            self.bestsellers_table.setItem(index, 1, QTableWidgetItem(f"{row['total_qty']} units"))
            self.bestsellers_table.setItem(index, 2, QTableWidgetItem(f"${row['total_sales']:.2f}"))

    def on_export_pdf_clicked(self):
        """Export dynamic high-fidelity financial summary statement PDF."""
        import os
        from pos_app.utils.export_helpers import export_pdf_summary_file
        
        summary = self.report_service.get_sales_summary()
        cashiers = self.report_service.get_cashier_performance()
        bestsellers = self.report_service.get_top_selling_products(limit=8)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "executive_sales_summary.pdf")
        
        success = export_pdf_summary_file(filepath, summary, cashiers, bestsellers)
        if success:
            QMessageBox.information(
                self,
                "PDF Exported",
                f"Financial statements PDF exported successfully!\nSaved to: {os.path.abspath(filepath)}"
            )
        else:
            QMessageBox.critical(self, "Export Failed", "Could not generate or write the PDF report file.")

    def on_export_excel_clicked(self):
        """Export dynamic itemized catalog sales spreadsheet workbook."""
        import os
        from pos_app.utils.export_helpers import export_excel_summary_file
        
        summary = self.report_service.get_sales_summary()
        cashiers = self.report_service.get_cashier_performance()
        bestsellers = self.report_service.get_top_selling_products(limit=8)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "itemized_catalog_sales.xlsx")
        
        success = export_excel_summary_file(filepath, summary, cashiers, bestsellers)
        if success:
            QMessageBox.information(
                self,
                "Excel Exported",
                f"Itemized catalog sales spreadsheet exported successfully!\nSaved to: {os.path.abspath(filepath)}"
            )
        else:
            QMessageBox.critical(self, "Export Failed", "Could not generate or write the Excel workbook file.")
