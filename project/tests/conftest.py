import asyncio
import os

import pytest
from alembic import command, config
from app.config import Settings, get_settings
from app.database import Base, DatabaseSessionManager, get_db_session
from app.main import create_application
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


settings = get_settings_override()
database_url = str(settings.database_url)
sessionmanager = DatabaseSessionManager(database_url)


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
    async with sessionmanager.session() as session:
        yield session


def truncate_tables():
    async def _truncate_tables():
        # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#asyncio-platform-installation-notes-including-apple-m1
        settings = get_settings_override()
        database_url = str(settings.database_url)
        engine = create_async_engine(database_url)
        async with engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE project"))

    asyncio.run(_truncate_tables())


@pytest.fixture(scope="module")
def test_app():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_app_with_db():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_db_session] = get_session_override
    run_latest_migration()
    with TestClient(app) as test_client:
        yield test_client
    truncate_tables()
