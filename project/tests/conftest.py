import asyncio
import os
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from alembic import command, config
from app.config import Settings, get_settings
from app.database import DatabaseSessionManager, get_db_session
from app.main import create_application
from app.models import Note, Project, Tag
from fastapi.testclient import TestClient
from sqlalchemy import delete, insert, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


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


async def get_mock_session_override():
    mock_session = AsyncMock()
    async with mock_session as session:
        yield session


async def get_test_session_override():
    database_url = os.environ.get("DATABASE_TEST_URL")
    sessionmanager = DatabaseSessionManager(database_url)
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture(scope="module")
def test_app():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_db_session] = get_test_session_override
    run_latest_migration()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_app_without_db():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_db_session] = get_mock_session_override
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def get_session():
    database_url = os.environ.get("DATABASE_TEST_URL")
    sessionmanager = DatabaseSessionManager(database_url)
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture(scope="function")
async def add_project_data(get_session):
    insert_stmt_1 = insert(Project).values(
        id=1, name="test_name", comment="test_comment"
    )
    insert_stmt_2 = insert(Project).values(
        id=2, name="test_name_2", comment="test_comment_2"
    )

    session = get_session
    await session.execute(insert_stmt_1)
    await session.execute(insert_stmt_2)
    await session.commit()
    yield


@pytest.fixture(scope="function")
async def delete_project_table_data(get_session):
    yield
    session = get_session
    await session.execute(delete(Project))
    await session.commit()


async def reset_table_sequence(table_name: str, session: AsyncSession) -> None:
    """Resets PostgreSQL auto-increment sequence"""
    await session.execute(
        text(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'),"
            f"(SELECT MAX(id) FROM {table_name}));"
        )
    )
    await session.commit()


@pytest.fixture(scope="function")
async def add_project_notes_data(get_session):
    """
    Inserts data in multiple tables so it can be used for multiple project_notes
    test scenarios:
      - two rows in projects table:
            id=1, name='project_1'
            id=2, name='project_2'
      - two rows in notes table (the notes are linked to projects.id=1):
            id=1, project_id=1, name='note_1'
            id=2, project_id=1, name='note_2'
      - two rows in tags table (the tags are linked to notes.id=1):
            id=1, name='tag_1'
            id=2, name='tag_2'

    Note: To clean_up the data use the following fixtures:
         'delete_project_notes_data', 'delete_tags_data'.
    Note: To set correctly PostgreSQL's primary key auto-increment sequence,
          'reset_table_sequence' function is used on all tables where ids were
          inserted manually.
    """
    insert_project_1 = insert(Project).values(
        id=1, name="project_1", comment="test_comment"
    )
    insert_project_2 = insert(Project).values(
        id=2, name="project_2", comment="test_comment_2"
    )
    insert_project_note_1 = insert(Note).values(
        id=1,
        project_id=1,
        name="note_1",
        author="test_author",
        publication_details="test_publication_details",
        publication_year=1889,
        comments="test_comments",
        created_at=datetime(2024, 12, 1),
    )
    insert_project_note_2 = insert(Note).values(
        id=2,
        project_id=1,
        name="note_2",
        author="test_author_2",
        publication_details="test_publication_details_2",
        publication_year=1989,
        comments="test_comments",
        created_at=datetime(2024, 12, 1),
    )
    insert_tag_1 = insert(Tag).values(id=1, name="tag_1")
    insert_tag_2 = insert(Tag).values(id=2, name="tag_2")

    session = get_session

    # insert project and note
    await session.execute(insert_project_1)
    await session.execute(insert_project_2)
    await session.execute(insert_project_note_1)
    await session.execute(insert_project_note_2)
    await session.commit()

    # insert tags
    await session.execute(insert_tag_1)
    await session.execute(insert_tag_2)
    await session.commit()

    # link tags to a note
    note_1 = await session.get(Note, 1)
    tag_1 = await session.get(Tag, 1)
    tag_2 = await session.get(Tag, 2)
    note_1.tags.extend([tag_1, tag_2])
    await session.commit()

    # reset PostgreSQL primary-key auto-increment sequence
    await reset_table_sequence(table_name="notes", session=session)
    await reset_table_sequence(table_name="tags", session=session)
    await reset_table_sequence(table_name="projects", session=session)

    yield


@pytest.fixture(scope="function")
async def delete_project_notes_data(get_session):
    """
    Deletes all the data from the following tables:
    - projects
    - notes
    """
    yield
    session = get_session
    await session.execute(delete(Note))
    await session.execute(delete(Project))
    await session.commit()


@pytest.fixture(scope="function")
async def add_tags_data(get_session):
    """
    Inserts two rows in 'tags' table:
    - id=3, name="tag_3"
    - id=4, name="tag_4"

    Note: To set correctly PostgreSQL's primary key auto-increment sequence,
          'reset_table_sequence' function is used on 'tags' table.

    """
    insert_tag_1 = insert(Tag).values(id=3, name="tag_3")
    insert_tag_2 = insert(Tag).values(id=4, name="tag_4")
    session = get_session
    await session.execute(insert_tag_1)
    await session.execute(insert_tag_2)
    await session.commit()

    await reset_table_sequence("tags", get_session)

    yield


@pytest.fixture(scope="function")
async def delete_tags_data(get_session):
    yield
    session = get_session
    await session.execute(delete(Tag))
    await session.commit()
