from sqlalchemy import Column, Integer, String, Float
from pos_app.database.base import Base

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    loyalty_points = Column(Integer, default=0)
    balance = Column(Float, default=0.0)

    def __repr__(self):
        return f"<Customer(name='{self.name}', points={self.loyalty_points})>"
