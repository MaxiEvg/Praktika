from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from .templating import templates  # ← относительный импорт!

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

# ← новый эндпоинт под ссылку из навигации
@router.get("/create_test", response_class=HTMLResponse)
async def create_test(request: Request):
    return templates.TemplateResponse("create_test.html", {"request": request})
