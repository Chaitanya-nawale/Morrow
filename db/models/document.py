"""Document SQLModel representing ingested files, git repositories, and external sources."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, Relationship

from db.models.base import TimestampModel, UUIDModel

if TYPE_CHECKING:
    from db.models.memory import Memory
    from db.models.project import Project


class Document(UUIDModel, TimestampModel, table=True):
    """Document entity tracking ingested raw files and extracted text."""

    __tablename__ = "documents"

    project_id: uuid.UUID = Field(
        foreign_key="projects.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the associated project",
    )
    uri: str = Field(
        index=True,
        nullable=False,
        description="File path, URL, or Git commit URI pointing to the source",
    )
    title: str = Field(
        nullable=False,
        description="Human-readable title or document file name",
    )
    mime_type: str = Field(
        default="text/plain",
        nullable=False,
        description="MIME type of the ingested document",
    )
    content_hash: str = Field(
        index=True,
        nullable=False,
        description="SHA-256 hash of the content at ingestion time for drift detection",
    )
    content: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Extracted or raw text content stored directly for immutable evidence",
    )
    size_bytes: int = Field(
        default=0,
        nullable=False,
        description="Size of the document in bytes",
    )
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON, nullable=False),
        description="Arbitrary document metadata such as author, commit date, or section headers",
    )

    # Relationships
    project: "Project" = Relationship(back_populates="documents")
    memories: list["Memory"] = Relationship(back_populates="document")


__all__ = ["Document"]
