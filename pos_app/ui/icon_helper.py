"""
icon_helper.py

Utility for loading and managing SVG icons for the QuickPOS application.
Supports light/dark theme switching and provides QIcon objects for PyQt6 widgets.
"""

import os
from pathlib import Path
from pos_app.ui.mock_pyqt import QIcon, QPixmap

# Base directory for assets
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
SVG_DIR = ASSETS_DIR / "svg"

# Theme directories
LIGHT_THEME_DIR = SVG_DIR / "light"
DARK_THEME_DIR = SVG_DIR / "dark"


class IconLoader:
    """Helper class for loading SVG icons as QIcon objects."""
    
    def __init__(self, theme: str = "light"):
        """
        Initialize icon loader with specified theme.
        
        Args:
            theme: Either "light" or "dark"
        """
        self.theme = theme
        self._icon_cache = {}
    
    def set_theme(self, theme: str):
        """Switch between light and dark themes."""
        if theme in ("light", "dark"):
            self.theme = theme
            self._icon_cache.clear()
    
    def get_icon(self, icon_name: str) -> QIcon:
        """
        Load an icon by name for the current theme.
        
        Args:
            icon_name: Name of the icon file (without .svg extension)
            
        Returns:
            QIcon object for the requested icon
        """
        cache_key = f"{self.theme}:{icon_name}"
        
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Determine the correct path based on theme
        if self.theme == "dark":
            icon_path = DARK_THEME_DIR / f"{icon_name}.svg"
        else:
            icon_path = LIGHT_THEME_DIR / f"{icon_name}.svg"
        
        # Fallback to currentColor version if theme-specific doesn't exist
        if not icon_path.exists():
            icon_path = SVG_DIR / f"{icon_name}.svg"
        
        if not icon_path.exists():
            # Return empty icon if file doesn't exist
            self._icon_cache[cache_key] = QIcon()
            return QIcon()
        
        # Load SVG as QIcon
        try:
            icon = QIcon(str(icon_path))
            self._icon_cache[cache_key] = icon
            return icon
        except Exception:
            # Return empty icon on error
            self._icon_cache[cache_key] = QIcon()
            return QIcon()
    
    def get_pixmap(self, icon_name: str, size: int = 24) -> QPixmap:
        """
        Load an icon as a QPixmap with specified size.
        
        Args:
            icon_name: Name of the icon file (without .svg extension)
            size: Size in pixels for the pixmap
            
        Returns:
            QPixmap object for the requested icon
        """
        icon = self.get_icon(icon_name)
        return icon.pixmap(size, size)


# Global icon loader instance
_icon_loader = IconLoader()


def set_icon_theme(theme: str):
    """Set the global icon theme (light or dark)."""
    _icon_loader.set_theme(theme)


def get_icon(icon_name: str) -> QIcon:
    """Get an icon by name using the global theme setting."""
    return _icon_loader.get_icon(icon_name)


def get_pixmap(icon_name: str, size: int = 24) -> QPixmap:
    """Get a pixmap by name using the global theme setting."""
    return _icon_loader.get_pixmap(icon_name, size)


# Available icon names for reference
AVAILABLE_ICONS = [
    "add", "barcode", "battery", "calendar", "card_payment", "cash_bills",
    "cash_drawer_open", "cash_register", "chart_manager", "check_success",
    "clock", "close_error", "customer", "delivery_truck", "discount", "edit",
    "filter", "gift_card", "help", "hold_order", "home", "inventory_box",
    "kitchen", "lock", "logout", "loyalty_star", "menu", "notification",
    "price_tag", "printer", "receipt", "refund", "scale_weight", "scan",
    "search", "settings", "shield_admin", "shopping_cart", "split_payment",
    "sync", "table_dine_in", "takeout_bag", "terminal_monitor", "trash",
    "user_cashier", "void", "wifi"
]
