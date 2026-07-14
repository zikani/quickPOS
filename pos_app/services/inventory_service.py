from pos_app.repositories.product_repository import ProductRepository
from pos_app.repositories.inventory_repository import InventoryRepository
from pos_app.models.product import Product
from pos_app.models.category import Category
from pos_app.models.inventory_log import InventoryLog
from pos_app.core.session import session

class InventoryService:
    def __init__(self, session_db):
        self.session_db = session_db
        self.product_repo = ProductRepository(session_db)
        self.inventory_repo = InventoryRepository(session_db)

    def create_category(self, name: str, parent_id: int | None = None) -> Category:
        category = Category(name=name, parent_id=parent_id)
        return self.product_repo.add_category(category)

    def create_product(self, sku: str, barcode: str, name: str, category_id: int, 
                       cost_price: float, sell_price: float, stock_qty: float, 
                       reorder_level: float = 5.0, unit: str = "pcs") -> Product:
        product = Product(
            sku=sku,
            barcode=barcode,
            name=name,
            category_id=category_id,
            cost_price=cost_price,
            sell_price=sell_price,
            stock_qty=stock_qty,
            reorder_level=reorder_level,
            unit=unit
        )
        saved_product = self.product_repo.add_product(product)
        
        # Log initial stock as restock
        if stock_qty > 0:
            user_id = session.current_user.id if session.current_user else 1
            log = InventoryLog(
                product_id=saved_product.id,
                change_qty=stock_qty,
                reason="Initial Stock Set",
                user_id=user_id
            )
            self.inventory_repo.add_inventory_log(log)
            
        return saved_product

    def adjust_stock(self, product_id: int, change_qty: float, reason: str) -> bool:
        """Adjust stock levels manually (e.g. wastage, stocktake correction, receiving)."""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
            
        product.stock_qty += change_qty
        user_id = session.current_user.id if session.current_user else 1
        
        log = InventoryLog(
            product_id=product.id,
            change_qty=change_qty,
            reason=reason,
            user_id=user_id
        )
        self.inventory_repo.add_inventory_log(log)
        return True

    def get_low_stock_products(self, threshold: float | None = None) -> list[Product]:
        """Find products whose stock is below reorder levels or a set threshold."""
        all_products = self.product_repo.search_products("")
        low_stock = []
        for p in all_products:
            limit = threshold if threshold is not None else p.reorder_level
            if p.stock_qty <= limit:
                low_stock.append(p)
        return low_stock
