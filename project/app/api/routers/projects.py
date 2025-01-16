from app.api.dependencies.core import DBSessionDep
from app.crud.project import (
    check_if_project_name_exists,
    get_all_projects,
    get_project_by_id,
    post_project,
    update_project,
)
from app.schemas.project import ProjectPayloadSchema, ProjectResponseSchema
from fastapi import APIRouter, HTTPException, Path

router = APIRouter()


@router.get(
    "/{project_id}/",
    response_model=ProjectResponseSchema,
)
async def get_project(
    project_id: int,
    db_session: DBSessionDep,
) -> ProjectResponseSchema:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found.")

    return project


@router.get("/", response_model=list[ProjectResponseSchema])
async def get_projects(db_session: DBSessionDep) -> list[ProjectResponseSchema]:
    all_projects = await get_all_projects(db_session)

    return all_projects


@router.post("/", response_model=ProjectResponseSchema, status_code=201)
async def create_project(
    payload: ProjectPayloadSchema, db_session: DBSessionDep
) -> ProjectResponseSchema:
    project_name_exists = await check_if_project_name_exists(payload.name, db_session)
    if project_name_exists:
        raise HTTPException(
            status_code=400,
            detail=f"Project name '{payload.name}' already exists. Please"
            " select a unique project name and try again.",
        )

    response = await post_project(payload, db_session)

    return response


@router.patch("/{project_id}/", response_model=ProjectResponseSchema, status_code=200)
async def patch_project(
    payload: ProjectPayloadSchema,
    db_session: DBSessionDep,
    project_id: int = Path(..., gt=0),
) -> ProjectResponseSchema:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found.")

    # check if the project name is requested to be updated
    if project.name != payload.name:
        # check if the updated_name already exists
        updated_name_exists = await check_if_project_name_exists(
            payload.name, db_session
        )
        if updated_name_exists:
            raise HTTPException(
                status_code=400,
                detail=f"Project name '{payload.name}' already exists."
                " Please select a unique project name and try again.",
            )

    await update_project(project_id, payload, db_session)

    return project
