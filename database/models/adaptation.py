# adaptation.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date
from .base import Base

class AdaptationPlan(Base):
    __tablename__ = 'adaptation_plan'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    position_id = Column(Integer, ForeignKey('position.id'))
    created_at = Column(DateTime)
    is_individual = Column(Boolean, default=False)

class AdaptationStage(Base):
    __tablename__ = 'adaptation_stage'
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('adaptation_plan.id'))
    title = Column(String, nullable=False)
    description = Column(String)
    sequence_number = Column(Integer)
    deadline = Column(Date)
    content_id = Column(Integer, ForeignKey('content_material.id'))

class UserAdaptationProgress(Base):
    __tablename__ = 'user_adaptation_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    stage_id = Column(Integer, ForeignKey('adaptation_stage.id'))
    status = Column(String)  # Например: 'pending', 'completed', 'delayed'
    completion_date = Column(Date)
    notes = Column(String)
