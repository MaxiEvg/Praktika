# schemas/departments.py
from pydantic import BaseModel, Field
from typing import Optional

class DepartmentBase(BaseModel):
    name: str = Field(..., description="Название отдела")
    description: Optional[str] = Field(None, description="Описание отдела")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название отдела")
    description: Optional[str] = Field(None, description="Описание отдела")

class DepartmentResponse(DepartmentBase):
    id: int = Field(..., description="Уникальный идентификатор отдела")
    
    class Config:
        orm_mode = True
