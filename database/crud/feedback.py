# crud_feedback.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate

def get_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def get_feedbacks(db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
    return db.query(Feedback).offset(skip).limit(limit).all()

def create_feedback(db: Session, feedback: FeedbackCreate) -> Feedback:
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def update_feedback(db: Session, feedback_id: int, feedback_update: FeedbackUpdate) -> Optional[Feedback]:
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback:
        for key, value in feedback_update.dict(exclude_unset=True).items():
            setattr(db_feedback, key, value)
        db.commit()
        db.refresh(db_feedback)
    return db_feedback

def delete_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback:
        db.delete(db_feedback)
        db.commit()
    return db_feedback
