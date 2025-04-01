# crud_content.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.content import ContentMaterial
from schemas.content import ContentMaterialCreate, ContentMaterialUpdate

def get_content_material(db: Session, material_id: int) -> Optional[ContentMaterial]:
    return db.query(ContentMaterial).filter(ContentMaterial.id == material_id).first()

def get_content_materials(db: Session, skip: int = 0, limit: int = 100) -> List[ContentMaterial]:
    return db.query(ContentMaterial).offset(skip).limit(limit).all()

def create_content_material(db: Session, material: ContentMaterialCreate) -> ContentMaterial:
    db_material = ContentMaterial(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def update_content_material(db: Session, material_id: int, material_update: ContentMaterialUpdate) -> Optional[ContentMaterial]:
    db_material = get_content_material(db, material_id)
    if db_material:
        for key, value in material_update.dict(exclude_unset=True).items():
            setattr(db_material, key, value)
        db.commit()
        db.refresh(db_material)
    return db_material

def delete_content_material(db: Session, material_id: int) -> Optional[ContentMaterial]:
    db_material = get_content_material(db, material_id)
    if db_material:
        db.delete(db_material)
        db.commit()
    return db_material
