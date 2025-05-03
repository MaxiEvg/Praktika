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

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("content_api.log")
    ]
)

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
logger.info(f"Upload directory set to: {UPLOAD_DIR}")

MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB
ALLOWED_TYPES = {
    TypeContent.IMAGE.value: ["image/jpeg", "image/png", "image/gif"],
    TypeContent.VIDEO.value: ["video/mp4", "video/quicktime"],
    TypeContent.DOCUMENT.value: ["application/pdf", "text/plain"]
}


async def get_session() -> AsyncSession:
    """Генератор сессий с логированием"""
    try:
        async with db_helper.session_factory() as session:
            logger.debug("Database session created")
            yield session
    except Exception as e:
        logger.error(f"Error creating database session: {str(e)}")
        raise


def validate_file(file: UploadFile, content_type: TypeContent):
    """Валидация файла с подробным логированием"""
    logger.info(f"Validating file: {file.filename} ({file.content_type}) for type {content_type}")

    if not file:
        logger.warning("Empty file received")
        return

    if content_type.value not in ALLOWED_TYPES:
        logger.error(f"Unsupported content type: {content_type.value}")
        raise HTTPException(
            status_code=400,
            detail="Unsupported content type"
        )

    if file.content_type not in ALLOWED_TYPES[content_type.value]:
        logger.error(f"Invalid file type {file.content_type} for {content_type.value}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for {content_type.value}"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    logger.debug(f"File size: {size} bytes")

    if size > MAX_FILE_SIZE:
        logger.error(f"File too large: {size} > {MAX_FILE_SIZE}")
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )


@router.get("/content", response_class=HTMLResponse)
async def list_content(
        request: Request,
        category: Optional[str] = Query(None),
        search: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)
):
    """Получение списка материалов с логированием параметров"""
    logger.info(f"Listing content. Category: {category}, Search: {search}")

    try:
        stmt = select(ContentMaterial).order_by(ContentMaterial.created_at.desc())

        if category:
            logger.debug(f"Applying category filter: {category}")
            stmt = stmt.where(ContentMaterial.category == category)

        if search:
            logger.debug(f"Applying search filter: {search}")
            stmt = stmt.where(
                ContentMaterial.title.ilike(f"%{search}%") |
                ContentMaterial.description.ilike(f"%{search}%")
            )

        result = await session.execute(stmt)
        materials = result.scalars().all()
        logger.info(f"Found {len(materials)} materials")

        return templates.TemplateResponse(
            "content_view.html",
            {
                "request": request,
                "materials": materials,
                "current_material": None,
                "TypeContent": TypeContent,
                "categories": await get_categories(session),
                "search_query": search,
                "selected_category": category
            }
        )
    except Exception as e:
        logger.error(f"Error listing content: {str(e)}", exc_info=True)
        raise


@router.get("/content/form", response_class=HTMLResponse)
async def create_content_form(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    """Форма создания нового материала"""
    logger.info("Rendering new content form")
    try:
        categories = await get_categories(session)
        logger.debug(f"Found {len(categories)} categories")
        return templates.TemplateResponse(
            "content_form.html",
            {
                "request": request,
                "TypeContent": TypeContent,
                "categories": categories,
                "material": None
            }
        )
    except Exception as e:
        logger.error(f"Error rendering form: {str(e)}", exc_info=True)
        raise


@router.get("/content/form/{material_id}", response_class=HTMLResponse)
async def edit_content_form(
        request: Request,
        material_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Форма редактирования материала"""
    logger.info(f"Editing material ID: {material_id}")
    try:
        material = await session.get(ContentMaterial, material_id)
        if not material:
            logger.warning(f"Material {material_id} not found")
            raise HTTPException(status_code=404, detail="Material not found")

        logger.debug(f"Editing material: {material.title} (ID: {material.id})")
        categories = await get_categories(session)
        return templates.TemplateResponse(
            "content_form.html",
            {
                "request": request,
                "TypeContent": TypeContent,
                "categories": categories,
                "material": material
            }
        )
    except Exception as e:
        logger.error(f"Error editing material {material_id}: {str(e)}", exc_info=True)
        raise


@router.get("/content/{material_id}", response_class=HTMLResponse)
async def content_view(
        request: Request,
        material_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Просмотр отдельного материала"""
    logger.info(f"Viewing material ID: {material_id}")
    try:
        material = await session.get(ContentMaterial, material_id)
        if not material:
            logger.warning(f"Material {material_id} not found")
            raise HTTPException(status_code=404, detail="Material not found")

        logger.debug(f"Showing material: {material.title}")
        return templates.TemplateResponse(
            "content_view.html",
            {
                "request": request,
                "current_material": material,
                "TypeContent": TypeContent,
                "categories": await get_categories(session)
            }
        )
    except Exception as e:
        logger.error(f"Error viewing material {material_id}: {str(e)}", exc_info=True)
        raise


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
    """Сохранение материала с детальным логированием"""
    logger.info(f"Starting save process. ID: {id}, Type: {type}, File: {file.filename if file else 'None'}")

    try:
        # Логирование входных данных
        logger.debug(f"Form data: id={id}, title={title}, type={type}, category={category}, "
                     f"description={description[:50]}..., file={file.filename if file else None}")

        # Валидация заголовка
        if not title.strip():
            logger.error("Empty title provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )

        if len(title) > 100:
            logger.error(f"Title too long: {len(title)} characters")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title too long (max 100 characters)"
            )

        # Валидация файла
        if id is None and file is None:
            logger.error("New material without file")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is required for new material"
            )

        if file:
            validate_file(file, type)

        # Поиск или создание материала
        if id:
            logger.info(f"Updating existing material ID: {id}")
            material = await session.get(ContentMaterial, id)
            if not material:
                logger.error(f"Material {id} not found for update")
                raise HTTPException(status_code=404, detail="Material not found")
        else:
            logger.info("Creating new material")
            material = ContentMaterial()
            session.add(material)
            await session.flush()
            logger.debug(f"New material ID generated: {material.id}")

        # Обновление полей
        material.title = title.strip()
        material.type = type
        material.category = category.strip() or None
        material.description = description.strip()
        logger.debug("Updated basic fields")

        # Обработка файла
        if file:
            logger.info("Processing file upload")
            if material.content_url:
                try:
                    file_name = material.content_url.split("/")[-1]
                    old_file = os.path.join(UPLOAD_DIR, file_name)
                    if os.path.isfile(old_file):
                        logger.debug(f"Deleting old file: {old_file}")
                        os.remove(old_file)
                except Exception as e:
                    logger.error(f"Error deleting old file: {str(e)}", exc_info=True)

            ext = os.path.splitext(file.filename)[1].lower()
            filename = f"{uuid4().hex}{ext}"
            dest = os.path.join(UPLOAD_DIR, filename)
            logger.debug(f"Saving file to: {dest}")

            try:
                async with aiofiles.open(dest, "wb") as out:
                    content = await file.read()
                    await out.write(content)
                material.content_url = f"uploads/{filename}"
                logger.info(f"File saved successfully: {filename}")
            except IOError as e:
                logger.error(f"File save error: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save file"
                )

        await session.commit()
        logger.info(f"Material saved successfully. ID: {material.id}")
        return RedirectResponse(url=f"/content/{material.id}", status_code=303)

    except HTTPException as he:
        logger.error(f"HTTP Error {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Critical error during save: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/content/delete/{material_id}")
async def delete_content(
        material_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Удаление материала с логированием"""
    logger.info(f"Deleting material ID: {material_id}")
    try:
        material = await session.get(ContentMaterial, material_id)
        if not material:
            logger.error(f"Material {material_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Material not found")

        # Удаление файла
        if material.content_url:
            try:
                file_name = material.content_url.split("/")[-1]
                file_path = os.path.join(UPLOAD_DIR, file_name)
                if os.path.isfile(file_path):
                    logger.debug(f"Deleting file: {file_path}")
                    os.remove(file_path)
                    logger.info("File deleted successfully")
                else:
                    logger.warning(f"File not found: {file_path}")
            except Exception as e:
                logger.error(f"File deletion error: {str(e)}", exc_info=True)

        # Удаление из БД
        await session.delete(material)
        await session.commit()
        logger.info(f"Material {material_id} deleted from database")
        return RedirectResponse(url="/content", status_code=303)

    except Exception as e:
        logger.error(f"Error deleting material {material_id}: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_categories(session: AsyncSession) -> List[str]:
    """Получение списка категорий с логированием"""
    logger.debug("Fetching categories")
    try:
        result = await session.execute(
            select(ContentMaterial.category)
            .distinct()
            .where(ContentMaterial.category.isnot(None))
        )
        categories = [row[0] for row in result.all()]
        logger.debug(f"Found {len(categories)} categories")
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        return []