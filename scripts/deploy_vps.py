#!/usr/bin/env python3
"""Deploy itinerary frontend + API to Tencent Lighthouse VPS.

Usage (PowerShell):
  $env:ITINERARY_SSH_PASSWORD = '...'
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
NGINX_CONF = ROOT / "server" / "nginx-itinerary.conf"
HOST = os.environ.get("ITINERARY_SSH_HOST", "124.222.108.66")
USER = os.environ.get("ITINERARY_SSH_USER", "ubuntu")
PASSWORD = os.environ.get("ITINERARY_SSH_PASSWORD", "")
EDIT_PASSWORD = os.environ.get("ITINERARY_EDIT_PASSWORD", "smallpig")
REMOTE_DIR = "/home/ubuntu/itinerary-api"
WEB_ROOT = "/var/www/itinerary"


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def make_api_tarball() -> bytes:
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


def upload_bytes(sftp: paramiko.SFTPClient, data: bytes, remote: str) -> None:
    with sftp.file(remote, "wb") as f:
        f.write(data)


def main() -> None:
    if not PASSWORD:
        die("Set ITINERARY_SSH_PASSWORD")
    if not LOCAL_APP.exists():
        die(f"missing {LOCAL_APP}")
    index_html = ROOT / "index.html"
    if not index_html.exists():
        die("missing index.html — run generate_html.py first")
    if not NGINX_CONF.exists():
        die(f"missing {NGINX_CONF}")

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
    run(ssh, "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx")
    run(ssh, "node -v && npm -v")
    run(ssh, f"mkdir -p {REMOTE_DIR}/data")
    run(ssh, f"sudo mkdir -p {WEB_ROOT}")

    tarball = make_api_tarball()
    remote_tar = "/tmp/itinerary-api.tgz"
    print(f"Uploading API {len(tarball)} bytes ...")
    upload_bytes(sftp, tarball, remote_tar)
    run(ssh, f"tar -xzf {remote_tar} -C {REMOTE_DIR} && rm -f {remote_tar}")
    run(ssh, f"cd {REMOTE_DIR} && npm install --omit=dev")

    print("Uploading frontend HTML ...")
    upload_bytes(sftp, index_html.read_bytes(), "/tmp/index.html")
    run(ssh, f"sudo mv /tmp/index.html {WEB_ROOT}/index.html")
    run(ssh, f"sudo rm -f {WEB_ROOT}/itinerary.html")
    run(ssh, f"sudo chown -R www-data:www-data {WEB_ROOT}")

    upload_bytes(sftp, NGINX_CONF.read_bytes(), "/tmp/nginx-itinerary.conf")
    run(ssh, "sudo mv /tmp/nginx-itinerary.conf /etc/nginx/sites-available/itinerary")
    run(ssh, "sudo ln -sfn /etc/nginx/sites-available/itinerary /etc/nginx/sites-enabled/itinerary")
    run(ssh, "sudo rm -f /etc/nginx/sites-enabled/default")
    run(ssh, "sudo nginx -t")
    run(ssh, "sudo systemctl enable nginx")
    run(ssh, "sudo systemctl restart nginx")

    env_body = (
        f"PORT=8787\nEDIT_PASSWORD={EDIT_PASSWORD}\nDATA_DIR={REMOTE_DIR}/data\n"
    )
    upload_bytes(sftp, env_body.encode("utf-8"), "/tmp/itinerary-api.env")
    run(ssh, "sudo mv /tmp/itinerary-api.env /etc/itinerary-api.env")
    run(ssh, "sudo chmod 600 /etc/itinerary-api.env")
    run(ssh, f"sudo cp {REMOTE_DIR}/itinerary-api.service /etc/systemd/system/itinerary-api.service")
    run(ssh, "sudo systemctl daemon-reload")
    run(ssh, "sudo systemctl enable itinerary-api")
    run(ssh, "sudo systemctl restart itinerary-api")
    time.sleep(1)
    run(ssh, "sudo systemctl --no-pager --lines=8 status itinerary-api")
    run(ssh, "curl -sS http://127.0.0.1:8787/healthz")
    run(ssh, "curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1/healthz")
    run(ssh, "curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1/")
    run(ssh, "sudo ufw allow 80/tcp || true", check=False)
    run(ssh, "sudo ufw allow 8787/tcp || true", check=False)
    run(ssh, "sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT || true", check=False)

    sftp.close()
    ssh.close()
    print(f"\nOK site: http://{HOST}/")
    print(f"OK api : http://{HOST}/api/itinerary")
    print("若外网不通：腾讯云轻量控制台 → 防火墙 → 放行 TCP 80")


if __name__ == "__main__":
    main()
