"""SQLAlchemy ORM models for EQA (External Quality Assessment)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import relationship

from backend.db.database import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


# ── Institution ────────────────────────────────────────────────────────

class Institution(Base):
    __tablename__ = "institutions"

    id            = Column(String(36), primary_key=True, default=_uuid)
    name          = Column(String(200), nullable=False, unique=True, index=True)
    address       = Column(String(500), nullable=True)
    contact_name  = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    created_at    = Column(DateTime(timezone=True), default=_now, nullable=False)

    participants  = relationship("EQAParticipant", back_populates="institution")


# ── EQA Program ────────────────────────────────────────────────────────

class EQAProgram(Base):
    __tablename__ = "eqa_programs"

    id           = Column(String(36), primary_key=True, default=_uuid)
    name         = Column(String(300), nullable=False)
    program_type = Column(String(50), nullable=False, default="定量")
    start_date   = Column(String(20), nullable=True)
    end_date     = Column(String(20), nullable=True)
    status       = Column(String(20), nullable=False, default="进行中")
    created_at   = Column(DateTime(timezone=True), default=_now, nullable=False)

    samples      = relationship("EQASample", back_populates="program",
                                cascade="all, delete-orphan", passive_deletes=True)
    participants = relationship("EQAParticipant", back_populates="program",
                                cascade="all, delete-orphan", passive_deletes=True)
    results      = relationship("EQAResult", back_populates="program",
                                cascade="all, delete-orphan", passive_deletes=True)


# ── EQA Sample ─────────────────────────────────────────────────────────

class EQASample(Base):
    __tablename__ = "eqa_samples"

    id           = Column(String(36), primary_key=True, default=_uuid)
    program_id   = Column(String(36), ForeignKey("eqa_programs.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    sample_code  = Column(String(50), nullable=False)
    item_name    = Column(String(200), nullable=False)
    unit         = Column(String(50), nullable=True)
    target_value = Column(Float, nullable=False)
    target_sd    = Column(Float, nullable=False)
    created_at   = Column(DateTime(timezone=True), default=_now, nullable=False)

    program      = relationship("EQAProgram", back_populates="samples")


# ── EQA Participant ────────────────────────────────────────────────────

class EQAParticipant(Base):
    __tablename__ = "eqa_participants"

    id             = Column(String(36), primary_key=True, default=_uuid)
    program_id     = Column(String(36), ForeignKey("eqa_programs.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    institution_id = Column(String(36), ForeignKey("institutions.id", ondelete="RESTRICT"),
                            nullable=False, index=True)
    lab_code       = Column(String(50), nullable=True)
    status         = Column(String(20), nullable=False, default="已报名")
    created_at     = Column(DateTime(timezone=True), default=_now, nullable=False)

    program        = relationship("EQAProgram", back_populates="participants")
    institution    = relationship("Institution", back_populates="participants")
    results        = relationship("EQAResult", back_populates="participant")


# ── EQA Result ─────────────────────────────────────────────────────────

class EQAResult(Base):
    __tablename__ = "eqa_results"

    id             = Column(String(36), primary_key=True, default=_uuid)
    program_id     = Column(String(36), ForeignKey("eqa_programs.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    sample_id      = Column(String(36), ForeignKey("eqa_samples.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("eqa_participants.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    reported_value = Column(Float, nullable=False)
    method         = Column(String(200), nullable=True)
    instrument     = Column(String(200), nullable=True)
    z_score        = Column(Float, nullable=True)
    grade          = Column(String(20), nullable=True)
    reported_at    = Column(DateTime(timezone=True), default=_now, nullable=False)

    program        = relationship("EQAProgram", back_populates="results")
    participant    = relationship("EQAParticipant", back_populates="results")


# ── EQA Settings ────────────────────────────────────────────────────────

class EQASettings(Base):
    __tablename__ = "eqa_settings"

    id             = Column(String(36), primary_key=True, default=_uuid)
    role           = Column(String(20), nullable=False, default="organizer")
    org_name       = Column(String(300), nullable=True)
    remote_api_url = Column(String(500), nullable=True)
    api_key        = Column(String(200), nullable=True)
    portal_enabled = Column(String(5), nullable=False, default="否")
    portal_access  = Column(String(50), nullable=True)
    updated_at     = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
