# schemas/users.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: str = Field(..., description="Имя пользователя")
    role: Optional[str] = Field(None, description="Роль пользователя (employee, HR и т.д.)")
    registration_date: Optional[date] = Field(None, description="Дата регистрации")
    department_id: Optional[int] = Field(None, description="ID отдела")
    position_id: Optional[int] = Field(None, description="ID должности")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    telegram_id: Optional[str] = Field(None, description="Telegram ID пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя")
    role: Optional[str] = Field(None, description="Роль пользователя")
    registration_date: Optional[date] = Field(None, description="Дата регистрации")
    department_id: Optional[int] = Field(None, description="ID отдела")
    position_id: Optional[int] = Field(None, description="ID должности")

class UserResponse(UserBase):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    
    class Config:
        orm_mode = True
