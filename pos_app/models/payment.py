from sqlalchemy import Column, Integer, String, Float, ForeignKey
from pos_app.database.base import Base

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    method = Column(String(30), nullable=False)  # Cash, Card, Mobile, Split
    amount = Column(Float, nullable=False)
    reference = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Payment(method='{self.method}', amount={self.amount})>"
