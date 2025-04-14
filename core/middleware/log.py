import logging
import time
import typing

from fastapi.requests import Request

logging.basicConfig(level=logging.INFO)


async def log_middleware(request: Request, call_next: typing.Callable):
    logging.info(f"[INFO] Incoming request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info("[INFO] Response status: %s, process time: %s", response.status_code, round(process_time, 3))
    return response
