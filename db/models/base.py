"""SQLModel base classes and reusable models."""

import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class UUIDModel(SQLModel):
    """Base model adding a primary key UUID to database models."""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class TimestampModel(SQLModel):
    """Base model adding timezone-aware creation and update timestamps."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )


__all__ = [
    "SQLModel",
    "TimestampModel",
    "UUIDModel",
]
