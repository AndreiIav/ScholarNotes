from app.models import Project as ProjectDBModel
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
