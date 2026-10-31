# Maintenance

## Sources of truth
- Agent guidance: [AGENTS.md](../AGENTS.md)
- Verification: [README.md](../README.md) (verification section)
- Research/decisions: [docs/research/](research/)

## Standard verification
Follow the **Verify** section in [README.md](../README.md). At a minimum:

```bash
uv sync --locked
uv run --locked ruff check scripts .github/scripts
uv run --locked ruff format --check scripts .github/scripts
uv run --locked ty check scripts .github/scripts
uv run --locked python scripts/validate.py
uvx --from git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref skills-ref validate skills/repo-architecture-skill
uv run --locked python scripts/validate.py --self-test
uv run --locked python scripts/run-codex-regression.py --self-test
uv run --locked python scripts/grade-codex-regression.py --self-test
uv run --locked python .github/scripts/check-portability.py
uv run --locked python scripts/verify-urls.py --self-test
uv run --locked python scripts/check-expiry.py --self-test
uv run --locked python scripts/check-expiry.py
```

Report network-dependent checks (e.g. live external URL verification) separately as they are not deterministic.

## Automation

- **GitHub Actions:** [.github/workflows/ci.yml](../.github/workflows/ci.yml)
  - `deterministic` (push/PR to `main`, non-schedule): runs on `ubuntu-26.04` with a Python matrix (`3.13`, `3.14`). Installs locked deps via `uv`, runs lint/format/typecheck on maintainer scripts, validates the canonical payload/behavioral contract, runs `skills-ref validate` (with retry), runs all self-tests (validator, behavioral eval, grader), checks cross-agent portability, and runs freshness/expiry self-tests + `check-expiry.py`.
  - `monitor-external-contracts` (schedule or `workflow_dispatch` only): verifies external URL contracts via `scripts/verify-urls.py` and checks expired freshness markers. Advisory/monitoring lane, not a required PR check.
- **Dependency updates:** [.github/dependabot.yml](../.github/dependabot.yml)
  - `github-actions` and `uv` ecosystems, weekly on Mondays (08:00 UTC), grouped updates with small open-PR limits.
- **Git hooks:** [.githooks/](../.githooks/)
  - `pre-commit` enforces `ruff check`, `ruff format --check`, `ty check`, portability check, payload validation, and expiry checks via `uv run --locked`.
- **Branch protection:** `main` is PR-only with required status checks; direct pushes are blocked.

## Volatility
Medium-High — monitor CI (deterministic matrix + CodeQL), Dependabot PRs, and weekly external-contract checks (schedule). Inspect before VCS writes and on exceptions.

## Escalation
- CI/workflow, runner, token, or Dependabot policy changes
- Conflicts with [docs/research/automation-bots-and-workflows.md](research/automation-bots-and-workflows.md)
- Portability/script failures in [.github/scripts/](../.github/scripts/) or payload validation failures in [scripts/validate.py](../scripts/validate.py)
- Skills-ref validation failures or behavioral evaluation contract breaks
