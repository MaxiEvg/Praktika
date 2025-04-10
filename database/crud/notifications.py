# crud_notifications.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.notifications import Notification
from schemas.notifications import NotificationCreate, NotificationUpdate

def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Notification]:
    query = db.query(Notification)
    if user_id is not None:
        query = query.filter(Notification.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def update_notification(db: Session, notification_id: int, notification_update: NotificationUpdate) -> Optional[Notification]:
    db_notification = get_notification(db, notification_id)
    if db_notification:
        for key, value in notification_update.dict(exclude_unset=True).items():
            setattr(db_notification, key, value)
        db.commit()
        db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: int) -> Optional[Notification]:
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db.delete(db_notification)
        db.commit()
    return db_notification
