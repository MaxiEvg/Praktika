from sqlalchemy import Column, Integer, String
from .base import Base

class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    file_path = Column(String)
    file_type = Column(String)