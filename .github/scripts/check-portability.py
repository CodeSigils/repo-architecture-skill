"""Check for agent-specific references in portable skill files.

Scans all skills/**/*.md for platform-specific tool names, CLI commands,
config paths, and directory patterns that would silently break non-Hermes
agents (Claude Code, Codex CLI, Gemini CLI, OpenCode, Cursor).

"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"

FORBIDDEN_PATTERNS = (
    ("Hermes tool name", re.compile(r"\bskill_(?:view|manage)\b", re.IGNORECASE)),
    ("Hermes Python import", re.compile(r"from hermes_tools\b", re.IGNORECASE)),
    ("Hermes config path", re.compile(r"~/\.hermes(?:/|\b)", re.IGNORECASE)),
    (
        "Hermes CLI command",
        re.compile(
            r"\bhermes\s+(?:skills?|config|tools?|setup|help|doctor|gateway|run|serve|cron)\b",
            re.IGNORECASE,
        ),
    ),
    ("Claude Code agent reference", re.compile(r"\bClaude\(\)", re.IGNORECASE)),
    ("Gemini CLI command", re.compile(r"\bgemini\s+skills?\b", re.IGNORECASE)),
    ("Codex CLI command", re.compile(r"\bcodex\s+run\b", re.IGNORECASE)),
    (
        "Platform-specific path",
        re.compile(r"\.(?:claude|cursor|codex|opencode|gemini)/"),
    ),
)


def scan_file(path: Path) -> list[tuple[Path, int, str, str]]:
    violations: list[tuple[Path, int, str, str]] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Reference files may intentionally discuss platform-specific examples.
    # Shipped SKILL.md files must use only line-level exemptions.
    if path.name != "SKILL.md":
        for i in range(min(3, len(lines))):
            if "# portability: allow-platform-ref" in lines[i]:
                return violations
    for line_no, line in enumerate(lines, start=1):
        if "# portability: allow-platform-ref" in line:
            continue
        for label, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                violations.append((path.relative_to(ROOT), line_no, label, line.rstrip()))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if not SKILLS_DIR.is_dir():
        print(f"FAIL: skills directory is missing: {SKILLS_DIR}", file=sys.stderr)
        return 1
    violations: list[tuple[Path, int, str, str]] = []
    skill_files = sorted(SKILLS_DIR.rglob("*.md"))
    if not skill_files:
        print(f"FAIL: no Markdown skill files found under {SKILLS_DIR}", file=sys.stderr)
        return 1
    for path in skill_files:
        try:
            violations.extend(scan_file(path))
        except OSError as exc:
            print(f"FAIL: could not read {path}: {exc}", file=sys.stderr)
            return 1

    if violations:
        print("FAIL: agent-specific references found in skills/:")
        for path, line_no, label, line in violations:
            print(f"  {path}:{line_no}: {label}: {line}")
        return 1

    print("PASS: no agent-specific references in skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
