# crud/__init__.py
from .user import UserCRUD, AdminCRUD, UserCourseCRUD
from .test import TestCRUD, QuestionCRUD, AnswerCRUD, TestResultCRUD
from .course import CourseCRUD, MaterialCRUD, ProgressCRUD
from .file import FileCRUD

__all__ = [
    # User-related CRUD
    'UserCRUD',
    'AdminCRUD',
    'UserCourseCRUD',
    
    # Test-related CRUD
    'TestCRUD',
    'QuestionCRUD', 
    'AnswerCRUD',
    'TestResultCRUD',
    
    # Course-related CRUD
    'CourseCRUD',
    'MaterialCRUD',
    'ProgressCRUD',
    
    # File-related CRUD
    'FileCRUD'
]