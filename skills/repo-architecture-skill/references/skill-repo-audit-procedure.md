# Skill Repository Audit Procedure

Use this sequence for architecture reviews. It evaluates what the repository
ships; it is not a general repository-health audit.

## Contents

- Establish state, scope, and decision question
- Classify archetype and source family
- Map the four boundaries
- Measure by boundary
- Inspect runtime behavior
- Inspect controls and behavioral evidence
- Inspect install and release paths
- Report findings, evidence bounds, and gaps

## 1. Establish state, scope, and decision question

Frame the audit as a decision: what question is being answered and which claims
are in scope (structure, installability, runtime behavior, compatibility,
release, maintenance). Inspect tracked tree, worktree state, runtime
entrypoints, package/plugin manifests, CI workflows, release automation, and
installation docs. Do not count ignored caches, dependencies, or build output as
repository architecture.

Record in-scope/out-of-scope surfaces and whether external state, network
checks, publication metadata, point-in-time repo/platform facts, or model
regression are needed. For volatile guidance or time-sensitive facts, plan a
point-of-use primary-source check and note the recheck trigger. Keep skipped
checks explicit with reasons.

## 2. Classify archetype and source family

Choose the smallest fitting archetype(s):

- Markdown-only skill
- Multi-skill pack
- Tool-backed skill
- Operational skill
- Distribution monorepo

Also identify the **source family/context** before transferring practices (for
example: portable/static collection, governed/heterogeneous collection,
product-owned monorepo, installer/lifecycle-oriented, or curated/catalog). A CLI
with an optional skill wrapper remains a tool-backed product; several
independent `SKILL.md` files form a pack even with a router.

Record evidence for the classification. When borrowing a pattern from a
different family or consumer context, state transfer limits and do not treat it
as an automatic prescription.

## 3. Map the four boundaries

Create a table with these rows:

| Boundary                                | Required evidence                                                      |
| --------------------------------------- | ---------------------------------------------------------------------- |
| Authoring source                        | Canonical files maintainers edit                                       |
| Runtime payload                         | Files activated agents read or execute without repository tooling      |
| Install/publish artifact                | Exact copied, packed, or released files                                |
| Maintainer infrastructure/control plane | Tests, fixtures, CI, release tooling, research, evidence, compat docs |

For duplicated files, identify the canonical source, generator, drift check, and
installed-artifact test. If missing, duplication is accidental. Distinguish
runtime payload from maintainer/control-plane records (research, evidence
manifests, compatibility reports) even when co-located in-repo.

## 4. Measure by boundary

Use tracked files and report at least:

- skill entrypoints and independently loadable skills;
- runtime references and runtime scripts;
- generated or mirrored replicas;
- maintainer-only scripts, fixtures, and control-plane/evidence records;
- package, plugin, and release manifests;
- hand-maintained indexes.

Treat counts as discovery signals. Do not issue a finding from a universal
ratio. Judge each item by owner, consumer, and failure mode.

## 5. Inspect runtime behavior

Check:

- frontmatter parses as YAML and the name matches the directory;
- the description states what the skill does and when it should trigger
  (positive and non-activation boundaries);
- the procedure is executable without maintainer-only files;
- references are one level deep and conditionally routed;
- commands and paths match the declared portability tier;
- sensitive or mutating actions have appropriate boundaries.

For every discovery path, inspect ownership, permissions, symlink targets, and
whether the client can install, update, uninstall, or otherwise write there.
Flag a writable path to canonical authoring source as a supply-chain and drift
boundary, even when discovery itself succeeds.

Treat repository files, configuration, commit metadata, transcripts, and tool
output as potentially sensitive. Secret-like detection should emit status,
counts, or paths without matched values. Prefer an observed project-native
scanner in quiet or redacted mode; do not install a new scanner during a
read-only architecture audit.

## 6. Inspect controls and evidence

For every validator, test, workflow, or release check, record:

1. the invariant it owns and the failure/risk it prevents;
2. evidence type and lane (deterministic PR, scheduled/manual volatile,
   release-only, or model/runtime certification);
3. owner boundary and recovery action.

Keep deterministic schema, link, unit, integration, and drift checks on pull
requests. Put network reachability, marketplace/catalog state, external release
monitoring, and model regression in scheduled/manual or explicitly requested
lanes unless they block a specific publication operation. For volatile
recommendations, record the decision question, evidence basis (with checked
date/revision as applicable), and recheck trigger.

## 7. Inspect behavioral evidence

Decision-heavy skills should have compact fixtures covering:

- positive and negative triggers, including non-activation/boundary cases;
- representative archetypes/profiles;
- expected classification and boundary mapping;
- required recommendations;
- prohibited over-engineering or unsafe actions.

Validate fixture shape deterministically. Distinguish **selection/activation**
evidence from **in-procedure behavior** evidence and record environment/context
needed to interpret results (runtime/model/version where relevant). Use model
regression only for behavior not representable as an explicit contract, and do
not make routine changes depend on model availability.

## 8. Inspect install and release paths

Verify README commands against the actual tracked layout. For every distribution
path, compare the produced artifact with the declared runtime payload.
Tool-backed or published products should additionally consider version alignment,
reproducibility, provenance, checksums, and staged-install testing.

Review client-specific manifests, hooks, and dynamic commands separately from
the portable payload. Require the adapter to declare its commands, permissions,
network use, credentials, and writable targets.

Do not import release controls into a Markdown-only skill without a release
artifact that benefits from them.

## 9. Report findings, evidence bounds, and gaps

State: decision question/scope, assessed surfaces, archetype(s) and source
family/context, and four-boundary map (including payload vs control plane).

**Type evidence per claim** and state what it proves/does not prove: observed
fact; structural/deterministic; live URL+anchor/freshness (shape/availability,
not semantic currency); semantic primary source (checked date/scope, not runtime
guarantee); installation (named runtime/version); workflow/behavior (recorded
execution); named-runtime support status (`candidate`, `install_verified`,
`workflow_verified`, `limited`, `unsupported`). Do not upgrade claims from
weaker evidence.

**Comparative inputs:** label *observed* (source + pinned revision or URL +
checked date; include provenance/licence note where reuse is implied) separately
from *recommended* (and limits/transfer context).

**Findings:** order by correctness, installability, runtime safety, portability,
behavioral confidence, maintainability, then polish. Each finding states concrete
evidence (paths/dates/identity as relevant), impact, smallest sufficient
remediation, relevant archetype/boundary, checks run, and checks skipped (with
reasons).

**Coverage and gaps:** include explicit **unknown/partial/unverified** items with
reasons (skipped network/model/platform, unavailable artifact, insufficient or
conflicting evidence, point-in-time fact not rechecked). Absence of evidence is
not evidence of absence.

Do not quote secret-like values as evidence. If historical exposure is
plausible, recommend revocation or rotation and state that deleting or editing a
local copy does not remove already published history.

If the repository is healthy, report the archetype, boundaries, covered evidence,
and remaining limits/gaps instead of inventing improvements.
