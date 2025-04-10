# feedback.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    material_id = Column(Integer, ForeignKey('content_material.id'))
    rating = Column(Integer)  # Например, 1-5
    comment = Column(String)
    submitted_at = Column(DateTime)
