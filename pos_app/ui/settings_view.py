from pos_app.ui.mock_pyqt import *

class SettingsView(QWidget):
    """Configuration panel to manage general storefront meta-data and SQLite backups."""
    def __init__(self, backup_service, parent=None):
        super().__init__(parent)
        self.backup_service = backup_service
        
        self.init_ui()
        self.refresh_backups()

    def init_ui(self):
        # Base layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # ================= LEFT SIDE: Shop & Tax Info =================
        self.left_panel = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(15)

        # Store Info Form
        self.store_box = QGroupBox("Store Profile Settings", self.left_panel)
        self.store_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.store_form_layout = QFormLayout(self.store_box)
        self.store_form_layout.setContentsMargins(15, 20, 15, 15)
        self.store_form_layout.setSpacing(10)

        self.store_name_input = QLineEdit(self.store_box)
        self.store_name_input.setText("QuickPOS Outlet #1")
        self.store_name_input.setStyleSheet("font-weight: normal; padding: 4px;")
        self.store_form_layout.addRow("Storefront Name:", self.store_name_input)

        self.store_address_input = QLineEdit(self.store_box)
        self.store_address_input.setText("100 Tech Innovation Blvd, London")
        self.store_address_input.setStyleSheet("font-weight: normal; padding: 4px;")
        self.store_form_layout.addRow("Physical Address:", self.store_address_input)

        self.tax_id_input = QLineEdit(self.store_box)
        self.tax_id_input.setText("GB-982-1240-00")
        self.tax_id_input.setStyleSheet("font-weight: normal; padding: 4px;")
        self.store_form_layout.addRow("VAT Registration ID:", self.tax_id_input)

        self.currency_combo = QComboBox(self.store_box)
        self.currency_combo.addItems(["USD ($)", "GBP (£)", "EUR (€)", "CAD ($)"])
        self.currency_combo.setStyleSheet("font-weight: normal; padding: 4px;")
        self.store_form_layout.addRow("Primary Currency:", self.currency_combo)

        self.left_layout.addWidget(self.store_box)

        # Tax Settings Form
        self.tax_box = QGroupBox("Tax Rate Config", self.left_panel)
        self.tax_box.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.tax_form_layout = QFormLayout(self.tax_box)
        self.tax_form_layout.setContentsMargins(15, 20, 15, 15)
        self.tax_form_layout.setSpacing(10)

        self.tax_spin = QDoubleSpinBox(self.tax_box)
        self.tax_spin.setRange(0.0, 100.0)
        self.tax_spin.setValue(15.0)
        self.tax_spin.setPrefix("% ")
        self.tax_spin.setStyleSheet("font-weight: normal; padding: 4px;")
        self.tax_form_layout.addRow("Default Value-Added Tax (VAT):", self.tax_spin)

        self.left_layout.addWidget(self.tax_box)

        self.btn_save_config = QPushButton("Save Store Parameters", self.left_panel)
        self.btn_save_config.setStyleSheet("background-color: #3b82f6; color: white; padding: 12px; font-weight: bold; border-radius: 5px;")
        self.btn_save_config.clicked.connect(self.on_save_config_clicked)
        self.left_layout.addWidget(self.btn_save_config)

        self.left_layout.addStretch()
        self.main_layout.addWidget(self.left_panel, stretch=1)

        # ================= RIGHT SIDE: SQLite Backups =================
        self.right_panel = QGroupBox("Database Maintenance & Backups", self)
        self.right_panel.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(15, 20, 15, 15)
        self.right_layout.setSpacing(10)

        # Help info
        self.lbl_help = QLabel("Manage point-of-sale terminal security archives below. System backups capture sales, products, categories, and customer loyalty records in offline-first SQLite snapshots.", self.right_panel)
        self.lbl_help.setStyleSheet("font-weight: normal; color: #64748b; line-height: 1.4;")
        self.lbl_help.setAlignment(Qt.AlignLeft)
        self.right_layout.addWidget(self.lbl_help)

        # Control row
        self.backup_ctrl_layout = QHBoxLayout()
        self.btn_create_backup = QPushButton("Create Hot Backup Now", self.right_panel)
        self.btn_create_backup.setStyleSheet("background-color: #16a34a; color: white; padding: 8px 14px; font-weight: bold; border-radius: 4px;")
        self.btn_create_backup.clicked.connect(self.on_create_backup_clicked)
        self.backup_ctrl_layout.addWidget(self.btn_create_backup)
        self.backup_ctrl_layout.addStretch()
        self.right_layout.addLayout(self.backup_ctrl_layout)

        # List of existing backups
        self.lbl_list_title = QLabel("Available Backups Archive:", self.right_panel)
        self.lbl_list_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #475569; margin-top: 5px;")
        self.right_layout.addWidget(self.lbl_list_title)

        self.backups_table = QTableWidget(self.right_panel)
        self.backups_table.setStyleSheet("font-weight: normal;")
        self.backups_table.setColumnCount(2)
        self.backups_table.setHorizontalHeaderLabels(["Archive File", "Action"])
        self.backups_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backups_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.right_layout.addWidget(self.backups_table)

        self.main_layout.addWidget(self.right_panel, stretch=1)

    # ================= Functional Controllers =================

    def refresh_backups(self):
        """Query BackupService to list files and draw interaction rows."""
        self.backups_table.setRowCount(0)
        files = self.backup_service.list_backups()
        
        self.backups_table.setRowCount(len(files))
        for index, filename in enumerate(files):
            self.backups_table.setItem(index, 0, QTableWidgetItem(filename))
            
            restore_btn = QPushButton("Restore", self.backups_table)
            restore_btn.setStyleSheet("background-color: #ef4444; color: white; max-height: 22px; font-weight: bold; border-radius: 3px;")
            restore_btn.clicked.connect(lambda checked=False, f=filename: self.on_restore_backup_clicked(f))
            self.backups_table.setCellWidget(index, 1, restore_btn)

    def on_save_config_clicked(self):
        """Mock config file adjustments."""
        QMessageBox.information(
            self,
            "Success",
            "Store profile parameters and VAT rates saved in system settings!"
        )

    def on_create_backup_clicked(self):
        """Generate fresh SQLite snapshot backup file."""
        dest_path = self.backup_service.create_backup()
        if dest_path:
            filename = os.path.basename(dest_path)
            QMessageBox.information(
                self,
                "Success",
                f"Hot Database snapshot completed successfully!\nFile: {filename}"
            )
            self.refresh_backups()
        else:
            QMessageBox.critical(self, "Backup Failed", "System could not execute hot snapshot. DB file might be locked.")

    def on_restore_backup_clicked(self, filename: str):
        """Prompts validation and executes restore overwrite."""
        res = QMessageBox.question(
            self,
            "Confirm System Restore",
            f"Are you absolutely sure you want to overwrite the current database with: {filename}?\n\nThis will undo all transactions since the backup timestamp!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if res == QMessageBox.Yes:
            success = self.backup_service.restore_backup(filename)
            if success:
                QMessageBox.information(
                    self,
                    "Restore Completed",
                    "Database state restored successfully! Please restart the terminal to load refreshed collections."
                )
            else:
                QMessageBox.critical(self, "Restore Error", "An input-output error occurred during restoration.")
import os
