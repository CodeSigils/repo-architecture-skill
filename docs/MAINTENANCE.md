# Maintenance

## Sources of truth
- Agent guidance: [AGENTS.md](../AGENTS.md)
- Verification: [README.md](../README.md) (verification section)
- Research/decisions: [research/](research/)

## Standard verification
- Run the smallest relevant deterministic checks from [README.md](../README.md).
- Report external checks separately.

## Automation
- GitHub Actions: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- Dependency updates: [.github/dependabot.yml](../.github/dependabot.yml)
- Git hooks: [.githooks/](../.githooks/)

## Volatility
Medium — check CI and open Dependabot PRs before maintenance work.

## Escalation
- CI/workflow, runner, token, or Dependabot policy changes
- Conflicts with `automation-bots-and-workflows.md` if present
- Portability/script failures in [.github/scripts/](../.github/scripts/)
