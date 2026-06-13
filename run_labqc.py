"""
LabQC Windows Launcher
=======================
Standalone entry point for Windows deployment. Starts the FastAPI server
and opens the default browser to the local dashboard.

Usage:
    python run_labqc.py [--port PORT] [--no-browser]

When bundled with PyInstaller, this is the main entry point.
"""

import os
import sys
import argparse
import threading
import webbrowser

def main():
    parser = argparse.ArgumentParser(description="LabQC 实验室质控管理系统")
    parser.add_argument("--port", type=int, default=8000, help="HTTP 端口 (默认: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址 (默认: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    # Enable standalone mode (serves frontend + SPA fallback)
    os.environ["LABQC_STANDALONE"] = "1"

    import uvicorn

    url = f"http://{args.host}:{args.port}"

    if not args.no_browser:
        # Open browser after a short delay so the server is ready
        def open_browser():
            import time
            time.sleep(1.5)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    print(f"\n  LabQC 启动中...")
    print(f"  本地访问: {url}")
    print(f"  按 Ctrl+C 停止服务\n")

    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )

if __name__ == "__main__":
    main()
