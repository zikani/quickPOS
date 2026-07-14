from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from pos_app.database.base import Base

class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    cashier_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_total = Column(Float, nullable=False, default=0.0)
    discount_total = Column(Float, nullable=False, default=0.0)
    grand_total = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), default='Completed')  # Completed, Voided, Refunded
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Sale(invoice='{self.invoice_no}', grand_total={self.grand_total})>"
