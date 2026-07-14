import os
from datetime import datetime, timedelta
from pos_app.database.base import engine, Base, SessionLocal
from pos_app.models.user import User
from pos_app.models.category import Category
from pos_app.models.product import Product
from pos_app.models.customer import Customer
from pos_app.models.supplier import Supplier
from pos_app.models.sale import Sale
from pos_app.models.sale_item import SaleItem
from pos_app.models.payment import Payment
from pos_app.models.inventory_log import InventoryLog
from pos_app.utils.security import hash_password

def initialize_and_seed_db():
    """Create all SQLite database tables and seed them with rich, polished demo data."""
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Check if database has users. If yes, it's already initialized.
        if session.query(User).count() > 0:
            return
            
        print("[*] Seeding database with fresh demonstration data...")
        
        # 1. Seed Users
        admin_user = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="Admin",
            full_name="Alex Mercer (Admin)"
        )
        manager_user = User(
            username="manager",
            password_hash=hash_password("manager123"),
            role="Manager",
            full_name="Sarah Connor (Manager)"
        )
        cashier_user = User(
            username="cashier",
            password_hash=hash_password("cashier123"),
            role="Cashier",
            full_name="John Doe (Cashier)"
        )
        session.add_all([admin_user, manager_user, cashier_user])
        session.flush() # get user IDs
        
        # 2. Seed Categories
        cat_beverages = Category(name="Beverages")
        cat_snacks = Category(name="Snacks & Chips")
        cat_bakery = Category(name="Fresh Bakery")
        cat_produce = Category(name="Fresh Produce")
        session.add_all([cat_beverages, cat_snacks, cat_bakery, cat_produce])
        session.flush()
        
        # 3. Seed Products
        p1 = Product(sku="BEV-001", barcode="012000000133", name="Organic Cola 355ml", category_id=cat_beverages.id, cost_price=0.75, sell_price=1.99, tax_rate=0.0825, stock_qty=120, reorder_level=20, unit="pcs")
        p2 = Product(sku="BEV-002", barcode="012000000244", name="Mineral Spring Water 500ml", category_id=cat_beverages.id, cost_price=0.25, sell_price=1.29, tax_rate=0.0825, stock_qty=300, reorder_level=50, unit="pcs")
        p3 = Product(sku="SNA-001", barcode="028400000199", name="Classic Salted Potato Chips", category_id=cat_snacks.id, cost_price=0.95, sell_price=2.99, tax_rate=0.0825, stock_qty=12, reorder_level=15, unit="pcs") # low stock
        p4 = Product(sku="SNA-002", barcode="028400000288", name="Chilli Tortilla Chips", category_id=cat_snacks.id, cost_price=1.10, sell_price=3.49, tax_rate=0.0825, stock_qty=75, reorder_level=15, unit="pcs")
        p5 = Product(sku="BAK-001", barcode="031200000177", name="Fresh Butter Croissant", category_id=cat_bakery.id, cost_price=0.45, sell_price=1.89, tax_rate=0.0, stock_qty=40, reorder_level=10, unit="pcs")
        p6 = Product(sku="BAK-002", barcode="031200000288", name="Choc-chip Muffin XL", category_id=cat_bakery.id, cost_price=0.60, sell_price=2.49, tax_rate=0.0, stock_qty=2, reorder_level=8, unit="pcs") # low stock
        p7 = Product(sku="PRD-001", barcode="041200000122", name="Honeycrisp Apple (Premium)", category_id=cat_produce.id, cost_price=0.40, sell_price=1.20, tax_rate=0.0, stock_qty=150, reorder_level=30, unit="kg")
        p8 = Product(sku="PRD-002", barcode="041200000233", name="Organic Cavendish Bananas", category_id=cat_produce.id, cost_price=0.30, sell_price=0.99, tax_rate=0.0, stock_qty=80, reorder_level=20, unit="kg")
        session.add_all([p1, p2, p3, p4, p5, p6, p7, p8])
        session.flush()
        
        # Log initial inventory
        for p in [p1, p2, p3, p4, p5, p6, p7, p8]:
            session.add(InventoryLog(
                product_id=p.id,
                change_qty=p.stock_qty,
                reason="Initial Seeding",
                user_id=admin_user.id
            ))
            
        # 4. Seed Customers
        cust1 = Customer(name="Jane Miller", phone="212-555-0199", email="jane.miller@example.com", loyalty_points=120, balance=0.0)
        cust2 = Customer(name="Robert Dow", phone="310-555-4422", email="robert.dow@example.com", loyalty_points=45, balance=15.50)
        cust3 = Customer(name="Emily Smith", phone="650-555-8811", email="emily.smith@example.com", loyalty_points=320, balance=0.0)
        session.add_all([cust1, cust2, cust3])
        session.flush()
        
        # 5. Seed Suppliers
        sup1 = Supplier(name="Mainstreet Wholesale Foods", contact="James Baker", email="orders@mainstreetfoods.com", address="500 Industrial Pkwy, Sector 4")
        sup2 = Supplier(name="Organic Farms Distributing", contact="Laura Green", email="contact@organicfarms.org", address="75 Rural Route 2, Green Valley")
        session.add_all([sup1, sup2])
        session.flush()
        
        # 6. Seed Historical Sales (for dashboard stats of the past 5 days)
        base_time = datetime.now()
        sales_data = [
            # Day -4
            {"days_ago": 4, "items": [(p1, 5), (p3, 2), (p5, 4)], "customer": cust1, "pm": "Cash"},
            {"days_ago": 4, "items": [(p2, 10), (p4, 3)], "customer": cust2, "pm": "Card"},
            # Day -3
            {"days_ago": 3, "items": [(p7, 3.5), (p8, 2.0), (p1, 2)], "customer": None, "pm": "Cash"},
            {"days_ago": 3, "items": [(p5, 6), (p6, 4)], "customer": cust3, "pm": "Card"},
            # Day -2
            {"days_ago": 2, "items": [(p4, 5), (p1, 12)], "customer": cust1, "pm": "Card"},
            {"days_ago": 2, "items": [(p2, 15), (p7, 6.0)], "customer": None, "pm": "Mobile"},
            # Day -1
            {"days_ago": 1, "items": [(p3, 8), (p5, 10)], "customer": cust3, "pm": "Card"},
            {"days_ago": 1, "items": [(p1, 20), (p8, 12.5)], "customer": cust2, "pm": "Cash"},
            # Today
            {"days_ago": 0, "items": [(p1, 4), (p2, 5), (p4, 2), (p7, 3.0)], "customer": cust1, "pm": "Card"}
        ]
        
        for index, item_data in enumerate(sales_data):
            days_ago = item_data["days_ago"]
            items_list = item_data["items"]
            customer = item_data["customer"]
            pay_method = item_data["pm"]
            
            created_at = base_time - timedelta(days=days_ago, hours=(index % 4) + 10)
            
            subtotal = 0.0
            tax_total = 0.0
            grand_total = 0.0
            
            invoice_no = f"INV-{created_at.strftime('%Y%m%d')}-000{index+1}"
            
            sale = Sale(
                invoice_no=invoice_no,
                customer_id=customer.id if customer else None,
                cashier_id=cashier_user.id,
                subtotal=0.0,
                tax_total=0.0,
                discount_total=0.0,
                grand_total=0.0,
                status="Completed",
                created_at=created_at
            )
            session.add(sale)
            session.flush() # get sale ID
            
            for p, qty in items_list:
                price = p.sell_price
                tax = price * qty * p.tax_rate
                line_total = (price * qty) + tax
                
                subtotal += price * qty
                tax_total += tax
                
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=p.id,
                    qty=qty,
                    unit_price=price,
                    discount=0.0,
                    tax=tax,
                    line_total=line_total
                )
                session.add(sale_item)
                
            grand_total = subtotal + tax_total
            sale.subtotal = subtotal
            sale.tax_total = tax_total
            sale.grand_total = grand_total
            
            payment = Payment(
                sale_id=sale.id,
                method=pay_method,
                amount=grand_total
            )
            session.add(payment)
            
        session.commit()
        print("[✓] Seeding complete! Database is primed and ready.")
    except Exception as e:
        session.rollback()
        print(f"[❌] Error during seeding: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    initialize_and_seed_db()
