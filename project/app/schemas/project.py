from datetime import datetime

from app.schemas.base import CustomCheckAtLeastOnePairValidator
from pydantic import BaseModel


class ProjectResponseSchema(BaseModel):
    id: int
    name: str
    comment: str | None = None
    created_at: datetime


class ProjectPayloadSchema(BaseModel, extra="forbid"):
    name: str
    comment: str | None = None


class ProjectUpdatePayloadSchema(
    BaseModel, CustomCheckAtLeastOnePairValidator, extra="forbid"
):
    name: str | None = None
    comment: str | None = None


class ProjectDeleteSchema(BaseModel):
    message: str
