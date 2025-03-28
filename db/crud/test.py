from sqlalchemy.orm import Session
from models.test import Test, Question, Answer, UserAnswer, TestResult
from db.schemas import TestCreate, QuestionCreate, AnswerCreate

class TestCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_test(self, test: TestCreate) -> Test:
        db_test = Test(**test.dict())
        self.db.add(db_test)
        self.db.commit()
        self.db.refresh(db_test)
        return db_test

    def get_test(self, test_id: int) -> Test:
        return self.db.query(Test).filter(Test.id == test_id).first()

class QuestionCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_question(self, question: QuestionCreate) -> Question:
        db_question = Question(**question.dict())
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        return db_question

    def get_test_questions(self, test_id: int):
        return self.db.query(Question).filter(
            Question.id_test == test_id
        ).all()

class AnswerCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_answer(self, answer: AnswerCreate) -> Answer:
        db_answer = Answer(**answer.dict())
        self.db.add(db_answer)
        self.db.commit()
        self.db.refresh(db_answer)
        return db_answer

    def get_correct_answers(self, question_id: int):
        return self.db.query(Answer).filter(
            Answer.id_question == question_id,
            Answer.is_correct == True
        ).all()

class TestResultCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_result(self, user_id: int, test_id: int, score: int) -> TestResult:
        result = TestResult(
            id_user=user_id,
            id_test=test_id,
            score=score
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_user_results(self, user_id: int):
        return self.db.query(TestResult).filter(
            TestResult.id_user == user_id
        ).all()