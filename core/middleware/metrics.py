import time

from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sentry_sdk import capture_exception as stry_caprure_exception

from core.prometheus import REQUEST_COUNT, REQUEST_LATENCY


async def metrics(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path

    try:
        response = await call_next(request)
    except ValidationError as e:
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=e.errors(),
        )
    except Exception as e:
        stry_caprure_exception(e)
        REQUEST_COUNT.labels(method, endpoint, 500).inc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error. Our admins are working on it"},
        )

    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method, endpoint).observe(latency)
    REQUEST_COUNT.labels(method, endpoint, response.status_code).inc()

    return response
