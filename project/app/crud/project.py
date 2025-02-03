from typing import Any

from app.models import Project as ProjectDBModel
from app.schemas.project import ProjectPayloadSchema
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_project_by_id(
    db_session: AsyncSession, project_id: int
) -> ProjectDBModel | None:
    query = select(ProjectDBModel).where(ProjectDBModel.id == project_id)
    project = await db_session.scalars(query)
    project = project.unique().one_or_none()

    return project


async def get_project_by_name(
    project_name: str, db_session: AsyncSession
) -> ProjectDBModel | None:
    query = select(ProjectDBModel).where(ProjectDBModel.name == project_name)
    project = await db_session.scalars(query)
    project = project.unique().one_or_none()

    return project


async def post_project(
    payload: ProjectPayloadSchema, db_session: AsyncSession
) -> ProjectDBModel:
    new_project = ProjectDBModel(name=payload.name, comment=payload.comment)
    db_session.add(new_project)
    await db_session.commit()
    await db_session.refresh(new_project)

    return new_project


async def get_all_projects(db_session: AsyncSession) -> list[ProjectDBModel] | None:
    query = select(ProjectDBModel).order_by(ProjectDBModel.id)
    all_projects = await db_session.scalars(query)

    return all_projects.unique()


async def update_project(
    project_id: int, payload: dict[str, Any], db_session: AsyncSession
) -> ProjectDBModel:
    query = (
        update(ProjectDBModel)
        .where(ProjectDBModel.id == project_id)
        .values(payload)
        .returning(ProjectDBModel)
    )
    result = await db_session.scalars(query)
    await db_session.commit()

    return result.unique().one()


async def remove_project(project_id: int, db_session: AsyncSession) -> None:
    query = delete(ProjectDBModel).where(ProjectDBModel.id == project_id)
    await db_session.execute(query)
    await db_session.commit()
