# users.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .base import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    role = Column(String)  # Например, 'employee' или 'HR'
    registration_date = Column(Date)
    department_id = Column(Integer, ForeignKey('department.id'))
    position_id = Column(Integer, ForeignKey('position.id'))
