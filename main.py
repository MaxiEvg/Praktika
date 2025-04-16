import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
import os
from typing import List, Dict, Any
from pydantic import BaseModel

app = FastAPI(
    title="Система адаптации сотрудников",
    description="API для управления процессом адаптации новых сотрудников",
    version="0.1.0"
)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Mount static files
static_dir = os.path.join(current_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Mock data for tests
tests_db = {
    1: {
        "id": 1,
        "title": "Тест по Python",
        "description": "Базовый тест по Python",
        "questions": [
            {
                "id": 1,
                "text": "Что такое Python?",
                "type": "single",
                "answers": [
                    {"id": 1, "text": "Язык программирования", "correct": True},
                    {"id": 2, "text": "Змея", "correct": False},
                    {"id": 3, "text": "Город", "correct": False}
                ]
            }
        ]
    }
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        return RedirectResponse(url="/dashboard", status_code=303)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return RedirectResponse(url="/login", status_code=303)

@app.get("/tests", response_class=HTMLResponse)
async def list_tests(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tests": list(tests_db.values())
    })

@app.get("/tests/create", response_class=HTMLResponse)
async def create_test_get(request: Request):
    return templates.TemplateResponse("create_test.html", {"request": request})

@app.post("/tests/create")
async def create_test_post(
    title: str = Form(...),
    description: str = Form(...),
    questions: List[Dict[str, Any]] = Form(...)
):
    # TODO: Save test to database
    return RedirectResponse(url="/tests", status_code=303)

@app.get("/tests/{test_id}", response_class=HTMLResponse)
async def take_test(request: Request, test_id: int):
    test = tests_db.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return templates.TemplateResponse("take_test.html", {
        "request": request,
        "test": test
    })

@app.post("/tests/{test_id}/submit")
async def submit_test(test_id: int, answers: Dict[str, Any] = Form(...)):
    test = tests_db.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # TODO: Process answers and save results
    return RedirectResponse(url=f"/tests/{test_id}/results", status_code=303)

@app.get("/tests/{test_id}/results", response_class=HTMLResponse)
async def test_results(request: Request, test_id: int):
    test = tests_db.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Mock results
    results = {
        "test": test,
        "correct_answers": 1,
        "total_questions": 1,
        "questions": [
            {
                "id": 1,
                "text": "Что такое Python?",
                "is_correct": True,
                "user_answer": "Язык программирования",
                "correct_answer": "Язык программирования",
                "explanation": "Python - это высокоуровневый язык программирования"
            }
        ]
    }
    
    return templates.TemplateResponse("test_results.html", {
        "request": request,
        **results
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 