"""License activation API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.license import check_license, verify_license, activate, get_machine_id, LICENSE_FILE, LICENSE_DIR

router = APIRouter(prefix="/license", tags=["license"])


class ActivateRequest(BaseModel):
    token: str


@router.get("/status")
def license_status():
    """Check if license is valid."""
    valid, msg = check_license()
    if valid:
        return {"valid": True, "message": msg, "machine_id": get_machine_id()}
    return {"valid": False, "message": msg, "machine_id": get_machine_id()}


@router.post("/activate")
def license_activate(req: ActivateRequest):
    """Activate with a license token."""
    lic = verify_license(req.token)
    if lic is None:
        raise HTTPException(400, "许可证无效（签名校验失败）")

    import time
    if lic.expires > 0 and time.time() > lic.expires:
        raise HTTPException(400, "许可证已过期")

    mid = get_machine_id()
    if lic.machine_id and lic.machine_id != mid:
        raise HTTPException(400, "许可证与当前机器不匹配")

    if not activate(lic, mid):
        raise HTTPException(400, "激活次数已达上限")

    # Re-sign with updated activations
    from backend.license import sign_license
    priv_key_file = LICENSE_DIR / "private_key.pem"
    if priv_key_file.exists():
        token = sign_license(lic, priv_key_file.read_text())
    else:
        token = req.token  # keep original (activations update not critical for client)

    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LICENSE_FILE.write_text(token)
    return {"valid": True, "message": f"激活成功: {lic.customer}"}
