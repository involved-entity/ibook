import typing

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.reviews.schemas import ReviewCreateSchema, ReviewSchema, ReviewUpdateSchema
from core.api.reviews.services import ReviewsCRUDService
from core.api.users.dependencies import check_user_role
from core.database import get_session
from core.database.models.user import User, UserRole

router = APIRouter(prefix="/reviews", tags=["Reviews API"])


@router.get("/", response_model=list[ReviewSchema])
async def get_reviews(
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER, exclude_admin=True))],
) -> ORJSONResponse:
    reviews = await ReviewsCRUDService().get_entities_list(session, user)
    return ORJSONResponse(reviews)


@router.post("/", response_model=ReviewSchema)
async def create_review(
    create_review_schema: ReviewCreateSchema,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER))],
) -> ORJSONResponse:
    review = await ReviewsCRUDService().create_entity(create_review_schema, session, user)
    return ORJSONResponse(review)


@router.patch("/{review_id}", response_model=ReviewSchema)
async def update_review(
    review_id: int,
    update_review_schema: ReviewUpdateSchema,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER))],
) -> ORJSONResponse:
    review = await ReviewsCRUDService().update_entity(review_id, update_review_schema, session, user)
    return ORJSONResponse(review, status_code=status.HTTP_200_OK)


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER))],
) -> Response:
    await ReviewsCRUDService().remove_entity(review_id, session, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
