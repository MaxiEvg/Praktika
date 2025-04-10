# crud_tests.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.tests import Test, TestQuestion, TestOption, UserTestAnswer
from schemas.tests import (
    TestCreate, TestUpdate,
    TestQuestionCreate, TestQuestionUpdate,
    TestOptionCreate, TestOptionUpdate,
    UserTestAnswerCreate, UserTestAnswerUpdate
)

# CRUD для теста
def get_test(db: Session, test_id: int) -> Optional[Test]:
    return db.query(Test).filter(Test.id == test_id).first()

def get_tests(db: Session, skip: int = 0, limit: int = 100) -> List[Test]:
    return db.query(Test).offset(skip).limit(limit).all()

def create_test(db: Session, test: TestCreate) -> Test:
    db_test = Test(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def update_test(db: Session, test_id: int, test_update: TestUpdate) -> Optional[Test]:
    db_test = get_test(db, test_id)
    if db_test:
        for key, value in test_update.dict(exclude_unset=True).items():
            setattr(db_test, key, value)
        db.commit()
        db.refresh(db_test)
    return db_test

def delete_test(db: Session, test_id: int) -> Optional[Test]:
    db_test = get_test(db, test_id)
    if db_test:
        db.delete(db_test)
        db.commit()
    return db_test

# CRUD для вопросов теста
def get_test_question(db: Session, question_id: int) -> Optional[TestQuestion]:
    return db.query(TestQuestion).filter(TestQuestion.id == question_id).first()

def get_test_questions(db: Session, test_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[TestQuestion]:
    query = db.query(TestQuestion)
    if test_id is not None:
        query = query.filter(TestQuestion.test_id == test_id)
    return query.offset(skip).limit(limit).all()

def create_test_question(db: Session, question: TestQuestionCreate) -> TestQuestion:
    db_question = TestQuestion(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def update_test_question(db: Session, question_id: int, question_update: TestQuestionUpdate) -> Optional[TestQuestion]:
    db_question = get_test_question(db, question_id)
    if db_question:
        for key, value in question_update.dict(exclude_unset=True).items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_test_question(db: Session, question_id: int) -> Optional[TestQuestion]:
    db_question = get_test_question(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
    return db_question

# CRUD для вариантов ответов
def get_test_option(db: Session, option_id: int) -> Optional[TestOption]:
    return db.query(TestOption).filter(TestOption.id == option_id).first()

def get_test_options(db: Session, question_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[TestOption]:
    query = db.query(TestOption)
    if question_id is not None:
        query = query.filter(TestOption.question_id == question_id)
    return query.offset(skip).limit(limit).all()

def create_test_option(db: Session, option: TestOptionCreate) -> TestOption:
    db_option = TestOption(**option.dict())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

def update_test_option(db: Session, option_id: int, option_update: TestOptionUpdate) -> Optional[TestOption]:
    db_option = get_test_option(db, option_id)
    if db_option:
        for key, value in option_update.dict(exclude_unset=True).items():
            setattr(db_option, key, value)
        db.commit()
        db.refresh(db_option)
    return db_option

def delete_test_option(db: Session, option_id: int) -> Optional[TestOption]:
    db_option = get_test_option(db, option_id)
    if db_option:
        db.delete(db_option)
        db.commit()
    return db_option

# CRUD для ответов пользователей на тесты
def get_user_test_answer(db: Session, answer_id: int) -> Optional[UserTestAnswer]:
    return db.query(UserTestAnswer).filter(UserTestAnswer.id == answer_id).first()

def get_user_test_answers(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[UserTestAnswer]:
    query = db.query(UserTestAnswer)
    if user_id is not None:
        query = query.filter(UserTestAnswer.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_user_test_answer(db: Session, answer: UserTestAnswerCreate) -> UserTestAnswer:
    db_answer = UserTestAnswer(**answer.dict())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

def update_user_test_answer(db: Session, answer_id: int, answer_update: UserTestAnswerUpdate) -> Optional[UserTestAnswer]:
    db_answer = get_user_test_answer(db, answer_id)
    if db_answer:
        for key, value in answer_update.dict(exclude_unset=True).items():
            setattr(db_answer, key, value)
        db.commit()
        db.refresh(db_answer)
    return db_answer

def delete_user_test_answer(db: Session, answer_id: int) -> Optional[UserTestAnswer]:
    db_answer = get_user_test_answer(db, answer_id)
    if db_answer:
        db.delete(db_answer)
        db.commit()
    return db_answer
