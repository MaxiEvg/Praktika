from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }



class Base(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=naming_convention)



class AdaptationPlan(Base):
    __tablename__ = 'adaptation_plans'
    id = Column('ID_adaptplan', Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime)
    position_id = Column('ID_position', Integer, ForeignKey('position.id'))

    position = relationship("Position", back_populates="adaptation_plans")
    stages = relationship("AdaptationStage", back_populates="plan")
    content_material = relationship("ContentMaterial", back_populates="adaptation_stages")


class AdaptationStage(Base):
    __tablename__ = 'adaptation_stages'
    id = Column('ID_adaptstage', Integer, primary_key=True)
    plan_id = Column('ID_adaptplan', Integer, ForeignKey('adaptation_plans.ID_adaptplan'))
    title = Column(String, nullable=False)
    sequence_number = Column(Integer)
    content_id = Column('ID_material', Integer, ForeignKey('content_material.id'))

    plan = relationship("AdaptationPlan", back_populates="stages")
    content = relationship("ContentMaterial", back_populates="stages")
    progress = relationship("UserAdaptationProgress", back_populates="stage")
    tests = relationship("Test", back_populates="stage")


class UserAdaptationProgress(Base):
    __tablename__ = 'user_adaptation_progress'
    id = Column('ID_useradaptprogress', Integer, primary_key=True)
    user_id = Column('ID_user', Integer, ForeignKey('users.ID_user'))
    stage_id = Column('ID_adaptstage', Integer, ForeignKey('adaptation_stages.ID_adaptstage'))
    status = Column(String)  # например: 'pending', 'completed'
    completion_date = Column(Date)
    notes = Column(String)

    user = relationship("User", back_populates="adaptation_progress")
    stage = relationship("AdaptationStage", back_populates="progress")

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

    # Связи
    adaptation_stages = relationship("AdaptationStage", back_populates="content_material", cascade="all, delete")
    feedbacks = relationship("Feedback", back_populates="material", cascade="all, delete")

class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    users = relationship("User", back_populates="department")

class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column('ID_feedback', Integer, primary_key=True)
    user_id = Column('ID_user', Integer, ForeignKey('users.ID_user'))
    material_id = Column('ID_material', Integer, ForeignKey('content_material.ID_material'))
    rating = Column(Integer)  # Например, 1-5
    comment = Column(String)
    submitted_at = Column(DateTime)

    user = relationship("User", back_populates="feedbacks")
    material = relationship("ContentMaterial", back_populates="feedbacks")

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    message = Column(String, nullable=False)
    status = Column(String)  # Например: 'sent', 'pending'
    created_at = Column(DateTime)

    user = relationship("User", back_populates="notifications")

class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    stage_id = Column(Integer, ForeignKey('adaptation_stage.id'), nullable=False)
    instructions = Column(String)
    test_type = Column(String)  # Например: 'open', 'closed'
    passing_score = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    stage = relationship("AdaptationStage", back_populates="test")
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete")


class TestQuestion(Base):
    __tablename__ = 'test_question'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False)
    question_text = Column(String)
    question_type = Column(String)  # Например: 'open', 'closed'
    sequence_number = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    test = relationship("Test", back_populates="questions")
    options = relationship("TestOption", back_populates="question", cascade="all, delete")
    user_answers = relationship("UserTestAnswer", back_populates="question", cascade="all, delete")


class TestOption(Base):
    __tablename__ = 'test_option'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('test_question.id'), nullable=False)
    option_text = Column(String)
    is_correct = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    question = relationship("TestQuestion", back_populates="options")
    user_answers = relationship("UserTestAnswer", back_populates="option", cascade="all, delete")


class UserTestAnswer(Base):
    __tablename__ = 'user_test_answer'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('test_question.id'), nullable=False)
    answer_text = Column(String)  # Для открытых вопросов
    option_id = Column(Integer, ForeignKey('test_option.id'))  # Для закрытых вопросов
    submitted_at = Column(DateTime)

    user = relationship("User", back_populates="test_answers")
    question = relationship("TestQuestion", back_populates="user_answers")
    option = relationship("TestOption", back_populates="user_answers")

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

    test_answers = relationship("UserTestAnswer", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete")
