# Repository Instructions

> Scope: maintainer routing only. This file is not part of the runtime payload.

This repository ships one portable skill from
`skills/repo-architecture-skill/`; that directory is both canonical source and
installable payload.

- Use `SKILL.md` for runtime triggers and procedure.
- Use runtime references only for conditionally loaded detail.
- Use `evals/` for intended classification and recommendation behavior.
- Use `README.md` for installation, layout, and maintainer verification.
- Treat `docs/` and research notes as evidence, not runtime authority.

For a runtime-payload change, read `SKILL.md` and only the reference relevant
to the affected decision. Update `evals/` when the expected classification or
recommendation behavior changes.

## Research routing

Read the relevant note in `docs/research/` before changing a policy that it
documents. The workflow, configuration, validator, and runtime payload remain
authoritative; research explains their evidence and maintenance boundary.

- For Dependabot, GitHub Actions, runner, workflow-token, or bot-authored PR
  changes, read `docs/research/automation-bots-and-workflows.md`.
- For named agent support, installation, skill discovery, or compatibility
  claims, read `docs/research/platform-skill-support-snapshot.md`.
- For payload layout, canonical-source, generated-artifact, or repository-shape
  decisions, read `docs/research/repository-structure-snapshot.md`.

Use `docs/research/README.md` when the task does not clearly match one route.

Do not recreate a root reference mirror or payload sync step unless a concrete
distribution consumer requires a generated artifact. Before claiming
completion, run the smallest relevant local deterministic checks from
`README.md`; report network-dependent validation separately rather than calling
it deterministic.
