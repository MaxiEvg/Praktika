# schemas/tests.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Схемы для теста
class TestBase(BaseModel):
    stage_id: int = Field(..., description="ID этапа адаптации, к которому привязан тест")
    instructions: Optional[str] = Field(None, description="Инструкции по прохождению теста")
    test_type: str = Field(..., description="Тип теста (open, closed)")
    passing_score: Optional[int] = Field(None, description="Проходной балл теста")

class TestCreate(TestBase):
    pass

class TestUpdate(BaseModel):
    instructions: Optional[str] = Field(None, description="Инструкции по тесту")
    test_type: Optional[str] = Field(None, description="Тип теста")
    passing_score: Optional[int] = Field(None, description="Проходной балл теста")

class TestResponse(TestBase):
    id: int = Field(..., description="Уникальный идентификатор теста")
    created_at: Optional[datetime] = Field(None, description="Дата создания теста")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления теста")
    
    class Config:
        orm_mode = True

# Схемы для вопросов теста
class TestQuestionBase(BaseModel):
    test_id: int = Field(..., description="ID теста")
    question_text: str = Field(..., description="Текст вопроса")
    question_type: str = Field(..., description="Тип вопроса (open, closed)")
    sequence_number: Optional[int] = Field(None, description="Порядковый номер вопроса")

class TestQuestionCreate(TestQuestionBase):
    pass

class TestQuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, description="Текст вопроса")
    question_type: Optional[str] = Field(None, description="Тип вопроса")
    sequence_number: Optional[int] = Field(None, description="Порядковый номер вопроса")

class TestQuestionResponse(TestQuestionBase):
    id: int = Field(..., description="Уникальный идентификатор вопроса")
    created_at: Optional[datetime] = Field(None, description="Дата создания вопроса")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления вопроса")
    
    class Config:
        orm_mode = True

# Схемы для вариантов ответов
class TestOptionBase(BaseModel):
    question_id: int = Field(..., description="ID вопроса")
    option_text: str = Field(..., description="Текст варианта ответа")
    is_correct: bool = Field(..., description="Является ли ответ правильным")

class TestOptionCreate(TestOptionBase):
    pass

class TestOptionUpdate(BaseModel):
    option_text: Optional[str] = Field(None, description="Текст варианта ответа")
    is_correct: Optional[bool] = Field(None, description="Является ли ответ правильным")

class TestOptionResponse(TestOptionBase):
    id: int = Field(..., description="Уникальный идентификатор варианта ответа")
    created_at: Optional[datetime] = Field(None, description="Дата создания варианта ответа")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления варианта ответа")
    
    class Config:
        orm_mode = True

# Схемы для ответов пользователей на тесты
class UserTestAnswerBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    question_id: int = Field(..., description="ID вопроса")
    answer_text: Optional[str] = Field(None, description="Ответ пользователя (для открытых вопросов)")
    option_id: Optional[int] = Field(None, description="ID выбранного варианта (для закрытых вопросов)")

class UserTestAnswerCreate(UserTestAnswerBase):
    pass

class UserTestAnswerUpdate(BaseModel):
    answer_text: Optional[str] = Field(None, description="Ответ пользователя")
    option_id: Optional[int] = Field(None, description="ID выбранного варианта")

class UserTestAnswerResponse(UserTestAnswerBase):
    id: int = Field(..., description="Уникальный идентификатор ответа пользователя")
    submitted_at: Optional[datetime] = Field(None, description="Дата и время ответа")
    
    class Config:
        orm_mode = True
