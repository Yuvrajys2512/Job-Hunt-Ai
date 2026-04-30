"""
Resume and Application models.

Resume: a tailored resume created for a specific job.
Application: records that we applied to a job, with its current status.

Key design decision: each resume is tied to ONE job.
Generic resumes are less effective. The whole point of JobHunt AI
is that every resume is a custom-crafted document for that specific JD.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class ApplicationStatus(str, PyEnum):
    RESUME_PENDING   = "resume_pending"    # job selected, resume not yet created
    RESUME_READY     = "resume_ready"      # resume created, awaiting human approval
    APPROVED         = "approved"          # user approved resume
    APPLYING         = "applying"          # agent is filling the application form
    APPLIED          = "applied"           # successfully submitted
    RESPONDED        = "responded"         # company replied (any kind)
    INTERVIEW        = "interview"         # interview scheduled
    REJECTED         = "rejected"          # explicit rejection
    NO_RESPONSE      = "no_response"       # applied >2 weeks ago, no reply


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    # The Q&A conversation that generated this resume
    qa_conversation: Mapped[str | None] = mapped_column(Text)   # JSON array of messages

    # Structured resume data (JSON)
    content: Mapped[str | None] = mapped_column(Text)           # parsed resume sections

    # Path to the generated PDF file
    pdf_path: Mapped[str | None] = mapped_column(String(500))

    is_approved: Mapped[bool] = mapped_column(default=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    application: Mapped["Application | None"] = relationship(back_populates="resume")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False, unique=True)
    resume_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resumes.id"), nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus), default=ApplicationStatus.RESUME_PENDING
    )

    applied_at: Mapped[datetime | None]  = mapped_column(DateTime, nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Notes from the agent (e.g. "Easy Apply used", "cover letter submitted")
    notes: Mapped[str | None] = mapped_column(Text)

    # Follow-up suggestion from LLM
    follow_up_suggestion: Mapped[str | None] = mapped_column(Text)
    follow_up_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")  # noqa: F821
    job: Mapped["Job"] = relationship(back_populates="application")  # noqa: F821
    resume: Mapped["Resume | None"] = relationship(back_populates="application")
