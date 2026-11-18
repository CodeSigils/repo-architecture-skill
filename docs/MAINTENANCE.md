# Maintenance

## Sources of truth
- Agent guidance: [AGENTS.md](../AGENTS.md)
- Verification: [README.md](../README.md) (verification section)
- Research/decisions: [docs/research/](research/)

## Standard verification

Follow the **Verify** section in [README.md](../README.md) for the canonical
command list, environment setup, matrix/interpreter notes, and network-dependent
check boundaries. Do not duplicate that command list here; update it in
`README.md` only.

## Automation

- **GitHub Actions:** [.github/workflows/ci.yml](../.github/workflows/ci.yml)
  - `deterministic` (push/PR to `main`, non-schedule): runs on `ubuntu-26.04` with a Python matrix (`3.13`, `3.14`). Installs locked deps via `uv`, runs lint/format/typecheck on maintainer scripts, validates the canonical payload/behavioral contract, runs `skills-ref validate` (with retry), runs all self-tests (validator, behavioral eval, grader), checks cross-agent portability, and runs freshness/expiry self-tests + `check-expiry.py`.
  - `monitor-external-contracts` (schedule or `workflow_dispatch` only): verifies external URL contracts via `scripts/verify-urls.py` and checks expired freshness markers. Advisory/monitoring lane, not a required PR check.
- **Dependency updates:** [.github/dependabot.yml](../.github/dependabot.yml)
  - `github-actions` and `uv` ecosystems, weekly on Mondays (08:00 UTC), grouped updates with small open-PR limits.
- **Git hooks:** [.githooks/](../.githooks/)
  - `pre-commit` enforces `ruff check`, `ruff format --check`, `ty check`, portability check, payload validation, and expiry checks via `uv run --locked`.
- **Branch protection:** `main` is PR-only with required status checks; direct pushes are blocked.

### Evidence and re-verification (volatile guidance)

Treat scheduled URL/freshness checks as a monitoring backstop, not proof of semantic currency or runtime support. Follow [docs/research/README.md — Evidence types and re-verification](research/README.md#evidence-types-and-re-verification) when refreshing evidence or changing volatile guidance:

- Keep claim types bounded: live URL/anchor/freshness (`docs/evidence-urls.json`, `verify-urls.py`, `check-expiry.py`) vs semantic guidance (dated `docs/research/*.md`) vs named-runtime/support (`docs/portability-contract.md`, `docs/compatibility/*.md`).
- Re-verify point-of-use before changing behavior/claims based on volatile guidance, on drift signals, or for point-in-time repo/platform facts (recheck via API/UI/CLI and record context/date).
- Record method/scope, exclusions/limits, checked context, and decision-relevant deltas (or "no material change observed for [specific claims checked]"); update dates only for what was actually checked.
- Do not upgrade compatibility/support status from docs or freshness checks; require recorded client version + installation + workflow evidence in `docs/compatibility/` with aligned claims. Update authoritative implementation/tests/config first, run relevant checks, then refresh research/evidence with clear `what:`/`why:`.

## Volatility
Medium-High — monitor CI (deterministic matrix + CodeQL), Dependabot PRs, and weekly external-contract checks (schedule). Inspect before VCS writes and on exceptions.

## Escalation
- CI/workflow, runner, token, or Dependabot policy changes
- Conflicts with [docs/research/automation-bots-and-workflows.md](research/automation-bots-and-workflows.md)
- Portability/script failures in [.github/scripts/](../.github/scripts/) or payload validation failures in [scripts/validate.py](../scripts/validate.py)
- Skills-ref validation failures or behavioral evaluation contract breaks
