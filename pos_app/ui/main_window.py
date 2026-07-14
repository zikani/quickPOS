from pos_app.ui.mock_pyqt import *
from pos_app.core.session import session

class POSMainWindow(QMainWindow):
    """The central shell of the PyQt6 POS Application, implementing a main menu, status bar and sidebar."""
    def __init__(self, auth_service, sales_service, inventory_service, customer_service, report_service):
        super().__init__()
        self.auth_service = auth_service
        self.sales_service = sales_service
        self.inventory_service = inventory_service
        self.customer_service = customer_service
        self.report_service = report_service
        
        self.setWindowTitle("QuickPOS Terminal")
        self.setMinimumSize(1024, 768)
        
        # Central stacked widget to handle switching screens
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize subviews
        self.init_views()
        
    def init_views(self):
        """Create and stack the login widget and main workspace views."""
        # Setup Login Widget
        self.login_widget = QWidget(self)
        self.login_layout = QVBoxLayout(self.login_widget)
        self.login_layout.setContentsMargins(100, 100, 100, 100)
        self.login_layout.setSpacing(20)
        
        self.title_label = QLabel("QuickPOS Terminal\nLogin", self.login_widget)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        self.login_layout.addWidget(self.title_label)
        
        self.username_input = QLineEdit(self.login_widget)
        self.username_input.setPlaceholderText("Username (e.g. admin, cashier)")
        self.username_input.setMinimumSize(300, 40)
        self.username_input.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px;")
        self.login_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit(self.login_widget)
        self.password_input.setPlaceholderText("Password (e.g. admin123, cashier123)")
        self.password_input.setEchoMode(Qt.Password)
        self.password_input.setMinimumSize(300, 40)
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px;")
        self.login_layout.addWidget(self.password_input)
        
        self.login_btn = QPushButton("Access Terminal", self.login_widget)
        self.login_btn.setMinimumSize(300, 45)
        self.login_btn.setStyleSheet("""
            background-color: #3b82f6; 
            color: white; 
            font-weight: bold; 
            border-radius: 6px;
            font-size: 14px;
        """)
        self.login_btn.clicked = self.on_login_clicked
        self.login_layout.addWidget(self.login_btn)
        
        self.stacked_widget.addWidget(self.login_widget)
        
    def on_login_clicked(self):
        """Handle login attempts, updating session and displaying main POS screens."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if self.auth_service.login(username, password):
            self.show_main_workspace()
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid username or password.")
            
    def show_main_workspace(self):
        """Construct the sidebar layout and POS panels upon successful sign-in."""
        self.workspace_widget = QWidget(self)
        self.workspace_layout = QHBoxLayout(self.workspace_widget)
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(0)
        
        # Sidebar Panel
        self.sidebar = QWidget(self.workspace_widget)
        self.sidebar.setMinimumSize(220, 0)
        self.sidebar.setMaximumSize(220, 99999)
        self.sidebar.setStyleSheet("background-color: #0f172a; color: #94a3b8;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 20)
        self.sidebar_layout.setSpacing(10)
        
        self.nav_title = QLabel("QuickPOS Menu", self.sidebar)
        self.nav_title.setAlignment(Qt.AlignCenter)
        self.nav_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        self.sidebar_layout.addWidget(self.nav_title)

        # Profile banner
        current_user_name = session.current_user.full_name if session.current_user else "Anonymous"
        current_user_role = session.current_user.role if session.current_user else "Cashier"
        
        self.profile_box = QWidget(self.sidebar)
        self.profile_box.setStyleSheet("background-color: #1e293b; border-radius: 6px; margin: 10px; padding: 10px;")
        self.profile_layout = QVBoxLayout(self.profile_box)
        self.profile_layout.setContentsMargins(10, 10, 10, 10)
        
        self.user_name_label = QLabel(current_user_name, self.profile_box)
        self.user_name_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        self.profile_layout.addWidget(self.user_name_label)
        
        self.user_role_label = QLabel(f"Role: {current_user_role}", self.profile_box)
        self.user_role_label.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: 500;")
        self.profile_layout.addWidget(self.user_role_label)
        
        self.sidebar_layout.addWidget(self.profile_box)
        
        # Nav Buttons filtered by Role permissions
        navs = [("Checkout Screen", self.show_pos_view)]
        
        if current_user_role in ["Admin", "Manager"]:
            navs.append(("Inventory Manager", self.show_inventory_view))
            
        navs.append(("Customer CRM", self.show_customer_view))
        
        if current_user_role in ["Admin", "Manager"]:
            navs.append(("Sales Reporting", self.show_reports_view))
            
        if current_user_role == "Admin":
            navs.append(("System Settings", self.show_settings_view))
            
        navs.append(("Sign Out", self.on_logout_clicked))
        
        for name, callback in navs:
            btn = QPushButton(name, self.sidebar)
            btn.setMinimumSize(0, 45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; 
                    color: #cbd5e1; 
                    text-align: left; 
                    padding-left: 20px; 
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1e293b;
                    color: white;
                }
            """)
            btn.clicked = callback
            self.sidebar_layout.addWidget(btn)
            
        self.sidebar_layout.addStretch()
        
        self.workspace_layout.addWidget(self.sidebar)
        
        # Right Workspace stack
        self.workspace_stack = QStackedWidget(self.workspace_widget)
        self.workspace_layout.addWidget(self.workspace_stack)
        
        # Setup specific screens
        self.setup_workspace_screens()
        
        self.stacked_widget.addWidget(self.workspace_widget)
        self.stacked_widget.setCurrentWidget(self.workspace_widget)
        
    def setup_workspace_screens(self):
        """Create each independent workspace tab panel."""
        self.pos_screen = QWidget(self)
        p_lay = QVBoxLayout(self.pos_screen)
        p_lbl = QLabel("POS Checkout Active Terminal", self.pos_screen)
        p_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        p_lay.addWidget(p_lbl)
        self.workspace_stack.addWidget(self.pos_screen)
        
        self.inventory_screen = QWidget(self)
        i_lay = QVBoxLayout(self.inventory_screen)
        i_lbl = QLabel("Inventory Catalog Management", self.inventory_screen)
        i_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        i_lay.addWidget(i_lbl)
        self.workspace_stack.addWidget(self.inventory_screen)
        
        self.customer_screen = QWidget(self)
        c_lay = QVBoxLayout(self.customer_screen)
        c_lbl = QLabel("Customer Relations Management", self.customer_screen)
        c_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        c_lay.addWidget(c_lbl)
        self.workspace_stack.addWidget(self.customer_screen)
        
        self.reports_screen = QWidget(self)
        r_lay = QVBoxLayout(self.reports_screen)
        r_lbl = QLabel("Sales Summary Reports and Analytics", self.reports_screen)
        r_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        r_lay.addWidget(r_lbl)
        self.workspace_stack.addWidget(self.reports_screen)
        
        self.settings_screen = QWidget(self)
        s_lay = QVBoxLayout(self.settings_screen)
        s_lbl = QLabel("Terminal Settings & SQLite Maintenance", self.settings_screen)
        s_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        s_lay.addWidget(s_lbl)
        self.workspace_stack.addWidget(self.settings_screen)
        
    def show_pos_view(self): self.workspace_stack.setCurrentWidget(self.pos_screen)
    def show_inventory_view(self): self.workspace_stack.setCurrentWidget(self.inventory_screen)
    def show_customer_view(self): self.workspace_stack.setCurrentWidget(self.customer_screen)
    def show_reports_view(self): self.workspace_stack.setCurrentWidget(self.reports_screen)
    def show_settings_view(self): self.workspace_stack.setCurrentWidget(self.settings_screen)
    
    def on_logout_clicked(self):
        """Sign out the current user, clearing state and returning to login form."""
        self.auth_service.logout()
        self.username_input.clear()
        self.password_input.clear()
        self.stacked_widget.setCurrentIndex(0)
