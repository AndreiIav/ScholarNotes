from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.api.routers.projects import project_router
from app.config import Settings, get_settings
from app.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI()

app.include_router(project_router)


@app.get("/")
async def root():
    return {"message": "Ok"}


@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
