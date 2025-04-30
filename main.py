import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from core.api import router
from core.config import settings
from core.middleware.error import server_error_middleware
from core.middleware.log import log_middleware

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0,
)


app = FastAPI()
app.include_router(router)

app.add_middleware(SentryAsgiMiddleware)  # noqa
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "PATCH", "POST"],
    allow_headers=["*"],
)
app.middleware("http")(log_middleware)
app.middleware("http")(server_error_middleware)

app.mount(settings.upload_book_images_url, StaticFiles(directory=settings.upload_book_images_dir), name="uploads")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
