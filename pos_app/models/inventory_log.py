from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from pos_app.database.base import Base

class InventoryLog(Base):
    __tablename__ = 'inventory_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    change_qty = Column(Float, nullable=False)  # Positive for additions, negative for reductions
    reason = Column(String(100), nullable=False)  # Sale, Restock, Damage, Manual Adjustment
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InventoryLog(product_id={self.product_id}, change={self.change_qty}, reason='{self.reason}')>"
