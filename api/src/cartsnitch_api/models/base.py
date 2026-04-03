"""Base model and mixins for all CartSnitch ORM models."""

import uuid as uuid_lib
from datetime import datetime

from sqlalchemy import DateTime, String, TypeDecorator, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UUIDString(TypeDecorator):
    """Store UUIDs as VARCHAR(36) strings in all dialects.

    This handles the fundamental mismatch between Python's uuid.UUID objects
    (used everywhere in application code) and SQLite's lack of a native UUID type.
    - On INSERT: converts uuid.UUID → str
    - On SELECT: returns uuid.UUID (so SQLAlchemy 2.0 sentinel tracking matches correctly)
    """

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid_lib.UUID):
            return str(value)
        return value  # already a string

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid_lib.UUID):
            return value
        return uuid_lib.UUID(value)  # convert str → UUID for correct sentinel tracking


class Base(DeclarativeBase):
    """Base class for all CartSnitch models."""


class TimestampMixin:
    """Mixin providing created_at / updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID primary key.

    Uses UUIDString so all DB dialects store the full 36-char UUID string
    without truncation, while Python code always works with uuid.UUID objects.
    """

    id: Mapped[uuid_lib.UUID] = mapped_column(
        UUIDString(),
        primary_key=True,
        default=uuid_lib.uuid4,
    )
