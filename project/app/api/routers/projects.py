from app.api.dependencies.core import DBSessionDep
from app.crud.project import get_all_projects, get_project, post_project
from app.schemas.project import ProjectPayloadSchema, ProjectResponseSchema
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/{project_id}",
    response_model=ProjectResponseSchema,
)
async def get_project_details(
    project_id: int,
    db_session: DBSessionDep,
) -> ProjectResponseSchema:
    project = await get_project(db_session, project_id)

    return project


@router.get("/", response_model=list[ProjectResponseSchema])
async def get_projects(db_session: DBSessionDep) -> list[ProjectResponseSchema]:
    all_projects = await get_all_projects(db_session)

    return all_projects


@router.post("/", response_model=ProjectResponseSchema, status_code=201)
async def create_project(
    payload: ProjectPayloadSchema, db_session: DBSessionDep
) -> ProjectResponseSchema:
    response = await post_project(payload, db_session)

    return response
