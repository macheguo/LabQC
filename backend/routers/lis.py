"""LIS interface router — HL7 MLLP listener + REST config API.

Listens for HL7 v2.x messages over TCP (MLLP), parses them, and logs 
received results. Configuration is stored via the AppSetting key-value store.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.settings_models import AppSetting
from backend.services.lis_parser import (
    parse_hl7_message,
    unwrap_mllp,
    build_ack,
)

logger = logging.getLogger("labqc.lis")
router = APIRouter(prefix="/lis", tags=["lis"])


# ── In-memory listener state ──────────────────────────────────────────────

_listener_task: Optional[asyncio.Task] = None
_listener_server: Optional[asyncio.AbstractServer] = None
_received_messages: list = []  # last 200 messages (ring buffer)
_current_status: str = "stopped"  # stopped | running | error
_current_error: str = ""


# ── Request / Response models ─────────────────────────────────────────────

class LisConfig(BaseModel):
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 5020
    status: str = "stopped"
    error: str = ""


class LisMessage(BaseModel):
    id: int
    timestamp: str
    message_type: str
    sending_app: str
    patient_id: str
    test_code: str
    test_name: str
    results: list
    raw: str


class LisTestRequest(BaseModel):
    """Send a test HL7 message to verify parsing."""
    raw_message: str


class LisTestResponse(BaseModel):
    success: bool
    parsed: Optional[dict] = None
    error: Optional[str] = None


# ── Settings keys ─────────────────────────────────────────────────────────

LIS_ENABLED_KEY = "lis_enabled"
LIS_HOST_KEY = "lis_host"
LIS_PORT_KEY = "lis_port"


def _get_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else default


def _set_setting(db: Session, key: str, value: str):
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        row.value = value
        row.updated_at = datetime.now(timezone.utc)
    else:
        db.add(AppSetting(key=key, value=value))
    db.commit()


# ── REST endpoints ────────────────────────────────────────────────────────

@router.get("/config", response_model=LisConfig)
def get_lis_config(db: Session = Depends(get_db)):
    """Get current LIS configuration."""
    return LisConfig(
        enabled=_get_setting(db, LIS_ENABLED_KEY, "false").lower() == "true",
        host=_get_setting(db, LIS_HOST_KEY, "0.0.0.0"),
        port=int(_get_setting(db, LIS_PORT_KEY, "5020") or "5020"),
        status=_current_status,
        error=_current_error,
    )


@router.put("/config", response_model=LisConfig)
def update_lis_config(config: LisConfig, db: Session = Depends(get_db)):
    """Update LIS configuration. If enabled=True and listener stopped, starts listener."""
    _set_setting(db, LIS_ENABLED_KEY, "true" if config.enabled else "false")
    if config.host:
        _set_setting(db, LIS_HOST_KEY, config.host)
    if config.port:
        _set_setting(db, LIS_PORT_KEY, str(config.port))

    # Start/stop listener based on enabled flag
    if config.enabled and _listener_task is None:
        _start_listener(config.host or "0.0.0.0", config.port or 5020)
    elif not config.enabled and _listener_task is not None:
        _stop_listener()

    return get_lis_config(db)


@router.post("/test-parse", response_model=LisTestResponse)
def test_parse_hl7(req: LisTestRequest):
    """Test-parse an HL7 message without connecting to LIS."""
    try:
        parsed = parse_hl7_message(req.raw_message.strip())
        if parsed is None:
            return LisTestResponse(success=False, error="无法解析：消息格式不正确（应以 MSH 开头）")
        return LisTestResponse(
            success=True,
            parsed={
                "message_type": parsed.message_type,
                "sending_app": parsed.sending_app,
                "patient_id": parsed.patient_id,
                "patient_name": parsed.patient_name,
                "order_number": parsed.order_number,
                "test_code": parsed.test_code,
                "test_name": parsed.test_name,
                "results": parsed.results,
                "segments": parsed.raw_segments,
            },
        )
    except Exception as e:
        return LisTestResponse(success=False, error=str(e))


@router.get("/messages", response_model=list[LisMessage])
def get_recent_messages(limit: int = 20):
    """Get recently received LIS messages."""
    return _received_messages[-limit:]


@router.post("/restart")
def restart_listener(db: Session = Depends(get_db)):
    """Restart the LIS listener."""
    _stop_listener()
    host = _get_setting(db, LIS_HOST_KEY, "0.0.0.0")
    port = int(_get_setting(db, LIS_PORT_KEY, "5020") or "5020")
    _start_listener(host, port)
    return {"status": _current_status, "error": _current_error}


# ── MLLP TCP listener ─────────────────────────────────────────────────────

def _start_listener(host: str, port: int):
    """Start the MLLP TCP listener in the background."""
    global _listener_task, _current_status, _current_error

    if _listener_task is not None:
        return

    async def _run_listener():
        global _listener_server, _current_status, _current_error
        try:
            _listener_server = await asyncio.start_server(
                _handle_connection, host, port
            )
            _current_status = "running"
            _current_error = ""
            logger.info(f"LIS MLLP listener started on {host}:{port}")

            async with _listener_server:
                await _listener_server.serve_forever()
        except OSError as e:
            _current_status = "error"
            _current_error = str(e)
            logger.error(f"LIS listener failed: {e}")
        except asyncio.CancelledError:
            pass

    try:
        loop = asyncio.get_event_loop()
        _listener_task = loop.create_task(_run_listener())
    except RuntimeError:
        logger.warning("No event loop available, LIS listener deferred")


def _stop_listener():
    """Stop the MLLP TCP listener."""
    global _listener_task, _listener_server, _current_status

    if _listener_server:
        _listener_server.close()
        _listener_server = None

    if _listener_task:
        _listener_task.cancel()
        _listener_task = None

    _current_status = "stopped"
    logger.info("LIS MLLP listener stopped")


async def _handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle a single TCP connection — read MLLP-framed HL7 message, ACK, store."""
    addr = writer.get_extra_info("peername")
    logger.info(f"LIS connection from {addr}")

    try:
        # Read until <EB><CR> (0x1C 0x0D)
        data = bytearray()
        while True:
            chunk = await asyncio.wait_for(reader.read(4096), timeout=30)
            if not chunk:
                break
            data.extend(chunk)
            # Check for MLLP end marker
            if data.find(b'\x1c\x0d') != -1:
                break

        if not data:
            return

        raw = unwrap_mllp(bytes(data))
        if not raw:
            return

        logger.info(f"HL7 message received: {raw[:200]}...")

        # Parse
        parsed = parse_hl7_message(raw)

        # Store in ring buffer (max 200)
        msg_entry = {
            "id": len(_received_messages) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_type": parsed.message_type if parsed else "unknown",
            "sending_app": parsed.sending_app if parsed else "",
            "patient_id": parsed.patient_id if parsed else "",
            "test_code": parsed.test_code if parsed else "",
            "test_name": parsed.test_name if parsed else "",
            "results": parsed.results if parsed else [],
            "raw": raw,
        }
        _received_messages.append(msg_entry)
        if len(_received_messages) > 200:
            _received_messages.pop(0)

        # Send ACK
        msg_id = parsed.message_control_id if parsed else "000000"
        ack = build_ack(msg_id)
        writer.write(ack)
        await writer.drain()

    except asyncio.TimeoutError:
        logger.warning(f"LIS connection from {addr} timed out")
    except Exception as e:
        logger.error(f"LIS handler error: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
