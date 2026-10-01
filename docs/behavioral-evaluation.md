# Behavioral Evaluation

The repository uses a shared evaluation vocabulary while retaining a
repository-native runner and semantic grader. This separation was adopted from
the established `repo-health-and-sync-skill` model regression: deterministic
fixture and grader tests run in ordinary CI, while authenticated model runs are
optional maintainer evidence.

## Cases

The bounded evaluation has two positive cases plus one shared negative scenario:

1. `architecture-duplicate-mirror` asks for a read-only architecture audit of a
   Markdown-only skill repository containing an undeclared duplicate root
   `SKILL.md`.
2. `markdown-only-discovery-skill` checks that volatile external monitoring is
   separated from deterministic pull-request validation.
3. The negative scenario asks about a narrow parser defect and must not activate
   the repository-architecture workflow.

The positive result follows `evals/codex/result.schema.json`. It retains the
common `case_id`, `skills_used`, `actions`, `changed_paths`, `outcome`,
`summary`, and `environment_limitations` fields, then adds the domain-specific
classification, four-boundary map, evidence paths, and recommendations.

## Deterministic CI

Run the model-free tests:

```bash
uv run --locked python scripts/run-codex-regression.py --self-test
uv run --locked python scripts/grade-codex-regression.py --self-test
```

These tests verify isolated fixture construction, skill installation, command
shape, result-schema parsing, transcript accounting, positive grading, negative
trigger behavior, and representative grader failure.

## Optional Live Run

An authenticated Codex CLI and network access are required:

```bash
uv run --locked python scripts/run-codex-regression.py \
  --codex-home "$CODEX_HOME"
```

`--codex-home` must point to a persistent writable Codex home prepared by the
maintainer. The runner records the path and observed CLI version but never
reads or prints credential values. `--expected-codex-version` is optional; use
it when reproducibility requires a pinned CLI, and treat a mismatch as an
environment failure before interpreting any model result.

For example, reproduce the 2026-07-22 compatibility record with its historical
CLI version pin:

```bash
uv run --locked python scripts/run-codex-regression.py \
  --codex-home "$CODEX_HOME" \
  --expected-codex-version "0.133.0"
```

The evaluated agent receives a read-only sandbox. Each run preserves positive
and negative transcripts, final results, stderr, deterministic grade, runtime
metadata, duration, usage when emitted, and the tested repository revision
under ignored `artifacts/codex-regression/`.

Use `--prepare-only` to inspect a generated fixture without running Codex. With
no `--fixture-dir`, the fixture persists beneath the selected `--output-dir` (or
the default ignored artifacts directory) instead of using temporary storage.

A single passing run verifies one payload, case, runtime, and model combination;
it is not a reliability baseline. Preserve failures and environment limitations
instead of counting them as product success or silently discarding them.

## Adoption Evidence

`docs/evaluation-adoption-ledger.yaml` records prospective adaptation time and
defects. The shared contract informed vocabulary and artifact boundaries only;
fixture construction, execution, and semantic grading remain local because
they encode this skill's architecture classifications and recommendations.

Sources:

- Agent Skills specification: https://agentskills.io/specification
- OpenAI Evals API: https://platform.openai.com/docs/api-reference/evals
- OpenAI Graders API: https://platform.openai.com/docs/api-reference/graders
- Repo-health regression methodology:
  https://github.com/CodeSigils/repo-health-and-sync-skill/blob/main/docs/codex-regression.md
