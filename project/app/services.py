from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project_notes import get_tags_to_be_inserted, insert_tags


async def insert_missing_tags(tags: list[str], db_session: AsyncSession):
    """
    Orchestrates inserting received tags that are not already in 'tags' table.

    This function takes a list of tags, it checks if they are present in 'tags'
    table, and if not, it inserts them.
    """
    tags_to_be_inserted = await get_tags_to_be_inserted(
        tags=tags, db_session=db_session
    )
    if tags_to_be_inserted:
        await insert_tags(tags=tags_to_be_inserted, db_session=db_session)
