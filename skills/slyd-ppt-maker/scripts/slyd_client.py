#!/usr/bin/env python3
"""Minimal dependency-free client for the SLYD asynchronous Agent API."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile


DEFAULT_BASE_URL = "https://slyd.top"
MIN_POLL_SECONDS = 30
TERMINAL_FAILURES = {"failed", "canceled", "expired"}
ALLOWED_FILE_FIELDS = {
    "smart_refactor": {"file", "files", "template", "style_reference"},
    "deep_restore": {"file", "files", "images", "template", "style_reference"},
    "pptx_beautify": {"file", "documents", "images", "template", "style_reference"},
}


class SlydError(RuntimeError):
    def __init__(self, message, *, status=None, payload=None, retry_after=None):
        super().__init__(message)
        self.status = status
        self.payload = payload or {}
        self.retry_after = retry_after


def _json_bytes(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _print_json(payload):
    sys.stdout.buffer.write(_json_bytes(payload) + b"\n")


def _retry_after(headers, payload, fallback=MIN_POLL_SECONDS):
    raw = headers.get("Retry-After") if headers else None
    candidates = (raw, payload.get("retry_after") if isinstance(payload, dict) else None)
    for candidate in candidates:
        try:
            return max(MIN_POLL_SECONDS, int(float(candidate)))
        except (TypeError, ValueError):
            continue
    return max(MIN_POLL_SECONDS, int(fallback))


def _decode_response(response):
    raw = response.read()
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        preview = raw[:200].decode("utf-8", errors="replace")
        raise SlydError(f"SLYD returned a non-JSON response: {preview}") from exc


def _multipart(fields, files):
    boundary = f"----slyd-{uuid.uuid4().hex}"
    body = bytearray()

    def add_line(value=b""):
        body.extend(value if isinstance(value, bytes) else str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for name, value in fields:
        add_line(f"--{boundary}")
        add_line(f'Content-Disposition: form-data; name="{name}"')
        add_line()
        add_line(value)

    for field, path in files:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        add_line(f"--{boundary}")
        add_line(
            f'Content-Disposition: form-data; name="{field}"; filename="{path.name}"'
        )
        add_line(f"Content-Type: {mime}")
        add_line()
        body.extend(path.read_bytes())
        body.extend(b"\r\n")

    add_line(f"--{boundary}--")
    return bytes(body), f"multipart/form-data; boundary={boundary}"


class SlydClient:
    def __init__(self, base_url, api_key=None, timeout=120):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    @classmethod
    def from_env(cls, *, require_key=True, timeout=120):
        base_url = os.environ.get("SLYD_API_BASE", DEFAULT_BASE_URL).strip()
        api_key = os.environ.get("SLYD_API_KEY", "").strip()
        if require_key and not api_key:
            raise SlydError(
                "SLYD_API_KEY is not set. Configure it outside Codex chat before continuing."
            )
        return cls(base_url, api_key or None, timeout=timeout)

    def request(self, method, path, *, data=None, headers=None, require_key=True):
        request_headers = {"Accept": "application/json", **(headers or {})}
        if require_key:
            if not self.api_key:
                raise SlydError("This request requires SLYD_API_KEY")
            request_headers["X-SLYD-API-Key"] = self.api_key
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=data, headers=request_headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return _decode_response(response), response.headers
        except urllib.error.HTTPError as exc:
            try:
                payload = _decode_response(exc)
            except SlydError:
                payload = {}
            message = payload.get("message") or f"SLYD request failed with HTTP {exc.code}"
            raise SlydError(
                message,
                status=exc.code,
                payload=payload,
                retry_after=_retry_after(exc.headers, payload),
            ) from exc
        except urllib.error.URLError as exc:
            raise SlydError(f"Unable to reach SLYD at {self.base_url}: {exc.reason}") from exc

    def health(self):
        payload, _ = self.request("GET", "/api/health", require_key=False)
        return payload

    def ensure_queue_available(self):
        health = self.health()
        flags = health.get("feature_flags") or {}
        missing = [
            name
            for name in ("user_agent_api", "user_agent_api_queue")
            if not flags.get(name)
        ]
        if missing:
            raise SlydError(
                f"SLYD Agent API is not available at {self.base_url}; disabled: {', '.join(missing)}"
            )
        return health

    def submit(self, mode, fields, files, idempotency_key):
        self.ensure_queue_available()
        body, content_type = _multipart([("mode", mode), *fields], files)
        payload, _ = self.request(
            "POST",
            "/api/agent/v1/jobs",
            data=body,
            headers={
                "Content-Type": content_type,
                "Idempotency-Key": idempotency_key,
            },
        )
        return payload

    def status(self, job_id):
        payload, headers = self.request("GET", f"/api/agent/v1/jobs/{job_id}")
        return payload, headers

    def cancel(self, job_id):
        payload, _ = self.request("DELETE", f"/api/agent/v1/jobs/{job_id}")
        return payload


def _parse_key_value(values, label):
    result = []
    for raw in values or []:
        if "=" not in raw:
            raise SlydError(f"{label} must use NAME=VALUE: {raw}")
        name, value = raw.split("=", 1)
        name = name.strip()
        if not name:
            raise SlydError(f"{label} name cannot be empty")
        result.append((name, value))
    return result


def _parse_files(mode, values):
    allowed = ALLOWED_FILE_FIELDS[mode]
    files = []
    for field, raw_path in _parse_key_value(values, "--file"):
        if field not in allowed:
            raise SlydError(
                f"File field '{field}' is not supported for {mode}; use {sorted(allowed)}"
            )
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise SlydError(f"Input file does not exist: {path}")
        files.append((field, path))
    if not files:
        raise SlydError("At least one --file FIELD=/absolute/path is required")
    if mode == "pptx_beautify":
        primary = [path for field, path in files if field == "file"]
        if len(primary) != 1 or primary[0].suffix.lower() != ".pptx":
            raise SlydError("pptx_beautify requires exactly one PPTX in field 'file'")
    return files


def validate_pptx(path):
    required = {"[Content_Types].xml", "ppt/presentation.xml"}
    try:
        with zipfile.ZipFile(path) as archive:
            missing = required - set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        raise SlydError(f"Downloaded file is not a valid PPTX ZIP: {path}") from exc
    if missing:
        raise SlydError(f"Downloaded PPTX is missing required entries: {sorted(missing)}")


def download_pptx(url, output, timeout=600):
    output = Path(output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.openxmlformats-officedocument.presentationml.presentation"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, output.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
    except (urllib.error.URLError, OSError) as exc:
        output.unlink(missing_ok=True)
        raise SlydError(f"Unable to download PPTX: {exc}") from exc
    try:
        validate_pptx(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return output


def wait_for_job(client, job_id, *, output=None, timeout=7200):
    deadline = time.monotonic() + timeout
    delay = MIN_POLL_SECONDS
    while True:
        if time.monotonic() >= deadline:
            raise SlydError(f"Timed out waiting for job {job_id}; query the same job later")
        time.sleep(delay)
        try:
            payload, headers = client.status(job_id)
        except SlydError as exc:
            if exc.status == 429:
                delay = exc.retry_after or MIN_POLL_SECONDS
                continue
            raise

        status = payload.get("status")
        if status == "completed":
            url = payload.get("download_url")
            if not url:
                raise SlydError(f"Job {job_id} completed without download_url", payload=payload)
            if output:
                saved = download_pptx(url, output)
                payload["saved_path"] = str(saved)
            return payload
        if status in TERMINAL_FAILURES:
            message = payload.get("last_error_message") or f"Job ended as {status}"
            raise SlydError(message, payload=payload)
        delay = _retry_after(headers, payload, delay)


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout in seconds")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Check SLYD API feature flags")

    submit = subparsers.add_parser("submit", help="Create an asynchronous SLYD job")
    submit.add_argument("--mode", choices=sorted(ALLOWED_FILE_FIELDS), required=True)
    submit.add_argument("--idempotency-key", default=None)
    submit.add_argument("--file", action="append", default=[], metavar="FIELD=PATH")
    submit.add_argument("--field", action="append", default=[], metavar="NAME=VALUE")

    status = subparsers.add_parser("status", help="Get one job status")
    status.add_argument("job_id")

    cancel = subparsers.add_parser("cancel", help="Request job cancellation")
    cancel.add_argument("job_id")

    wait = subparsers.add_parser("wait", help="Wait for a job and optionally save its PPTX")
    wait.add_argument("job_id")
    wait.add_argument("--output")
    wait.add_argument("--wait-timeout", type=int, default=7200)

    download = subparsers.add_parser("download", help="Download and validate a PPTX URL")
    download.add_argument("url")
    download.add_argument("output")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "health":
            client = SlydClient.from_env(require_key=False, timeout=args.timeout)
            _print_json(client.health())
            return 0

        if args.command == "download":
            output = download_pptx(args.url, args.output, timeout=max(args.timeout, 600))
            _print_json({"success": True, "saved_path": str(output)})
            return 0

        client = SlydClient.from_env(timeout=args.timeout)
        if args.command == "submit":
            idempotency_key = args.idempotency_key or str(uuid.uuid4())
            print(f"Idempotency-Key: {idempotency_key}", file=sys.stderr, flush=True)
            payload = client.submit(
                args.mode,
                _parse_key_value(args.field, "--field"),
                _parse_files(args.mode, args.file),
                idempotency_key,
            )
        elif args.command == "status":
            payload, _ = client.status(args.job_id)
        elif args.command == "cancel":
            payload = client.cancel(args.job_id)
        else:
            payload = wait_for_job(
                client, args.job_id, output=args.output, timeout=args.wait_timeout
            )
        _print_json(payload)
        return 0
    except SlydError as exc:
        error = {
            "success": False,
            "message": str(exc),
            "status": exc.status,
            "retry_after": exc.retry_after,
        }
        if exc.payload:
            error["details"] = exc.payload
        _print_json(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
