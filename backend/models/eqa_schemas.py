"""Pydantic schemas for EQA module."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Institution ────────────────────────────────────────────────────────

class InstitutionBase(BaseModel):
    name: str = Field(..., max_length=200)
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None

class InstitutionOut(InstitutionBase):
    id: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Program ────────────────────────────────────────────────────────────

class EQAProgramCreate(BaseModel):
    name: str
    program_type: str = "定量"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class EQAProgramUpdate(BaseModel):
    name: Optional[str] = None
    program_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None

class EQAProgramOut(BaseModel):
    id: str
    name: str
    program_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Sample ─────────────────────────────────────────────────────────────

class EQASampleCreate(BaseModel):
    sample_code: str
    item_name: str
    unit: Optional[str] = None
    target_value: float
    target_sd: float

class EQASampleOut(BaseModel):
    id: str
    program_id: str
    sample_code: str
    item_name: str
    unit: Optional[str] = None
    target_value: float
    target_sd: float
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Participant ────────────────────────────────────────────────────────

class EQAParticipantCreate(BaseModel):
    institution_id: str
    lab_code: Optional[str] = None

class EQAParticipantOut(BaseModel):
    id: str
    program_id: str
    institution_id: str
    institution_name: str = ""
    lab_code: Optional[str] = None
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Result ─────────────────────────────────────────────────────────────

class EQAResultCreate(BaseModel):
    participant_id: str
    sample_id: str
    reported_value: float
    method: Optional[str] = None
    instrument: Optional[str] = None

class EQAResultOut(BaseModel):
    id: str
    program_id: str
    sample_id: str
    participant_id: str
    institution_id: str = ""
    institution_name: str = ""
    reported_value: float
    method: Optional[str] = None
    instrument: Optional[str] = None
    z_score: Optional[float] = None
    grade: Optional[str] = None
    reported_at: datetime
    model_config = {"from_attributes": True}


# ── Stats ──────────────────────────────────────────────────────────────

class EQASampleStat(BaseModel):
    sample_id: str
    sample_code: str
    item_name: str
    target_value: float
    target_sd: float
    n: int
    mean: float
    sd: float
    cv: float
    results: list[EQAResultOut] = []

class EQAInstitutionSummary(BaseModel):
    institution_name: str
    total: int
    satisfactory: int
    questionable: int
    unsatisfactory: int
    pass_rate: float

class EQAProgramStats(BaseModel):
    program: EQAProgramOut
    sample_stats: list[EQASampleStat] = []
    institution_summary: list[EQAInstitutionSummary] = []


# ── Settings ────────────────────────────────────────────────────────────

class EQASettingsOut(BaseModel):
    id: str
    role: str
    org_name: Optional[str] = None
    remote_api_url: Optional[str] = None
    api_key: Optional[str] = None
    portal_enabled: str
    portal_access: Optional[str] = None
    model_config = {"from_attributes": True}

class EQASettingsUpdate(BaseModel):
    role: Optional[str] = None
    org_name: Optional[str] = None
    remote_api_url: Optional[str] = None
    api_key: Optional[str] = None
    portal_enabled: Optional[str] = None
    portal_access: Optional[str] = None


# ── Import / Export ─────────────────────────────────────────────────────

class EQAResultImportRow(BaseModel):
    """One row from an uploaded spreadsheet."""
    institution_name: str
    lab_code: Optional[str] = None
    sample_code: str
    reported_value: float
    method: Optional[str] = None
    instrument: Optional[str] = None

class EQAResultExportRow(BaseModel):
    """One row for participant export."""
    program_name: str
    sample_code: str
    item_name: str
    reported_value: float
    target_value: float
    target_sd: float
    z_score: Optional[float] = None
    grade: Optional[str] = None
    method: Optional[str] = None
    instrument: Optional[str] = None
