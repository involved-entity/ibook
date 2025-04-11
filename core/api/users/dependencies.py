import typing

from fastapi import HTTPException, status
from fastapi.params import Depends

from core.api.authentication.routers import fastapi_users
from core.database.models.user import User, UserRole

current_active_verified_user = fastapi_users.current_user(active=True, verified=True)


def check_user_role(*valid_roles: UserRole, exclude_admin: bool = False) -> typing.Callable:
    if not exclude_admin:
        valid_roles = list(valid_roles)
        valid_roles.append(UserRole.ADMIN)

    def dependency(current_user: typing.Annotated[User, Depends(current_active_verified_user)]) -> User:
        if current_user.role not in valid_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

        return current_user

    return dependency
