# notifications.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Notification(Base):
    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(String)
    status = Column(String)  # Например: 'sent', 'pending'
    created_at = Column(DateTime)
