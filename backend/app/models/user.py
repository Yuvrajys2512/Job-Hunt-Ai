"""
User model.

This table stores registered users. The password is NEVER stored in plain text —
only the bcrypt hash. If your DB is ever compromised, raw passwords are safe.

UUID primary keys (instead of integers):
- Can't enumerate users by guessing IDs (/users/1, /users/2...)
- Safe to expose in URLs
- Work in distributed systems without collision
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profile data (stored as text/JSON for flexibility)
    profile_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)       # JSON array
    experience: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON array
    education: Mapped[str | None] = mapped_column(Text, nullable=True)    # JSON array

    # Timestamps — func.now() uses the DB server's clock, not the app server's
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships — SQLAlchemy will load related records automatically
    job_searches: Mapped[list["JobSearch"]] = relationship(back_populates="user")  # noqa: F821
    applications: Mapped[list["Application"]] = relationship(back_populates="user")  # noqa: F821

    def __repr__(self) -> str:
        return f"<User {self.email}>"
