import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.api import router
from core.config import settings

app = FastAPI()
app.include_router(router)
app.mount(settings.upload_book_images_url, StaticFiles(directory=settings.upload_book_images_dir), name="uploads")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
