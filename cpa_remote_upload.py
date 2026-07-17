from __future__ import annotations

import json
import mimetypes
import uuid
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def normalize_cpamp_base(base: str) -> str:
    b = (base or "").strip().rstrip("/")
    if not b:
        return ""
    # Users often paste the management UI URL.
    for junk in (
        "/management.html#",
        "/management.html",
        "/management#",
        "/management",
        "/#",
    ):
        if b.lower().endswith(junk):
            b = b[: -len(junk)].rstrip("/")
            break
    if b.endswith("#"):
        b = b[:-1].rstrip("/")
    return b


def resolve_cpamp_upload_config(cfg: dict | None) -> tuple[bool, str, str]:
    cfg = cfg or {}
    enabled = bool(cfg.get("cpa_remote_upload_enabled", False))
    base = normalize_cpamp_base(
        str(cfg.get("cpa_remote_base") or cfg.get("grok2api_remote_base") or "")
    )
    key = str(
        cfg.get("cpa_remote_management_key")
        or cfg.get("grok2api_remote_app_key")
        or ""
    ).strip()
    return enabled, base, key


def upload_auth_file_to_cpamp(
    path: str | Path,
    *,
    base: str,
    management_key: str,
    timeout: float = 60.0,
    log: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Upload one xai-*.json to CPA Manager Plus via multipart /v0/management/auth-files."""
    log = log or (lambda m: None)
    src = Path(path)
    base = normalize_cpamp_base(base)
    key = (management_key or "").strip()
    if not base or not key:
        return {"ok": False, "error": "missing base or management key"}
    if not src.is_file():
        return {"ok": False, "error": f"file not found: {src}"}

    url = f"{base}/v0/management/auth-files"
    data = src.read_bytes()
    boundary = f"----codex{uuid.uuid4().hex}"
    filename = src.name
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += (
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
    ).encode()
    body += b"Content-Type: application/json\r\n\r\n"
    body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "grok-regkit-cpamp-upload",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = int(getattr(resp, "status", 200) or 200)
    except HTTPError as exc:
        err_body = ""
        try:
            err_body = exc.read().decode("utf-8", "replace")
        except Exception:
            err_body = str(exc)
        log(f"[cpa] CPAMP upload HTTP {exc.code}: {err_body[:300]}")
        return {"ok": False, "error": f"HTTP {exc.code}: {err_body[:300]}", "url": url}
    except URLError as exc:
        log(f"[cpa] CPAMP upload network error: {exc}")
        return {"ok": False, "error": f"network: {exc}", "url": url}
    except Exception as exc:  # noqa: BLE001
        log(f"[cpa] CPAMP upload failed: {exc}")
        return {"ok": False, "error": str(exc), "url": url}

    parsed: Any = raw
    try:
        parsed = json.loads(raw) if raw else {}
    except Exception:
        parsed = {"raw": raw}

    ok = status < 400
    if isinstance(parsed, dict) and str(parsed.get("status", "")).lower() in {"ok", "success"}:
        ok = True
    if ok:
        log(f"[cpa] CPAMP upload ok -> {filename}")
    else:
        log(f"[cpa] CPAMP upload unexpected response: {raw[:300]}")
    return {"ok": ok, "status": status, "response": parsed, "url": url, "file": filename}


def maybe_upload_to_cpamp(
    path: str | Path,
    cfg: dict | None,
    log: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    enabled, base, key = resolve_cpamp_upload_config(cfg)
    if not enabled:
        return {"ok": False, "skipped": True, "reason": "disabled"}
    return upload_auth_file_to_cpamp(path, base=base, management_key=key, log=log)
