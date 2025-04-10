from fastapi import APIRouter

from core.api.books.views import router as books_router

router = APIRouter(prefix="/api")
router.include_router(books_router)
