# schemas/notifications.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NotificationBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя, которому отправлено уведомление")
    message: str = Field(..., description="Текст уведомления")
    status: str = Field(..., description="Статус уведомления (например, sent, pending)")

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    message: Optional[str] = Field(None, description="Текст уведомления")
    status: Optional[str] = Field(None, description="Статус уведомления")

class NotificationResponse(NotificationBase):
    id: int = Field(..., description="Уникальный идентификатор уведомления")
    created_at: Optional[datetime] = Field(None, description="Дата создания уведомления")
    
    class Config:
        orm_mode = True
