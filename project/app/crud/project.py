from app.models import Project as ProjectDBModel
from app.schemas.project import ProjectPayloadSchema
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_project(db_session: AsyncSession, project_id: int):
    project = (
        await db_session.scalars(
            select(ProjectDBModel).where(ProjectDBModel.id == project_id)
        )
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def post_project(payload: ProjectPayloadSchema, db_session: AsyncSession):
    check_project_name_query = select(ProjectDBModel).where(
        ProjectDBModel.name == payload.name
    )
    project = await db_session.execute(check_project_name_query)
    project = project.one_or_none()
    if project:
        raise HTTPException(
            status_code=400,
            detail=f"Project name '{payload.name}' already exists. Please"
            " select a unique project name and try again.",
        )
    new_project = ProjectDBModel(name=payload.name, comment=payload.comment)
    db_session.add(new_project)
    await db_session.commit()
    await db_session.refresh(new_project)

    return new_project


async def get_all_projects(db_session: AsyncSession):
    all_projects = await db_session.scalars(
        select(ProjectDBModel).order_by(ProjectDBModel.id)
    )

    return all_projects
