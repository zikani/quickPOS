from pos_app.models.inventory_log import InventoryLog
from pos_app.models.supplier import Supplier
from pos_app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from pos_app.models.product import Product

class InventoryRepository:
    def __init__(self, session):
        self.session = session

    def get_supplier_by_id(self, supplier_id: int):
        return self.session.query(Supplier).filter(Supplier.id == supplier_id).first()

    def list_all_suppliers(self):
        return self.session.query(Supplier).all()

    def search_suppliers(self, query: str):
        if not query:
            return self.list_all_suppliers()
        search_filter = f"%{query}%"
        return self.session.query(Supplier).filter(
            (Supplier.name.like(search_filter)) |
            (Supplier.contact.like(search_filter))
        ).all()

    def add_supplier(self, supplier: Supplier):
        self.session.add(supplier)
        self.session.commit()
        return supplier

    def add_inventory_log(self, log: InventoryLog):
        self.session.add(log)
        self.session.commit()
        return log

    def get_logs_for_product(self, product_id: int):
        return self.session.query(InventoryLog).filter(InventoryLog.product_id == product_id).order_by(InventoryLog.created_at.desc()).all()

    def create_purchase_order(self, po: PurchaseOrder, items: list[PurchaseOrderItem]):
        try:
            self.session.add(po)
            self.session.flush()
            for item in items:
                item.po_id = po.id
                self.session.add(item)
            self.session.commit()
            return po
        except Exception as e:
            self.session.rollback()
            raise e
