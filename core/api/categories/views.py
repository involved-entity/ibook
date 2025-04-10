import typing

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.categories.schemas import CategorySchema
from core.api.categories.services import CategoriesCRUDService
from core.database import get_session

router = APIRouter(prefix="/categories", tags=["Categories API"])


@router.get("/", response_model=list[CategorySchema])
async def get_categories(session: typing.Annotated[AsyncSession, Depends(get_session)]) -> JSONResponse:
    categories = await CategoriesCRUDService().get_entities_list(session)
    return JSONResponse(categories)
