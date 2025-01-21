from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

NoteTag = Table(
    "notes_tags",
    Base.metadata,
    Column("note_id", ForeignKey("notes.id"), primary_key=True, nullable=False),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True, nullable=False),
)


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
    name: Mapped[str] = mapped_column(index=True, nullable=False)
    author: Mapped[Optional[str]]
    publication_details: Mapped[Optional[str]]
    publication_year: Mapped[Optional[str]]
    comments: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    project: Mapped["Project"] = relationship(
        lazy="joined", innerjoin=True, back_populates="notes"
    )
    tags: Mapped[list["Tag"]] = relationship(
        lazy="selectin", secondary=NoteTag, back_populates="notes"
    )

    UniqueConstraint(project_id, name)

    def __repr__(self):
        return f"Note({self.id}, '{self.name}')"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), index=True, unique=True)

    notes: Mapped[list["Note"]] = relationship(
        lazy="selectin", secondary=NoteTag, back_populates="tags"
    )

    def __repr__(self):
        return f"Tag({self.id}, '{self.name}')"
