from pos_app.models.sale import Sale
from pos_app.models.sale_item import SaleItem
from pos_app.models.payment import Payment

class SaleRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, sale_id: int):
        return self.session.query(Sale).filter(Sale.id == sale_id).first()

    def get_by_invoice(self, invoice_no: str):
        return self.session.query(Sale).filter(Sale.invoice_no == invoice_no).first()

    def create_sale(self, sale: Sale, items: list[SaleItem], payments: list[Payment]):
        """Create a new sale transaction, line items, and payments with rollback capability."""
        try:
            self.session.add(sale)
            self.session.flush()  # Gets the sale ID
            
            for item in items:
                item.sale_id = sale.id
                self.session.add(item)
                
            for payment in payments:
                payment.sale_id = sale.id
                self.session.add(payment)
                
            self.session.commit()
            return sale
        except Exception as e:
            self.session.rollback()
            raise e

    def get_sale_items(self, sale_id: int):
        return self.session.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def get_sale_payments(self, sale_id: int):
        return self.session.query(Payment).filter(Payment.sale_id == sale_id).all()

    def list_all_sales(self):
        return self.session.query(Sale).order_by(Sale.created_at.desc()).all()
