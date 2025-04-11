import typing

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.addresses.schemas import AddressSchema, AddressSchemaCreate
from core.api.addresses.services import AddressesCRUDService
from core.api.users.dependencies import check_user_role
from core.database import get_session
from core.database.models.user import User, UserRole

router = APIRouter(prefix="/addresses", tags=["Addresses API"])


@router.get("/", response_model=list[AddressSchema])
async def get_addresses(
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER, exclude_admin=True))],
) -> JSONResponse:
    addresses_list = await AddressesCRUDService().get_entities_list(session, user)
    return JSONResponse(addresses_list)


@router.post("/", response_model=AddressSchema)
async def create_address(
    create_address_schema: AddressSchemaCreate,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER, exclude_admin=True))],
) -> JSONResponse:
    address = await AddressesCRUDService().create_entity(create_address_schema, session, user)
    return JSONResponse(address, status_code=status.HTTP_201_CREATED)


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    session: typing.Annotated[AsyncSession, Depends(get_session)],
    user: typing.Annotated[User, Depends(check_user_role(UserRole.CUSTOMER))],
) -> Response:
    await AddressesCRUDService().remove_entity(address_id, session, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
