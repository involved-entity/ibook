from fastapi import APIRouter

from core.api.addresses.views import router as addresses_router
from core.api.authentication.routers import router as auth_router
from core.api.books.views import router as books_router
from core.api.categories.views import router as categories_router
from core.api.orders.views import router as orders_router
from core.api.reviews.views import router as reviews_router

router = APIRouter(prefix="/api")
router.include_router(books_router)
router.include_router(categories_router)
router.include_router(auth_router)
router.include_router(addresses_router)
router.include_router(reviews_router)
router.include_router(orders_router)
