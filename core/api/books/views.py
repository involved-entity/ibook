import typing

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.books.schemas import BookSchema
from core.api.books.services import get_books_list
from core.database import get_session

router = APIRouter(prefix="/books", tags=["Books API"])


@router.get("/", response_model=BookSchema)
async def get_books(session: typing.Annotated[AsyncSession, Depends(get_session)]) -> JSONResponse:
    books_list = await get_books_list(session)
    return JSONResponse(books_list)
