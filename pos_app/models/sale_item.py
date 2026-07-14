from sqlalchemy import Column, Integer, Float, ForeignKey
from pos_app.database.base import Base

class SaleItem(Base):
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    qty = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)

    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, qty={self.qty})>"
