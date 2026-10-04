"""Database models module using SQLModel."""

from db.models.base import SQLModel, TimestampModel, UUIDModel

__all__ = [
    "SQLModel",
    "TimestampModel",
    "UUIDModel",
]
