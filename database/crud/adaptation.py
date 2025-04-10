# crud_adaptation.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.adaptation import AdaptationPlan, AdaptationStage, UserAdaptationProgress
from schemas.adaptation import (
    AdaptationPlanCreate, AdaptationPlanUpdate,
    AdaptationStageCreate, AdaptationStageUpdate,
    UserAdaptationProgressCreate, UserAdaptationProgressUpdate
)

# CRUD для плана адаптации
def get_adaptation_plan(db: Session, plan_id: int) -> Optional[AdaptationPlan]:
    return db.query(AdaptationPlan).filter(AdaptationPlan.id == plan_id).first()

def get_adaptation_plans(db: Session, skip: int = 0, limit: int = 100) -> List[AdaptationPlan]:
    return db.query(AdaptationPlan).offset(skip).limit(limit).all()

def create_adaptation_plan(db: Session, plan: AdaptationPlanCreate) -> AdaptationPlan:
    db_plan = AdaptationPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_adaptation_plan(db: Session, plan_id: int, plan_update: AdaptationPlanUpdate) -> Optional[AdaptationPlan]:
    db_plan = get_adaptation_plan(db, plan_id)
    if db_plan:
        for key, value in plan_update.dict(exclude_unset=True).items():
            setattr(db_plan, key, value)
        db.commit()
        db.refresh(db_plan)
    return db_plan

def delete_adaptation_plan(db: Session, plan_id: int) -> Optional[AdaptationPlan]:
    db_plan = get_adaptation_plan(db, plan_id)
    if db_plan:
        db.delete(db_plan)
        db.commit()
    return db_plan

# CRUD для этапа адаптации
def get_adaptation_stage(db: Session, stage_id: int) -> Optional[AdaptationStage]:
    return db.query(AdaptationStage).filter(AdaptationStage.id == stage_id).first()

def get_adaptation_stages(db: Session, plan_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[AdaptationStage]:
    query = db.query(AdaptationStage)
    if plan_id is not None:
        query = query.filter(AdaptationStage.plan_id == plan_id)
    return query.offset(skip).limit(limit).all()

def create_adaptation_stage(db: Session, stage: AdaptationStageCreate) -> AdaptationStage:
    db_stage = AdaptationStage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage

def update_adaptation_stage(db: Session, stage_id: int, stage_update: AdaptationStageUpdate) -> Optional[AdaptationStage]:
    db_stage = get_adaptation_stage(db, stage_id)
    if db_stage:
        for key, value in stage_update.dict(exclude_unset=True).items():
            setattr(db_stage, key, value)
        db.commit()
        db.refresh(db_stage)
    return db_stage

def delete_adaptation_stage(db: Session, stage_id: int) -> Optional[AdaptationStage]:
    db_stage = get_adaptation_stage(db, stage_id)
    if db_stage:
        db.delete(db_stage)
        db.commit()
    return db_stage

# CRUD для прогресса адаптации пользователя
def get_user_progress(db: Session, progress_id: int) -> Optional[UserAdaptationProgress]:
    return db.query(UserAdaptationProgress).filter(UserAdaptationProgress.id == progress_id).first()

def get_user_progress_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[UserAdaptationProgress]:
    return db.query(UserAdaptationProgress).filter(UserAdaptationProgress.user_id == user_id).offset(skip).limit(limit).all()

def create_user_progress(db: Session, progress: UserAdaptationProgressCreate) -> UserAdaptationProgress:
    db_progress = UserAdaptationProgress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def update_user_progress(db: Session, progress_id: int, progress_update: UserAdaptationProgressUpdate) -> Optional[UserAdaptationProgress]:
    db_progress = get_user_progress(db, progress_id)
    if db_progress:
        for key, value in progress_update.dict(exclude_unset=True).items():
            setattr(db_progress, key, value)
        db.commit()
        db.refresh(db_progress)
    return db_progress

def delete_user_progress(db: Session, progress_id: int) -> Optional[UserAdaptationProgress]:
    db_progress = get_user_progress(db, progress_id)
    if db_progress:
        db.delete(db_progress)
        db.commit()
    return db_progress
