import typing

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.categories.schemas import CategorySchema
from core.api.categories.services import CategoriesCRUDService
from core.api.users.dependencies import check_user_role
from core.database import get_session
from core.database.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories API"])


@router.get("/", response_model=list[CategorySchema])
async def get_categories(session: typing.Annotated[AsyncSession, Depends(get_session)]) -> JSONResponse:
    categories = await CategoriesCRUDService().get_entities_list(session)
    return JSONResponse(categories)


@router.post("/", response_model=CategorySchema)
async def create_category(
    create_category_schema: CategorySchema,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role())],
) -> JSONResponse:
    category = await CategoriesCRUDService().create_entity(create_category_schema, session, user)
    return JSONResponse(category)
