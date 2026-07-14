from pos_app.repositories.user_repository import UserRepository
from pos_app.models.user import User
from pos_app.models.audit_log import AuditLog
from pos_app.core.session import session
from pos_app.utils.security import hash_password, verify_password

class AuthService:
    def __init__(self, session_db):
        self.session_db = session_db
        self.user_repo = UserRepository(session_db)

    def login(self, username: str, password: str) -> bool:
        """Authenticate a user by username and password, starting their session."""
        user = self.user_repo.get_by_username(username)
        if user and user.is_active and verify_password(password, user.password_hash):
            session.login(user)
            self._log_audit(user.id, "Login", "User", user.id)
            return True
        return False

    def logout(self):
        """End the current user's session."""
        if session.current_user:
            self._log_audit(session.current_user.id, "Logout", "User", session.current_user.id)
            session.logout()

    def register_user(self, username: str, password: str, role: str, full_name: str) -> User:
        """Register a new active user account with hashed password."""
        hashed_pw = hash_password(password)
        new_user = User(
            username=username,
            password_hash=hashed_pw,
            role=role,
            full_name=full_name,
            is_active=True
        )
        return self.user_repo.add(new_user)

    def _log_audit(self, user_id: int, action: str, entity: str, entity_id: int):
        log = AuditLog(user_id=user_id, action=action, entity=entity, entity_id=entity_id)
        self.session_db.add(log)
        self.session_db.commit()
