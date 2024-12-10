from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    comment: str
    created_at: datetime
