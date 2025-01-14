import asyncio
import os

import pytest
from alembic import command, config
from app.config import Settings, get_settings
from app.database import DatabaseSessionManager, get_db_session
from app.main import create_application
from app.models import Project
from fastapi.testclient import TestClient
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import create_async_engine


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


def run_latest_migration():
    # from Alembic docs:
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio
    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    async def run_async_upgrade():
        async_engine = create_async_engine(
            os.environ.get("DATABASE_TEST_URL"), echo=True
        )
        async with async_engine.begin() as conn:
            await conn.run_sync(run_upgrade, config.Config("alembic.ini"))

    asyncio.run(run_async_upgrade())


async def get_session_override():
    database_url = os.environ.get("DATABASE_TEST_URL")
    sessionmanager = DatabaseSessionManager(database_url)
    async with sessionmanager.session() as session:
        yield session
        await session.close()


@pytest.fixture(scope="class")
async def get_session():
    database_url = os.environ.get("DATABASE_TEST_URL")
    sessionmanager = DatabaseSessionManager(database_url)
    async with sessionmanager.session() as session:
        yield session
        await session.close()


@pytest.fixture(scope="function")
async def delete_project_table_data(get_session):
    yield
    session = get_session
    await session.execute(delete(Project))
    await session.commit()


@pytest.fixture(scope="function")
async def add_project_data(get_session):
    insert_stmt_1 = insert(Project).values(name="test_name", comment="test_comment")
    insert_stmt_2 = insert(Project).values(name="test_name_2", comment="test_comment_2")

    session = get_session
    await session.execute(insert_stmt_1)
    await session.execute(insert_stmt_2)
    await session.commit()
    yield


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_db_session] = get_session_override
    run_latest_migration()
    with TestClient(app) as test_client:
        yield test_client
