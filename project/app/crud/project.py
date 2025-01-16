from app.models import Project as ProjectDBModel
from app.schemas.project import ProjectPayloadSchema
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_project_by_id(db_session: AsyncSession, project_id: int):
    query = select(ProjectDBModel).where(ProjectDBModel.id == project_id)
    project = await db_session.scalars(query)
    project = project.one_or_none()

    return project


async def get_project_by_name(project_name: str, db_session: AsyncSession):
    query = select(ProjectDBModel).where(ProjectDBModel.name == project_name)
    project = await db_session.scalars(query)
    project = project.one_or_none()

    return project


async def post_project(payload: ProjectPayloadSchema, db_session: AsyncSession):
    new_project = ProjectDBModel(name=payload.name, comment=payload.comment)
    db_session.add(new_project)
    await db_session.commit()
    await db_session.refresh(new_project)

    return new_project


async def get_all_projects(db_session: AsyncSession):
    query = select(ProjectDBModel).order_by(ProjectDBModel.id)
    all_projects = await db_session.scalars(query)

    return all_projects


async def update_project(
    project_id: int, payload: ProjectPayloadSchema, db_session: AsyncSession
):
    query = (
        update(ProjectDBModel)
        .where(ProjectDBModel.id == project_id)
        .values(name=payload.name, comment=payload.comment)
    )
    await db_session.execute(query)
    await db_session.commit()
