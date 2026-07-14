from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from pos_app.database.base import Base

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    status = Column(String(20), default='Pending')  # Pending, Received, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

class PurchaseOrderItem(Base):
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    po_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    qty = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
