from pos_app.models.product import Product
from pos_app.models.category import Category

class ProductRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, product_id: int):
        return self.session.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str):
        return self.session.query(Product).filter(Product.sku == sku).first()

    def get_by_barcode(self, barcode: str):
        return self.session.query(Product).filter(Product.barcode == barcode).first()

    def search_products(self, query: str):
        """Search products by SKU, name, or barcode."""
        if not query:
            return self.session.query(Product).all()
        
        search_filter = f"%{query}%"
        return self.session.query(Product).filter(
            (Product.name.like(search_filter)) |
            (Product.sku.like(search_filter)) |
            (Product.barcode.like(search_filter))
        ).all()

    def list_categories(self):
        return self.session.query(Category).all()

    def add_product(self, product: Product):
        self.session.add(product)
        self.session.commit()
        return product

    def add_category(self, category: Category):
        self.session.add(category)
        self.session.commit()
        return category
