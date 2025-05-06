import os, logging
from uuid import uuid4
from typing import Optional
import aiofiles

from fastapi import (
    APIRouter, Request, Depends,
    Form, File, UploadFile,
    HTTPException, status
)
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .templating import templates
from database.models import ContentMaterial, TypeContent
from db_helper import db_helper

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#  ─── Папка для загрузок ──────────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

# 1) Список материалов — теперь корректный template
@router.get("/content", response_class=HTMLResponse, name="list_content")
async def list_content(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ContentMaterial))
    materials = result.scalars().all()
    return templates.TemplateResponse("content_list.html", {
        "request": request,
        "materials": materials
    })

# 2) Форма создания
@router.get("/content/form", response_class=HTMLResponse, name="create_content_form")
async def create_content_form(request: Request):
    return templates.TemplateResponse("content_form.html", {
        "request": request,
        "material": None,
        "TypeContent": TypeContent,
        "errors": {}
    })

# 3) Форма редактирования
@router.get("/content/form/{material_id}", response_class=HTMLResponse, name="edit_content_form")
async def edit_content_form(request: Request, material_id: int, session: AsyncSession = Depends(get_session)):
    material = await session.get(ContentMaterial, material_id)
    if not material:
        raise HTTPException(404, "Material not found")
    return templates.TemplateResponse("content_form.html", {
        "request": request,
        "material": material,
        "TypeContent": TypeContent,
        "errors": {}
    })

# 4) Создать или обновить
@router.post("/content/", response_class=RedirectResponse, name="create_update_content")
async def create_update_content(
    material_id: Optional[int]  = Form(None),
    title: str                = Form(...),
    description: Optional[str] = Form(None),
    type: TypeContent         = Form(...),
    category: Optional[str]   = Form(None),
    file: Optional[UploadFile]= File(None),
    session: AsyncSession     = Depends(get_session)
):
    # 4.1) Создаём или достаём существующий
    if material_id:
        material = await session.get(ContentMaterial, material_id)
        if not material:
            raise HTTPException(404, "Material not found")
    else:
        material = ContentMaterial(title=title, type=type)
        session.add(material)
        await session.flush()

    # 4.2) Обновляем поля
    material.title       = title
    material.description = description
    material.type        = type
    material.category    = category

    # 4.3) Загружаем файл, если он пришёл
    if file:
        ext   = os.path.splitext(file.filename)[1]
        fname = f"{uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        async with aiofiles.open(fpath, "wb") as out:
            await out.write(await file.read())
        material.content_url = f"uploads/{fname}"

    await session.commit()
    # редирект на просмотр
    return RedirectResponse(f"/content/{material.id}", status_code=status.HTTP_303_SEE_OTHER)

# 5) Просмотр одного материала
@router.get("/content/{material_id}", response_class=HTMLResponse, name="content_view")
async def content_view(request: Request, material_id: int, session: AsyncSession = Depends(get_session)):
    material = await session.get(ContentMaterial, material_id)
    if not material:
        raise HTTPException(404, "Material not found")
    return templates.TemplateResponse("content_view.html", {
        "request": request,
        "current_material": material,
        "TypeContent": TypeContent
    })

# 6) Удаление
@router.post("/content/delete/{material_id}", name="delete_content")
async def delete_content(material_id: int, session: AsyncSession = Depends(get_session)):
    material = await session.get(ContentMaterial, material_id)
    if material:
        # удалить файл
        if material.content_url:
            p = os.path.join(UPLOAD_DIR, os.path.basename(material.content_url))
            if os.path.isfile(p):
                os.remove(p)
        await session.delete(material)
        await session.commit()
    return RedirectResponse("/content", status_code=status.HTTP_303_SEE_OTHER)
