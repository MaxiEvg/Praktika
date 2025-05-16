from pydantic import BaseModel, PostgresDsn
from enum import Enum
from typing import Annotated, Optional, List
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Boolean, Date, MetaData,
    text, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class DatabaseConfig(BaseModel):
    url: PostgresDsn = "postgres://username:password@localhost:5432/your_database"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=naming_convention)


IntPk = Annotated[int, mapped_column(primary_key=True)]


# Correct Enum definitions
class TypeContent(str, Enum):
    IMAGE    = "IMAGE"
    VIDEO    = "VIDEO"
    DOCUMENT = "DOCUMENT"


class ProgressStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TestType(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class NotificationStatus(str, Enum):
    SENT = "sent"
    PENDING = "pending"


class UserRole(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    ADMIN = "ADMIN"

class Positions(Base):
    __tablename__ = 'positions'

    id: Mapped[IntPk]
    name: Mapped[str]
    description: Mapped[Optional[str]]
    adaptation_plans: Mapped[List["AdaptationPlan"]] = relationship(
        back_populates="position"
    )
    users: Mapped[List["User"]] = relationship(
        back_populates="position",
        cascade="all, delete"
    )

class AdaptationPlan(Base):
    __tablename__ = 'adaptation_plans'

    id: Mapped[IntPk]
    name: Mapped[str]
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    position_id: Mapped[int] = mapped_column(ForeignKey('positions.id', ondelete="CASCADE"))
    position: Mapped["Positions"] = relationship(back_populates="adaptation_plans")
    stages: Mapped[List["AdaptationStage"]] = relationship(
        "AdaptationStage",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class AdaptationStage(Base):
    __tablename__ = 'adaptation_stages'

    id: Mapped[IntPk]
    plan_id: Mapped[int] = mapped_column(ForeignKey("adaptation_plans.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    sequence_number: Mapped[Optional[int]]
    content_id: Mapped[Optional[int]] = mapped_column(ForeignKey("content_material.id"))
    test_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("test.id"), nullable=True
    )
    plan: Mapped["AdaptationPlan"] = relationship(back_populates="stages")
    content: Mapped[Optional["ContentMaterial"]] = relationship(back_populates="adaptation_stages", lazy="selectin")
    test: Mapped[Optional["Test"]] = relationship(
        "Test",
        back_populates="stages",
        foreign_keys=[test_id],
        lazy="selectin"
    )
    adaptation_progress: Mapped[List["UserAdaptationProgress"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan"
    )


class UserAdaptationProgress(Base):
    __tablename__ = 'user_adaptation_progress'

    id: Mapped[IntPk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    stage_id: Mapped[int] = mapped_column(ForeignKey("adaptation_stages.id"))
    status: Mapped[ProgressStatus] = mapped_column(SQLEnum(ProgressStatus), nullable=False)
    completion_date: Mapped[Optional[date]]
    notes: Mapped[Optional[str]]
    user: Mapped["User"] = relationship(back_populates="adaptation_progress")
    stage: Mapped["AdaptationStage"] = relationship(back_populates="adaptation_progress")

class ContentMaterial(Base):
    __tablename__ = 'content_material'

    id: Mapped[IntPk]
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]
    type: Mapped[TypeContent] = mapped_column(SQLEnum(TypeContent), nullable=False)
    content_url: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[Optional[datetime]]
    category: Mapped[Optional[str]]
    adaptation_stages: Mapped[List["AdaptationStage"]] = relationship(
        back_populates="content",
        cascade="all, delete"
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(
        back_populates="material",
        cascade="all, delete"
    )


class Department(Base):
    __tablename__ = 'department'

    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[Optional[str]]
    users: Mapped[List["User"]] = relationship(
        back_populates="department",
        cascade="all, delete"
    )


class Feedback(Base):
    __tablename__ = 'feedback'

    id: Mapped[IntPk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("content_material.id"))
    rating: Mapped[Optional[int]]
    comment: Mapped[Optional[str]]
    submitted_at: Mapped[Optional[datetime]]
    user: Mapped["User"] = relationship(back_populates="feedbacks")
    material: Mapped["ContentMaterial"] = relationship(back_populates="feedbacks")


class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[IntPk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    user: Mapped["User"] = relationship(back_populates="notifications")


class Test(Base):
    __tablename__ = 'test'

    id: Mapped[IntPk]
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]
    instructions: Mapped[Optional[str]]
    test_type: Mapped[Optional[TestType]] = mapped_column(SQLEnum(TestType))
    passing_score: Mapped[Optional[int]]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[Optional[datetime]]
    stages: Mapped[List[AdaptationStage]] = relationship(
        "AdaptationStage",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    questions: Mapped[List["TestQuestion"]] = relationship(
        back_populates="test",
        cascade="all, delete"
    )


class TestQuestion(Base):
    __tablename__ = 'test_question'

    id: Mapped[IntPk]
    test_id: Mapped[int] = mapped_column(ForeignKey("test.id"), nullable=False)
    question_text: Mapped[Optional[str]]
    question_type: Mapped[Optional[str]]
    sequence_number: Mapped[Optional[int]]
    image_path: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[Optional[datetime]]
    test: Mapped["Test"] = relationship(back_populates="questions")
    options: Mapped[List["TestOption"]] = relationship(
        back_populates="question",
        cascade="all, delete"
    )
    user_answers: Mapped[List["UserTestAnswer"]] = relationship(
        back_populates="question",
        cascade="all, delete"
    )


class TestOption(Base):
    __tablename__ = 'test_option'

    id: Mapped[IntPk]
    question_id: Mapped[int] = mapped_column(ForeignKey("test_question.id"), nullable=False)
    option_text: Mapped[Optional[str]]
    is_correct: Mapped[Optional[bool]]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    updated_at: Mapped[Optional[datetime]]
    question: Mapped["TestQuestion"] = relationship(back_populates="options")
    user_answers: Mapped[List["UserTestAnswer"]] = relationship(
        back_populates="option",
        cascade="all, delete"
    )


class UserTestAnswer(Base):
    __tablename__ = 'user_test_answer'

    id: Mapped[IntPk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("test_question.id"), nullable=False)
    answer_text: Mapped[Optional[str]]
    option_id: Mapped[Optional[int]] = mapped_column(ForeignKey("test_option.id"))
    submitted_at: Mapped[Optional[datetime]]
    user: Mapped["User"] = relationship(back_populates="test_answers")
    question: Mapped["TestQuestion"] = relationship(back_populates="user_answers")
    option: Mapped[Optional["TestOption"]] = relationship(back_populates="user_answers")


class User(Base):
    __tablename__ = 'user'

    id: Mapped[IntPk]
    telegram_id:    Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    first_name:     Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name:      Mapped[Optional[str]] = mapped_column(String, nullable=True)
    username:       Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    email:          Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    hashed_password:Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active:      Mapped[bool]           = mapped_column(Boolean, default=True, nullable=False)
    last_login:     Mapped[Optional[datetime]]
    role:           Mapped[UserRole]       = mapped_column(SQLEnum(UserRole), nullable=False)
    registration_date: Mapped[datetime]    = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
        nullable=False
    )
    department_id:  Mapped[Optional[int]]  = mapped_column(ForeignKey("department.id"), nullable=True)
    position_id:    Mapped[Optional[int]]  = mapped_column(ForeignKey("positions.id"),  nullable=True)

    # Relationships
    test_answers: Mapped[List["UserTestAnswer"]] = relationship(
        back_populates="user",
        cascade="all, delete"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user",
        cascade="all, delete"
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(
        back_populates="user",
        cascade="all, delete"
    )
    adaptation_progress: Mapped[List["UserAdaptationProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete"
    )
    department: Mapped["Department"] = relationship(back_populates="users")
    position: Mapped["Positions"] = relationship(back_populates="users")