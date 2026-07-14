from pos_app.models.user import User

class Session:
    def __init__(self):
        self.current_user: User | None = None

    def login(self, user: User):
        self.current_user = user

    def logout(self):
        self.current_user = None

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def has_role(self, roles: list[str]) -> bool:
        if not self.current_user:
            return False
        return self.current_user.role in roles

session = Session()
