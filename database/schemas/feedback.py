# schemas/feedback.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FeedbackBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    material_id: int = Field(..., description="ID обучающего материала")
    rating: int = Field(..., description="Оценка (например, от 1 до 5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Текст отзыва")

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, description="Оценка (от 1 до 5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Текст отзыва")

class FeedbackResponse(FeedbackBase):
    id: int = Field(..., description="Уникальный идентификатор отзыва")
    submitted_at: Optional[datetime] = Field(None, description="Дата и время отзыва")
    
    class Config:
        orm_mode = True
