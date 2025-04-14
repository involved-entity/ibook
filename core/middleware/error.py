from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def server_error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:  # noqa
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error. Our admins are working on it"},
        )
