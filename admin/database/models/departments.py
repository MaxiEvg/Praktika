# departments.py
from sqlalchemy import Column, Integer, String
from .base import Base

class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
