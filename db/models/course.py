from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from .base import Base

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    creator = Column(String)
    date = Column(Date)

class CourseMaterial(Base):
    __tablename__ = 'course_material'
    id = Column(Integer, primary_key=True)
    id_course = Column(Integer, ForeignKey('course.id'))
    number = Column(Integer)
    name = Column(String)
    text = Column(String)
    date = Column(Date)

class CourseMaterialFile(Base):
    __tablename__ = 'course_material_file'
    id = Column(Integer, primary_key=True)
    id_test = Column(Integer, ForeignKey('test.id'))
    id_file = Column(Integer, ForeignKey('file.id'))
    id_course_material = Column(Integer, ForeignKey('course_material.id'))

class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer, primary_key=True)
    id_test_result = Column(Integer, ForeignKey('test_result.id'))
    id_course_material = Column(Integer, ForeignKey('course_material.id'))
    is_flag = Column(Boolean)
    date = Column(Date)

class UserCourse(Base):
    __tablename__ = 'user_course'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('user.id'))
    id_course = Column(Integer, ForeignKey('course.id'))
    date_enrolled = Column(Date)