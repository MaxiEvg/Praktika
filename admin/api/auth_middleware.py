from fastapi import Request, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from api.auth import SECRET_KEY, ALGORITHM  # ← абсолютный импорт

# пути, которые не требуют авторизации
WHITELIST = {"/welcome", "/login", "/register", "/token"}

def register_auth_middleware(app):
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        path = request.url.path
        if path in WHITELIST or path.startswith("/static"):
            return await call_next(request)

        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            jwt_token = token.split(" ", 1)[1]
            try:
                jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
                return await call_next(request)
            except JWTError:
                pass

        return RedirectResponse(url="/welcome", status_code=status.HTTP_303_SEE_OTHER)
