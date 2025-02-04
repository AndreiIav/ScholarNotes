from typing import Any, Iterable

from app.models import Note, Project, Tag
from app.schemas.project_notes import ProjectNotePayloadSchema
from sqlalchemy import Row, and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_note_by_name_and_project(
    note_name: str, project_id: int, db_session: AsyncSession
) -> Row[tuple[str, str]] | None:
    query = (
        select(Note.name.label("note_name"), Project.name.label("project_name"))
        .join(Note.project)
        .where(and_(Note.name == note_name, Note.project_id == project_id))
    )
    query_result = await db_session.execute(query)
    note = query_result.unique().one_or_none()

    return note


async def get_all_notes_for_project(
    project_id: int, db_session: AsyncSession
) -> Iterable[Note]:
    query = select(Note).where(Note.project_id == project_id)
    all_project_notes = await db_session.scalars(query)
    result = all_project_notes.unique().all()

    return result


async def insert_note(
    payload: ProjectNotePayloadSchema, project_id: int, db_session: AsyncSession
) -> Note:
    new_note = Note(
        project_id=project_id,
        name=payload.note_name,
        author=payload.note_author,
        publication_details=payload.note_publication_details,
        publication_year=payload.note_publication_year,
        comments=payload.note_comments,
    )
    db_session.add(new_note)
    await db_session.commit()
    await db_session.refresh(new_note)

    if payload.note_tags:
        await add_tags_to_note(
            tags=payload.note_tags, note=new_note, db_session=db_session
        )

    return new_note


async def get_tags_to_be_inserted(
    tags: Iterable[str], db_session: AsyncSession
) -> list[str]:
    query = select(Tag.name).where(Tag.name.in_(tags))
    result = await db_session.scalars(query)
    existing_tags_result = result.all()

    all_tags = set(tags)
    existing_tags = set(existing_tags_result)
    missing_tags = all_tags - existing_tags

    return list(missing_tags)


async def insert_tags(tags: list[str], db_session: AsyncSession) -> None:
    for tag in tags:
        new_tag = Tag(name=tag)
        db_session.add(new_tag)

    await db_session.commit()


async def get_tags_by_name(
    tags: Iterable[str], db_session: AsyncSession
) -> Iterable[Tag]:
    query = select(Tag).where(Tag.name.in_(tags))
    query_result = await db_session.scalars(query)
    result = query_result.all()

    return result


async def get_note_by_id(note_id: int, db_session: AsyncSession) -> Note | None:
    query = select(Note).where(Note.id == note_id)
    query_result = await db_session.scalars(query)
    note = query_result.unique().one_or_none()

    return note


async def update_note(
    payload: dict[str, Any], note_id: int, db_session: AsyncSession
) -> Note:
    query = update(Note).where(Note.id == note_id).values(payload).returning(Note)
    result = await db_session.scalars(query)
    await db_session.commit()

    return result.unique().one()


async def add_tags_to_note(
    tags: Iterable[str], note: Note, db_session: AsyncSession
) -> None:
    tags_to_be_added: Iterable[Tag] = await get_tags_by_name(
        tags=tags, db_session=db_session
    )
    note.tags.extend(tags_to_be_added)

    await db_session.commit()
    await db_session.refresh(note)


async def remove_tags_from_note(
    tags: Iterable[str], note: Note, db_session: AsyncSession
) -> None:
    tags_to_be_removed: Iterable[Tag] = await get_tags_by_name(
        tags=tags, db_session=db_session
    )
    for tag in tags_to_be_removed:
        note.tags.remove(tag)

    await db_session.commit()
    await db_session.refresh(note)


async def delete_note(note_id: int, db_session: AsyncSession) -> None:
    query = delete(Note).where(Note.id == note_id)
    await db_session.execute(query)
    await db_session.commit()
