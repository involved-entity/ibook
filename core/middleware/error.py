from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sentry_sdk import capture_exception as stry_caprure_exception


async def server_error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=e.errors(),
        )
    except Exception as e:
        stry_caprure_exception(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error. Our admins are working on it"},
        )
