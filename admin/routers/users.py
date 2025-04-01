from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.session import async_session
from database.crud.user import get_user, get_users, create_user, update_user, delete_user
from database.schemas.users import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

# Зависимость для получения сессии БД
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = await get_users(db, skip, limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_existing_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_existing_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user 