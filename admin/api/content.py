import os
from uuid import uuid4
from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .templating import templates
from database.models import ContentMaterial, TypeContent
from db_helper import db_helper

router = APIRouter()
UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_session() -> AsyncSession:
    async for s in db_helper.session_getter():
        yield s

@router.get("/content")
async def list_content(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ContentMaterial))
    materials = result.scalars().all()
    return templates.TemplateResponse("content.html", {
        "request": request,
        "materials": materials,
        "material_to_edit": None,
        "TypeContent": TypeContent
    })

@router.get("/content/form/{material_id}")
async def edit_content(request: Request, material_id: int, session: AsyncSession = Depends(get_session)):
    content = await session.get(ContentMaterial, material_id)
    if not content:
        raise HTTPException(status_code=404, detail="Материал не найден")
    result = await session.execute(select(ContentMaterial))
    materials = result.scalars().all()
    return templates.TemplateResponse("content.html", {
        "request": request,
        "materials": materials,
        "material_to_edit": content,
        "TypeContent": TypeContent
    })

@router.post("/content/save")
async def save_content(
    request: Request,
    id: int = Form(None),
    title: str = Form(...),
    type: TypeContent = Form(...),
    category: str = Form(""),
    description: str = Form(""),
    file: UploadFile = File(None),
    session: AsyncSession = Depends(get_session)
):
    # Получаем или создаём запись
    if id:
        content = await session.get(ContentMaterial, id)
        if not content:
            content = ContentMaterial()
            session.add(content)
    else:
        content = ContentMaterial()
        session.add(content)

    content.title = title
    content.type = type
    content.category = category
    content.description = description

    # Если пришёл файл — сохраняем его и обновляем content_url
    if file:
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{uuid4().hex}{ext}"
        dest = os.path.join(UPLOAD_DIR, filename)
        with open(dest, "wb") as out:
            out.write(await file.read())
        content.content_url = f"uploads/{filename}"
    # Иначе, при создании без файла, оставляем предыдущий URL

    await session.commit()
    return RedirectResponse(url="/content", status_code=303)

@router.post("/content/delete/{material_id}")
async def delete_content(material_id: int, session: AsyncSession = Depends(get_session)):
    content = await session.get(ContentMaterial, material_id)
    if content:
        await session.delete(content)
        await session.commit()
    return RedirectResponse(url="/content", status_code=303)
