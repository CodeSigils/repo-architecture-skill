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
