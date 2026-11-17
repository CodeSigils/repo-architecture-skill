# Portability and Runtime Evidence Contract

Status: normative maintainer contract. This file is not shipped in the runtime
payload.

## Canonical payload

`skills/repo-architecture-skill/` is the sole runtime source and installable
artifact. Adapters may point at it or add required metadata, but must not copy
its methodology.

## Evidence levels

Use these claims consistently:

| Claim             | Required evidence                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| Payload portable  | Canonical files parse under the claimed format and have no known platform-only runtime dependency |
| Install verified  | A named runtime and version discovers or installs the exact payload through a recorded procedure  |
| Workflow verified | That runtime completes representative positive and negative tasks against the behavioral contract |

Evidence at one level does not establish the next.

## Runtime states

Use `candidate`, `install_verified`, `workflow_verified`, `limited`, or
`unsupported`. Record the runtime version, date, installation path, explicit and
implicit selection, scenarios, evidence or grading criteria, and limitations.

Do not extrapolate a result to untested runtimes or later versions. A material
change to `SKILL.md`, the behavioral contract, prompt, or grader starts a new
evidence baseline.

## Current status

The canonical payload passes deterministic format, frontmatter, reference,
portability-marker, and behavioral-contract validation.

| Runtime | Version | Status |
| --- | --- | --- |
| OpenAI Codex CLI | 0.133.0 | `workflow_verified` (historical result) |
| OpenAI Codex CLI | 0.167.2 | `limited`; the prior exact boundary-value contract was not satisfied |
| OpenAI Codex CLI | 0.169.0 | `workflow_verified` against the 2026-11-17 semantic-boundary contract |
| Hermes Agent | 0.19.0 | `workflow_verified` with a post-response shutdown-warning limitation |
| Claude Code | 2.1.159 | `candidate`; discovery and behavior were inconclusive |
| Gemini CLI | not installed | `candidate` |

The dated procedure, prompts, grading, and limitations are recorded in
[the compatibility reports](compatibility/2026-07-22.md), including the
[2026-11-17 Codex regression record](compatibility/2026-11-17.md).

## Adding runtime evidence

1. Select one runtime as an active target.
2. Record its exact version and discovery or installation path.
3. Test explicit and implicit selection with positive and negative scenarios.
4. Preserve reproducible or raw evidence without exposing sensitive values.
5. Grade against `evals/cases/architecture-audit.json`.
6. Record limitations and the narrowest supported state.

Keep model evaluation non-blocking. Reuse this contract and fixture vocabulary
before creating a runtime-specific runner. Extract a generic harness only after
two concrete uses share the same lifecycle and grading needs.
