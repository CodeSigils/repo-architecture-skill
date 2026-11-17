"""Run isolated positive and negative repo-architecture Codex evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

from evaluation_contract import fixture_path_is_safe, load_case_contract

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/repo-architecture-skill"
POSITIVE_PROMPT = ROOT / "evals/codex/positive-prompt.md"
PROMPTS = {
    "architecture-duplicate-mirror": POSITIVE_PROMPT,
    "markdown-only-discovery-skill": ROOT / "evals/codex/markdown-only-prompt.md",
}
NEGATIVE_PROMPT = ROOT / "evals/codex/negative-prompt.md"
RESULT_SCHEMA = ROOT / "evals/codex/result.schema.json"
CASE_DIR = ROOT / "evals/cases"
GRADER = ROOT / "scripts/grade-codex-regression.py"
CONTRACT_INPUTS = (
    SKILL_DIR,
    POSITIVE_PROMPT,
    NEGATIVE_PROMPT,
    RESULT_SCHEMA,
    GRADER,
    ROOT / "scripts/evaluation_contract.py",
)
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def positive_int(value: str) -> int:
    """Parse a strictly positive CLI integer."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def timestamp(value: datetime) -> str:
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def contract_digest(case_id: str) -> str:
    """Hash the payload and deterministic inputs that define one evaluated contract."""
    digest = hashlib.sha256()
    paths = (*CONTRACT_INPUTS, CASE_DIR / f"{case_id}.json")
    for input_path in paths:
        files = (
            sorted(path for path in input_path.rglob("*") if path.is_file()) if input_path.is_dir() else [input_path]
        )
        for path in files:
            relative = path.relative_to(ROOT).as_posix().encode("utf-8")
            digest.update(len(relative).to_bytes(4, "big"))
            digest.update(relative)
            content = path.read_bytes()
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
    return digest.hexdigest()


def working_tree_dirty() -> bool:
    """Return whether evaluation inputs may differ from the recorded Git revision."""
    return bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    )


def run_checked(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({' '.join(command)}): {detail}")


def prepare_fixture(root: Path, case_id: str) -> None:
    """Create an isolated fixture from a shared case contract."""
    if root.exists():
        raise FileExistsError(f"fixture path already exists: {root}")
    contract = load_case_contract(CASE_DIR, case_id)
    installed = root / ".agents/skills/repo-architecture-skill"
    installed.parent.mkdir(parents=True)
    shutil.copytree(SKILL_DIR, installed)
    fixture_root = root.resolve()
    for relative, content in contract.fixture_files.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(fixture_root) or path == fixture_root:
            raise ValueError(f"unsafe fixture path: {relative!r}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    run_checked(["git", "init", "-b", "main"], root)
    run_checked(["git", "config", "user.name", "Codex Eval"], root)
    run_checked(["git", "config", "user.email", "codex-eval@example.invalid"], root)
    run_checked(["git", "config", "commit.gpgsign", "false"], root)
    run_checked(["git", "add", "."], root)
    run_checked(["git", "commit", "-m", "feat: add example skill"], root)


def codex_version(binary: str) -> str | None:
    try:
        result = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (result.stdout.strip() or result.stderr.strip()) if result.returncode == 0 else None


def codex_command(
    binary: str,
    fixture: Path,
    prompt: Path,
    output: Path,
    schema: Path | None = None,
) -> list[str]:
    command = [
        binary,
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--cd",
        str(fixture),
        "--output-last-message",
        str(output),
    ]
    if schema:
        command.extend(["--output-schema", str(schema)])
    command.append(prompt.read_text(encoding="utf-8"))
    return command


def transcript_summary(path: Path) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
    usage = {field: 0 for field in TOKEN_FIELDS}
    completed = False
    model = None
    for event in events:
        if event.get("type") == "turn.completed":
            completed = True
            values = event.get("usage", {})
            if isinstance(values, dict):
                for field in TOKEN_FIELDS:
                    if isinstance(values.get(field), int):
                        usage[field] += values[field]
        if model is None and isinstance(event.get("model"), str):
            model = event["model"]
    return {
        "event_count": len(events),
        "last_event_type": events[-1].get("type") if events else None,
        "turn_completed": completed,
        "model": model,
        "usage": usage if completed else None,
    }


def execute(
    command: list[str],
    transcript: Path,
    stderr_path: Path,
    timeout_seconds: int,
    environment: dict[str, str],
) -> dict[str, Any]:
    started = datetime.now(UTC)
    clock = monotonic()
    transcript.parent.mkdir(parents=True, exist_ok=True)
    status = "completed"
    error = None
    with (
        transcript.open("w", encoding="utf-8") as stdout,
        stderr_path.open("w", encoding="utf-8") as stderr,
    ):
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                text=True,
                check=False,
                timeout=timeout_seconds,
                env=environment,
            )
            if result.returncode:
                status = "failed"
                error = f"Codex exited {result.returncode}"
        except subprocess.TimeoutExpired:
            status = "timeout"
            error = f"Codex exceeded {timeout_seconds}s"
    ended = datetime.now(UTC)
    return {
        "status": status,
        "error": error,
        "started_at": timestamp(started),
        "ended_at": timestamp(ended),
        "duration_seconds": round(monotonic() - clock, 3),
        "transcript": transcript_summary(transcript),
    }


def grade(output_dir: Path, case_id: str) -> int:
    return subprocess.run(
        [
            sys.executable,
            str(GRADER),
            "--positive-result",
            str(output_dir / "positive-result.json"),
            "--negative-result",
            str(output_dir / "negative-result.txt"),
            "--output",
            str(output_dir / "grade.json"),
            "--case-id",
            case_id,
        ],
        cwd=ROOT,
        check=False,
    ).returncode


def run_self_tests() -> int:
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory) / "fixture"
        prepare_fixture(fixture, "architecture-duplicate-mirror")
        assert (fixture / ".agents/skills/repo-architecture-skill/SKILL.md").is_file()
        assert (fixture / "SKILL.md").read_bytes() == (fixture / "skills/example/SKILL.md").read_bytes()
        assert (
            subprocess.run(
                ["git", "status", "--short"],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            == ""
        )
        command = codex_command("codex", fixture, POSITIVE_PROMPT, fixture / "result.json", RESULT_SCHEMA)
        assert command[-3:-1] == ["--output-schema", str(RESULT_SCHEMA)]
        assert json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))["type"] == "object"
        transcript = Path(directory) / "complete.jsonl"
        transcript.write_text(
            "\n".join(
                [
                    json.dumps({"type": "turn.started"}),
                    json.dumps(
                        {
                            "type": "turn.completed",
                            "usage": {"input_tokens": 10, "output_tokens": 2},
                        }
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        summary = transcript_summary(transcript)
        assert summary["turn_completed"] is True
        assert summary["usage"]["input_tokens"] == 10
        try:
            load_case_contract(CASE_DIR, "../escape")
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe case IDs must fail")
        assert fixture_path_is_safe("src/example.py")
        assert not fixture_path_is_safe("../escape.py")
        assert not fixture_path_is_safe("src//example.py")
        assert not fixture_path_is_safe(".")
        assert positive_int("1") == 1
        assert len(contract_digest("architecture-duplicate-mirror")) == 64
        try:
            positive_int("0")
        except argparse.ArgumentTypeError:
            pass
        else:
            raise AssertionError("non-positive timeouts must fail")
    print("PASS: run-codex-regression.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--case-id", choices=sorted(PROMPTS), default="architecture-duplicate-mirror")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Persistent writable CODEX_HOME for the run; credentials remain user-managed.",
    )
    parser.add_argument(
        "--expected-codex-version",
        help="Fail before evaluation unless codex --version contains this text.",
    )
    parser.add_argument("--timeout-seconds", type=positive_int, default=900)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()

    started = datetime.now(UTC)
    clock = monotonic()
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    output_dir = (args.output_dir or ROOT / "artifacts/codex-regression" / run_id).resolve()
    environment = os.environ.copy()
    codex_home = None
    if args.codex_home:
        codex_home = args.codex_home.expanduser().resolve()
        codex_home.mkdir(parents=True, exist_ok=True)
        environment["CODEX_HOME"] = str(codex_home)
    elif environment.get("CODEX_HOME"):
        codex_home = Path(environment["CODEX_HOME"]).expanduser().resolve()
    observed_version = codex_version(args.codex_bin)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    fixture = args.fixture_dir.resolve() if args.fixture_dir else None
    summary: dict[str, Any] = {
        "schema_version": 1,
        "status": "running",
        "started_at": timestamp(started),
        "ended_at": None,
        "duration_seconds": None,
        "repository_revision": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip(),
        "working_tree_dirty": working_tree_dirty(),
        "evaluation_contract_sha256": contract_digest(args.case_id),
        "runtime": {
            "codex_cli": observed_version,
            "codex_home": str(codex_home) if codex_home else None,
        },
        "timeout_seconds": args.timeout_seconds,
        "scenarios": {},
        "grade": {"status": "not_run", "path": str(output_dir / "grade.json")},
        "artifacts": {
            "positive_transcript": str(output_dir / "positive-transcript.jsonl"),
            "positive_result": str(output_dir / "positive-result.json"),
            "positive_stderr": str(output_dir / "positive-stderr.log"),
            "negative_transcript": str(output_dir / "negative-transcript.jsonl"),
            "negative_result": str(output_dir / "negative-result.txt"),
            "negative_stderr": str(output_dir / "negative-stderr.log"),
        },
        "error": None,
    }
    exit_code = 1
    try:
        if args.expected_codex_version and (
            observed_version is None or args.expected_codex_version not in observed_version
        ):
            raise RuntimeError(
                f"codex version mismatch: expected {args.expected_codex_version!r}, observed {observed_version!r}"
            )
        if fixture is None and args.prepare_only:
            fixture = output_dir / "fixture"
        elif fixture is None:
            temporary = tempfile.TemporaryDirectory(prefix="repo-architecture-eval-")
            fixture = Path(temporary.name) / "fixture"
        prepare_fixture(fixture, args.case_id)
        if args.prepare_only:
            print(f"Prepared Codex evaluation fixture: {fixture}")
            return 0
        output_dir.mkdir(parents=True, exist_ok=True)
        cases = (
            ("positive", PROMPTS[args.case_id], RESULT_SCHEMA),
            ("negative", NEGATIVE_PROMPT, None),
        )
        for name, prompt, schema in cases:
            suffix = "json" if name == "positive" else "txt"
            result_path = output_dir / f"{name}-result.{suffix}"
            scenario = execute(
                codex_command(args.codex_bin, fixture, prompt, result_path, schema),
                output_dir / f"{name}-transcript.jsonl",
                output_dir / f"{name}-stderr.log",
                args.timeout_seconds,
                environment,
            )
            summary["scenarios"][name] = scenario
            if scenario["status"] != "completed":
                raise RuntimeError(f"{name} scenario {scenario['status']}")
        grade_code = grade(output_dir, args.case_id)
        summary["grade"]["status"] = "passed" if grade_code == 0 else "failed"
        summary["status"] = summary["grade"]["status"]
        exit_code = grade_code
        print(f"Codex evaluation artifacts: {output_dir}")
    except (FileExistsError, OSError, RuntimeError, TypeError, ValueError) as exc:
        summary["status"] = "failed"
        summary["error"] = str(exc)
        print(f"ERROR: {exc}", file=sys.stderr)
    finally:
        ended = datetime.now(UTC)
        summary["ended_at"] = timestamp(ended)
        summary["duration_seconds"] = round(monotonic() - clock, 3)
        if not args.prepare_only:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "run-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        if temporary:
            temporary.cleanup()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
