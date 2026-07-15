import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pos_app.database.base import Base
from pos_app.services.sales_service import SalesService
from pos_app.services.inventory_service import InventoryService
from pos_app.models.user import User
from pos_app.models.customer import Customer
from pos_app.models.product import Product
from pos_app.models.sale import Sale
from pos_app.models.sale_item import SaleItem
from pos_app.models.payment import Payment
from pos_app.models.inventory_log import InventoryLog
from pos_app.core.session import session as pos_session

class TestSalesService(unittest.TestCase):
    def setUp(self):
        # Setup clean test memory database
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        self.inventory_service = InventoryService(self.session)
        self.sales_service = SalesService(self.session)
        
        # Create a mock user session
        self.cashier = User(username="test_cashier", password_hash="hash", role="Cashier", full_name="Test Staff")
        self.session.add(self.cashier)
        self.session.commit()
        pos_session.login(self.cashier)
        
        # Setup standard category & product
        self.cat = self.inventory_service.create_category("Beverages")
        self.product = self.inventory_service.create_product(
            sku="COLA-01",
            barcode="8888",
            name="Classic Cola",
            category_id=self.cat.id,
            cost_price=0.50,
            sell_price=2.00,
            stock_qty=100.0,
            reorder_level=5.0
        )
        
        # Setup loyal customer
        self.customer = Customer(name="John Watson", phone="123", email="john@example.com", loyalty_points=0)
        self.session.add(self.customer)
        self.session.commit()

    def tearDown(self):
        pos_session.logout()
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_checkout_decrements_stock_and_creates_records(self):
        cart_items = [
            {"product_id": self.product.id, "qty": 5.0, "discount": 1.0}  # total price = 5 * $2 - $1 = $9
        ]
        payments = [
            {"method": "Cash", "amount": 10.0}
        ]
        
        sale = self.sales_service.process_checkout(cart_items, payments, self.customer.id)
        
        self.assertIsNotNone(sale.id)
        self.assertEqual(sale.status, "Completed")
        self.assertEqual(sale.subtotal, 10.0) # 5 * 2.00
        self.assertEqual(sale.discount_total, 1.0)
        
        # Verify product stock decremented
        updated_prod = self.session.query(Product).filter(Product.id == self.product.id).first()
        self.assertEqual(updated_prod.stock_qty, 95.0) # 100 - 5
        
        # Verify customer loyalty points (1 point per $10 spent. Total with tax at 8.25%: sub $10 - disc $1 = $9 * 1.0825 = $9.74. Point: 0)
        updated_customer = self.session.query(Customer).filter(Customer.id == self.customer.id).first()
        self.assertEqual(updated_customer.loyalty_points, 0)
        
        # Let's verify inventory log was written
        inv_logs = self.session.query(InventoryLog).filter(InventoryLog.product_id == self.product.id, InventoryLog.reason == "Sale").all()
        self.assertEqual(len(inv_logs), 1)
        self.assertEqual(inv_logs[0].change_qty, -5.0)

    def test_void_reverses_stock_and_points(self):
        # Give customer points first to test reversal
        self.customer.loyalty_points = 50
        self.session.commit()
        
        cart_items = [
            {"product_id": self.product.id, "qty": 10.0, "discount": 0.0} # 10 * 2.00 = $20 -> tax-inclusive total ~$21.65 -> points earned: 2
        ]
        payments = [
            {"method": "Card", "amount": 21.65}
        ]
        
        sale = self.sales_service.process_checkout(cart_items, payments, self.customer.id)
        
        # Verify points grew by 2
        self.assertEqual(self.customer.loyalty_points, 52)
        
        # Void the transaction
        success = self.sales_service.void_transaction(sale.id)
        self.assertTrue(success)
        
        # Verify sale status is now Voided
        updated_sale = self.session.query(Sale).filter(Sale.id == sale.id).first()
        self.assertEqual(updated_sale.status, "Voided")
        
        # Verify product stock returned to 100
        updated_prod = self.session.query(Product).filter(Product.id == self.product.id).first()
        self.assertEqual(updated_prod.stock_qty, 100.0)
        
        # Verify points returned to 50
        self.assertEqual(self.customer.loyalty_points, 50)
