from pos_app.models.sale import Sale
from pos_app.models.sale_item import SaleItem
from pos_app.models.payment import Payment
from pos_app.models.inventory_log import InventoryLog
from pos_app.models.product import Product
from pos_app.models.customer import Customer
from pos_app.repositories.sale_repository import SaleRepository
from pos_app.repositories.product_repository import ProductRepository
from pos_app.repositories.customer_repository import CustomerRepository
from pos_app.core.session import session
import datetime

class SalesService:
    def __init__(self, session_db):
        self.session_db = session_db
        self.sale_repo = SaleRepository(session_db)
        self.product_repo = ProductRepository(session_db)
        self.customer_repo = CustomerRepository(session_db)

    def process_checkout(self, cart_items: list[dict], payments: list[dict], customer_id: int | None = None) -> Sale:
        """Process checkout: save sale, decrement stocks, issue loyalty points, write logs."""
        if not session.current_user:
            raise PermissionError("No user logged in to current session.")

        subtotal = 0.0
        tax_total = 0.0
        discount_total = 0.0
        
        db_items = []
        for item in cart_items:
            product = self.product_repo.get_by_id(item['product_id'])
            if not product:
                raise ValueError(f"Product ID {item['product_id']} not found.")
            
            if product.stock_qty < item['qty']:
                # Allow sell-through, but raise alert
                pass
                
            qty = item['qty']
            price = product.sell_price
            discount = item.get('discount', 0.0)  # absolute discount
            tax = (price * qty - discount) * product.tax_rate
            line_total = (price * qty) - discount + tax
            
            subtotal += price * qty
            tax_total += tax
            discount_total += discount
            
            # Decrement stock qty
            product.stock_qty -= qty
            
            # Create sale item
            db_item = SaleItem(
                product_id=product.id,
                qty=qty,
                unit_price=price,
                discount=discount,
                tax=tax,
                line_total=line_total
            )
            db_items.append(db_item)
            
            # Create inventory log
            inv_log = InventoryLog(
                product_id=product.id,
                change_qty=-qty,
                reason="Sale",
                user_id=session.current_user.id
            )
            self.session_db.add(inv_log)

        grand_total = subtotal - discount_total + tax_total
        
        # Format Invoice No: INV-YYYYMMDD-HHMMSS
        now = datetime.datetime.now()
        invoice_no = f"INV-{now.strftime('%Y%m%d-%H%M%S')}"
        
        sale = Sale(
            invoice_no=invoice_no,
            customer_id=customer_id,
            cashier_id=session.current_user.id,
            subtotal=subtotal,
            tax_total=tax_total,
            discount_total=discount_total,
            grand_total=grand_total,
            status='Completed'
        )
        
        db_payments = []
        for pm in payments:
            db_payment = Payment(
                method=pm['method'],
                amount=pm['amount'],
                reference=pm.get('reference')
            )
            db_payments.append(db_payment)
            
        # Update Customer Loyalty Points
        if customer_id:
            customer = self.customer_repo.get_by_id(customer_id)
            if customer:
                # 1 point per $10 spent
                points_earned = int(grand_total // 10)
                customer.loyalty_points += points_earned

        return self.sale_repo.create_sale(sale, db_items, db_payments)

    def void_transaction(self, sale_id: int) -> bool:
        """Void a sale and reverse stock quantities with inventory logs."""
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale or sale.status == 'Voided':
            return False
            
        sale.status = 'Voided'
        items = self.sale_repo.get_sale_items(sale_id)
        
        for item in items:
            product = self.product_repo.get_by_id(item.product_id)
            if product:
                product.stock_qty += item.qty
                
                inv_log = InventoryLog(
                    product_id=product.id,
                    change_qty=item.qty,
                    reason="Void Transaction",
                    user_id=session.current_user.id if session.current_user else 1
                )
                self.session_db.add(inv_log)
                
        # Reverse customer points
        if sale.customer_id:
            customer = self.customer_repo.get_by_id(sale.customer_id)
            if customer:
                points_deducted = int(sale.grand_total // 10)
                customer.loyalty_points = max(0, customer.loyalty_points - points_deducted)
                
        self.session_db.commit()
        return True
