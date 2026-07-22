#!/usr/bin/env python3
"""Deploy itinerary-api to a VPS over SSH. Usage:
  set ITINERARY_SSH_PASSWORD=...
  python scripts/deploy_vps.py
"""
from __future__ import annotations

import io
import os
import sys
import tarfile
import time
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
LOCAL_APP = ROOT / "server" / "itinerary-api"
HOST = os.environ.get("ITINERARY_SSH_HOST", "124.222.108.66")
USER = os.environ.get("ITINERARY_SSH_USER", "ubuntu")
PASSWORD = os.environ.get("ITINERARY_SSH_PASSWORD", "")
EDIT_PASSWORD = os.environ.get("ITINERARY_EDIT_PASSWORD", "smallpig")
REMOTE_DIR = "/home/ubuntu/itinerary-api"


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def make_tarball() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for path in LOCAL_APP.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(LOCAL_APP).as_posix()
            if rel.startswith("node_modules/"):
                continue
            if rel.startswith("data/") and rel != "data/.gitkeep":
                continue
            if rel.endswith(".tmp"):
                continue
            tar.add(path, arcname=rel)
    return buf.getvalue()


def run(ssh: paramiko.SSHClient, cmd: str, check: bool = True) -> str:
    print(f"$ {cmd}")
    _stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if out.strip():
        print(out.rstrip())
    if err.strip():
        print(err.rstrip(), file=sys.stderr)
    if check and code != 0:
        die(f"command failed ({code}): {cmd}")
    return out


def main() -> None:
    if not PASSWORD:
        die("Set ITINERARY_SSH_PASSWORD")
    if not LOCAL_APP.exists():
        die(f"missing {LOCAL_APP}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting {USER}@{HOST} ...")
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    sftp = ssh.open_sftp()

    run(ssh, "sudo apt-get update -y")
    run(
        ssh,
        "command -v node >/dev/null || (curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs)",
    )
    run(ssh, "node -v && npm -v")
    run(ssh, f"mkdir -p {REMOTE_DIR}/data")

    tarball = make_tarball()
    remote_tar = "/tmp/itinerary-api.tgz"
    print(f"Uploading {len(tarball)} bytes ...")
    with sftp.file(remote_tar, "wb") as f:
        f.write(tarball)
    run(ssh, f"tar -xzf {remote_tar} -C {REMOTE_DIR} && rm -f {remote_tar}")
    run(ssh, f"cd {REMOTE_DIR} && npm install --omit=dev")

    env_body = (
        f"PORT=8787\nEDIT_PASSWORD={EDIT_PASSWORD}\nDATA_DIR={REMOTE_DIR}/data\n"
    )
    with sftp.file("/tmp/itinerary-api.env", "w") as f:
        f.write(env_body)
    run(ssh, "sudo mv /tmp/itinerary-api.env /etc/itinerary-api.env")
    run(ssh, "sudo chmod 600 /etc/itinerary-api.env")
    run(ssh, f"sudo cp {REMOTE_DIR}/itinerary-api.service /etc/systemd/system/itinerary-api.service")
    run(ssh, "sudo systemctl daemon-reload")
    run(ssh, "sudo systemctl enable itinerary-api")
    run(ssh, "sudo systemctl restart itinerary-api")
    time.sleep(1)
    run(ssh, "sudo systemctl --no-pager status itinerary-api")
    run(ssh, "curl -sS http://127.0.0.1:8787/healthz")
    run(ssh, "sudo ufw allow 8787/tcp || true", check=False)
    run(ssh, "sudo iptables -I INPUT -p tcp --dport 8787 -j ACCEPT || true", check=False)

    sftp.close()
    ssh.close()
    print(f"\nOK API base: http://{HOST}:8787")
    print("若外网仍不通：腾讯云轻量控制台 → 防火墙 → 放行 TCP 8787")


if __name__ == "__main__":
    main()
