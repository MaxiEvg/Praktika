import enum
from typing import Annotated
from datetime import datetime, date
from sqlalchemy import (
    Integer, String, DateTime, ForeignKey, Boolean, Date, MetaData, text, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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

IntPk = Annotated[int, mapped_column(primary_key=True)]

class TypeContent(enum.Enum):
    article = "article"
    video = "video"
    image = "image"

class ProgressStatus(enum.Enum):
    pending = "pending"
    completed = "completed"

class TestType(enum.Enum):
    open = "open"
    closed = "closed"

class NotificationStatus(enum.Enum):
    sent = "sent"
    pending = "pending"

class UserRole(enum.Enum):
    employee = "employee"
    hr = "HR"

class AdaptationPlan(Base):
    __tablename__ = 'adaptation_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    position_id: Mapped[int] = mapped_column(ForeignKey('positions.id', ondelete="CASCADE"))
    position: Mapped["Positions"] = relationship("Positions", back_populates="adaptation_plans")
    stages: Mapped[list["AdaptationStage"]] = relationship("AdaptationStage", back_populates="plan", cascade="all, delete-orphan")

class AdaptationStage(Base):
    __tablename__ = 'adaptation_stages'

    id: Mapped[int] = mapped_column("ID_adaptstage", Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column("ID_adaptplan", Integer, ForeignKey("adaptation_plans.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    sequence_number: Mapped[int | None]
    content_id: Mapped[int] = mapped_column("ID_material", Integer, ForeignKey("content_material.id"))
    plan: Mapped["AdaptationPlan"] = relationship("AdaptationPlan", back_populates="stages")
    content: Mapped["ContentMaterial"] = relationship("ContentMaterial", back_populates="adaptation_stages")

class Positions(Base):
    __tablename__ = 'positions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    adaptation_plans: Mapped[list["AdaptationPlan"]] = relationship("AdaptationPlan", back_populates="position")
    users: Mapped[list["User"]] = relationship("User", back_populates="position", cascade="all, delete")

class UserAdaptationProgress(Base):
    __tablename__ = 'user_adaptation_progress'

    id: Mapped[int] = mapped_column("ID_useradaptprogress", Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("ID_user", Integer, ForeignKey("user.id"))
    stage_id: Mapped[int] = mapped_column("ID_adaptstage", Integer, ForeignKey("adaptation_stages.ID_adaptstage"))
    status: Mapped[ProgressStatus] = mapped_column(SQLEnum(ProgressStatus), nullable=False)
    completion_date: Mapped[date | None]
    notes: Mapped[str | None]

class ContentMaterial(Base):
    __tablename__ = 'content_material'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None]
    type: Mapped[TypeContent] = mapped_column(SQLEnum(TypeContent), nullable=False)
    content_url: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[datetime | None]
    category: Mapped[str | None]
    adaptation_stages: Mapped[list["AdaptationStage"]] = relationship("AdaptationStage", back_populates="content", cascade="all, delete")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="material", cascade="all, delete")

class Department(Base):
    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None]
    users: Mapped[list["User"]] = relationship("User", back_populates="department", cascade="all, delete")

class Feedback(Base):
    __tablename__ = 'feedback'

    id: Mapped[int] = mapped_column("ID_feedback", Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("ID_user", Integer, ForeignKey("user.id"))
    material_id: Mapped[int] = mapped_column("ID_material", Integer, ForeignKey("content_material.id"))
    rating: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None]
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    user: Mapped["User"] = relationship("User", back_populates="feedbacks")
    material: Mapped["ContentMaterial"] = relationship("ContentMaterial", back_populates="feedbacks")

class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    user: Mapped["User"] = relationship("User", back_populates="notifications")

class Test(Base):
    __tablename__ = 'test'

    id: Mapped[int] = mapped_column(primary_key=True)
    stage_id: Mapped[int] = mapped_column(Integer, ForeignKey("adaptation_stages.ID_adaptstage"), nullable=False)
    instructions: Mapped[str | None]
    test_type: Mapped[TestType] = mapped_column(SQLEnum(TestType), nullable=False)
    passing_score: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[datetime | None]
    stage: Mapped["AdaptationStage"] = relationship("AdaptationStage", back_populates="tests")
    questions: Mapped[list["TestQuestion"]] = relationship("TestQuestion", back_populates="test", cascade="all, delete")

AdaptationStage.tests = relationship("Test", back_populates="stage", cascade="all, delete-orphan")

class TestQuestion(Base):
    __tablename__ = 'test_question'

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("test.id"), nullable=False)
    question_text: Mapped[str | None]
    question_type: Mapped[str | None]
    sequence_number: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[datetime | None]
    test: Mapped["Test"] = relationship("Test", back_populates="questions")
    options: Mapped[list["TestOption"]] = relationship("TestOption", back_populates="question", cascade="all, delete")
    user_answers: Mapped[list["UserTestAnswer"]] = relationship("UserTestAnswer", back_populates="question", cascade="all, delete")

class TestOption(Base):
    __tablename__ = 'test_option'

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_question.id"), nullable=False)
    option_text: Mapped[str | None]
    is_correct: Mapped[bool | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[datetime | None]
    question: Mapped["TestQuestion"] = relationship("TestQuestion", back_populates="options")
    user_answers: Mapped[list["UserTestAnswer"]] = relationship("UserTestAnswer", back_populates="option", cascade="all, delete")

class UserTestAnswer(Base):
    __tablename__ = 'user_test_answer'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_question.id"), nullable=False)
    answer_text: Mapped[str | None]
    option_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("test_option.id"))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    user: Mapped["User"] = relationship("User", back_populates="test_answers")
    question: Mapped["TestQuestion"] = relationship("TestQuestion", back_populates="user_answers")
    option: Mapped["TestOption"] = relationship("TestOption", back_populates="user_answers")

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column("ID_user", Integer, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    registration_date: Mapped[date] = mapped_column(Date)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("department.id"))
    position_id: Mapped[int] = mapped_column(Integer, ForeignKey("positions.id"))
    test_answers = relationship("UserTestAnswer", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete")
    adaptation_progress = relationship("UserAdaptationProgress", back_populates="user", cascade="all, delete")
    department = relationship("Department", back_populates="users")
    position = relationship("Positions", back_populates="users")
