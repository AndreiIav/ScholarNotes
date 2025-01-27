from typing import Annotated

from app.api.dependencies.core import DBSessionDep
from app.crud.project import get_project_by_id
from app.crud.project_notes import (
    get_all_notes_for_project,
    get_note_by_id,
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


@router.get("/", response_model=list[ProjectNoteResponseSchema], status_code=200)
async def get_all_project_notes(
    db_session: DBSessionDep,
    project_id: Annotated[
        int, Path(title="The ID of the project to get the notes for", gt=0)
    ],
) -> list[ProjectNoteResponseSchema]:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found")
    all_project_notes = await get_all_notes_for_project(project_id, db_session)

    response = []

    for project_note in all_project_notes:
        note_response = {
            "note_id": project_note.id,
            "project_id": project_note.project_id,
            "note_name": project_note.name,
            "note_author": project_note.author,
            "note_publication_details": project_note.publication_details,
            "note_publication_year": project_note.publication_year,
            "note_comments": project_note.comments,
            "created_at": project_note.created_at,
            "note_tags": [tag.name for tag in project_note.tags],
        }
        response.append(note_response)

    return response


@router.get("/{note_id}/")
async def get_project_note(
    db_session: DBSessionDep,
    project_id: Annotated[
        int, Path(title="The ID of the project to get the note for", gt=0)
    ],
    note_id: Annotated[int, Path(title="The ID of the note to get", gt=0)],
) -> ProjectNoteResponseSchema:
    project = await get_project_by_id(db_session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found")

    note = await get_note_by_id(note_id=note_id, db_session=db_session)
    if not note:
        raise HTTPException(status_code=404, detail="Note id not found")

    note_response = {
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

    return note_response
