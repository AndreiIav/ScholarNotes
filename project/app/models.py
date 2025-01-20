from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    notes: Mapped[list["Note"]] = relationship(
        lazy="joined",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"Project({self.id}, '{self.name}')"


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    author: Mapped[Optional[str]]
    publication_details: Mapped[Optional[str]]
    publication_year: Mapped[Optional[str]]
    comments: Mapped[Optional[str]]
    tag: Mapped[Optional[int]]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    project: Mapped["Project"] = relationship(
        lazy="joined", innerjoin=True, back_populates="notes"
    )

    def __repr__(self):
        return f"Note({self.id}, '{self.name}')"
