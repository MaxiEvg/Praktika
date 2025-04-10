# schemas/content.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ContentMaterialBase(BaseModel):
    title: str = Field(..., description="Название материала")
    description: Optional[str] = Field(None, description="Описание материала")
    type: str = Field(..., description="Тип материала (article, video и т.д.)")
    content_url: str = Field(..., description="Ссылка или путь к материалу")
    category: Optional[str] = Field(None, description="Категория материала")

class ContentMaterialCreate(ContentMaterialBase):
    pass

class ContentMaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Название материала")
    description: Optional[str] = Field(None, description="Описание материала")
    type: Optional[str] = Field(None, description="Тип материала")
    content_url: Optional[str] = Field(None, description="Ссылка или путь к материалу")
    category: Optional[str] = Field(None, description="Категория материала")

class ContentMaterialResponse(ContentMaterialBase):
    id: int = Field(..., description="Уникальный идентификатор материала")
    created_at: Optional[datetime] = Field(None, description="Дата создания материала")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления материала")
    
    class Config:
        orm_mode = True
