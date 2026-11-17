"""Grade repo-architecture Codex evaluation artifacts deterministically."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from evaluation_contract import fixture_path_is_safe, load_case_contract

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "evals/cases"
COMMON_FIELDS = {
    "case_id",
    "skills_used",
    "actions",
    "changed_paths",
    "outcome",
    "summary",
    "environment_limitations",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected a JSON object")
    return value


def has_fixture_evidence(value: object, fixture_files: dict[str, str]) -> bool:
    """Return whether value is a non-empty list of declared fixture evidence paths."""
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(path, str) and fixture_path_is_safe(path) and path in fixture_files for path in value)
    )


def maps_boundaries(boundaries: object, contract: Any) -> bool:
    """Return whether every required boundary has its case-defined semantic anchors."""
    if not isinstance(boundaries, dict) or set(boundaries) != set(contract.boundaries):
        return False
    for name, expected_terms in contract.boundary_term_sets.items():
        value = boundaries.get(name)
        if not isinstance(value, str):
            return False
        if value == contract.boundaries[name]:
            continue
        normalized = value.casefold()
        if not all(term in normalized for term in expected_terms):
            return False
    return True


def grade_positive(result: dict[str, Any], case_id: str = "architecture-duplicate-mirror") -> list[str]:
    errors: list[str] = []
    contract = load_case_contract(CASE_DIR, case_id)
    missing = COMMON_FIELDS - result.keys()
    if missing:
        errors.append(f"result lacks common fields: {sorted(missing)}")
        return errors
    if result["case_id"] != case_id:
        errors.append("positive result has the wrong case_id")
    skills = result.get("skills_used")
    if not isinstance(skills, list) or "repo-architecture-skill" not in skills:
        errors.append("repo-architecture-skill was not selected")
    if result.get("changed_paths") != []:
        errors.append("read-only audit must not report changed paths")
    if result.get("outcome") not in {"passed", "limited"}:
        errors.append("positive audit did not complete")

    classification = result.get("classification")
    if not isinstance(classification, dict):
        errors.append("classification is missing")
        return errors
    if classification.get("archetype") != contract.archetype:
        errors.append(f"fixture was not classified as {contract.archetype}")
    boundaries = classification.get("boundaries")
    if not maps_boundaries(boundaries, contract):
        errors.append("classification does not map all four boundaries")
    evidence = classification.get("evidence_paths")
    if not has_fixture_evidence(evidence, contract.fixture_files):
        errors.append("classification lacks declared fixture evidence")

    recommendations = result.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        errors.append("audit lacks recommendations")
        return errors
    combined = " ".join(
        str(item.get("recommendation", "")) for item in recommendations if isinstance(item, dict)
    ).casefold()
    if not any(all(term in combined for term in term_set) for term_set in contract.recommendation_term_sets):
        errors.append("audit does not address the case contract's required recommendation")
    for index, item in enumerate(recommendations):
        paths = item.get("evidence_paths") if isinstance(item, dict) else None
        if not has_fixture_evidence(paths, contract.fixture_files):
            errors.append(f"recommendation {index} lacks declared fixture evidence")
    return errors


def grade_negative(text: str) -> list[str]:
    if not text.strip():
        return ["negative run produced no response"]
    lowered = text.lower()
    markers = (
        "repo-architecture-skill",
        "four boundaries",
        "runtime payload",
        "install artifact",
    )
    found = [marker for marker in markers if marker in lowered]
    return [f"negative run appears to activate architecture audit: {found}"] if found else []


def run_self_tests() -> int:
    passing = {
        "case_id": "architecture-duplicate-mirror",
        "skills_used": ["repo-architecture-skill"],
        "actions": ["inspected tracked files"],
        "changed_paths": [],
        "outcome": "passed",
        "summary": "Found an unowned duplicate.",
        "environment_limitations": [],
        "classification": {
            "archetype": "markdown-only-skill",
            "boundaries": {
                "authoring_source": "skills/example/",
                "runtime_payload": "skills/example/",
                "install_artifact": "copied skill directory",
                "maintainer_infrastructure": "README.md and repository metadata",
            },
            "evidence_paths": ["skills/example/SKILL.md"],
        },
        "recommendations": [
            {
                "recommendation": "Remove the duplicate mirror; keep the skill canonical.",
                "evidence_paths": ["SKILL.md", "skills/example/SKILL.md"],
            }
        ],
    }
    assert grade_positive(passing) == []
    verbose = json.loads(json.dumps(passing))
    verbose["classification"]["boundaries"] = {
        "authoring_source": "Edit skills/example/SKILL.md as the canonical source.",
        "runtime_payload": "skills/example/SKILL.md is the sole runtime entry point.",
        "install_artifact": "Install skills/example/ as the documented installable directory.",
        "maintainer_infrastructure": "README.md records the maintainer-facing repository metadata.",
    }
    assert grade_positive(verbose) == []
    failing = json.loads(json.dumps(passing))
    failing["classification"]["boundaries"].pop("runtime_payload")
    assert any("four boundaries" in error for error in grade_positive(failing))
    wrong_boundary = json.loads(json.dumps(passing))
    wrong_boundary["classification"]["boundaries"]["install_artifact"] = "The root mirror is useful."
    assert any("four boundaries" in error for error in grade_positive(wrong_boundary))
    fabricated = json.loads(json.dumps(passing))
    fabricated["skills_used"] = ["not-repo-architecture-skill"]
    fabricated["classification"]["boundaries"]["authoring_source"] = "invented/source"
    fabricated["classification"]["evidence_paths"] = ["invented-evidence.md"]
    fabricated["recommendations"][0]["evidence_paths"] = ["invented-recommendation.md"]
    errors = grade_positive(fabricated)
    assert "repo-architecture-skill was not selected" in errors
    assert "classification does not map all four boundaries" in errors
    assert "classification lacks declared fixture evidence" in errors
    assert "recommendation 0 lacks declared fixture evidence" in errors
    assert grade_negative("Use split('=', 1) in parser.py.") == []
    assert grade_negative("Run repo-architecture-skill and map the runtime payload.")
    print("PASS: grade-codex-regression.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive-result", type=Path)
    parser.add_argument("--negative-result", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case-id", default="architecture-duplicate-mirror")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()
    if args.positive_result is None or args.negative_result is None:
        parser.error("--positive-result and --negative-result are required")
    try:
        errors = grade_positive(read_json(args.positive_result), args.case_id)
        errors.extend(grade_negative(args.negative_result.read_text(encoding="utf-8")))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors = [f"cannot read evaluation artifacts: {exc}"]
    report = {"passed": not errors, "errors": errors}
    try:
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot write grade report: {exc}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS: Codex architecture regression")
    return 0


if __name__ == "__main__":
    sys.exit(main())
