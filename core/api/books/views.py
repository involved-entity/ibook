import typing

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.books.schemas import BookCreateSchema, BookSchema, BookUpdateSchema
from core.api.books.services import BooksCRUDService
from core.api.users.dependencies import check_user_role
from core.database import get_session
from core.database.models.user import User, UserRole

router = APIRouter(prefix="/books", tags=["Books API"])


@router.get("/", response_model=list[BookSchema])
async def get_books(session: typing.Annotated[AsyncSession, Depends(get_session)]) -> ORJSONResponse:
    books_list = await BooksCRUDService().get_entities_list(session)
    return ORJSONResponse(books_list)


@router.post("/", response_model=BookSchema)
async def create_book(
    create_book_schema: BookCreateSchema,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.SELLER))],
) -> ORJSONResponse:
    book = await BooksCRUDService().create_entity(create_book_schema, session, user)
    return ORJSONResponse(book, status_code=status.HTTP_201_CREATED)


@router.patch("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    update_book_schema: BookUpdateSchema,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.SELLER))],
) -> ORJSONResponse:
    book = await BooksCRUDService().update_entity(book_id, update_book_schema, session, user)
    return ORJSONResponse(book, status_code=status.HTTP_200_OK)


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.SELLER))],
) -> Response:
    await BooksCRUDService().remove_entity(book_id, session, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
