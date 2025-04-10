import typing

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.books.schemas import BookCreateSchema, BookSchema
from core.api.books.services import BooksCRUDService
from core.database import get_session

router = APIRouter(prefix="/books", tags=["Books API"])


@router.get("/", response_model=list[BookSchema])
async def get_books(session: typing.Annotated[AsyncSession, Depends(get_session)]) -> JSONResponse:
    books_list = await BooksCRUDService().get_entities_list(session)
    return JSONResponse(books_list)


@router.post("/", response_model=BookSchema)
async def create_book(
    create_book_schema: BookCreateSchema, session: typing.Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    book = await BooksCRUDService().create_entity(create_book_schema, session)
    return JSONResponse(book, status_code=status.HTTP_201_CREATED)
