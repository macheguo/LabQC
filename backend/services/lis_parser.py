"""HL7 v2.x message parser for LabQC LIS interface.

Parses standard HL7 v2.x messages with MLLP (Minimal Lower Layer Protocol) 
framing. Supported message types: ORU^R01 (observation result).

MLLP frame: <SB>message<EB><CR>
<SB> = 0x0B (VT), <EB> = 0x1C (FS), <CR> = 0x0D
"""

import re
from dataclasses import dataclass, field
from typing import Optional

# ── MLLP framing ──────────────────────────────────────────────────────────
SB = b'\x0b'
EB = b'\x1c'
CR = b'\x0d'


@dataclass
class Hl7Message:
    """Parsed HL7 v2.x message."""
    message_type: str = ""           # e.g. "ORU^R01"
    sending_app: str = ""
    sending_facility: str = ""
    message_control_id: str = ""
    hl7_version: str = ""
    patient_id: str = ""
    patient_name: str = ""
    order_number: str = ""
    test_code: str = ""
    test_name: str = ""
    results: list = field(default_factory=list)  # [{"code","name","value","unit","ref_range","abnormal"}]

    # Raw segments preserved for debugging
    raw_segments: list = field(default_factory=list)
    raw_message: str = ""


def parse_hl7_message(raw: str) -> Optional[Hl7Message]:
    """
    Parse a raw HL7 v2.x message string (without MLLP framing bytes).
    Returns Hl7Message or None if the message cannot be parsed.
    """
    if not raw or not raw.startswith("MSH"):
        return None

    segments = _split_segments(raw)
    msg = Hl7Message(raw_segments=segments, raw_message=raw)

    for seg in segments:
        fields = seg.split("|")
        seg_type = fields[0] if fields else ""

        if seg_type == "MSH":
            _parse_msh(msg, fields)
        elif seg_type == "PID":
            _parse_pid(msg, fields)
        elif seg_type == "OBR":
            _parse_obr(msg, fields)
        elif seg_type == "OBX":
            _parse_obx(msg, fields)

    return msg


def _split_segments(raw: str) -> list:
    """Split HL7 message into segments. Segments are separated by \\r."""
    parts = raw.replace("\r\n", "\r").split("\r")
    return [p.strip() for p in parts if p.strip()]


def _parse_msh(msg: Hl7Message, fields: list):
    """Parse MSH segment. Handles variable field positions by content matching."""
    if len(fields) > 2:
        msg.sending_app = fields[2]
    if len(fields) > 3:
        msg.sending_facility = fields[3]

    # Message type: look for "^" containing field (e.g., "ORU^R01")
    for f in fields[8:12]:
        if f and "^" in f and any(f.startswith(p) for p in ("ORU", "ACK", "ADT", "ORM", "MDM")):
            msg.message_type = f
            break

    # Message control ID: the field right after message type
    try:
        type_idx = fields.index(msg.message_type)
        if type_idx + 1 < len(fields):
            msg.message_control_id = fields[type_idx + 1]
    except ValueError:
        pass

    # HL7 version: last field that looks like a version number
    for f in reversed(fields):
        if f and f[0].isdigit() and "." in f:
            msg.hl7_version = f
            break


def _parse_pid(msg: Hl7Message, fields: list):
    """Parse PID segment."""
    if len(fields) > 3:
        msg.patient_id = fields[3]
    if len(fields) > 5:
        # "^" separates last^first
        name_parts = fields[5].split("^")
        msg.patient_name = " ".join(reversed(name_parts)) if len(name_parts) > 1 else fields[5]


def _parse_obr(msg: Hl7Message, fields: list):
    """Parse OBR segment."""
    if len(fields) > 2:
        msg.order_number = fields[2]
    if len(fields) > 4:
        # "^" separates code^name
        test = fields[4].split("^")
        msg.test_code = test[0] if len(test) > 0 else ""
        msg.test_name = test[1] if len(test) > 1 else ""


def _parse_obx(msg: Hl7Message, fields: list):
    """Parse OBX segment."""
    if len(fields) < 6:
        return

    # OBX|1|NM|TEST_CODE^TEST_NAME||RESULT|UNIT|REF_RANGE|FLAG
    test = fields[3].split("^") if len(fields) > 3 else ["", ""]
    result = {
        "set_id": fields[1] if len(fields) > 1 else "",
        "value_type": fields[2] if len(fields) > 2 else "",
        "code": test[0] if test else "",
        "name": test[1] if len(test) > 1 else "",
        "value": fields[5] if len(fields) > 5 else "",
        "unit": fields[6] if len(fields) > 6 else "",
        "ref_range": fields[7] if len(fields) > 7 else "",
        "abnormal": fields[8] if len(fields) > 8 else "",
    }
    msg.results.append(result)


# ── MLLP framing ──────────────────────────────────────────────────────────

def frame_ack(message_control_id: str, sending_app: str = "LabQC") -> bytes:
    """Build an HL7 ACK message with MLLP framing."""
    import datetime
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    ack = (
        f"MSH|^~\\&|{sending_app}||LIS||{now}||ACK||P|2.3.1\r"
        f"MSA|AA|{message_control_id}\r"
    )
    return SB + ack.encode("ascii") + EB + CR


def frame_nack(message_control_id: str, error_text: str = "Parse error",
               sending_app: str = "LabQC") -> bytes:
    """Build an HL7 NACK message with MLLP framing."""
    import datetime
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    nack = (
        f"MSH|^~\\&|{sending_app}||LIS||{now}||ACK||P|2.3.1\r"
        f"MSA|AE|{message_control_id}|{error_text}\r"
    )
    return SB + nack.encode("ascii") + EB + CR


def unwrap_mllp(data: bytes) -> Optional[str]:
    """Extract HL7 message from MLLP-framed bytes."""
    if not data:
        return None
    # Find <SB> ... <EB><CR>
    start = data.find(SB)
    if start == -1:
        # Message may not have SB prefix
        start = 0
    else:
        start += 1

    end = data.find(EB + CR, start)
    if end == -1:
        # Try just CR
        end = data.find(CR, start)
        if end == -1:
            end = len(data)

    raw = data[start:end].decode("ascii", errors="replace")
    return raw.strip()


def build_ack(message_control_id: str) -> bytes:
    """Alias for frame_ack."""
    return frame_ack(message_control_id)
