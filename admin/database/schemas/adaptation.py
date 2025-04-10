# schemas/adaptation.py
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field

# План адаптации
class AdaptationPlanBase(BaseModel):
    name: str = Field(..., description="Название плана адаптации")
    description: Optional[str] = Field(None, description="Описание плана")
    position_id: int = Field(..., description="ID должности, к которой привязан план")
    is_individual: bool = Field(False, description="Флаг индивидуального плана")

class AdaptationPlanCreate(AdaptationPlanBase):
    pass

class AdaptationPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название плана адаптации")
    description: Optional[str] = Field(None, description="Описание плана")
    position_id: Optional[int] = Field(None, description="ID должности")
    is_individual: Optional[bool] = Field(None, description="Индивидуальный ли план")

class AdaptationPlanResponse(AdaptationPlanBase):
    id: int = Field(..., description="Уникальный идентификатор плана адаптации")
    created_at: Optional[datetime] = Field(None, description="Дата создания плана")
    
    class Config:
        orm_mode = True

# Этап адаптации
class AdaptationStageBase(BaseModel):
    plan_id: int = Field(..., description="ID плана адаптации")
    title: str = Field(..., description="Название этапа")
    description: Optional[str] = Field(None, description="Описание этапа")
    sequence_number: Optional[int] = Field(None, description="Порядковый номер этапа")
    deadline: Optional[date] = Field(None, description="Срок выполнения этапа")
    content_id: Optional[int] = Field(None, description="ID связанного обучающего материала")

class AdaptationStageCreate(AdaptationStageBase):
    pass

class AdaptationStageUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Название этапа")
    description: Optional[str] = Field(None, description="Описание этапа")
    sequence_number: Optional[int] = Field(None, description="Порядковый номер этапа")
    deadline: Optional[date] = Field(None, description="Срок выполнения этапа")
    content_id: Optional[int] = Field(None, description="ID связанного материала")

class AdaptationStageResponse(AdaptationStageBase):
    id: int = Field(..., description="Уникальный идентификатор этапа")
    
    class Config:
        orm_mode = True

# Прогресс адаптации пользователя
class UserAdaptationProgressBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    stage_id: int = Field(..., description="ID этапа адаптации")
    status: str = Field(..., description="Статус этапа (pending, completed, delayed)")
    completion_date: Optional[date] = Field(None, description="Дата завершения этапа")
    notes: Optional[str] = Field(None, description="Комментарии к этапу")

class UserAdaptationProgressCreate(UserAdaptationProgressBase):
    pass

class UserAdaptationProgressUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Новый статус этапа")
    completion_date: Optional[date] = Field(None, description="Дата завершения этапа")
    notes: Optional[str] = Field(None, description="Комментарии к этапу")

class UserAdaptationProgressResponse(UserAdaptationProgressBase):
    id: int = Field(..., description="Уникальный идентификатор записи о прогрессе")
    
    class Config:
        orm_mode = True
