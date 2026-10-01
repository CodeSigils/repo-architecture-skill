"""Verify reachable HTTP(S) URLs referenced by docs and skill files.

The URL list lives in docs/evidence-urls.json so the research evidence base has
one machine-readable source of truth. If the doc adds or removes URLs, update
that manifest instead of editing this script's code.

Usage:
  python3 scripts/verify-urls.py
  python3 scripts/verify-urls.py --self-test

Outputs a table of URL -> final status with drift annotations.
Exit code 0 = all URLs match documented expected state.
Exit code 1 = one or more URLs differs from the manifest.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import urlsplit

from evidence_manifest import EvidenceManifest, load_evidence_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"
MAX_RESPONSE_BYTES = 6 * 1024 * 1024
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1
TRANSIENT_HTTP_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})


@dataclass(frozen=True)
class UrlCheckResult:
    """Result of a single URL check."""

    status: int | str
    content: str | None


def check_required_text(body: str, required_text: list[str]) -> str:
    """Return a body-validation label without exposing response content."""
    if any(anchor not in body for anchor in required_text):
        return "MISSING_ANCHOR"
    return "ANCHORS_OK"


def check_url(
    url: str,
    content_type: str | None = None,
    required_text: list[str] | None = None,
) -> UrlCheckResult:
    """Return UrlCheckResult for one URL.

    Read response bodies only when JSON or semantic anchors need validation.
    """
    # Keep the scheme boundary next to urlopen so future callers cannot
    # accidentally introduce file/custom-URL access.
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return UrlCheckResult("ERROR", "invalid URL scheme or host")
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "repo-architecture-skill-url-verify"},
    )

    for attempt in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                status = response.status
                if status in TRANSIENT_HTTP_STATUSES and attempt < MAX_ATTEMPTS - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                    continue
                body: str | None = None
                if content_type == "json" or required_text:
                    try:
                        payload = response.read(MAX_RESPONSE_BYTES + 1)
                        if len(payload) > MAX_RESPONSE_BYTES:
                            return UrlCheckResult(status, "CONTENT_TOO_LARGE")
                        body = payload.decode("utf-8")
                    except UnicodeDecodeError:
                        return UrlCheckResult(status, "INVALID_ENCODING")
                if content_type == "json" and body is not None:
                    try:
                        json.loads(body)
                    except (json.JSONDecodeError, ValueError):
                        return UrlCheckResult(status, "INVALID_JSON")
                if required_text and body is not None:
                    return UrlCheckResult(status, check_required_text(body, required_text))
                if content_type == "json":
                    return UrlCheckResult(status, "VALID")
                return UrlCheckResult(status, None)

        except urllib.error.HTTPError as exc:
            if exc.code in TRANSIENT_HTTP_STATUSES and attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            return UrlCheckResult(exc.code, f"HTTP {exc.code}")
        except urllib.error.URLError as exc:
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            return UrlCheckResult("ERROR", str(exc.reason))
        except TimeoutError:
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            return UrlCheckResult("TIMEOUT", "timeout")
        except ValueError as exc:
            return UrlCheckResult("ERROR", f"invalid URL: {exc}")

    raise AssertionError("URL check exhausted without a result")


def classify_status(status: int | str, expected_statuses: list[int]) -> str:
    """Return OK when status matches the manifest, else DRIFT."""
    if isinstance(status, int) and status in expected_statuses:
        return "OK"
    return "DRIFT"


def check_self_test() -> None:
    """Run internal self-tests for the validation logic."""
    # Test classify_status
    assert classify_status(200, [200]) == "OK"
    assert classify_status(404, [200]) == "DRIFT"
    assert classify_status("ERROR", [200]) == "DRIFT"
    assert classify_status(200, [200, 201]) == "OK"
    assert classify_status(201, [200, 201]) == "OK"
    print("  PASS  classify_status")
    assert check_required_text("alpha beta", ["alpha", "beta"]) == "ANCHORS_OK"
    assert check_required_text("alpha beta", ["gamma"]) == "MISSING_ANCHOR"
    print("  PASS  check_required_text")

    oversized_response = MagicMock()
    oversized_response.__enter__.return_value = oversized_response
    oversized_response.status = 200
    oversized_response.read.return_value = b"x" * (MAX_RESPONSE_BYTES + 1)
    with patch("urllib.request.urlopen", return_value=oversized_response):
        assert check_url("https://example.com", required_text=["anchor"]).content == "CONTENT_TOO_LARGE"
    print("  PASS  bounded response reading")
    assert check_url("file:///tmp/secret").content == "invalid URL scheme or host"
    print("  PASS  URL scheme boundary")

    retry_response = MagicMock()
    retry_response.__enter__.return_value = retry_response
    retry_response.status = 200
    with (
        patch("urllib.request.urlopen", side_effect=[urllib.error.URLError("temporary"), retry_response]),
        patch("time.sleep") as sleep,
    ):
        assert check_url("https://example.com").status == 200
        sleep.assert_called_once_with(RETRY_BACKOFF_SECONDS)
    print("  PASS  transient URL retry")

    # Test evidence manifest loading via the shared loader
    with tempfile.TemporaryDirectory() as directory:
        manifest_dir = Path(directory)

        def load_case(payload: object) -> EvidenceManifest:
            manifest_path = manifest_dir / "manifest.json"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            return load_evidence_manifest(manifest_path)

        base = {
            "name": "example",
            "url": "https://example.com",
            "expected_statuses": [200],
            "source_section": "README.md",
            "status": "active",
            "last_verified": "2026-07-29",
        }
        manifest = load_case({"version": 3, "urls": [base]})
        assert len(manifest.entries) == 1
        entry = manifest.entries[0]
        assert entry.name == "example"
        assert entry.monitor is True
        assert entry.content_type is None
        print("  PASS  evidence manifest valid")

        invalid_cases: list[tuple[str, object]] = [
            ("non-object top level", ["not", "an", "object"]),
            ("missing version", {"urls": [base]}),
            ("non-integer version", {"version": 3.0, "urls": [base]}),
            ("empty urls", {"version": 3, "urls": []}),
            ("missing name", {"version": 3, "urls": [{k: v for k, v in base.items() if k != "name"}]}),
            ("non-int status", {"version": 3, "urls": [{**base, "expected_statuses": [True]}]}),
            ("non-http url", {"version": 3, "urls": [{**base, "url": "ftp://example.com"}]}),
            ("non-bool monitor", {"version": 3, "urls": [{**base, "monitor": 0}]}),
            ("unknown status", {"version": 3, "urls": [{**base, "status": "acitve"}]}),
            ("monitored retired entry", {"version": 3, "urls": [{**base, "status": "retired"}]}),
            ("duplicate name", {"version": 3, "urls": [base, {**base, "url": "https://example.org"}]}),
            ("duplicate url", {"version": 3, "urls": [base, {**base, "name": "second"}]}),
            ("non-str last_verified", {"version": 3, "urls": [{**base, "last_verified": 123}]}),
            ("bad content_type", {"version": 3, "urls": [{**base, "content_type": "text"}]}),
            (
                "missing source_section",
                {"version": 3, "urls": [{k: v for k, v in base.items() if k != "source_section"}]},
            ),
        ]
        for label, payload in invalid_cases:
            try:
                load_case(payload)
            except ValueError:
                print(f"  PASS  evidence manifest rejects {label}")
            else:
                raise AssertionError(f"evidence manifest {label} must fail")

    print("  PASS  verify-urls.py self-tests")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        check_self_test()
        return 0

    try:
        manifest = load_evidence_manifest(MANIFEST_PATH)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("=== Evidence URL Re-verification ===")
    print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Content':<16s} {'Note':<10s}")
    print("-" * 82)

    drift_found = False
    for entry in sorted(manifest.entries, key=lambda item: item.name.casefold()):
        if entry.status != "active" or not entry.monitor:
            print(f"  {entry.name:<30s} {'—':<8s} {'immutable':<12s} {'—':<16s} SKIPPED")
            continue

        result = check_url(entry.url, entry.content_type, list(entry.required_text))
        expected = list(entry.expected_statuses)
        note = classify_status(result.status, expected)
        if note == "DRIFT":
            drift_found = True

        # Content check trumps status check for JSON endpoints
        content_label = result.content or "—"
        if result.content in {"CONTENT_TOO_LARGE", "INVALID_ENCODING", "INVALID_JSON", "MISSING_ANCHOR"}:
            note = "BROKEN"
            drift_found = True

        expected_text = "/".join(str(code) for code in expected)
        marker = "  ← DRIFT" if note == "DRIFT" else ""
        marker = "  ← BROKEN" if note == "BROKEN" else marker
        print(
            f"  {entry.name:<30s} {result.status!s:<8s} {expected_text:<12s} {content_label:<16s} {note:<10s}{marker}"
        )

    if drift_found:
        print("\nRESULT: Drift or broken content detected — one or more URLs differ from docs/evidence-urls.json.")
        print("Update the manifest and research doc together after investigating the changed URL state.")
        return 1

    print("\nRESULT: All URLs match documented expected state and content validates OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
