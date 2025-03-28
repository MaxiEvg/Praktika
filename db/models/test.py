from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    date = Column(Date)

class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    type = Column(Boolean)
    id_test = Column(Integer, ForeignKey('test.id'))

class Answer(Base):
    __tablename__ = 'answer'
    id_question = Column(Integer, ForeignKey('question.id'), primary_key=True)
    id = Column(Integer, primary_key=True)
    text = Column(String)
    is_correct = Column(Boolean)

class UserAnswer(Base):
    __tablename__ = 'user_answer'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('user.id'))
    id_question = Column(Integer, ForeignKey('question.id'))
    id_answer = Column(Integer, ForeignKey('answer.id'))
    is_correct = Column(Boolean)
    date = Column(Date)

class TestResult(Base):
    __tablename__ = 'test_result'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('user.id'))
    id_test = Column(Integer, ForeignKey('test.id'))
    score = Column(Integer)
    field_5 = Column(Integer)
    date = Column(Date)