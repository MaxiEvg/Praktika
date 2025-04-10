# crud_positions.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.positions import Position
from schemas.positions import PositionCreate, PositionUpdate

def get_position(db: Session, position_id: int) -> Optional[Position]:
    return db.query(Position).filter(Position.id == position_id).first()

def get_positions(db: Session, skip: int = 0, limit: int = 100) -> List[Position]:
    return db.query(Position).offset(skip).limit(limit).all()

def create_position(db: Session, position: PositionCreate) -> Position:
    db_position = Position(**position.dict())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def update_position(db: Session, position_id: int, position_update: PositionUpdate) -> Optional[Position]:
    db_position = get_position(db, position_id)
    if db_position:
        for key, value in position_update.dict(exclude_unset=True).items():
            setattr(db_position, key, value)
        db.commit()
        db.refresh(db_position)
    return db_position

def delete_position(db: Session, position_id: int) -> Optional[Position]:
    db_position = get_position(db, position_id)
    if db_position:
        db.delete(db_position)
        db.commit()
    return db_position
