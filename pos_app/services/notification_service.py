from pos_app.repositories.product_repository import ProductRepository
from pos_app.config.settings import settings

class NotificationService:
    def __init__(self, session_db):
        self.product_repo = ProductRepository(session_db)

    def check_for_alerts(self) -> list[str]:
        """Check all products and return string alert list for low stock levels."""
        alerts = []
        products = self.product_repo.search_products("")
        for p in products:
            if p.stock_qty <= p.reorder_level:
                alerts.append(f"Low Stock Alert: '{p.name}' ({p.sku}) has {p.stock_qty:.1f} {p.unit} remaining (Reorder point: {p.reorder_level:.1f})")
        return alerts
