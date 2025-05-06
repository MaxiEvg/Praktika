from fastapi import APIRouter
from .pages import router as pages_router
from .auth import router as auth_router
from .tests import router as tests_router
from .content import router as content_router
from .adaptation import router as adaptation_router

router = APIRouter()

router.include_router(pages_router)
router.include_router(auth_router)
router.include_router(tests_router)
router.include_router(content_router)
router.include_router(adaptation_router)