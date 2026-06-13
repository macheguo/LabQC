"""EQA module router — External Quality Assessment (室间质评)."""

from __future__ import annotations

import csv
import io
import statistics

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.eqa_repository import (
    list_institutions, get_institution, create_institution,
    update_institution, delete_institution,
    list_programs, get_program, create_program, update_program,
    list_samples, create_sample,
    list_participants, create_participant,
    list_results, create_result,
    get_settings, update_settings, import_results, export_participant_results,
)
from backend.models.eqa_schemas import (
    InstitutionCreate, InstitutionUpdate, InstitutionOut,
    EQAProgramCreate, EQAProgramUpdate, EQAProgramOut,
    EQASampleCreate, EQASampleOut,
    EQAParticipantCreate, EQAParticipantOut,
    EQAResultCreate, EQAResultOut,
    EQAProgramStats, EQASampleStat, EQAInstitutionSummary,
    EQASettingsOut, EQASettingsUpdate,
)

router = APIRouter(prefix="/eqa", tags=["eqa"])


# ── Institutions ───────────────────────────────────────────────────────

@router.get("/institutions", response_model=list[InstitutionOut])
def api_list_institutions(db: Session = Depends(get_db)):
    return list_institutions(db)


@router.post("/institutions", response_model=InstitutionOut, status_code=201)
def api_create_institution(body: InstitutionCreate, db: Session = Depends(get_db)):
    return create_institution(db, body.model_dump())


@router.get("/institutions/{inst_id}", response_model=InstitutionOut)
def api_get_institution(inst_id: str, db: Session = Depends(get_db)):
    inst = get_institution(db, inst_id)
    if not inst:
        raise HTTPException(404, "机构不存在")
    return inst


@router.put("/institutions/{inst_id}", response_model=InstitutionOut)
def api_update_institution(inst_id: str, body: InstitutionUpdate, db: Session = Depends(get_db)):
    inst = update_institution(db, inst_id, body.model_dump(exclude_unset=True))
    if not inst:
        raise HTTPException(404, "机构不存在")
    return inst


@router.delete("/institutions/{inst_id}", status_code=204)
def api_delete_institution(inst_id: str, db: Session = Depends(get_db)):
    if not delete_institution(db, inst_id):
        raise HTTPException(404, "机构不存在")


# ── Programs ───────────────────────────────────────────────────────────

@router.get("/programs", response_model=list[EQAProgramOut])
def api_list_programs(db: Session = Depends(get_db)):
    return list_programs(db)


@router.post("/programs", response_model=EQAProgramOut, status_code=201)
def api_create_program(body: EQAProgramCreate, db: Session = Depends(get_db)):
    return create_program(db, body.model_dump())


@router.get("/programs/{prog_id}", response_model=EQAProgramOut)
def api_get_program(prog_id: str, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    return prog


@router.put("/programs/{prog_id}", response_model=EQAProgramOut)
def api_update_program(prog_id: str, body: EQAProgramUpdate, db: Session = Depends(get_db)):
    prog = update_program(db, prog_id, body.model_dump(exclude_unset=True))
    if not prog:
        raise HTTPException(404, "计划不存在")
    return prog


# ── Samples ────────────────────────────────────────────────────────────

@router.get("/programs/{prog_id}/samples", response_model=list[EQASampleOut])
def api_list_samples(prog_id: str, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    return list_samples(db, prog_id)


@router.post("/programs/{prog_id}/samples", response_model=EQASampleOut, status_code=201)
def api_create_sample(prog_id: str, body: EQASampleCreate, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    return create_sample(db, prog_id, body.model_dump())


# ── Participants ───────────────────────────────────────────────────────

@router.get("/programs/{prog_id}/participants", response_model=list[EQAParticipantOut])
def api_list_participants(prog_id: str, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    return [
        _participant_out(p)
        for p in list_participants(db, prog_id)
    ]


def _participant_out(p) -> EQAParticipantOut:
    return EQAParticipantOut(
        id=p.id,
        program_id=p.program_id,
        institution_id=p.institution_id,
        institution_name=p.institution.name if p.institution else "",
        lab_code=p.lab_code,
        status=p.status,
        created_at=p.created_at,
    )


@router.post("/programs/{prog_id}/participants", response_model=EQAParticipantOut, status_code=201)
def api_create_participant(prog_id: str, body: EQAParticipantCreate, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    p = create_participant(db, prog_id, body.model_dump())
    return _participant_out(p)


# ── Results ────────────────────────────────────────────────────────────

@router.get("/programs/{prog_id}/results", response_model=list[EQAResultOut])
def api_list_results(prog_id: str, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    return [
        _result_out(r)
        for r in list_results(db, prog_id)
    ]


def _result_out(r) -> EQAResultOut:
    inst_name = ""
    inst_id = ""
    if r.participant and r.participant.institution:
        inst_name = r.participant.institution.name
        inst_id = r.participant.institution_id
    return EQAResultOut(
        id=r.id,
        program_id=r.program_id,
        sample_id=r.sample_id,
        participant_id=r.participant_id,
        institution_id=inst_id,
        institution_name=inst_name,
        reported_value=r.reported_value,
        method=r.method,
        instrument=r.instrument,
        z_score=r.z_score,
        grade=r.grade,
        reported_at=r.reported_at,
    )


@router.post("/programs/{prog_id}/results", response_model=EQAResultOut, status_code=201)
def api_create_result(prog_id: str, body: EQAResultCreate, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")
    r = create_result(db, prog_id, body.model_dump())
    return _result_out(r)


# ── Stats ──────────────────────────────────────────────────────────────

@router.get("/programs/{prog_id}/stats", response_model=EQAProgramStats)
def api_eqa_stats(prog_id: str, db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")

    samples = list_samples(db, prog_id)
    participants_raw = list_participants(db, prog_id)
    results_raw = list_results(db, prog_id)

    participants = [_participant_out(p) for p in participants_raw]
    results = [_result_out(r) for r in results_raw]

    sample_stats: list[EQASampleStat] = []
    for s in samples:
        vals = [r.reported_value for r in results if r.sample_id == s.id]
        n = len(vals)
        mean_val = round(statistics.mean(vals), 3) if n >= 2 else (vals[0] if n == 1 else 0.0)
        sd_val = round(statistics.stdev(vals), 3) if n >= 2 else 0.0
        cv_val = round((sd_val / mean_val) * 100, 1) if mean_val else 0.0
        sample_results = [r for r in results if r.sample_id == s.id]
        sample_stats.append(EQASampleStat(
            sample_id=s.id, sample_code=s.sample_code, item_name=s.item_name,
            target_value=s.target_value, target_sd=s.target_sd,
            n=n, mean=mean_val, sd=sd_val, cv=cv_val,
            results=sample_results,
        ))

    inst_summary: list[EQAInstitutionSummary] = []
    names = sorted(set(r.institution_name for r in results))
    for name in names:
        inst_results = [r for r in results if r.institution_name == name]
        total = len(inst_results)
        satisfactory = sum(1 for r in inst_results if r.grade == "满意")
        questionable = sum(1 for r in inst_results if r.grade == "可疑")
        unsatisfactory = sum(1 for r in inst_results if r.grade == "不满意")
        pass_rate = round((satisfactory / total) * 100, 1) if total else 0.0
        inst_summary.append(EQAInstitutionSummary(
            institution_name=name, total=total,
            satisfactory=satisfactory, questionable=questionable,
            unsatisfactory=unsatisfactory, pass_rate=pass_rate,
        ))

    return EQAProgramStats(
        program=EQAProgramOut.model_validate(prog),
        sample_stats=sample_stats,
        institution_summary=inst_summary,
    )


# ════════════════════════════════════════════════════════════════════════
# Settings — 角色 & 连通配置
# ════════════════════════════════════════════════════════════════════════

@router.get("/settings", response_model=EQASettingsOut)
def api_get_settings(db: Session = Depends(get_db)):
    return get_settings(db)


@router.put("/settings", response_model=EQASettingsOut)
def api_update_settings(body: EQASettingsUpdate, db: Session = Depends(get_db)):
    return update_settings(db, body.model_dump(exclude_unset=True))


# ════════════════════════════════════════════════════════════════════════
# Import — 组织者批量导入参评结果 (CSV/Excel)
# ════════════════════════════════════════════════════════════════════════

@router.post("/programs/{prog_id}/import")
def api_import_results(prog_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        # Normalize column names (strip BOM, whitespace)
        normalized = {k.strip().lstrip("\ufeff"): v.strip() for k, v in row.items()}
        # Accept either Chinese or English column names
        mapped = {
            "institution_name": normalized.get("institution_name")
                              or normalized.get("机构名称")
                              or normalized.get("参评机构", ""),
            "lab_code": normalized.get("lab_code") or normalized.get("实验室编号", ""),
            "sample_code": normalized.get("sample_code") or normalized.get("样品编号", ""),
            "reported_value": normalized.get("reported_value") or normalized.get("回报值", "0"),
            "method": normalized.get("method") or normalized.get("方法", ""),
            "instrument": normalized.get("instrument") or normalized.get("仪器", ""),
        }
        if mapped["institution_name"] and mapped["sample_code"]:
            rows.append(mapped)

    result = import_results(db, prog_id, rows)
    return result


# ════════════════════════════════════════════════════════════════════════
# Export — 参评机构导出结果 (参与者下载，可按机构名筛选)
# ════════════════════════════════════════════════════════════════════════

@router.get("/programs/{prog_id}/export")
def api_export_results(prog_id: str, institution: str = "", db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")

    if not institution:
        raise HTTPException(400, "请提供 institution 参数（机构名称）")

    rows = export_participant_results(db, prog_id, institution.strip())
    return rows


# ════════════════════════════════════════════════════════════════════════
# Participant Portal — 公开参评门户 (带 access code 校验)
# ════════════════════════════════════════════════════════════════════════

@router.get("/portal/{prog_id}")
def api_portal_info(prog_id: str, access: str = "", db: Session = Depends(get_db)):
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")

    settings = get_settings(db)
    if settings.portal_enabled != "是":
        raise HTTPException(403, "参评门户未启用")
    if settings.portal_access and access != settings.portal_access:
        raise HTTPException(403, "访问码错误")

    samples = list_samples(db, prog_id)
    participants = list_participants(db, prog_id)

    return {
        "program": EQAProgramOut.model_validate(prog).model_dump(),
        "samples": [EQASampleOut.model_validate(s).model_dump() for s in samples],
        "participants": [_participant_out(p).model_dump() for p in participants],
    }


@router.post("/portal/{prog_id}/submit")
def api_portal_submit(prog_id: str, body: dict, access: str = "", db: Session = Depends(get_db)):
    """Public participant result submission.
    Body: {institution_name, results: [{sample_id, reported_value, method, instrument}]}
    """
    prog = get_program(db, prog_id)
    if not prog:
        raise HTTPException(404, "计划不存在")

    settings = get_settings(db)
    if settings.portal_enabled != "是":
        raise HTTPException(403, "参评门户未启用")
    if settings.portal_access and access != settings.portal_access:
        raise HTTPException(403, "访问码错误")

    inst_name = body.get("institution_name", "").strip()
    if not inst_name:
        raise HTTPException(400, "缺少 institution_name")

    items = body.get("results", [])
    if not items:
        raise HTTPException(400, "缺少 results 列表")

    rows = []
    for item in items:
        rows.append({
            "institution_name": inst_name,
            "lab_code": body.get("lab_code", ""),
            "sample_code": "",  # Will be resolved by sample_id below
            "reported_value": item.get("reported_value", 0),
            "method": item.get("method", ""),
            "instrument": item.get("instrument", ""),
        })

    # Resolve sample_id to sample_code for import function
    samples_map = {s.id: s.sample_code for s in list_samples(db, prog_id)}
    for row, item in zip(rows, items):
        sid = item.get("sample_id", "")
        row["sample_code"] = samples_map.get(sid, "")

    result = import_results(db, prog_id, rows)
    return result
