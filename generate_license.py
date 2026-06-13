#!/usr/bin/env python3
"""
LabQC License Generator
========================
Generate signed license tokens for customers.

Usage:
  # 1. Generate key pair (one-time)
  python generate_license.py keygen
  
  # 2. Create a license
  python generate_license.py issue --customer "凯思康-呼市一院" --days 365
  
  # 3. Create with machine binding
  python generate_license.py issue --customer "某医院" --days 90 --machine-id abc123def456
  
  # 4. Create with activation limit
  python generate_license.py issue --customer "某客户" --days 180 --max-activations 3

Output: a license token string → send to customer
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backend.license import (
    generate_key_pair, sign_license, LicenseData,
    LICENSE_DIR, PUBLIC_KEY_FILE,
)


def cmd_keygen():
    """Generate RSA key pair and save public key to the app."""
    priv, pub = generate_key_pair()
    # Save private key (KEEP SECRET!)
    priv_path = LICENSE_DIR / "private_key.pem"
    priv_path.parent.mkdir(parents=True, exist_ok=True)
    priv_path.write_text(priv)
    priv_path.chmod(0o600)
    # Save public key (embedded in app)
    PUBLIC_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_KEY_FILE.write_text(pub)
    print(f"✅ 私钥已保存: {priv_path}  (❗ 务必保密，勿提交 Git)")
    print(f"✅ 公钥已保存: {PUBLIC_KEY_FILE}")


def cmd_issue(args):
    """Issue a signed license."""
    priv_path = LICENSE_DIR / "private_key.pem"
    if not priv_path.exists():
        print("❌ 未找到私钥，请先运行: python generate_license.py keygen")
        sys.exit(1)
    private_key = priv_path.read_text()

    now = int(time.time())
    expires = now + args.days * 86400 if args.days > 0 else 0

    lic = LicenseData(
        customer=args.customer,
        issued=now,
        expires=expires,
        machine_id=args.machine_id or "",
        max_activations=args.max_activations,
        activations=[],
    )

    token = sign_license(lic, private_key)

    # Verify
    verified = Path(__file__).resolve().parent
    sys.path.insert(0, str(verified))
    from backend.license import verify_license
    check = verify_license(token)
    assert check is not None, "signature verification failed!"

    exp_str = time.strftime("%Y-%m-%d", time.localtime(expires)) if expires else "永久"
    print(f"✅ 许可证已生成")
    print(f"   客户: {args.customer}")
    print(f"   到期: {exp_str}")
    print(f"   机器绑定: {'是' if args.machine_id else '否（首次激活绑定）'}")
    print(f"   最大激活次数: {'不限' if args.max_activations == 0 else args.max_activations}")
    print()
    print(f"许可证密钥（发给客户）:")
    print(f"{'='*60}")
    print(token)
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="LabQC License Generator")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("keygen", help="Generate RSA key pair")

    issue = sub.add_parser("issue", help="Issue a signed license")
    issue.add_argument("--customer", required=True, help="Customer name")
    issue.add_argument("--days", type=int, default=365, help="Days until expiry (0=never)")
    issue.add_argument("--machine-id", default="", help="Pre-bind to machine ID")
    issue.add_argument("--max-activations", type=int, default=1, help="Max activations (0=unlimited)")

    args = parser.parse_args()
    if args.cmd == "keygen":
        cmd_keygen()
    elif args.cmd == "issue":
        cmd_issue(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
