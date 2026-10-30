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

1. Locate each runtime entrypoint and record every supported installation or
   publication path.
2. Classify the repository using the archetypes below. Use more than one only
   when the repository genuinely has multiple products.
3. Declare the four boundaries: authoring source, runtime payload, install or
   publish artifact, and maintainer infrastructure.
4. Measure each boundary independently. Do not infer health from a raw
   script-to-skill or reference-to-skill ratio.
5. Read the runtime instructions for trigger quality, procedure clarity,
   reference routing, portability, and verification behavior.
6. Load only the references needed for the observed archetype or failure mode.
7. Inspect validation, behavioral fixtures, CI, and release automation. Map each
   control to a concrete invariant and recovery path.
8. Run deterministic local checks when available. Separate their results from
   skipped network, model, platform, or publication checks.
9. Bound portability and compatibility claims to the evidence actually
   collected: payload structure, named-runtime installation, or workflow behavior.
10. Recommend changes in this order: correctness, installability, runtime safety,
    portability, behavioral confidence, maintainability, then polish.

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

### Keep controls proportionate

Add a check only for a concrete failure mode or high-cost invariant. A useful
check is simpler than what it verifies, fails deterministically when possible,
and names a recovery action.

Separate deterministic pull-request checks from volatile monitoring. URL
reachability, catalog state, model behavior, and external releases normally
belong in scheduled or explicitly requested jobs.

### Test behavior as well as shape

Schema and link validation cannot prove that a skill chooses the right workflow.
For decision-heavy skills, keep a small fixture contract containing positive and
negative triggers, representative repository profiles, expected classifications,
required boundaries, and prohibited recommendations. Add model regression only
when fixture validation cannot cover the costly failure mode.

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

Use three separate evidence claims:

| Claim             | Evidence required                                                   |
| ----------------- | ------------------------------------------------------------------- |
| Payload portable  | Canonical payload parses and has no known platform-only dependency  |
| Install verified  | A named runtime and version discovers or installs the exact payload |
| Workflow verified | That runtime passes representative positive and negative behavior   |

Evidence at one level does not prove the next. Use `candidate`,
`install_verified`, `workflow_verified`, `limited`, or `unsupported` for named
runtime status. Do not use unqualified `compatible`, `universal`, or
`agent-agnostic` claims.

### Measure the right surface

Report runtime files, runtime references and scripts, generated replicas,
maintainer scripts, distribution/version sources, and behavioral fixtures
separately. Counts are prompts for investigation, not universal pass/fail
thresholds. Judge whether each item has an owner, consumer, and failure mode.

### Preserve reusable findings economically

Keep one-off findings inline, repeated conditional guidance in a reference, and
widely reused active knowledge in a dedicated maintained source. Record the
transfer question and evidence scope, not only the originating anecdote.

## Reference Routing

- Read `references/skill-repo-audit-procedure.md` for the complete audit sequence.
- Read `references/file-swamp-patterns.md` when ownership or file growth is unclear.
- Read `references/portability-patterns.md` when choosing a portability tier.
- Read `references/payload-manifest-pattern.md` only for generated or packaged payloads.
- Read `references/dev-workflow-patterns.md` for canonical-source and drift decisions.
- Read `references/operational-patterns.md` for CI and behavioral-evaluation design.
- Read `references/npm-publishing-for-agent-skills.md` only for npm distribution.
- Read `references/portability-migration.md` when extracting a portable core.

## Completion Checklist

- [ ] Archetype selection is supported by observed files and distribution paths.
- [ ] All four boundaries are declared, including empty or identical ones.
- [ ] Canonical sources and any generated replicas are explicit.
- [ ] Runtime references and scripts have direct consumers.
- [ ] Portability and compatibility claims match their recorded evidence level.
- [ ] Deterministic validation and volatile monitoring are separated.
- [ ] When behavior is decision-heavy, representative positive and negative fixtures exist.
- [ ] When discovery paths exist, their ownership, permissions, symlink, and write boundaries are reviewed.
- [ ] When client-specific metadata or commands exist, they are isolated and security-reviewed.
- [ ] Sensitive evidence is reported without exposing matched values.
- [ ] Install instructions match the actual artifact layout.
- [ ] Checks were run or skipped with exact reasons.
