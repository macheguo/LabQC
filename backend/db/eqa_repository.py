"""EQA repository — CRUD for institutions, programs, samples, participants, results."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from backend.models.eqa_models import (
    Institution,
    EQAProgram, EQASample, EQAParticipant, EQAResult,
    EQASettings,
)


# ── Institutions ───────────────────────────────────────────────────────

def list_institutions(db: Session) -> list[Institution]:
    return db.query(Institution).order_by(Institution.name).all()


def get_institution(db: Session, inst_id: str) -> Institution | None:
    return db.query(Institution).filter(Institution.id == inst_id).first()


def create_institution(db: Session, data: dict) -> Institution:
    inst = Institution(**data)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


def update_institution(db: Session, inst_id: str, data: dict) -> Institution | None:
    inst = get_institution(db, inst_id)
    if not inst:
        return None
    for k, v in data.items():
        setattr(inst, k, v)
    db.commit()
    db.refresh(inst)
    return inst


def delete_institution(db: Session, inst_id: str) -> bool:
    inst = get_institution(db, inst_id)
    if not inst:
        return False
    db.delete(inst)
    db.commit()
    return True


# ── Programs ───────────────────────────────────────────────────────────

def list_programs(db: Session) -> list[EQAProgram]:
    return db.query(EQAProgram).order_by(EQAProgram.created_at.desc()).all()


def get_program(db: Session, prog_id: str) -> EQAProgram | None:
    return db.query(EQAProgram).filter(EQAProgram.id == prog_id).first()


def create_program(db: Session, data: dict) -> EQAProgram:
    prog = EQAProgram(**data)
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


def update_program(db: Session, prog_id: str, data: dict) -> EQAProgram | None:
    prog = get_program(db, prog_id)
    if not prog:
        return None
    for k, v in data.items():
        setattr(prog, k, v)
    db.commit()
    db.refresh(prog)
    return prog


# ── Samples ────────────────────────────────────────────────────────────

def list_samples(db: Session, prog_id: str) -> list[EQASample]:
    return db.query(EQASample).filter(EQASample.program_id == prog_id).all()


def create_sample(db: Session, prog_id: str, data: dict) -> EQASample:
    data["program_id"] = prog_id
    s = EQASample(**data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# ── Participants ───────────────────────────────────────────────────────

def list_participants(db: Session, prog_id: str) -> list[EQAParticipant]:
    return (db.query(EQAParticipant)
            .options(joinedload(EQAParticipant.institution))
            .filter(EQAParticipant.program_id == prog_id)
            .all())


def create_participant(db: Session, prog_id: str, data: dict) -> EQAParticipant:
    data["program_id"] = prog_id
    p = EQAParticipant(**data)
    db.add(p)
    db.commit()
    db.refresh(p)
    # Eager-load institution name for response
    db.refresh(p, attribute_names=["institution"])
    return p


# ── Results ────────────────────────────────────────────────────────────

def list_results(db: Session, prog_id: str) -> list[EQAResult]:
    return (db.query(EQAResult)
            .options(joinedload(EQAResult.participant).joinedload(EQAParticipant.institution))
            .filter(EQAResult.program_id == prog_id)
            .order_by(EQAResult.participant_id, EQAResult.sample_id)
            .all())


def create_result(db: Session, prog_id: str, data: dict) -> EQAResult:
    data["program_id"] = prog_id

    # Compute z-score and grade
    sample_id = data["sample_id"]
    sample = db.query(EQASample).filter(EQASample.id == sample_id).first()
    if sample and sample.target_sd > 0:
        z = round((data["reported_value"] - sample.target_value) / sample.target_sd, 2)
    else:
        z = 0.0
    data["z_score"] = z
    if abs(z) <= 2:
        data["grade"] = "满意"
    elif abs(z) < 3:
        data["grade"] = "可疑"
    else:
        data["grade"] = "不满意"

    r = EQAResult(**data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


# ── Settings ────────────────────────────────────────────────────────────

def get_settings(db: Session) -> EQASettings:
    """Get or create the singleton EQA settings row."""
    s = db.query(EQASettings).first()
    if not s:
        s = EQASettings(role="organizer")
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def update_settings(db: Session, data: dict) -> EQASettings:
    s = get_settings(db)
    for k, v in data.items():
        if v is not None:
            setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


# ── Import ──────────────────────────────────────────────────────────────

def import_results(db: Session, prog_id: str, rows: list[dict]) -> dict:
    """Batch import results. Auto-resolves institutions and participants.
    Returns {imported: int, skipped: int, errors: [str]}"""
    prog = db.query(EQAProgram).filter(EQAProgram.id == prog_id).first()
    if not prog:
        return {"imported": 0, "skipped": 0, "errors": ["Program not found"]}

    samples = {s.sample_code: s for s in db.query(EQASample).filter(EQASample.program_id == prog_id).all()}
    institutions = {i.name: i for i in db.query(Institution).all()}
    participants_cache = {}  # (institution_id, program_id) -> participant

    imported, skipped, errors = 0, 0, []

    for i, row in enumerate(rows):
        # Resolve sample
        sample = samples.get(row.get("sample_code", ""))
        if not sample:
            skipped += 1
            errors.append(f"Row {i+1}: unknown sample_code '{row.get('sample_code')}'")
            continue

        # Resolve or create institution
        inst_name = row.get("institution_name", "").strip()
        if not inst_name:
            skipped += 1
            errors.append(f"Row {i+1}: missing institution_name")
            continue

        inst = institutions.get(inst_name)
        if not inst:
            inst = Institution(name=inst_name)
            db.add(inst)
            db.flush()
            institutions[inst_name] = inst

        # Resolve or create participant
        key = (inst.id, prog_id)
        participant = participants_cache.get(key)
        if not participant:
            participant = db.query(EQAParticipant).filter(
                EQAParticipant.institution_id == inst.id,
                EQAParticipant.program_id == prog_id
            ).first()
            if not participant:
                participant = EQAParticipant(
                    program_id=prog_id,
                    institution_id=inst.id,
                    lab_code=row.get("lab_code"),
                    status="已报名"
                )
                db.add(participant)
                db.flush()
            participants_cache[key] = participant

        # Check duplicate
        existed = db.query(EQAResult).filter(
            EQAResult.participant_id == participant.id,
            EQAResult.sample_id == sample.id
        ).first()
        if existed:
            skipped += 1
            errors.append(f"Row {i+1}: duplicate ({inst_name} / {sample.sample_code})")
            continue

        # Compute z-score
        reported = float(row["reported_value"])
        if sample.target_sd > 0:
            z = round((reported - sample.target_value) / sample.target_sd, 2)
        else:
            z = 0.0
        if abs(z) <= 2:
            grade = "满意"
        elif abs(z) < 3:
            grade = "可疑"
        else:
            grade = "不满意"

        r = EQAResult(
            program_id=prog_id,
            sample_id=sample.id,
            participant_id=participant.id,
            reported_value=reported,
            method=row.get("method"),
            instrument=row.get("instrument"),
            z_score=z,
            grade=grade,
        )
        db.add(r)
        imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors[-10:]}


# ── Export ──────────────────────────────────────────────────────────────

def export_participant_results(db: Session, prog_id: str, institution_name: str) -> list[dict]:
    """Export all results for one institution in a program."""
    inst = db.query(Institution).filter(Institution.name == institution_name).first()
    if not inst:
        return []

    participant = db.query(EQAParticipant).filter(
        EQAParticipant.institution_id == inst.id,
        EQAParticipant.program_id == prog_id
    ).first()
    if not participant:
        return []

    results = (db.query(EQAResult)
               .options(joinedload(EQAResult.program))
               .filter(EQAResult.participant_id == participant.id)
               .all())

    out = []
    for r in results:
        sample = db.query(EQASample).filter(EQASample.id == r.sample_id).first()
        if not sample:
            continue
        out.append({
            "program_name": r.program.name if r.program else "",
            "sample_code": sample.sample_code,
            "item_name": sample.item_name,
            "reported_value": r.reported_value,
            "target_value": sample.target_value,
            "target_sd": sample.target_sd,
            "z_score": r.z_score,
            "grade": r.grade,
            "method": r.method,
            "instrument": r.instrument,
        })
    return out
