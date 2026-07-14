from pos_app.models.user import User

class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str):
        return self.session.query(User).filter(User.username == username).first()

    def list_all_active(self):
        return self.session.query(User).filter(User.is_active == True).all()

    def add(self, user: User):
        self.session.add(user)
        self.session.commit()
        return user
