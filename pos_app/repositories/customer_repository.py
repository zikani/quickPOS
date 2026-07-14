from pos_app.models.customer import Customer

class CustomerRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, customer_id: int):
        return self.session.query(Customer).filter(Customer.id == customer_id).first()

    def search_customers(self, query: str):
        if not query:
            return self.session.query(Customer).all()
        
        search_filter = f"%{query}%"
        return self.session.query(Customer).filter(
            (Customer.name.like(search_filter)) |
            (Customer.phone.like(search_filter)) |
            (Customer.email.like(search_filter))
        ).all()

    def add(self, customer: Customer):
        self.session.add(customer)
        self.session.commit()
        return customer
