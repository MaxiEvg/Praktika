# content.py
from sqlalchemy import Column, Integer, String, DateTime
from .base import Base

class ContentMaterial(Base):
    __tablename__ = 'content_material'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    type = Column(String)  # Например: 'article', 'video'
    content_url = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    category = Column(String)
