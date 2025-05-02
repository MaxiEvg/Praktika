# api/content.py
import os
import logging
from uuid import uuid4
from typing import Optional, List
import aiofiles

from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    Query,
    status
)
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .templating import templates
from database.models import ContentMaterial, TypeContent
from db_helper import db_helper

router = APIRouter()
logger = logging.getLogger(__name__)
UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB
ALLOWED_TYPES = {
    TypeContent.IMAGE.value: ["image/jpeg", "image/png", "image/gif"],
    TypeContent.VIDEO.value: ["video/mp4", "video/quicktime"],
    TypeContent.DOCUMENT.value: ["application/pdf", "text/plain"]
}


async def get_session() -> AsyncSession:
    async for s in db_helper.session_getter():
        yield s


def validate_file(file: UploadFile, content_type: TypeContent):
    if not file:
        return

    if content_type.value not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported content type"
        )

    if file.content_type not in ALLOWED_TYPES[content_type.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for {content_type.value}"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )


@router.get("/content/form/{material_id}", response_class=HTMLResponse)
async def edit_content_form(
        request: Request,
        material_id: int,
        session: AsyncSession = Depends(get_session)
):
    material = await session.get(ContentMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return templates.TemplateResponse(
        "content_form.html",
        {
            "request": request,
            "TypeContent": TypeContent,
            "categories": await get_categories(session),
            "material": material
        }
    )


@router.get("/content/form", response_class=HTMLResponse)
async def create_content_form(request: Request):
    return templates.TemplateResponse(
        "content_form.html",
        {
            "request": request,
            "TypeContent": TypeContent,
            "categories": [],
            "material": None
        }
    )


@router.get("/content/{material_id}", response_class=HTMLResponse)
async def content_view(
        request: Request,
        material_id: int,
        session: AsyncSession = Depends(get_session)
):
    material = await session.get(ContentMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return templates.TemplateResponse(
        "content_view.html",
        {
            "request": request,
            "current_material": material,
            "TypeContent": TypeContent,
            "categories": await get_categories(session)
        }
    )


@router.post("/content/save")
async def save_content(
        request: Request,
        id: Optional[int] = Form(None),
        title: str = Form(...),
        type: TypeContent = Form(...),
        category: str = Form(""),
        description: str = Form(""),
        file: UploadFile = File(None),
        session: AsyncSession = Depends(get_session)
):
    try:
        logger.info(f"Starting save process. ID: {id}, Title: {title}")

        if file:
            logger.debug(f"File received: {file.filename}, Type: {file.content_type}")
            validate_file(file, type)

        # Поиск или создание материала
        if id:
            logger.debug(f"Editing existing material ID: {id}")
            material = await session.get(ContentMaterial, id)
            if not material:
                logger.error(f"Material not found for ID: {id}")
                raise HTTPException(status_code=404, detail="Material not found")
        else:
            logger.debug("Creating new material")
            material = ContentMaterial()
            session.add(material)

        # Обновление полей
        material.title = title
        material.type = type
        material.category = category
        material.description = description.strip()

        if file:
            logger.debug("Processing file upload")
            # Удаление старого файла
            if material.content_url:
                old_file = os.path.join(UPLOAD_DIR, material.content_url.split("/")[-1])
                if os.path.exists(old_file):
                    logger.debug(f"Removing old file: {old_file}")
                    os.remove(old_file)

            # Генерация нового имени файла
            ext = os.path.splitext(file.filename)[1].lower()
            filename = f"{uuid4().hex}{ext}"
            dest = os.path.join(UPLOAD_DIR, filename)

            # Сохранение файла
            logger.debug(f"Saving file to: {dest}")
            async with aiofiles.open(dest, "wb") as out:
                content = await file.read()
                await out.write(content)

            material.content_url = f"uploads/{filename}"

        # Валидация обязательных полей
        if not material.title:
            logger.error("Title is required")
            raise HTTPException(status_code=400, detail="Title is required")

        if not material.type:
            logger.error("Type is required")
            raise HTTPException(status_code=400, detail="Type is required")

        await session.commit()
        await session.refresh(material)
        logger.info(f"Material saved successfully. ID: {material.id}")
        return RedirectResponse(url=f"/content/{material.id}", status_code=303)

    except HTTPException as he:
        logger.error(f"HTTP Error: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please check logs."
        )


@router.post("/content/delete/{material_id}")
async def delete_content(
        material_id: int,
        session: AsyncSession = Depends(get_session)
):
    material = await session.get(ContentMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        if material.content_url:
            file_path = os.path.join(UPLOAD_DIR, material.content_url.split("/")[-1])
            if os.path.exists(file_path):
                os.remove(file_path)

        await session.delete(material)
        await session.commit()
        return RedirectResponse(url="/content", status_code=303)

    except Exception as e:
        logger.error(f"Error deleting content: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/content", response_class=HTMLResponse)
async def list_content(
        request: Request,
        category: Optional[str] = Query(None),
        search: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)
):
    """
    Главная страница контента с фильтрацией и поиском
    """
    try:
        # Базовый запрос
        stmt = select(ContentMaterial).order_by(ContentMaterial.created_at.desc())

        # Применяем фильтры
        if category:
            stmt = stmt.where(ContentMaterial.category == category)

        if search:
            stmt = stmt.where(
                ContentMaterial.title.ilike(f"%{search}%") |
                ContentMaterial.description.ilike(f"%{search}%")
            )

        # Выполняем запрос
        result = await session.execute(stmt)
        materials = result.scalars().all()

        # Получаем список категорий для фильтров
        categories = await get_categories(session)

        return templates.TemplateResponse(
            "content_view.html",
            {
                "request": request,
                "materials": materials,
                "current_material": None,
                "TypeContent": TypeContent,
                "categories": categories,
                "search_query": search,
                "selected_category": category
            }
        )

    except Exception as e:
        logger.error(f"Error loading content list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

async def get_categories(session: AsyncSession) -> List[str]:
    result = await session.execute(
        select(ContentMaterial.category)
        .distinct()
        .where(ContentMaterial.category.isnot(None))
    )
    return [row[0] for row in result.all()]