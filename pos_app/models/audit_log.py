from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from pos_app.database.base import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)  # Login, Void, Refund, DB Backup, Reset
    entity = Column(String(50), nullable=True)  # User, Sale, Product, Database
    entity_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, action='{self.action}', entity='{self.entity}')>"
