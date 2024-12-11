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
    new_project = ProjectDBModel(name=payload.name, comment=payload.comment)
    db_session.add(new_project)
    await db_session.commit()
    await db_session.refresh(new_project)

    return new_project


async def get_all_projects(db_sessions: AsyncSession):
    all_projects = await db_sessions.scalars(select(ProjectDBModel))

    return all_projects
