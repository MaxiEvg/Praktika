from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse

from .templating import templates


def register_error_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Обработка типовых HTTP-ошибок
        status = exc.status_code
        detail = exc.detail if isinstance(exc.detail, str) else ""

        if status == 400:
            return templates.TemplateResponse(
                "400.html", {"request": request, "error": detail}, status_code=400
            )
        elif status == 401:
            return templates.TemplateResponse(
                "401.html", {"request": request, "error": detail}, status_code=401
            )
        elif status == 403:
            return templates.TemplateResponse(
                "403.html", {"request": request, "error": detail}, status_code=403
            )
        elif status == 404:
            return templates.TemplateResponse(
                "404.html", {"request": request, "error": detail}, status_code=404
            )
        elif status >= 500:
            return templates.TemplateResponse(
                "500.html", {"request": request, "error": detail}, status_code=status
            )

        # Для прочих статусов — дефолтный обработчик
        return await app.default_exception_handler(request, exc)