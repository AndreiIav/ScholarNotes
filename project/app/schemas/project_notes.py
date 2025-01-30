from datetime import datetime

from pydantic import BaseModel


class ProjectNotePayloadSchema(BaseModel):
    note_name: str
    note_author: str | None = None
    note_publication_details: str | None = None
    note_publication_year: int | None = None
    note_comments: str | None = None
    note_tags: list[str] = []


class ProjectNoteResponseSchema(BaseModel):
    note_id: int
    project_id: int
    note_name: str
    note_author: str | None = None
    note_publication_details: str | None = None
    note_publication_year: int | None = None
    note_comments: str | None = None
    created_at: datetime
    note_tags: list[str] = []


class ProjectNoteUpdateSchema(BaseModel, extra="forbid"):
    name: str | None = None
    author: str | None = None
    publication_details: str | None = None
    publication_year: int | None = None
    comments: str | None = None
    tags: list[str] = []


class ProjectNoteDeleteResponseSchema(BaseModel):
    message: str
