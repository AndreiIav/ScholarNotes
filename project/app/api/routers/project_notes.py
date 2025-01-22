from typing import Annotated

from app.api.dependencies.core import DBSessionDep
from app.crud.project import get_project_by_id
from app.crud.project_notes import (
    get_note_by_name_and_project,
    get_tags_to_be_inserted,
    insert_note,
    insert_tags,
)
from app.schemas.project_notes import (
    ProjectNotePayloadSchema,
    ProjectNoteResponseSchema,
)
from fastapi import APIRouter, HTTPException, Path

router = APIRouter()


@router.post("/", response_model=ProjectNoteResponseSchema, status_code=200)
async def add_note_to_project(
    db_session: DBSessionDep,
    project_id: Annotated[
        int, Path(title="The ID of the project to add the note for", gt=0)
    ],
    payload: ProjectNotePayloadSchema,
) -> ProjectNoteResponseSchema:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found")
    note_info = await get_note_by_name_and_project(
        payload.note_name, project_id, db_session
    )
    if note_info:
        raise HTTPException(
            status_code=400,
            detail=f"Note '{payload.note_name}' already exists for"
            f" project '{note_info.project_name}'. Please select a unique note"
            " name for this project.",
        )

    # if the payload.note_tags is not an empty list, check if the tags from
    # note_tags already exists and if not, insert them
    if payload.note_tags:
        tags_to_be_inserted: list[str] = await get_tags_to_be_inserted(
            tags=payload.note_tags, db_session=db_session
        )
        if tags_to_be_inserted:
            await insert_tags(tags_to_be_inserted, db_session)

    note = await insert_note(payload, project_id, db_session)

    response = {
        "note_id": note.id,
        "project_id": note.project_id,
        "note_name": note.name,
        "note_author": note.author,
        "note_publication_details": note.publication_details,
        "note_publication_year": note.publication_year,
        "note_comments": note.comments,
        "created_at": note.created_at,
        "note_tags": [tag.name for tag in note.tags],
    }

    return response
