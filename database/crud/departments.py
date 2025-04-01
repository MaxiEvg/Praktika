# crud_departments.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.departments import Department
from schemas.departments import DepartmentCreate, DepartmentUpdate

def get_department(db: Session, department_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100) -> List[Department]:
    return db.query(Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: DepartmentCreate) -> Department:
    db_department = Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(db: Session, department_id: int, department_update: DepartmentUpdate) -> Optional[Department]:
    db_department = get_department(db, department_id)
    if db_department:
        for key, value in department_update.dict(exclude_unset=True).items():
            setattr(db_department, key, value)
        db.commit()
        db.refresh(db_department)
    return db_department

def delete_department(db: Session, department_id: int) -> Optional[Department]:
    db_department = get_department(db, department_id)
    if db_department:
        db.delete(db_department)
        db.commit()
    return db_department
