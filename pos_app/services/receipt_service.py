from pos_app.models.sale import Sale
from pos_app.config.settings import settings

class ReceiptService:
    def __init__(self, session_db):
        self.session_db = session_db

    def generate_receipt_text(self, sale_id: int) -> str:
        """Generate a formatted receipt layout for receipt printers."""
        sale = self.session_db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            return "Transaction not found."
            
        from pos_app.models.sale_item import SaleItem
        from pos_app.models.product import Product
        from pos_app.models.payment import Payment
        from pos_app.models.user import User
        
        items = self.session_db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
        payments = self.session_db.query(Payment).filter(Payment.sale_id == sale_id).all()
        cashier = self.session_db.query(User).filter(User.id == sale.cashier_id).first()
        cashier_name = cashier.full_name if cashier else "Staff"
        
        lines = []
        lines.append(settings.STORE_NAME.center(40))
        lines.append(settings.STORE_ADDRESS.center(40))
        lines.append(settings.STORE_PHONE.center(40))
        lines.append(f"Tax ID: {settings.STORE_TAX_ID}".center(40))
        lines.append("-" * 40)
        lines.append(f"Invoice: {sale.invoice_no}")
        lines.append(f"Date: {sale.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Cashier: {cashier_name}")
        lines.append("-" * 40)
        lines.append(f"{'Item':<20} {'Qty':>4} {'Price':>6} {'Total':>7}")
        lines.append("-" * 40)
        
        for item in items:
            p = self.session_db.query(Product).filter(Product.id == item.product_id).first()
            p_name = p.name[:18] if p else f"Item #{item.product_id}"
            qty_str = f"{item.qty:.1f}" if item.qty % 1 != 0 else f"{int(item.qty)}"
            lines.append(f"{p_name:<20} {qty_str:>4} {settings.CURRENCY}{item.unit_price:>5.2f} {settings.CURRENCY}{item.line_total:>6.2f}")
            if item.discount > 0:
                lines.append(f"  * Discount: -{settings.CURRENCY}{item.discount:.2f}")
                
        lines.append("-" * 40)
        lines.append(f"{'Subtotal:':<25} {settings.CURRENCY}{sale.subtotal:>13.2f}")
        if sale.discount_total > 0:
            lines.append(f"{'Discount Total:':<25} -{settings.CURRENCY}{sale.discount_total:>12.2f}")
        lines.append(f"{'Tax:':<25} {settings.CURRENCY}{sale.tax_total:>13.2f}")
        lines.append(f"{'Grand Total:':<25} {settings.CURRENCY}{sale.grand_total:>13.2f}")
        lines.append("-" * 40)
        
        for pm in payments:
            lines.append(f"{pm.method + ' Tendered:':<25} {settings.CURRENCY}{pm.amount:>13.2f}")
            
        lines.append("-" * 40)
        lines.append("Thank you for your business!".center(40))
        lines.append("Please retain this receipt for return".center(40))
        lines.append("\n\n")
        
        return "\n".join(lines)
