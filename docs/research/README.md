# Maintainer Research Map

This directory preserves dated evidence for maintainers. It is not part of the
installed skill and does not override the runtime payload, configuration,
validators, or repository policy files. Use it to understand why a current
decision exists and which volatile claims need fresh verification.

## Choose a note by task

| If the task involves | Read first | Then treat as authoritative |
| --- | --- | --- |
| Dependabot, GitHub Actions, runner images, workflow permissions, or bot-authored pull requests | [Automation Bots and Workflow Boundaries](automation-bots-and-workflows.md) | `.github/`, `scripts/validate.py`, and repository settings |
| A claim about Codex, Claude Code, Gemini CLI, Hermes, installation, discovery, or skill compatibility | [Platform Skill Support Snapshot](platform-skill-support-snapshot.md) | Current official platform documentation and the matching compatibility report |
| Canonical source, payload boundaries, generated artifacts, repository structure, or distribution layout | [Skill Repository Structure Snapshot](repository-structure-snapshot.md) | The current repository inventory, `README.md`, `SKILL.md`, and validation rules |

## How to use research safely

1. Start with the note selected above when the task changes the policy it
   documents.
2. Check its review date and evidence type before relying on a volatile claim.
3. Verify current external facts with the primary source before changing a
   configuration or support claim.
4. Update the authoritative implementation and its tests first; refresh the
   note to explain the resulting decision and evidence.

Research captures the basis for a decision. It does not authorize a broader
change, create a runtime guarantee, or replace direct inspection of the files
that implement the behavior.

## Evidence types and re-verification

Keep claims bounded by the evidence that supports them:

| Evidence type | Primary artifacts | What it proves | What it does not prove |
| --- | --- | --- | --- |
| Live URL / anchor / freshness | `docs/evidence-urls.json`, `scripts/verify-urls.py`, `scripts/check-expiry.py` | The cited page is reachable, contains required anchors (when checked), and was checked on a recorded date (shape/availability/freshness). | Semantic currency of guidance or runtime/support behavior. |
| Semantic guidance | Dated notes in `docs/research/*.md` | What was reviewed on the stated `Reviewed`/`Refreshed` date, with the recorded scope/method. | A runtime guarantee, or that guidance is still current beyond the specific claims and date checked. |
| Named runtime / support | `docs/portability-contract.md`, dated `docs/compatibility/*.md` | Evidence for payload/structure, installation, and workflow behavior as separately claimed and recorded (client/version/method/results/limits). | Broader, future-version, or untested compatibility; docs or freshness checks do not upgrade support status. |

### Triggers for semantic re-verification (point-of-use)

- **Before changing behavior or claims** based on volatile guidance (CI/runner/permissions/Dependabot policy, platform skill discovery/activation/install paths, compatibility/support statements), re-read the relevant primary source for the specific claim and treat the research note as context, not proof.
- **On drift signals:** `verify-urls.py` failure or missing anchor, observed page-content change, upstream announcement/release notes, or ambiguity surfaced during review.
- **Point-in-time repo/platform facts** (for example, a repository API/security-setting state checked on a specific date): re-verify via API/UI/CLI at use time and record the checked date/context; do not rely on an old observation.

### When refreshing, record scope explicitly

- Update `last_verified` / `Reviewed` / `Refreshed` dates only for what was actually checked.
- State **method/scope** (for example, live URL + required-anchor checks via `scripts/verify-urls.py`, or local config/contract review against authoritative files) and **exclusions/limits** (for example, no semantic diff beyond anchors, no named-runtime workflow re-certification, point-in-time API claims not re-queried).
- For point-in-time facts, record the checked context (source surface/API/UI/CLI, date, and what was observed).
- Capture **decision-relevant deltas**, or explicitly state "no material change observed for [specific claims checked]," rather than only bumping dates.
- Keep `required_text` anchors in `docs/evidence-urls.json` to critical, stable invariants that detect meaningful breakage; avoid brittle phrasing.

### Runtime certification and operating practice

- Treat platform documentation as intended behavior, not proof. Do not upgrade support/status (for example, `candidate` to `workflow_verified`) without recorded client version + installation + workflow evidence in `docs/compatibility/` and aligned claims in `docs/portability-contract.md`/`README.md`; state inconclusive results and limitations when not re-certified.
- Use scheduled checks as a monitoring/backstop (breakage/aging). Use point-of-use semantic review for decisions. Update authoritative implementation/tests/config first, run relevant deterministic checks, then refresh research/evidence to explain the resulting decision and what was/was not verified. For high-impact surfaces (runner images, Actions permissions/trust model, Dependabot semantics, client skill discovery/activation), prefer a targeted semantic recheck when planning related changes, not only at weekly cadence. Keep freshness edits scoped and commit them with clear `what:`/`why:` and validation noted.
