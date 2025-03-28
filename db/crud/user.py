from sqlalchemy.orm import Session
from models.user import User, Admin
from models.course import UserCourse
from db.schemas import UserCreate, AdminCreate, UserUpdate

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        db_user = User(username=user.username)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.get_user(user_id)
        if user:
            for key, value in user_data.dict().items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

class AdminCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_admin(self, admin: AdminCreate) -> Admin:
        db_admin = Admin(
            username=admin.username,
            password=admin.password
        )
        self.db.add(db_admin)
        self.db.commit()
        self.db.refresh(db_admin)
        return db_admin

    def get_admin_by_username(self, username: str) -> Admin:
        return self.db.query(Admin).filter(Admin.username == username).first()

class UserCourseCRUD:
    def __init__(self, db: Session):
        self.db = db

    def enroll_user(self, user_id: int, course_id: int) -> UserCourse:
        enrollment = UserCourse(
            id_user=user_id,
            id_course=course_id
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_user_courses(self, user_id: int):
        return self.db.query(UserCourse).filter(
            UserCourse.id_user == user_id
        ).all()