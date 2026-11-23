---
name: repo-architecture-skill
description: Design, review, and tighten agent skill repositories. Use when creating or auditing a skill repo, choosing between a single skill, skill pack, tool-backed skill, operational skill, or distribution monorepo, defining source and shipping boundaries, reducing file-swamp, selecting portability and release controls, or adding proportionate validation and behavioral evaluation.
---

# Repo Architecture Skill

Design or audit a skill repository by classifying what it ships before applying
structural rules. Prefer a compact runtime procedure with conditional references.

Do not substitute this skill for domain-specific authoring guidance, distribution
documentation, or a general repository-health audit.

## Procedure

1. **Frame the decision and inspect repository shape.** Name the
   audit/recommendation question and the claim being made (structure,
   installability, runtime behavior, compatibility, release, maintenance).
   Record in scope and out of scope. Inspect the observed repository shape
   first - inventory files, entrypoints, install/publication paths, and control
   surfaces before prescribing controls. When the question depends on volatile
   guidance or time-sensitive repo/platform facts, plan a point-of-use check
   and note the recheck trigger/date.
2. **Locate artifacts and paths.** Record every runtime entrypoint and every
   supported installation or publication path. Treat this inventory as evidence
   for later boundary and control decisions, not as something to assume.
3. **Classify by source family/archetype and product.** Choose the smallest
   fitting archetype(s) below and identify the source family/context before
   borrowing practices (portable/static collection, governed/heterogeneous
   collection, product-owned monorepo, installer/lifecycle, curated/catalog).
   State transfer limits when a pattern comes from a different family or
   consumer context. Use more than one archetype only for genuinely multiple
   products.
4. **Declare the four boundaries.** Map authoring source, runtime payload,
   install or publish artifact, and maintainer infrastructure/control plane
   (including evidence, CI, research, compatibility records, and release
   tooling). A file may be copied only when the distribution mechanism requires
   it; identify the canonical copy, generator, drift check, and installed test.
5. **Measure and inspect by boundary.** Measure each boundary independently (do
   not infer health from raw ratios). Inspect runtime behavior for trigger
   quality (positive and non-activation boundaries), procedure clarity,
   reference routing, portability, sensitive/mutating actions, and verification.
6. **Load only needed references.** Read the conditional references for the
   observed archetype or failure mode.
7. **Inspect controls and behavioral evidence.** Map each validator/fixture/
   CI/release control to a concrete invariant, evidence, owner, and recovery
   path. Separate deterministic checks from volatile monitoring and from
   model/runtime certification; distinguish selection/activation evidence from
   in-procedure behavior evidence where applicable.
8. **Run and record checks.** Run deterministic local checks when available.
   Record results, exact reasons for skipped checks, and evidence type/date for
   each claim. Do not treat freshness/anchor checks, schema/shape checks, or a
   green run as semantic currency or runtime/support certification.
9. **Report bounded findings and gaps.** Classify evidence per claim (observed
   fact, structural/deterministic, live URL+anchor/freshness, semantic primary
   source, installation, workflow/behavior, named-runtime support status) and
   state what it proves and does not prove. Include assessed scope, covered
   findings (with evidence paths/dates), and explicit unknown/partial/unverified
   items with reasons. For comparative inputs, label *observed* (source+revision
   or URL+checked date) separately from *recommended* (and limits). For volatile
   recommendations record the decision question, evidence basis, and recheck
   trigger.
10. **Recommend smallest sufficient changes.** Order by correctness,
    installability, runtime safety, portability, behavioral confidence,
    maintainability, then polish. Keep recommendations proportional to the
    artifact/risk and bounded to the evidence collected.

## Repository Archetypes

| Archetype             | Defining characteristic                                               | Typical controls                                         |
| --------------------- | --------------------------------------------------------------------- | -------------------------------------------------------- |
| Markdown-only skill   | Static instructions and optional references                           | frontmatter, links, portability, behavior fixtures       |
| Multi-skill pack      | Router or several independently loadable skills                       | routing, name uniqueness, standalone safety              |
| Tool-backed skill     | Skill invokes bundled or separately installed code                    | unit/integration tests, runtime manifest, staged install |
| Operational skill     | Methodology depends on rich maintainer evidence or changing contracts | fixtures, trust checks, scheduled monitoring             |
| Distribution monorepo | Multiple install formats, plugins, or release artifacts               | version alignment, reproducibility, provenance           |

Treat a non-skill build repository as a useful control, not as evidence that
every skill needs release engineering. Import only practices justified by the
skill's actual artifact and risk.

## Four Boundaries

For every file, assign exactly one primary ownership boundary:

| Boundary                    | Question                                                                 |
| --------------------------- | ------------------------------------------------------------------------ |
| Authoring source            | Where does a maintainer edit the canonical content?                      |
| Runtime payload             | What can the activated skill read or execute without repository tooling? |
| Install or publish artifact | What exact files reach a client, package registry, plugin, or release?   |
| Maintainer infrastructure   | What exists only to develop, test, evaluate, or publish the payload?     |

A file may be copied into another boundary only when the distribution mechanism
requires it. Declare the canonical copy, generate the replica, verify drift, and
test the installed artifact. Prefer one tracked copy for static skill packages.

## Design Rules

### Choose methodology or collection intentionally

Ship navigation and evaluation criteria when useful resources already exist.
Ship a collection when the items themselves are scarce, uniform, and difficult
to discover.

### Classify before transferring practices

Identify the source family/archetype and consumer context before adopting a
layout, control, release, installer, or governance pattern. State what transfers
and what does not (for example, plugin/monorepo release, marketplace intake, or
installer lifecycle patterns may not transfer to a markdown-only or single-skill
repo). Treat comparisons as evidence inputs, not automatic prescriptions.

### Keep controls proportionate

Add a check only for a concrete failure mode or high-cost invariant. A useful
check is simpler than what it verifies, fails deterministically when possible,
and names a recovery action.

Separate deterministic pull-request checks from volatile monitoring and from
model/runtime certification. URL reachability, catalog state, external releases,
and live model behavior normally belong in scheduled/manual or explicitly
requested lanes.

### Test behavior as well as shape

Schema and link validation cannot prove that a skill chooses the right workflow.
For decision-heavy skills, keep a small fixture contract covering positive and
negative triggers (including non-activation boundaries), representative profiles,
expected classifications/boundaries, required recommendations, and prohibited or
unsafe actions. Record environment/context needed to interpret results and treat
selection/activation evidence separately from in-procedure behavior evidence. Add
model regression only when fixture validation cannot cover the costly failure
mode.

### Type evidence and bound claims

For every material claim, name the evidence type, checked date/revision or
runtime identity as relevant, and what it proves/does not prove:

- **Observed fact** — repository/runtime state directly inspected.
- **Structural/deterministic** — schema, link, unit, policy, or local checks on
  fixed inputs (proves the checked invariant, not runtime behavior).
- **Live URL/anchor/freshness** — reachability, required anchors, recorded
  verification date (shape/availability, not semantic currency).
- **Semantic primary source** — primary docs/specs/guidance re-read for a
  specific claim on a stated date (context for decisions, not a runtime
  guarantee).
- **Installation evidence** — named runtime/version discovers or installs the
  exact payload.
- **Workflow/behavior evidence** — representative positive/negative execution
  recorded against a contract.
- **Named-runtime support status** — bounded claim aligned to collected evidence.

Do not upgrade a claim from weaker evidence: deterministic/freshness/green
checks do not prove semantic correctness or runtime behavior; platform docs do
not prove workflow certification. For volatile recommendations, record the
decision question, evidence basis, and recheck trigger.

### Protect sensitive evidence

Treat repository content, commit metadata, configuration, transcripts, and tool
output as potentially sensitive. Report secret-like matches as status, counts,
or paths without echoing values. Prefer project-native scanners in quiet or
redacted mode, and distinguish heuristic detection from proof. If exposure may
have occurred, recommend revocation or rotation rather than implying that a
local edit removes published history.

### Use progressive disclosure

Keep the operating procedure in `SKILL.md`. Put conditional, historical, or
variant-specific detail in one-level-deep references and state when to read it.
Do not duplicate explanations across runtime files.

### Choose portability deliberately

| Tier              | Content                                             | Expected reach            |
| ----------------- | --------------------------------------------------- | ------------------------- |
| Fully portable    | Markdown and portable metadata; no tool assumptions | Compatible skill runtimes |
| Tool-portable     | General tools such as `git`, `python3`, or `node`   | Runtimes with those tools |
| Platform-specific | One client's APIs, hooks, commands, or paths        | That client only          |

Keep platform adapters outside a portable core. A README may document install
paths without making those paths runtime requirements.

Use separate evidence claims and statuses: `candidate`, `install_verified`,
`workflow_verified`, `limited`, or `unsupported` for named runtime/version
results. Evidence at one level does not prove the next. Do not use unqualified
`compatible`, `universal`, or `agent-agnostic` claims.

### Measure the right surface and keep boundaries distinct

Report runtime files, runtime references and scripts, generated replicas,
maintainer scripts, distribution/version sources, behavioral fixtures, and
maintainer evidence/control-plane records separately. Map items to the four
boundaries (authoring source, runtime payload, install/publish artifact,
maintainer infrastructure/control plane). Counts are prompts for investigation,
not universal pass/fail thresholds. Do not import maintainer/control-plane
assumptions into portable runtime payload or support claims.

### Preserve reusable findings economically

Keep one-off findings inline, repeated conditional guidance in a reference, and
widely reused active knowledge in a dedicated maintained source. Record the
transfer question, source family/context, and evidence scope. For comparative
inputs distinguish *observed* (source + pinned revision or URL + checked date,
with provenance/licence note where reuse is implied) from *recommended* (and
limits), not only the originating anecdote.

## Reference Routing

- Read `references/skill-repo-audit-procedure.md` for the complete audit sequence.
- Read `references/file-swamp-patterns.md` when ownership or file growth is unclear.
- Read `references/portability-patterns.md` when choosing a portability tier.
- Read `references/payload-manifest-pattern.md` only for generated or packaged payloads.
- Read `references/dev-workflow-patterns.md` for canonical-source and drift decisions.
- Read `references/operational-patterns.md` for CI and behavioral-evaluation design.
- Read `references/npm-publishing-for-agent-skills.md` only for npm distribution.
- Read `references/portability-migration.md` when extracting a portable core.
- Read `references/concern-evidence-checklist.md` for a lightweight, non-normative concern-to-evidence prompt checklist.

## Completion Checklist

- [ ] Decision question/scope is stated; repository shape was inspected first and archetype/source family/context are supported by observed files and distribution paths (transfer limits noted where relevant). No controls were prescribed before boundaries/artifacts were identified.
- [ ] All four boundaries are declared (including empty/identical ones), with canonical sources/replicas, consumers, and payload vs maintainer/control-plane items explicit.
- [ ] Runtime references/scripts have direct consumers; reference routing is bidirectionally complete (every `references/*.md` routed, every routed ref exists); counts treated as signals, not ratios.
- [ ] Claims are evidence-typed and bounded (observed/deterministic/freshness/semantic/installation/behavior/support status) with what they prove and do not prove.
- [ ] Deterministic validation, volatile monitoring, and model/runtime certification are separated; selection/activation vs behavior evidence distinguished where relevant.
- [ ] Volatile recommendations (if any) include decision question, evidence basis/checked date, and recheck trigger.
- [ ] Comparative inputs distinguish *observed* (source+revision or URL+checked date) from *recommended* (with limits/provenance where applicable).
- [ ] When behavior is decision-heavy, representative positive and negative (including non-activation) fixtures exist; when discovery paths or client-specific metadata/commands exist, ownership/mutation boundaries and security review are recorded.
- [ ] Sensitive evidence is reported without exposing matched values; install instructions match the actual artifact layout.
- [ ] Checks were run or skipped with exact reasons; report includes covered findings and explicit unknown/partial/unverified items.
