from app.api.dependencies.core import DBSessionDep
from app.crud.project import get_project
from app.schemas.project import Project
from fastapi import APIRouter

project_router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)


@project_router.get(
    "/{project_id}",
    response_model=Project,
)
async def user_details(
    project_id: int,
    db_session: DBSessionDep,
):
    """
    Get any user details
    """
    user = await get_project(db_session, project_id)
    return user
