from datetime import datetime

from pydantic import BaseModel


class ProjectResponseSchema(BaseModel):
    id: int
    name: str
    comment: str | None = None
    created_at: datetime


class ProjectPayloadSchema(BaseModel, extra="forbid"):
    name: str
    comment: str | None = None


class ProjectDeleteSchema(BaseModel):
    message: str
