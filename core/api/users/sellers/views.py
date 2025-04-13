from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.users.dependencies import check_user_role
from core.api.users.sellers.services import get_seller_data
from core.database import get_session
from core.database.models import User
from core.database.models.user import UserRole

router = APIRouter(prefix="/sellers", tags=["Sellers API"])


@router.get("/{seller_id}")
async def get_seller_info(
    seller_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(check_user_role(UserRole.SELLER, UserRole.CUSTOMER)),
) -> ORJSONResponse:
    seller = await get_seller_data(seller_id, session)
    return ORJSONResponse(seller)
