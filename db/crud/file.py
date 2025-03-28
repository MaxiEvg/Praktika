from sqlalchemy.orm import Session
from models.file import File
from db.schemas import FileCreate

class FileCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_file(self, file: FileCreate) -> File:
        db_file = File(**file.dict())
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def get_file(self, file_id: int) -> File:
        return self.db.query(File).filter(File.id == file_id).first()

    def delete_file(self, file_id: int) -> bool:
        file = self.get_file(file_id)
        if file:
            self.db.delete(file)
            self.db.commit()
            return True
        return False