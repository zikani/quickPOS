from sqlalchemy import Column, Integer, String
from pos_app.database.base import Base

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    contact = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<Supplier(name='{self.name}')>"
