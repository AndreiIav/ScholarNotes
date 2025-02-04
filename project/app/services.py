from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project_notes import (
    add_tags_to_note,
    get_tags_to_be_inserted,
    insert_tags,
    remove_tags_from_note,
)
from app.models import Note


async def insert_missing_tags(tags: Iterable[str], db_session: AsyncSession) -> None:
    """
    Orchestrates inserting tags that are not already in 'tags' table.

    This function takes a list of tags, it checks if they are present in 'tags'
    table, and if not, it inserts them.
    """
    tags_to_be_inserted = await get_tags_to_be_inserted(
        tags=tags, db_session=db_session
    )
    if tags_to_be_inserted:
        await insert_tags(tags=tags_to_be_inserted, db_session=db_session)


async def handle_note_tags_update(
    note: Note,
    existing_note_tags: Iterable[str],
    payload_tags: Iterable[str],
    db_session: AsyncSession,
) -> None:
    """
    Orchestrates adding or removing tags for a single note.

    If the tag/tags that need to be added to the note are not already present in
    'tags' table, they are first inserted there and then the tags are added to
    note.

    Args:
        note (Note): The note to add or remove tags for.
        existing_note_tags (list[str]): The list of tags already attached to note.
        payload_tags (list[str]): The list of tags the note tags must be updated to.
        db_session (AsyncSession)
    """
    tags_to_be_removed = set(existing_note_tags) - set(payload_tags)
    if tags_to_be_removed:
        await remove_tags_from_note(
            tags=tags_to_be_removed, note=note, db_session=db_session
        )
    tags_to_be_added = set(payload_tags) - set(existing_note_tags)
    if tags_to_be_added:
        await insert_missing_tags(tags=tags_to_be_added, db_session=db_session)
        await add_tags_to_note(tags=tags_to_be_added, note=note, db_session=db_session)
