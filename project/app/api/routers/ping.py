from typing import Any

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

ping_router = APIRouter()


@ping_router.get("/ping")
async def pong(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
