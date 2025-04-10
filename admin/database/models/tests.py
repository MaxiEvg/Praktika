# tests.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from .base import Base

class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    stage_id = Column(Integer, ForeignKey('adaptation_stage.id'))
    instructions = Column(String)
    test_type = Column(String)  # Например: 'open', 'closed'
    passing_score = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class TestQuestion(Base):
    __tablename__ = 'test_question'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'))
    question_text = Column(String)
    question_type = Column(String)  # Например: 'open', 'closed'
    sequence_number = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class TestOption(Base):
    __tablename__ = 'test_option'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('test_question.id'))
    option_text = Column(String)
    is_correct = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class UserTestAnswer(Base):
    __tablename__ = 'user_test_answer'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    question_id = Column(Integer, ForeignKey('test_question.id'))
    answer_text = Column(String)  # Для открытых вопросов
    option_id = Column(Integer, ForeignKey('test_option.id'))  # Для закрытых вопросов
    submitted_at = Column(DateTime)
