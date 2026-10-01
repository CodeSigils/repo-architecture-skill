"""Load and validate shared Codex evaluation case contracts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

CASE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class CaseContract:
    """Validated inputs and grading expectations for one evaluation case."""

    case_id: str
    fixture_files: dict[str, str]
    archetype: str
    boundaries: dict[str, str]
    recommendation_term_sets: tuple[tuple[str, ...], ...]


def object_mapping(value: object, context: str) -> dict[str, object]:
    """Narrow an untrusted JSON value to a string-keyed mapping."""
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{context}: expected an object with string keys")
    return value


def fixture_path_is_safe(value: str) -> bool:
    """Return whether a fixture path is a normalized repository-relative POSIX path."""
    path = PurePosixPath(value)
    return (
        value not in {"", "."}
        and value == path.as_posix()
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
    )


def load_case_contract(case_dir: Path, case_id: str) -> CaseContract:
    """Load one case contract and validate every field consumed by the runner and grader."""
    if CASE_ID_RE.fullmatch(case_id) is None:
        raise ValueError(f"invalid case_id: {case_id!r}")
    path = case_dir / f"{case_id}.json"
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: unreadable case contract: {exc}") from exc
    data = object_mapping(raw, str(path))
    if data.get("case_id") != case_id:
        raise ValueError(f"{path}: case_id must be {case_id!r}")

    raw_files = object_mapping(data.get("fixture_files"), f"{path}: fixture_files")
    if not raw_files:
        raise ValueError(f"{path}: fixture_files must not be empty")
    fixture_files: dict[str, str] = {}
    for relative, content in raw_files.items():
        if not fixture_path_is_safe(relative):
            raise ValueError(f"{path}: unsafe fixture path {relative!r}")
        if not isinstance(content, str):
            raise TypeError(f"{path}: fixture content for {relative!r} must be a string")
        fixture_files[relative] = content

    expected = object_mapping(data.get("expected"), f"{path}: expected")
    archetype = expected.get("archetype")
    if not isinstance(archetype, str) or not archetype:
        raise TypeError(f"{path}: expected.archetype must be a non-empty string")
    boundaries = object_mapping(expected.get("boundaries"), f"{path}: expected.boundaries")
    if not boundaries:
        raise ValueError(f"{path}: expected.boundaries must contain non-empty string values")
    typed_boundaries: dict[str, str] = {}
    for name, value in boundaries.items():
        if not isinstance(value, str) or not value:
            raise ValueError(f"{path}: expected.boundaries must contain non-empty string values")
        typed_boundaries[name] = value

    grading = object_mapping(data.get("grading"), f"{path}: grading")
    raw_term_sets = grading.get("recommendation_term_sets")
    if not isinstance(raw_term_sets, list) or not raw_term_sets:
        raise TypeError(f"{path}: grading.recommendation_term_sets must be a non-empty list")
    term_sets: list[tuple[str, ...]] = []
    for index, raw_terms in enumerate(raw_term_sets):
        if (
            not isinstance(raw_terms, list)
            or not raw_terms
            or not all(isinstance(term, str) and term for term in raw_terms)
        ):
            raise TypeError(f"{path}: recommendation_term_sets[{index}] must contain non-empty strings")
        term_sets.append(tuple(term.casefold() for term in raw_terms))

    return CaseContract(
        case_id=case_id,
        fixture_files=fixture_files,
        archetype=archetype,
        boundaries=typed_boundaries,
        recommendation_term_sets=tuple(term_sets),
    )
