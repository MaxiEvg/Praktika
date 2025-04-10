# schemas/positions.py
from pydantic import BaseModel, Field
from typing import Optional

class PositionBase(BaseModel):
    title: str = Field(..., description="Название должности")
    description: Optional[str] = Field(None, description="Описание должности")

class PositionCreate(PositionBase):
    pass

class PositionUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Название должности")
    description: Optional[str] = Field(None, description="Описание должности")

class PositionResponse(PositionBase):
    id: int = Field(..., description="Уникальный идентификатор должности")
    
    class Config:
        orm_mode = True
