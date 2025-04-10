from fastapi import APIRouter

from core.api.authentication.routers import router as auth_router
from core.api.books.views import router as books_router
from core.api.categories.views import router as categories_router

router = APIRouter(prefix="/api")
router.include_router(books_router)
router.include_router(categories_router)
router.include_router(auth_router)
