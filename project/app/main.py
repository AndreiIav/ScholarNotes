import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import ping, project_notes, projects
from app.database import sessionmanager

log = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    """
    log.info("Starting up...")
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()
    log.info("Shutting down...")


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    application.include_router(ping.ping_router)
    application.include_router(projects.router, prefix="/projects", tags=["projects"])
    application.include_router(
        project_notes.router,
        prefix="/projects/{project_id}/notes",
        tags=["project_notes"],
    )

    return application


app = create_application()
