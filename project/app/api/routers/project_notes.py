from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path

from app.api.dependencies.core import DBSessionDep
from app.crud.project import get_project_by_id
from app.crud.project_notes import (
    delete_note,
    get_all_notes_for_project,
    get_note_by_id,
    get_note_by_name_and_project,
    insert_note,
    update_note,
)
from app.schemas.project_notes import (
    ProjectNoteDeleteResponseSchema,
    ProjectNotePayloadSchema,
    ProjectNoteResponseSchema,
    ProjectNoteUpdateSchema,
)
from app.services import handle_note_tags_update, insert_missing_tags

router = APIRouter()


@router.post("/", response_model=ProjectNoteResponseSchema, status_code=200)
async def add_note_to_project(
    db_session: DBSessionDep,
    project_id: Annotated[
        int, Path(title="The ID of the project to add the note for", gt=0)
    ],
    payload: ProjectNotePayloadSchema,
) -> dict[str, Any]:
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
) -> list[dict[str, Any]]:
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
) -> dict[str, Any]:
    project = await get_project_by_id(db_session, project_id)
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
) -> dict[str, Any]:
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
    if payload.name:
        if note.name != payload.name:
            # check if the updated name already exists on the project
            note_updated_name = await get_note_by_name_and_project(
                note_name=payload.name, project_id=project_id, db_session=db_session
            )
            if note_updated_name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Note name '{payload.name}' already exists on "
                    f"'{project.name}' project. Please select a unique note name and "
                    "try again.",
                )

    update_data = payload.model_dump(exclude_unset=True)

    # handle updating tags data
    if "tags" in update_data.keys():
        existing_note_tags = [tag.name for tag in note.tags]
        await handle_note_tags_update(
            note=note,
            existing_note_tags=existing_note_tags,
            payload_tags=payload.tags,
            db_session=db_session,
        )

    # updating tags is handled separately
    if "tags" in update_data.keys():
        update_data.pop("tags")

    # at this point update_data may be an empty dict if only "tags" was sent
    # in the payload; in this case we don't need to perform any update in
    # "notes" table
    if update_data:
        updated_note: Any = await update_note(
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


@router.delete(
    "/{note_id}/", response_model=ProjectNoteDeleteResponseSchema, status_code=200
)
async def delete_project_note(
    db_session: DBSessionDep,
    project_id: Annotated[int, Path(title="The ID of the note to delete", gt=0)],
    note_id: Annotated[int, Path(title="The ID of the note to update", gt=0)],
) -> dict[str, str]:
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

    await delete_note(note_id=note_id, db_session=db_session)

    response = {"message": "Note deleted"}

    return response
