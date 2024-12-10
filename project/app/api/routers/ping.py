from app.config import Settings, get_settings
from fastapi import APIRouter, Depends

ping_router = APIRouter()


@ping_router.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
