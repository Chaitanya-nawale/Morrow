"""User SQLModel representing system users and agent personalization."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from db.models.base import TimestampModel, UUIDModel

if TYPE_CHECKING:
    from db.models.project import Project
    from db.models.task import Task


class User(UUIDModel, TimestampModel, table=True):
    """User entity for personal research workspaces."""

    __tablename__ = "users"

    username: str = Field(
        default="default",
        unique=True,
        index=True,
        nullable=False,
        description="Unique username identifier for the workspace owner",
    )
    full_name: str = Field(
        default="Default User",
        nullable=False,
        description="Display name of the user",
    )
    persona: str = Field(
        default="Rigorous, evidence-oriented research and engineering assistant.",
        nullable=False,
        description="Custom instructions and persona directly injected into LLM system prompts",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Active status flag",
    )

    # Relationships
    projects: list["Project"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    tasks: list["Task"] = Relationship(
        back_populates="user",
    )


__all__ = ["User"]
