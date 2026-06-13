"""Settings endpoints -- AI config and lab profile."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.settings_models import AppSetting

router = APIRouter(tags=["settings"])


# ── Request / Response models ──────────────────────────────

class AiConfig(BaseModel):
    api_key_set: bool = False
    base_url: str = ""
    model: str = "gpt-4o"


class SetApiKeyRequest(BaseModel):
    api_key: str


class SetBaseUrlRequest(BaseModel):
    base_url: str


class SetModelRequest(BaseModel):
    model: str


class LabProfile(BaseModel):
    lab_name: str = ""
    lab_code: str = ""
    institution: str = ""
    address: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    accreditation: str = ""


class LabProfileUpdate(BaseModel):
    lab_name: str | None = None
    lab_code: str | None = None
    institution: str | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    accreditation: str | None = None


# ── Helpers ─────────────────────────────────────────────────

def _get_setting(db: Session, key: str) -> str | None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else None


def _set_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=key, value=value))
    db.commit()


def _del_setting(db: Session, key: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        db.delete(row)
        db.commit()


# ── AI Config Endpoints ─────────────────────────────────────

@router.get("/settings/ai-config", response_model=AiConfig)
def get_ai_config(db: Session = Depends(get_db)):
    return AiConfig(
        api_key_set=bool(_get_setting(db, "openai_api_key")),
        base_url=_get_setting(db, "openai_base_url") or "",
        model=_get_setting(db, "openai_model") or "gpt-4o",
    )


@router.put("/settings/api-key")
def set_api_key(req: SetApiKeyRequest, db: Session = Depends(get_db)):
    _set_setting(db, "openai_api_key", req.api_key)
    return {"ok": True}


@router.delete("/settings/api-key")
def remove_api_key(db: Session = Depends(get_db)):
    _del_setting(db, "openai_api_key")
    return {"ok": True}


@router.put("/settings/base-url")
def set_base_url(req: SetBaseUrlRequest, db: Session = Depends(get_db)):
    _set_setting(db, "openai_base_url", req.base_url)
    return {"ok": True}


@router.put("/settings/model")
def set_model(req: SetModelRequest, db: Session = Depends(get_db)):
    _set_setting(db, "openai_model", req.model)
    return {"ok": True}


# ── Lab Profile Endpoints ───────────────────────────────────

LAB_KEYS = [
    "lab_name", "lab_code", "institution", "address",
    "contact_name", "contact_email", "contact_phone", "accreditation",
]


@router.get("/settings/lab-profile", response_model=LabProfile)
def get_lab_profile(db: Session = Depends(get_db)):
    vals = {k: _get_setting(db, k) or "" for k in LAB_KEYS}
    return LabProfile(**vals)


@router.put("/settings/lab-profile")
def update_lab_profile(req: LabProfileUpdate, db: Session = Depends(get_db)):
    for field, value in req.model_dump(exclude_unset=True).items():
        if value is not None:
            _set_setting(db, field, value)
    return {"ok": True}
