from sqlalchemy.orm import Session
from models.course import Course, CourseMaterial, CourseMaterialFile, Progress
from db.schemas import CourseCreate, MaterialCreate

class CourseCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_course(self, course: CourseCreate) -> Course:
        db_course = Course(**course.dict())
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course

    def get_course(self, course_id: int) -> Course:
        return self.db.query(Course).filter(Course.id == course_id).first()

class MaterialCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_material(self, material: MaterialCreate) -> CourseMaterial:
        db_material = CourseMaterial(**material.dict())
        self.db.add(db_material)
        self.db.commit()
        self.db.refresh(db_material)
        return db_material

    def get_course_materials(self, course_id: int):
        return self.db.query(CourseMaterial).filter(
            CourseMaterial.id_course == course_id
        ).order_by(CourseMaterial.number).all()

class ProgressCRUD:
    def __init__(self, db: Session):
        self.db = db

    def update_progress(self, user_id: int, material_id: int) -> Progress:
        progress = Progress(
            id_user=user_id,
            id_course_material=material_id,
            is_flag=True
        )
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_user_progress(self, user_id: int):
        return self.db.query(Progress).filter(
            Progress.id_user == user_id
        ).all()