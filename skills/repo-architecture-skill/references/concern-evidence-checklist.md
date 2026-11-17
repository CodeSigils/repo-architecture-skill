# Concern-to-Evidence Checklist (Non-Normative)

Lightweight prompt checklist to reduce missed concerns during audits. This is
**guidance, not a standard or pass/fail gate**. For each applicable concern,
record the decision question, evidence type/date or runtime identity, what is
proven/not proven, and any unknown/partial/unverified items or recheck triggers.

| Concern | Questions to ask | Expected evidence (examples) | Common limits |
| --- | --- | --- | --- |
| Scope & decision | What claim/decision is in scope? What is explicitly out of scope? | Observed repo state, stated question, in/out-of-scope notes | Uninspected surfaces remain unverified |
| Archetype & source family | What archetype(s) and source family/context fit? Are borrowed practices transferable? | Observed entrypoints/artifacts/distribution paths; *observed* comparison with source+revision or URL+checked date | Transfer limits; unlike artifacts not interchangeable |
| Boundaries & ownership | What is authoring source, runtime payload, install/publish artifact, maintainer/control plane? Who consumes each item? | File inventory by boundary, canonical/replica/generator/drift relations | Maintainer evidence ≠ runtime payload; counts are signals |
| Trigger & activation | What should/should not trigger or route here? | Positive and non-activation descriptions/cases, selection evidence where tested | Description/shape checks ≠ selection or behavior proof |
| Instruction & procedure | Is the procedure executable, scoped, and verifiable? Are references routed? | Readthrough, link checks, fixture expectations, success criteria | Deterministic checks ≠ model adherence |
| Payload & progressive disclosure | Is runtime payload self-contained and lean? Are conditional details correctly placed? | Payload inventory, reference routing, install artifact contents | Generated/installed copies can drift |
| Capability, trust & safety | What tools/permissions/mutations/network/credentials are involved? How is sensitive evidence handled? | Observed manifests/hooks/commands/paths, redaction policy, adapter review | Heuristic detection ≠ proof; local edits ≠ history remediation |
| Portability & adaptation | What portability tier applies? What adapters exist and what do they require? | Payload scan, adapter isolation, named-runtime install/workflow records | Payload portability ≠ install ≠ workflow; docs ≠ certification |
| Installation & lifecycle | How is it installed/updated/removed? Do docs match artifacts? | Staged/install tests, artifact inventory, client/version evidence, recheck trigger | Installer/platform behavior is volatile and runtime-specific |
| Validation & CI | What invariants are checked, in which lane, with what recovery? | Deterministic/volatile/release/model evidence, CI config, run results or skip reasons | Green/freshness/anchors ≠ semantic currency or behavior |
| Behavioral evaluation | Is selection/activation separated from in-procedure behavior? Are boundaries covered? | Fixture contracts, deterministic grading, recorded live runs with environment/limits | Single run ≠ reliability; unrun cases remain unverified |
| Provenance & freshness | Are sources/claims dated and traceable? What is point-in-time or volatile? | Pinned revisions/URLs+checked dates, provenance/licence notes, recheck triggers | Point-in-time facts need re-verification; popularity ≠ evidence |