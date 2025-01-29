from typing import Annotated

from app.api.dependencies.core import DBSessionDep
from app.crud.project import get_project_by_id
from app.crud.project_notes import (
    add_tags_to_note,
    get_all_notes_for_project,
    get_note_by_id,
    get_note_by_name_and_project,
    get_tags_to_be_inserted,
    insert_note,
    insert_tags,
    remove_tags_from_note,
    update_note,
)
from app.schemas.project_notes import (
    ProjectNotePayloadSchema,
    ProjectNoteResponseSchema,
    ProjectNoteUpdateSchema,
)
from app.services import insert_missing_tags
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

    if payload.note_tags:
        await insert_missing_tags(tags=payload.note_tags, db_session=db_session)

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


@router.patch("/{note_id}/")
async def patch_note(
    payload: ProjectNoteUpdateSchema,
    db_session: DBSessionDep,
    project_id: Annotated[
        int, Path(title="The ID of the project to update the note for", gt=0)
    ],
    note_id: Annotated[int, Path(title="The ID of the note to update", gt=0)],
) -> ProjectNoteResponseSchema:
    project = await get_project_by_id(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project id not found")

    note = await get_note_by_id(note_id=note_id, db_session=db_session)
    if not note:
        raise HTTPException(status_code=404, detail="Note id not found")

    # check if the requested note belongs to the requested project_id
    if note.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="The note id cannot be found for this project."
        )

    # check if the note name is requested to be updated
    if note.name != payload.name:
        # check if the updated name already exists on the project
        note_updated_name = await get_note_by_name_and_project(
            note_name=payload.name, project_id=project_id, db_session=db_session
        )
        if note_updated_name:
            raise HTTPException(
                status_code=400,
                detail=f"Note name '{payload.name}' already exists on "
                f"{project.name} project. Please select a unique note name and "
                "try again.",
            )

    # handle updating tags data
    existing_note_tags = set([tag.name for tag in note.tags])
    payload_tags = set(payload.tags)
    tags_to_be_removed = existing_note_tags - payload_tags
    if tags_to_be_removed:
        await remove_tags_from_note(
            tags=tags_to_be_removed, note=note, db_session=db_session
        )
    tags_to_be_added = payload_tags - existing_note_tags
    if tags_to_be_added:
        # check if the tags already exist, and if not insert them
        tags_to_be_inserted = await get_tags_to_be_inserted(
            tags=tags_to_be_added, db_session=db_session
        )
        if tags_to_be_inserted:
            await insert_tags(tags_to_be_inserted, db_session)
        await add_tags_to_note(tags=tags_to_be_added, note=note, db_session=db_session)

    update_data = payload.model_dump(exclude_unset=True)

    # updating tags is handled separately
    if "tags" in update_data.keys():
        update_data.pop("tags")

    # at this point update_data may be an empty dict if only "tags" were sent
    # in the payload; in this case we don't need to perform any update in
    # "notes" table
    if update_data:
        updated_note = await update_note(
            payload=update_data, note_id=note_id, db_session=db_session
        )
    else:
        updated_note = await get_note_by_id(note_id=note_id, db_session=db_session)

    return {
        "note_id": updated_note.id,
        "project_id": updated_note.project_id,
        "note_name": updated_note.name,
        "note_author": updated_note.author,
        "note_publication_details": updated_note.publication_details,
        "note_publication_year": updated_note.publication_year,
        "note_comments": updated_note.comments,
        "created_at": updated_note.created_at,
        "note_tags": [tag.name for tag in updated_note.tags],
    }
