from datetime import date
from pydantic import BaseModel
from typing import List, Optional

# Базовые схемы для пользователей
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    
    class Config:
        orm_mode = True

# Схемы для администраторов
class AdminCreate(BaseModel):
    username: str
    password: str

# Схемы для тестов
class TestBase(BaseModel):
    name: str
    description: Optional[str] = None

class TestCreate(TestBase):
    pass

class TestResponse(TestBase):
    id: int
    date: date
    
    class Config:
        orm_mode = True

# Схемы для вопросов и ответов
class AnswerCreate(BaseModel):
    text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    text: str
    type: bool
    answers: List[AnswerCreate]

# Схемы для курсов
class CourseBase(BaseModel):
    name: str
    creator: str

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    date: date
    
    class Config:
        orm_mode = True

# Схемы для файлов
class FileCreate(BaseModel):
    name: str
    file_type: str

class FileResponse(FileCreate):
    id: int
    file_path: str
    
    class Config:
        orm_mode = True

# Схемы для результатов тестов
class TestResultCreate(BaseModel):
    user_id: int
    test_id: int
    score: int

class TestResultResponse(TestResultCreate):
    id: int
    date: date
    
    class Config:
        orm_mode = True