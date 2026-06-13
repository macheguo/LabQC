"""LabQC License System — RSA-signed licenses with hardware binding."""
import hashlib
import hmac
import json
import os
import platform
import subprocess
import time
from base64 import urlsafe_b64encode, urlsafe_b64decode
from dataclasses import dataclass, asdict
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature


LICENSE_DIR = Path(os.environ.get("LABQC_LICENSE_DIR", Path(__file__).resolve().parent / "data"))
LICENSE_FILE = LICENSE_DIR / "license.lic"
PUBLIC_KEY_FILE = LICENSE_DIR / "public_key.pem"


# ── machine fingerprint ──────────────────────────────────────────
def get_machine_id() -> str:
    """Stable machine identifier (MAC + OS + hostname hash)."""
    try:
        # primary MAC address
        import uuid
        node = uuid.getnode()
        mac = format(node, '02x')
    except Exception:
        mac = platform.node()
    seed = f"{mac}|{platform.system()}|{platform.node()}"
    return hashlib.sha256(seed.encode()).hexdigest()[:16]


# ── key generation ───────────────────────────────────────────────
def generate_key_pair() -> tuple[str, str]:
    """Return (private_key_pem, public_key_pem)."""
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = private.public_key()
    priv_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return priv_pem, pub_pem


# ── load keys ────────────────────────────────────────────────────
def _load_public_key() -> rsa.RSAPublicKey:
    key_bytes = PUBLIC_KEY_FILE.read_bytes()
    return serialization.load_pem_public_key(key_bytes)


# ── license data ─────────────────────────────────────────────────
@dataclass
class LicenseData:
    customer: str       # e.g. "凯思康-呼和浩特第一医院"
    issued: int         # unix timestamp
    expires: int        # unix timestamp (0 = never)
    machine_id: str     # "" = any machine (activation), "hash" = bound
    max_activations: int  # 1 = single machine, 0 = unlimited
    activations: list   # list of activated machine_id hashes

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True).encode()

    @classmethod
    def from_json(cls, data: bytes) -> "LicenseData":
        return cls(**json.loads(data))


# ── sign / verify ────────────────────────────────────────────────
def sign_license(lic: LicenseData, private_key_pem: str) -> str:
    """Sign license data → base64 token."""
    private = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    payload = lic.to_json()
    signature = private.sign(payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    token = urlsafe_b64encode(payload + b"." + signature).decode().rstrip("=")
    return token


def verify_license(token: str) -> LicenseData | None:
    """Parse + verify a license token. Returns LicenseData or None."""
    try:
        raw = urlsafe_b64decode(token + "===")
        payload, signature = raw.split(b".", 1)
        pub = _load_public_key()
        pub.verify(signature, payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return LicenseData.from_json(payload)
    except Exception:
        return None


# ── activation ───────────────────────────────────────────────────
def activate(lic: LicenseData, machine_id: str) -> bool:
    """Bind license to this machine. Returns True if successful."""
    mid_hash = hashlib.sha256(machine_id.encode()).hexdigest()[:16]
    if mid_hash in lic.activations:
        return True  # already activated
    if lic.max_activations > 0 and len(lic.activations) >= lic.max_activations:
        return False  # activation limit reached
    lic.activations.append(mid_hash)
    return True


# ── check ────────────────────────────────────────────────────────
def check_license() -> tuple[bool, str]:
    """Validate stored license. Returns (valid, message)."""
    if not LICENSE_FILE.exists():
        return False, "未找到许可证文件，请激活软件"
    token = LICENSE_FILE.read_text().strip()
    lic = verify_license(token)
    if lic is None:
        return False, "许可证无效（签名校验失败）"
    if lic.expires > 0 and time.time() > lic.expires:
        return False, f"许可证已过期（有效期至 {time.strftime('%Y-%m-%d', time.localtime(lic.expires))}）"
    if lic.machine_id:
        mid = get_machine_id()
        if lic.machine_id != mid:
            return False, "许可证与当前机器不匹配"
    return True, f"已授权: {lic.customer}"
