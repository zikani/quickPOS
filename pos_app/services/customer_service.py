from pos_app.repositories.customer_repository import CustomerRepository
from pos_app.models.customer import Customer

class CustomerService:
    def __init__(self, session_db):
        self.session_db = session_db
        self.customer_repo = CustomerRepository(session_db)

    def create_customer(self, name: str, phone: str = None, email: str = None) -> Customer:
        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            loyalty_points=0,
            balance=0.0
        )
        return self.customer_repo.add(customer)

    def search_customers(self, query: str) -> list[Customer]:
        return self.customer_repo.search_customers(query)

    def get_customer_by_id(self, customer_id: int) -> Customer | None:
        return self.customer_repo.get_by_id(customer_id)
