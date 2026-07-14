from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pos_app.database.base import Base

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    cost_price = Column(Float, nullable=False, default=0.0)
    sell_price = Column(Float, nullable=False, default=0.0)
    tax_rate = Column(Float, nullable=False, default=0.0825)  # Default 8.25%
    stock_qty = Column(Float, nullable=False, default=0.0)
    reorder_level = Column(Float, nullable=False, default=5.0)
    unit = Column(String(20), nullable=False, default='pcs')  # pcs, kg, box, etc.
    image_path = Column(String(255), nullable=True)
    
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(name='{self.name}', sku='{self.sku}', stock={self.stock_qty})>"
