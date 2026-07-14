import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pos_app.database.base import Base
from pos_app.services.inventory_service import InventoryService
from pos_app.models.product import Product
from pos_app.models.category import Category
from pos_app.models.inventory_log import InventoryLog

class TestInventoryService(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for fast unit testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.inventory_service = InventoryService(self.session)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_category(self):
        cat = self.inventory_service.create_category("Soft Drinks")
        self.assertIsNotNone(cat.id)
        self.assertEqual(cat.name, "Soft Drinks")

    def test_create_product_sets_initial_stock_and_logs(self):
        cat = self.inventory_service.create_category("Snacks")
        
        prod = self.inventory_service.create_product(
            sku="SNA-11",
            barcode="111111",
            name="Salted Peanuts",
            category_id=cat.id,
            cost_price=0.50,
            sell_price=1.50,
            stock_qty=50.0,
            reorder_level=10.0
        )
        
        self.assertIsNotNone(prod.id)
        self.assertEqual(prod.stock_qty, 50.0)
        
        # Verify inventory log was created for initial stock
        log = self.session.query(InventoryLog).filter(InventoryLog.product_id == prod.id).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.change_qty, 50.0)
        self.assertEqual(log.reason, "Initial Stock Set")

    def test_adjust_stock_logs_properly(self):
        cat = self.inventory_service.create_category("Fresh Bakery")
        prod = self.inventory_service.create_product(
            sku="BAK-99",
            barcode="9999",
            name="Bagel",
            category_id=cat.id,
            cost_price=0.30,
            sell_price=1.00,
            stock_qty=10.0
        )
        
        success = self.inventory_service.adjust_stock(prod.id, -2.0, "Damaged")
        self.assertTrue(success)
        self.assertEqual(prod.stock_qty, 8.0)
        
        # Check logs
        logs = self.session.query(InventoryLog).filter(InventoryLog.product_id == prod.id).all()
        self.assertEqual(len(logs), 2) # Initial Stock Set and Damaged
        self.assertEqual(logs[1].change_qty, -2.0)
        self.assertEqual(logs[1].reason, "Damaged")

    def test_low_stock_checks(self):
        cat = self.inventory_service.create_category("Pantry")
        p1 = self.inventory_service.create_product("P1", "1", "Product 1", cat.id, 0.5, 1.0, 15.0, reorder_level=5.0)
        p2 = self.inventory_service.create_product("P2", "2", "Product 2", cat.id, 0.5, 1.0, 2.0, reorder_level=5.0)
        
        low_stock = self.inventory_service.get_low_stock_products()
        self.assertEqual(len(low_stock), 1)
        self.assertEqual(low_stock[0].sku, "P2")
