#!/usr/bin/env python3
"""Install this checkout's read-only dashboard as a per-user macOS service."""

import argparse
import os
from pathlib import Path
import plistlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time


LABEL = "com.dav-rob.model-use-dashboard"
DEFAULT_PORT = 48173


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("background installation requires macOS; run server.py directly elsewhere")
    if not 1024 <= args.port <= 65535:
        parser.error("choose a port between 1024 and 65535")

    root = Path(__file__).resolve().parent.parent
    server = root / "dashboard/server.py"
    if not server.is_file():
        parser.error("dashboard/server.py is missing")
    # Homebrew's stable bin link survives Python patch-version upgrades.
    python = shutil.which("python3") or sys.executable
    agent = Path.home() / "Library/LaunchAgents" / f"{LABEL}.plist"
    logs = Path.home() / "Library/Logs/model-use-dashboard"
    if agent.is_symlink() or logs.is_symlink():
        parser.error("refusing a symbolic link at the service configuration or log directory")

    domain = f"gui/{os.getuid()}"
    service = f"{domain}/{LABEL}"
    loaded = subprocess.run(
        ["launchctl", "print", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0
    if not loaded:
        try:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", args.port))
        except OSError:
            parser.error(f"port {args.port} is already in use; choose another --port")

    config = {
        "Label": LABEL,
        "ProgramArguments": [python, str(server), "--port", str(args.port)],
        "WorkingDirectory": str(root),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 10,
        "EnvironmentVariables": {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"},
        "StandardOutPath": str(logs / "stdout.log"),
        "StandardErrorPath": str(logs / "stderr.log"),
    }
    agent.parent.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, mode=0o700, exist_ok=True)
    if loaded:
        subprocess.run(["launchctl", "bootout", service], check=True)
    with tempfile.NamedTemporaryFile(dir=agent.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            plistlib.dump(config, handle)
            handle.flush()
            os.fchmod(handle.fileno(), 0o644)
            temporary.replace(agent)
        finally:
            temporary.unlink(missing_ok=True)
    # launchd may still be releasing a just-booted-out job when bootstrap starts.
    # Retry that specific transient result briefly; do not ask for root access.
    for attempt in range(10):
        result = subprocess.run(
            ["launchctl", "bootstrap", domain, str(agent)], capture_output=True, text=True
        )
        if result.returncode == 0:
            break
        if result.returncode != 5 or attempt == 9:
            raise SystemExit("Could not start the dashboard service; inspect its logs and launchctl status")
        time.sleep(0.3)
    print(f"Dashboard service installed: http://127.0.0.1:{args.port}/")


if __name__ == "__main__":
    main()
