from pos_app.models.sale import Sale
from pos_app.models.sale_item import SaleItem
from pos_app.models.product import Product
from pos_app.models.user import User
from sqlalchemy import func

class ReportService:
    def __init__(self, session_db):
        self.session_db = session_db

    def get_sales_summary(self, start_date=None, end_date=None) -> dict:
        """Calculate total sales revenue, tax, discounts, and transaction counts."""
        query = self.session_db.query(Sale).filter(Sale.status == 'Completed')
        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
            
        sales = query.all()
        
        total_revenue = sum(s.grand_total for s in sales)
        total_cost = 0.0
        
        # Calculate profits
        for sale in sales:
            items = self.session_db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
            for item in items:
                p = self.session_db.query(Product).filter(Product.id == item.product_id).first()
                if p:
                    total_cost += p.cost_price * item.qty

        net_profit = total_revenue - total_cost
        
        return {
            "transaction_count": len(sales),
            "total_revenue": total_revenue,
            "total_tax": sum(s.tax_total for s in sales),
            "total_discount": sum(s.discount_total for s in sales),
            "net_profit": net_profit,
            "profit_margin_pct": (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0
        }

    def get_top_selling_products(self, limit: int = 5) -> list[dict]:
        """Aggregate product sales by item quantity."""
        results = self.session_db.query(
            SaleItem.product_id,
            func.sum(SaleItem.qty).label('total_qty'),
            func.sum(SaleItem.line_total).label('total_sales')
        ).join(Sale).filter(Sale.status == 'Completed')\
         .group_by(SaleItem.product_id)\
         .order_by(func.sum(SaleItem.qty).desc())\
         .limit(limit).all()
         
        top_products = []
        for r in results:
            p = self.session_db.query(Product).filter(Product.id == r.product_id).first()
            name = p.name if p else f"Product #{r.product_id}"
            top_products.append({
                "product_id": r.product_id,
                "name": name,
                "total_qty": r.total_qty,
                "total_sales": r.total_sales
            })
        return top_products

    def get_cashier_performance(self) -> list[dict]:
        """Group and total sale values per active cashier."""
        results = self.session_db.query(
            Sale.cashier_id,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.grand_total).label('revenue_total')
        ).filter(Sale.status == 'Completed')\
         .group_by(Sale.cashier_id).all()
         
        performance = []
        for r in results:
            u = self.session_db.query(User).filter(User.id == r.cashier_id).first()
            cashier_name = u.full_name if u else f"Cashier #{r.cashier_id}"
            performance.append({
                "cashier_id": r.cashier_id,
                "name": cashier_name,
                "sales_count": r.sales_count,
                "revenue_total": r.revenue_total
            })
        return performance
