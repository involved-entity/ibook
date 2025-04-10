from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from fastapi_users import FastAPIUsers

from core.api.authentication.backend import auth_backend
from core.api.authentication.dependencies import get_user_manager
from core.api.authentication.schemas import UserCreate, UserRead
from core.database.models import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["Authentication API"], dependencies=[Depends(http_bearer)])

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_verify_router(UserRead))
router.include_router(fastapi_users.get_reset_password_router())
