from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pos_app.database.base import Base

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"
