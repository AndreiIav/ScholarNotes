from typing import Annotated, Iterable

from fastapi import APIRouter, HTTPException, Path

from app.api.dependencies.core import DBSessionDep
from app.crud.project import (
    get_all_projects,
    get_project_by_id,
    get_project_by_name,
    post_project,
    remove_project,
    update_project,
)
from app.models import Project
from app.schemas.project import (
    ProjectDeleteSchema,
    ProjectPayloadSchema,
    ProjectResponseSchema,
    ProjectUpdatePayloadSchema,
)

router = APIRouter()


@router.get(
    "/{project_id}/",
    response_model=ProjectResponseSchema,
)
async def get_project(
    db_session: DBSessionDep,
    project_id: Annotated[int, Path(title="The ID of the item to get", gt=0)],
) -> Project:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found.")

    return project


@router.get("/", response_model=list[ProjectResponseSchema])
async def get_projects(db_session: DBSessionDep) -> Iterable[Project] | None:
    all_projects = await get_all_projects(db_session)

    return all_projects


@router.post("/", response_model=ProjectResponseSchema, status_code=201)
async def create_project(
    payload: ProjectPayloadSchema, db_session: DBSessionDep
) -> Project:
    project = await get_project_by_name(payload.name, db_session)
    if project:
        raise HTTPException(
            status_code=400,
            detail=f"Project name '{payload.name}' already exists. Please"
            " select a unique project name and try again.",
        )

    response = await post_project(payload, db_session)

    return response


@router.patch("/{project_id}/", response_model=ProjectResponseSchema, status_code=200)
async def patch_project(
    payload: ProjectUpdatePayloadSchema,
    db_session: DBSessionDep,
    project_id: Annotated[int, Path(title="The ID of the item to update", gt=0)],
) -> Project:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found.")

    # check if the project name is requested to be updated
    if payload.name:
        if project.name != payload.name:
            # check if the updated_name already exists
            updated_name = await get_project_by_name(payload.name, db_session)
            if updated_name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Project name '{payload.name}' already exists."
                    " Please select a unique project name and try again.",
                )

    update_data = payload.model_dump(exclude_unset=True)

    updated_project = await update_project(
        project_id=project.id, payload=update_data, db_session=db_session
    )

    return updated_project


@router.delete("/{project_id}/", response_model=ProjectDeleteSchema, status_code=200)
async def delete_project(
    db_session: DBSessionDep,
    project_id: Annotated[int, Path(title="The ID of the item to delete", gt=0)],
) -> dict[str, str]:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found.")

    await remove_project(project_id=project_id, db_session=db_session)

    response = {"message": "Project deleted"}

    return response
