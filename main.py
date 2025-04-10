import uvicorn
from fastapi import FastAPI

from core.api import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
