# Portability Migration

Use this procedure to extract a portable runtime core from a skill that currently
depends on one client's commands, paths, hooks, or APIs.

## 1. Inventory platform coupling and scope

Frame the migration decision (target portability tier, supported adapters, and
out-of-scope surfaces). Search the runtime payload for:

- client-specific tool or API names;
- installation and configuration paths;
- hook, plugin, or lifecycle assumptions;
- platform-only frontmatter or metadata;
- commands whose output or availability is client-specific.

Classify each occurrence as runtime-essential, optional optimization,
installation documentation, or historical/example. Record observed evidence
(paths/checked context) and note unknowns; volatile client behavior should be
verified point-of-use from primary sources with checked date and recheck trigger.

## 2. Separate the portable core

Move task reasoning, filesystem inspection, general CLI use, and reporting into
the portable `SKILL.md` and runtime payload. Prefer capability checks such as
executable discovery, project manifests, or observed files over asking one agent
runtime whether a tool exists.

Keep platform adapters outside the portable core and separate from
maintainer/control-plane material. If an adapter is essential, declare the skill
platform-specific rather than hiding the dependency behind a fallback. State
transfer limits when borrowing patterns from a different source family/context.

## 3. Move install detail to the README or adapter docs

Document client-specific discovery and installation paths in clearly separated
sections. Installation paths may vary without changing the runtime methodology.
Verify current client documentation before publishing commands and record checked
dates for volatile guidance.

Do not place every client's setup instructions in the activated skill unless the
runtime procedure must configure those clients. Keep install/documentation claims
separate from runtime portability and support claims.

## 4. Define degraded behavior

For optional capabilities, state what the skill can still do when a tool, API,
network connection, or credential is unavailable. Report skipped checks and gaps;
do not fabricate passes or silently substitute a materially different workflow.

## 5. Validate and record evidence

Type evidence for each claim and record what it proves/does not prove:

- **Payload/structural:** parse claimed frontmatter/format and scan runtime files
  for unapproved platform markers (not install/workflow proof).
- **Install verified (named runtime/version):** locate or install the exact
  canonical payload through a recorded procedure from an installed/staged copy.
- **Workflow/behavior verified:** representative positive/negative (and
  non-activation where relevant) tasks against the contract in a recorded
  runtime/context (not universal compatibility).

Keep platform examples marked and conditional. Add or update fixtures showing
selection/non-activation boundaries as appropriate. Record checks run, skipped
checks with reasons, limitations, and recheck triggers for volatile facts.

Read `portability-patterns.md` for tier selection and `operational-patterns.md`
for CI lane design and evidence recording.
