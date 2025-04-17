from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Dict, Any
from .templating import templates

router = APIRouter()

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


@router.get("/tests", response_class=HTMLResponse)
async def list_tests(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tests": list(tests_db.values())
    })


@router.get("/tests/create", response_class=HTMLResponse)
async def create_test_get(request: Request):
    return templates.TemplateResponse("create_test.html", {"request": request})


@router.post("/tests/create")
async def create_test_post(
        title: str = Form(...),
        description: str = Form(...),
        questions: List[Dict[str, Any]] = Form(...)
):
    return RedirectResponse(url="/tests", status_code=303)


@router.get("/tests/{test_id}", response_class=HTMLResponse)
async def take_test(request: Request, test_id: int):
    test = tests_db.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return templates.TemplateResponse("take_test.html", {
        "request": request,
        "test": test
    })


@router.post("/tests/{test_id}/submit")
async def submit_test(test_id: int, answers: Dict[str, Any] = Form(...)):
    test = tests_db.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return RedirectResponse(url=f"/tests/{test_id}/results", status_code=303)


@router.get("/tests/{test_id}/results", response_class=HTMLResponse)
async def test_results(request: Request, test_id: int):
    test = tests_db.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

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