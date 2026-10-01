"""Validate the canonical skill payload and behavioral contract."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import NoReturn

import yaml
from evaluation_contract import load_case_contract, object_mapping
from evidence_manifest import load_evidence_manifest

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "repo-architecture-skill"
SKILL = SKILL_DIR / "SKILL.md"
REF_DIR = SKILL_DIR / "references"
README = ROOT / "README.md"
EVAL = ROOT / "evals" / "cases" / "architecture-audit.json"
CODEX_SCHEMA = ROOT / "evals" / "codex" / "result.schema.json"
CODEX_POSITIVE = ROOT / "evals" / "codex" / "positive-prompt.md"
CODEX_NEGATIVE = ROOT / "evals" / "codex" / "negative-prompt.md"
CODEX_CASE_IDS = {"architecture-duplicate-mirror", "markdown-only-discovery-skill"}
EVIDENCE = ROOT / "docs" / "evidence-urls.json"
PORTABILITY_CONTRACT = ROOT / "docs" / "portability-contract.md"
SECURITY = ROOT / "SECURITY.md"
GITIGNORE = ROOT / ".gitignore"
CI = ROOT / ".github" / "workflows" / "ci.yml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
PYPROJECT = ROOT / "pyproject.toml"
UV_LOCK = ROOT / "uv.lock"
PAYLOAD_LICENSE = SKILL_DIR / "LICENSE.txt"
ROOT_LICENSE = ROOT / "LICENSE"

ALLOWED_FIELDS = {"name", "description"}
REQUIRED_SECTIONS = {
    "## Procedure",
    "## Repository Archetypes",
    "## Four Boundaries",
    "## Reference Routing",
    "## Completion Checklist",
}
ARCHETYPES = {
    "markdown-only-skill",
    "multi-skill-pack",
    "tool-backed-skill",
    "operational-skill",
    "distribution-monorepo",
    "non-skill-control",
}
BOUNDARIES = {
    "authoring_source",
    "runtime_payload",
    "install_artifact",
    "maintainer_infrastructure",
}
LINK_RE = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PINNED_ACTION_RE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
SKILLS_REF_SPEC = "git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref"
MATRIX_PYTHON_VERSION = "${{ matrix.python-version }}"
RUFF_CHECK_COMMAND = "uv run --locked ruff check scripts .github/scripts"
RUFF_FORMAT_COMMAND = "uv run --locked ruff format --check scripts .github/scripts"
TYPE_CHECK_COMMAND = "uv run --locked ty check scripts .github/scripts"
CANONICAL_VALIDATION_COMMAND = "uv run --locked python scripts/validate.py"
EXPECTED_REFERENCES = {
    "dev-workflow-patterns.md",
    "file-swamp-patterns.md",
    "npm-publishing-for-agent-skills.md",
    "operational-patterns.md",
    "payload-manifest-pattern.md",
    "portability-migration.md",
    "portability-patterns.md",
    "skill-repo-audit-procedure.md",
}
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |ENCRYPTED )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("credential-bearing URL", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")),
)
DANGEROUS_RUNTIME_PATTERNS = (
    ("destructive Git reset", re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE)),
    ("forced Git push", re.compile(r"\bgit\s+push\b[^\n]*(?:--force(?:-with-lease)?|-f\b)", re.IGNORECASE)),
    ("privilege escalation", re.compile(r"(?:^|[`\s])sudo\s+", re.IGNORECASE | re.MULTILINE)),
    (
        "verification bypass",
        re.compile(r"--no-verify\b|\bbypass(?:ing)?\s+(?:approval|review|checks?)\b", re.IGNORECASE),
    ),
    (
        "raw secret-file output",
        re.compile(r"\b(?:cat|type|get-content)\s+[^\n]*(?:\.env\b|credentials\b|id_rsa\b)", re.IGNORECASE),
    ),
    (
        "raw commit-body output",
        re.compile(r"\bgit\s+(?:log|show)\b[^\n]*(?:--format=.?%B|--pretty=.?%B)", re.IGNORECASE),
    ),
)


def fail(message: str) -> NoReturn:
    raise ValueError(message)


def mapping_list(value: object, context: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not value:
        fail(f"{context}: expected a non-empty list")
    return [object_mapping(item, context) for item in value]


def validate_preflight_steps(steps: list[dict[str, object]]) -> None:
    required_commands = (
        RUFF_CHECK_COMMAND,
        RUFF_FORMAT_COMMAND,
        TYPE_CHECK_COMMAND,
        CANONICAL_VALIDATION_COMMAND,
    )
    positions: list[int] = []
    for command in required_commands:
        matches = [index for index, step in enumerate(steps) if step.get("run") == command]
        if len(matches) != 1:
            fail(f"{CI}: deterministic checks must run exactly one {command!r} step")
        positions.append(matches[0])
    if positions != sorted(positions):
        fail(f"{CI}: lint, formatting, and type checks must precede canonical validation")


def parse_skill(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path}: missing opening YAML frontmatter delimiter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"{path}: unclosed YAML frontmatter") from exc
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        fail(f"{path}: frontmatter must be a YAML mapping")
    return data, body


def validate_frontmatter(data: dict[str, object], path: Path) -> None:
    extra = set(data) - ALLOWED_FIELDS
    if extra:
        fail(f"{path}: unsupported frontmatter fields: {sorted(extra)}")
    if set(data) != ALLOWED_FIELDS:
        fail(f"{path}: frontmatter must contain exactly name and description")
    name = data["name"]
    description = data["description"]
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        fail(f"{path}: invalid skill name")
    if name != path.parent.name:
        fail(f"{path}: skill name must match directory {path.parent.name!r}")
    if not isinstance(description, str) or not description.strip():
        fail(f"{path}: description must be a non-empty string")
    if len(description) > 1024:
        fail(f"{path}: description exceeds 1024 characters")
    if len(description.split()) < 12:
        fail(f"{path}: description is too short to trigger reliably")


def local_link_errors(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
        target = target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if relative and not (path.parent / relative).resolve().is_relative_to(root.resolve()):
            errors.append(f"{path}: local link escapes repository: {target}")
        elif relative and not (path.parent / relative).exists():
            errors.append(f"{path}: missing local link target: {target}")
    return errors


def validate_payload_inventory() -> list[Path]:
    allowed_files = {SKILL, PAYLOAD_LICENSE, *(REF_DIR / name for name in EXPECTED_REFERENCES)}
    allowed_directories = {SKILL_DIR, REF_DIR}
    observed_files: set[Path] = set()
    for path in sorted(SKILL_DIR.rglob("*")):
        if path.is_symlink():
            fail(f"{path}: symlinks are not allowed in the runtime payload")
        if path.is_dir():
            if path not in allowed_directories:
                fail(f"{path}: unexpected runtime payload directory")
            continue
        if path not in allowed_files:
            fail(f"{path}: unexpected runtime payload file")
        if path.stat().st_mode & 0o111:
            fail(f"{path}: executable files are not allowed in the runtime payload")
        observed_files.add(path)
    missing = allowed_files - observed_files
    if missing:
        fail(f"runtime payload inventory is missing: {[str(path.relative_to(SKILL_DIR)) for path in sorted(missing)]}")
    if PAYLOAD_LICENSE.read_text(encoding="utf-8") != ROOT_LICENSE.read_text(encoding="utf-8"):
        fail(f"{PAYLOAD_LICENSE}: must match the repository LICENSE exactly")
    return sorted(observed_files)


def validate_skill() -> None:
    if not SKILL.exists():
        fail(f"missing canonical runtime entrypoint: {SKILL}")
    data, body = parse_skill(SKILL)
    validate_frontmatter(data, SKILL)
    for section in sorted(REQUIRED_SECTIONS):
        if section not in body:
            fail(f"{SKILL}: missing section {section!r}")
    if len(SKILL.read_text(encoding="utf-8").splitlines()) > 500:
        fail(f"{SKILL}: exceeds the 500-line runtime budget")

    payload_files = validate_payload_inventory()
    references = [path for path in payload_files if path.parent == REF_DIR]
    for reference in references:
        route = f"references/{reference.name}"
        if route not in body:
            fail(f"{SKILL}: does not route {route}")

    for path in [SKILL, *references]:
        errors = local_link_errors(path, SKILL_DIR)
        if errors:
            fail("\n".join(errors))


def repository_text_files() -> list[Path]:
    try:
        output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT, stderr=subprocess.DEVNULL)
        paths = [ROOT / item.decode() for item in output.split(b"\0") if item]
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        paths = [
            path
            for path in ROOT.rglob("*")
            if path.is_file() and not {".git", ".venv"}.intersection(path.relative_to(ROOT).parts)
        ]
    required = (SECURITY, GITIGNORE, CI, DEPENDABOT, PYPROJECT, UV_LOCK)
    return sorted({path for path in [*paths, *required] if path.is_file()})


def secret_types(text: str) -> list[str]:
    return [label for label, pattern in SECRET_PATTERNS if pattern.search(text)]


def validate_repository_secrets() -> None:
    findings: list[str] = []
    for path in repository_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label in secret_types(text):
            findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        fail("secret-like material detected (values suppressed):\n" + "\n".join(findings))


def validate_runtime_trust() -> None:
    findings: list[str] = []
    for path in [SKILL, *(REF_DIR / name for name in sorted(EXPECTED_REFERENCES))]:
        text = path.read_text(encoding="utf-8")
        for label, pattern in DANGEROUS_RUNTIME_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        fail("unsafe runtime instruction detected:\n" + "\n".join(findings))


def python_release(value: str) -> tuple[int, int]:
    """Parse a major.minor Python release into a comparable tuple."""
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)", value.strip())
    if match is None:
        fail(f"Python version must be a major.minor release: {value!r}")
    return int(match.group(1)), int(match.group(2))


def minimum_python_release() -> tuple[int, int]:
    """Read the Python floor from pyproject so CI policy tracks packaging metadata."""
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    declared = str(object_mapping(project.get("project"), f"{PYPROJECT}: project").get("requires-python", "")).strip()
    if not re.fullmatch(r">=[0-9]+\.[0-9]+", declared):
        fail(f"{PYPROJECT}: requires-python must be a simple lower bound")
    return python_release(declared.removeprefix(">="))


def validate_security_contract() -> None:
    text = SECURITY.read_text(encoding="utf-8")
    required = (
        "## Supported Versions",
        "## Reporting a Vulnerability",
        "/security/advisories/new",
        "## Repository Security Scope",
        "## Shipped Payload Inventory",
        "## Runtime Trust Guarantees",
        "## Sensitive Evidence",
        "## Maintainer Security Checklist",
        "Last reviewed:",
    )
    for phrase in required:
        if phrase not in text:
            fail(f"{SECURITY}: missing {phrase!r}")

    ignored = set(GITIGNORE.read_text(encoding="utf-8").splitlines())
    for rule in (".env", ".env.*", "!.env.example", "!.env.*.example"):
        if rule not in ignored:
            fail(f"{GITIGNORE}: missing local-secret rule {rule!r}")

    # BaseLoader deliberately keeps every YAML scalar as text. This lets the
    # policy validator compare workflow expressions without implicit coercion.
    # The workflow is repository-controlled input; no YAML object construction
    # or arbitrary tags are permitted by this loader.
    workflow_raw: object = yaml.load(CI.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    workflow = object_mapping(workflow_raw, str(CI))
    permissions = object_mapping(workflow.get("permissions"), f"{CI}: permissions")
    if permissions.get("contents") != "read":
        fail(f"{CI}: workflow permissions must restrict contents to read")
    workflow_env = object_mapping(workflow.get("env"), f"{CI}: env")
    floor = minimum_python_release()
    if workflow_env.get("PYTHON_VERSION") != f"{floor[0]}.{floor[1]}":
        fail(f"{CI}: PYTHON_VERSION must track the minimum supported Python declared in pyproject")
    if workflow_env.get("UV_VERSION") != "0.11.30":
        fail(f"{CI}: UV_VERSION must be 0.11.30")
    if workflow_env.get("SKILLS_REF_SPEC") != SKILLS_REF_SPEC:
        fail(f"{CI}: SKILLS_REF_SPEC must pin the skills-ref validator to a full commit SHA")
    concurrency = object_mapping(workflow.get("concurrency"), f"{CI}: concurrency")
    if concurrency.get("group") != "${{ github.workflow }}-${{ github.event_name }}-${{ github.ref }}":
        fail(f"{CI}: concurrency group must keep event types independent")
    if concurrency.get("cancel-in-progress") != "true":
        fail(f"{CI}: concurrency must cancel superseded runs")
    jobs = object_mapping(workflow.get("jobs"), f"{CI}: jobs")
    required_jobs = {"deterministic", "monitor-external-contracts"}
    if not required_jobs <= jobs.keys():
        fail(f"{CI}: missing required jobs {sorted(required_jobs - jobs.keys())}")
    for job_name, raw_job in jobs.items():
        job = object_mapping(raw_job, f"{CI}: jobs.{job_name}")
        if "permissions" in job:
            fail(f"{CI}: jobs.{job_name} must not override workflow permissions")
        timeout = job.get("timeout-minutes")
        if not isinstance(timeout, str) or not timeout.isdigit() or int(timeout) <= 0:
            fail(f"{CI}: jobs.{job_name} needs a positive timeout-minutes")
        steps = mapping_list(job.get("steps"), f"{CI}: jobs.{job_name}.steps")
        checkout_steps = [step for step in steps if str(step.get("uses", "")).startswith("actions/checkout@")]
        if len(checkout_steps) != 1:
            fail(f"{CI}: jobs.{job_name} must contain exactly one checkout step")
        checkout_with = object_mapping(checkout_steps[0].get("with"), f"{CI}: jobs.{job_name}.checkout.with")
        if checkout_with.get("persist-credentials") != "false":
            fail(f"{CI}: jobs.{job_name} checkout must disable persisted credentials")
        for step in steps:
            uses = step.get("uses")
            if isinstance(uses, str) and not uses.startswith("./") and PINNED_ACTION_RE.fullmatch(uses) is None:
                fail(f"{CI}: jobs.{job_name} action must use a full commit SHA: {uses}")
        python_steps = [
            step
            for step in steps
            if str(step.get("uses", "")).startswith(("actions/setup-python@", "astral-sh/setup-uv@"))
        ]
        if len(python_steps) != 1:
            fail(f"{CI}: jobs.{job_name} must contain exactly one Python setup step")
        python_with = object_mapping(python_steps[0].get("with"), f"{CI}: jobs.{job_name}.python.with")
        if python_with.get("python-version") != "${{ env.PYTHON_VERSION }}":
            fail(f"{CI}: jobs.{job_name} must use the shared Python version")

    monitor_job = object_mapping(jobs["monitor-external-contracts"], f"{CI}: monitor job")
    if monitor_job.get("if") != "github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'":
        fail(f"{CI}: external monitoring must be limited to schedule and manual dispatch")
    monitor_steps = mapping_list(monitor_job.get("steps"), f"{CI}: monitor step")
    freshness_steps = [step for step in monitor_steps if step.get("run") == "python3 scripts/check-expiry.py"]
    if len(freshness_steps) != 1 or freshness_steps[0].get("if") != "${{ !cancelled() }}":
        fail(f"{CI}: scheduled freshness must run independently after URL monitoring")

    deterministic_job = object_mapping(jobs["deterministic"], f"{CI}: deterministic job")
    deterministic_steps = mapping_list(deterministic_job.get("steps"), f"{CI}: deterministic step")
    validate_preflight_steps(deterministic_steps)

    strategy = object_mapping(deterministic_job.get("strategy"), f"{CI}: deterministic job strategy")
    if strategy.get("fail-fast") != "false":
        fail(f"{CI}: deterministic matrix must report every Python release instead of cancelling siblings")
    matrix = object_mapping(strategy.get("matrix"), f"{CI}: deterministic job strategy matrix")
    raw_versions = matrix.get("python-version")
    if not isinstance(raw_versions, list) or not raw_versions or not all(isinstance(v, str) for v in raw_versions):
        fail(f"{CI}: deterministic job must declare a non-empty python-version matrix of release strings")
    releases = [python_release(version) for version in raw_versions]
    if len(set(releases)) != len(releases):
        fail(f"{CI}: deterministic matrix must not repeat a Python release")
    if floor not in releases:
        fail(f"{CI}: deterministic matrix must test the minimum supported Python {floor[0]}.{floor[1]}")
    if max(releases) <= floor:
        fail(f"{CI}: deterministic matrix must also test a Python newer than the {floor[0]}.{floor[1]} floor")
    deterministic_env = object_mapping(deterministic_job.get("env"), f"{CI}: deterministic job env")
    if deterministic_env.get("PYTHON_VERSION") != MATRIX_PYTHON_VERSION:
        fail(f"{CI}: deterministic job must derive PYTHON_VERSION from its matrix")

    skills_ref_steps = [step for step in deterministic_steps if "skills-ref validate" in str(step.get("run", ""))]
    if len(skills_ref_steps) != 1:
        fail(f"{CI}: deterministic checks must run the skills-ref validator exactly once")
    skills_ref_run = str(skills_ref_steps[0]["run"])
    expected_skills_ref = 'uvx --from "${SKILLS_REF_SPEC}" skills-ref validate skills/repo-architecture-skill'
    if expected_skills_ref not in skills_ref_run:
        fail(f"{CI}: deterministic checks must invoke skills-ref through the pinned SKILLS_REF_SPEC")
    if not re.search(r"^MAX_ATTEMPTS=([2-9]|[1-9][0-9]+)$", skills_ref_run, re.MULTILINE):
        fail(f"{CI}: deterministic checks must bound skills-ref retries to a finite attempt count")
    if "exit 1" not in skills_ref_run:
        fail(f"{CI}: deterministic checks must still fail once skills-ref retries are exhausted")

    dependabot = yaml.safe_load(DEPENDABOT.read_text(encoding="utf-8"))
    if not isinstance(dependabot, dict) or not isinstance(dependabot.get("updates"), list):
        fail(f"{DEPENDABOT}: updates must be a list")
    if not all(isinstance(entry, dict) for entry in dependabot["updates"]):
        fail(f"{DEPENDABOT}: every update must be a mapping")
    ecosystems = {entry.get("package-ecosystem") for entry in dependabot["updates"]}
    if ecosystems != {"github-actions", "uv"}:
        fail(f"{DEPENDABOT}: must monitor github-actions and uv")
    for entry in dependabot["updates"]:
        ecosystem = entry["package-ecosystem"]
        if entry.get("open-pull-requests-limit") != 2:
            fail(f"{DEPENDABOT}: {ecosystem} must cap open PRs at 2")
        expected_labels = {
            "github-actions": {"dependencies", "github_actions"},
            "uv": {"dependencies", "python:uv"},
        }[ecosystem]
        if set(entry.get("labels", [])) != expected_labels:
            fail(f"{DEPENDABOT}: {ecosystem} labels must be {sorted(expected_labels)}")
        groups = object_mapping(entry.get("groups"), f"{DEPENDABOT}: {ecosystem}.groups")
        group_name = "actions-maintenance" if ecosystem == "github-actions" else "uv-maintenance"
        maintenance = object_mapping(groups.get(group_name), f"{DEPENDABOT}: {ecosystem}.{group_name}")
        if maintenance.get("patterns") != ["*"]:
            fail(f"{DEPENDABOT}: {ecosystem} maintenance group must match all dependencies")
        if maintenance.get("update-types") != ["minor", "patch"]:
            fail(f"{DEPENDABOT}: {ecosystem} maintenance group must contain only minor and patch updates")


def validate_maintainer_environment() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    dependency_groups = object_mapping(project.get("dependency-groups"), f"{PYPROJECT}: dependency-groups")
    dependencies = dependency_groups.get("dev")
    if not isinstance(dependencies, list) or not all(isinstance(dependency, str) for dependency in dependencies):
        fail(f"{PYPROJECT}: dependency-groups.dev must be a string list")
    pins: dict[str, str] = {}
    for dependency in dependencies:
        match = re.fullmatch(
            r"(pyyaml|ruff|ty)==([0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9.+-]*))",
            dependency,
        )
        if match is None or match.group(1) in pins:
            fail(f"{PYPROJECT}: dev dependencies must be unique exact pins")
        pins[match.group(1)] = match.group(2)
    if set(pins) != {"pyyaml", "ruff", "ty"}:
        fail(f"{PYPROJECT}: dev dependencies must be exactly pyyaml, ruff, and ty")

    lock = tomllib.loads(UV_LOCK.read_text(encoding="utf-8"))
    packages = lock.get("package", [])
    if not isinstance(packages, list) or not all(isinstance(package, dict) for package in packages):
        fail(f"{UV_LOCK}: package must be a list of objects")
    locked_versions: dict[str, str] = {}
    for package in packages:
        name = package.get("name")
        version = package.get("version")
        if name in pins and isinstance(name, str) and isinstance(version, str):
            locked_versions[name] = version
    if locked_versions != pins:
        fail(f"{UV_LOCK}: locked dev dependency versions must match {PYPROJECT}")
    tool = object_mapping(project.get("tool"), f"{PYPROJECT}: tool")
    uv_config = object_mapping(tool.get("uv"), f"{PYPROJECT}: tool.uv")
    if uv_config.get("package") is not False:
        fail(f"{PYPROJECT}: maintainer environment must be a non-package uv project")
    if not UV_LOCK.is_file():
        fail(f"{UV_LOCK}: committed uv lockfile is required")


def validate_readme() -> None:
    if not README.exists():
        fail("README.md is missing")
    text = README.read_text(encoding="utf-8")
    required = (
        "## Install",
        "## Support status",
        "## Architecture",
        "## Verify",
        "## Maintainer ownership",
        "skills/repo-architecture-skill/",
        "evals/cases/architecture-audit.json",
        "docs/portability-contract.md",
        "uv sync --locked",
        "SECURITY.md",
    )
    for phrase in required:
        if phrase not in text:
            fail(f"README.md is missing {phrase!r}")
    errors = local_link_errors(README, ROOT)
    if errors:
        fail("\n".join(errors))
    documentation_errors = [
        error for path in sorted((ROOT / "docs").rglob("*.md")) for error in local_link_errors(path, ROOT)
    ]
    if documentation_errors:
        fail("\n".join(documentation_errors))


def validate_eval() -> None:
    try:
        raw: object = json.loads(EVAL.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{EVAL}: unreadable behavioral contract: {exc}") from exc
    data = object_mapping(raw, str(EVAL))
    if data.get("schema_version") != 1:
        fail(f"{EVAL}: schema_version must be 1")
    if data.get("skill_name") != "repo-architecture-skill":
        fail(f"{EVAL}: skill_name mismatch")
    trigger = data.get("trigger")
    if not isinstance(trigger, dict):
        fail(f"{EVAL}: trigger must be an object")
    for polarity in ("positive", "negative"):
        values = trigger.get(polarity)
        if not isinstance(values, list) or not values or not all(isinstance(v, str) for v in values):
            fail(f"{EVAL}: trigger.{polarity} must be a non-empty string list")

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 5:
        fail(f"{EVAL}: at least five representative fixtures are required")
    seen: set[str] = set()
    covered: set[str] = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict) or not isinstance(fixture.get("name"), str):
            fail(f"{EVAL}: every fixture needs a string name")
        name = fixture["name"]
        if name in seen:
            fail(f"{EVAL}: duplicate fixture name {name!r}")
        seen.add(name)
        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            fail(f"{EVAL}: fixture {name!r} needs expected behavior")
        archetype = expected.get("archetype")
        if archetype not in ARCHETYPES:
            fail(f"{EVAL}: fixture {name!r} has invalid archetype {archetype!r}")
        covered.add(archetype)
        boundaries = expected.get("boundaries")
        if not isinstance(boundaries, dict) or set(boundaries) != BOUNDARIES:
            fail(f"{EVAL}: fixture {name!r} must declare all four boundaries")
        for field in ("required_recommendations", "prohibited_recommendations"):
            values = expected.get(field)
            if not isinstance(values, list) or not values or not all(isinstance(v, str) for v in values):
                fail(f"{EVAL}: fixture {name!r} needs a non-empty {field} list")
    if covered != ARCHETYPES:
        fail(f"{EVAL}: archetype coverage mismatch: {sorted(ARCHETYPES - covered)} missing")
    required_fixtures = {
        "portable-payload-without-runtime-certification",
        "audit-with-secret-like-evidence",
        "shared-core-with-client-discovery-adapters",
        "writable-external-skill-directory",
        "client-extension-isolated-in-adapter",
    }
    if not required_fixtures <= seen:
        fail(f"{EVAL}: required evidence fixtures missing: {sorted(required_fixtures - seen)}")


def validate_codex_eval() -> None:
    try:
        raw: object = json.loads(CODEX_SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{CODEX_SCHEMA}: unreadable result schema: {exc}") from exc
    schema = object_mapping(raw, str(CODEX_SCHEMA))
    raw_required = schema.get("required")
    if not isinstance(raw_required, list) or not all(isinstance(field, str) for field in raw_required):
        fail(f"{CODEX_SCHEMA}: required must be a string list")
    required = set(raw_required)
    common = {
        "case_id",
        "skills_used",
        "actions",
        "changed_paths",
        "outcome",
        "summary",
        "environment_limitations",
    }
    if not common <= required:
        fail(f"{CODEX_SCHEMA}: missing common result fields {sorted(common - required)}")
    schema_properties = object_mapping(schema.get("properties"), f"{CODEX_SCHEMA}: properties")
    classification = object_mapping(
        schema_properties.get("classification"),
        f"{CODEX_SCHEMA}: properties.classification",
    )
    properties = object_mapping(
        classification.get("properties"),
        f"{CODEX_SCHEMA}: properties.classification.properties",
    )
    archetype_schema = object_mapping(
        properties.get("archetype"),
        f"{CODEX_SCHEMA}: properties.classification.properties.archetype",
    )
    raw_archetypes = archetype_schema.get("enum")
    if not isinstance(raw_archetypes, list) or not all(isinstance(archetype, str) for archetype in raw_archetypes):
        fail(f"{CODEX_SCHEMA}: archetype enum must be a string list")
    if set(raw_archetypes) != ARCHETYPES:
        fail(f"{CODEX_SCHEMA}: archetypes must match the behavioral contract")
    boundary_schema = object_mapping(
        properties.get("boundaries"),
        f"{CODEX_SCHEMA}: properties.classification.properties.boundaries",
    )
    raw_schema_boundaries = boundary_schema.get("required")
    if not isinstance(raw_schema_boundaries, list) or not all(
        isinstance(boundary, str) for boundary in raw_schema_boundaries
    ):
        fail(f"{CODEX_SCHEMA}: boundary requirements must be a string list")
    schema_boundaries = set(raw_schema_boundaries)
    if schema_boundaries != BOUNDARIES:
        fail(f"{CODEX_SCHEMA}: classification boundaries must match the behavioral contract")
    for path in (CODEX_POSITIVE, CODEX_NEGATIVE):
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            fail(f"{path}: evaluation prompt must be non-empty")
    for case_id in sorted(CODEX_CASE_IDS):
        contract = load_case_contract(ROOT / "evals/cases", case_id)
        if contract.archetype not in ARCHETYPES:
            fail(f"evals/cases/{case_id}.json: unknown archetype {contract.archetype!r}")
        if set(contract.boundaries) != BOUNDARIES:
            fail(f"evals/cases/{case_id}.json: boundaries must match the behavioral contract")


def validate_portability_contract() -> None:
    try:
        text = PORTABILITY_CONTRACT.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"{PORTABILITY_CONTRACT}: unreadable: {exc}") from exc
    required = (
        "## Evidence levels",
        "## Runtime states",
        "## Current status",
        "Payload portable",
        "Install verified",
        "Workflow verified",
        "`candidate`",
    )
    for phrase in required:
        if phrase not in text:
            fail(f"{PORTABILITY_CONTRACT}: missing {phrase!r}")


def validate_evidence_sources() -> None:
    try:
        manifest = load_evidence_manifest(EVIDENCE)
    except ValueError as exc:
        raise ValueError(f"{EVIDENCE}: invalid evidence manifest: {exc}") from exc
    for entry in manifest.entries:
        source = (ROOT / entry.source_section).resolve()
        if not source.is_relative_to(ROOT.resolve()) or not source.is_file():
            fail(f"{EVIDENCE}: source file does not exist: {entry.source_section}")
        if entry.url not in source.read_text(encoding="utf-8"):
            fail(f"{EVIDENCE}: {entry.url} is not present in {entry.source_section}")


def self_test() -> None:
    folded = "---\nname: example-skill\ndescription: >\n  Folded descriptions parse as one complete and useful YAML string for reliable skill triggering.\n---\n# Body\n"
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        skill = root / "example-skill" / "SKILL.md"
        skill.parent.mkdir()
        skill.write_text(folded, encoding="utf-8")
        data, _ = parse_skill(skill)
        validate_frontmatter(data, skill)
        source = root / "README.md"
        source.write_text("[missing](nope.md)", encoding="utf-8")
        assert local_link_errors(source, root)
    try:
        validate_frontmatter({"name": "Bad_Name", "description": "word " * 12}, SKILL)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid skill names must fail")
    synthetic_token = "ghp_" + ("a" * 36)
    assert secret_types(synthetic_token) == ["GitHub token"]
    assert not secret_types("tokens should be redacted")
    assert DANGEROUS_RUNTIME_PATTERNS[0][1].search("git reset --hard")
    assert DANGEROUS_RUNTIME_PATTERNS[4][1].search("cat .env")
    assert python_release("3.14") == (3, 14)
    assert minimum_python_release() == python_release("3.13")
    assert sorted(python_release(version) for version in ("3.14", "3.13")) == [(3, 13), (3, 14)]
    for rejected in ("3", "3.13.1", "latest", ""):
        try:
            python_release(rejected)
        except ValueError:
            pass
        else:
            raise AssertionError(f"non major.minor Python versions must fail: {rejected!r}")
    preflight_steps: list[dict[str, object]] = [
        {"run": RUFF_CHECK_COMMAND},
        {"run": RUFF_FORMAT_COMMAND},
        {"run": TYPE_CHECK_COMMAND},
        {"run": CANONICAL_VALIDATION_COMMAND},
    ]
    validate_preflight_steps(preflight_steps)
    for invalid_steps in (
        [step for step in preflight_steps if step["run"] != TYPE_CHECK_COMMAND],
        [preflight_steps[1], preflight_steps[0], *preflight_steps[2:]],
    ):
        try:
            validate_preflight_steps(invalid_steps)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid deterministic preflight must fail")
    print("PASS: validator self-tests")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            validate_skill()
            validate_runtime_trust()
            validate_readme()
            validate_eval()
            validate_codex_eval()
            validate_portability_contract()
            validate_evidence_sources()
            validate_security_contract()
            validate_maintainer_environment()
            validate_repository_secrets()
            print("PASS: payload, docs, behavior, security, and maintainer environment")
    except (AssertionError, OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
