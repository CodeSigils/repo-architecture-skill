# File-Swamp and Ownership Patterns

File-swamp is an ownership problem, not a file-count threshold. It appears when
files lack a clear consumer, canonical source, or deletion condition.

## Diagnostic questions

For each suspicious file or directory, ask:

1. Which of the four boundaries owns it (authoring source, runtime payload,
   install/publish artifact, maintainer/control plane)?
2. What reads, executes, installs, publishes, or validates it, and is that
   consumer real and in scope?
3. Is it canonical, generated, installed artifact, or historical/evidence?
4. What concrete failure, risk, or drift occurs if it disappears or diverges?
5. Is the same information maintained elsewhere, and which source is canonical?

## Strong signals

- Tracked replicas without a canonical source, generator, and drift check.
- Runtime references that `SKILL.md` never routes to.
- Maintainer plans, research, fixtures, CI helpers, or evidence/compatibility
  records inside the runtime payload.
- Hand-maintained indexes that duplicate filesystem or manifest discovery.
- Scripts with no caller in runtime instructions, package scripts, CI, or docs.
- Several sources claiming ownership of the same workflow or claim.
- Validators that enforce prose layout without protecting behavior or an artifact.
- Generated/installed artifacts committed even though installation can consume
  the canonical source (unless the distribution path requires them).

## Archetype- and context-sensitive interpretation

Interpret signals relative to archetype and source family/context; do not transfer
controls from a different family as automatic prescriptions.

| Observation                | Healthy possibility                                              | Unhealthy possibility                        |
| -------------------------- | ---------------------------------------------------------------- | -------------------------------------------- |
| Many scripts, one skill    | Tool-backed skill with tested runtime code                       | Static skill with speculative helpers        |
| Many references, one skill | Conditional domain variants with direct routing                  | Historical notes copied into payload         |
| Large maintainer surface   | Operational/released product or control plane with owned checks  | Checks/records added without failure evidence |
| Duplicate payload tree     | Required install/publish artifact with generator and drift test  | Convenience copy with no install consumer    |
| Several skills             | Independently loadable pack with router/entrypoint tests         | Accidental fragmentation of one procedure    |

## Remediation order

1. Classify archetype/source family and declare all four boundaries (including
   payload vs maintainer/control plane).
2. Choose one canonical authoring source for every concept or claim.
3. Remove unconsumed files and relocate maintainer-only or evidence material.
4. Inline small fragments; route genuinely conditional detail to references.
5. Eliminate tracked replicas when clients can install the canonical payload.
6. Where replication is required, generate it and test the installed artifact.
7. Add only the smallest check needed to prevent an observed recurrence, in the
   cheapest appropriate lane.

Report counts as discovery signals, not findings by themselves. Base findings on
ownership, consumers, failure modes, and evidence bounds; record gaps/unknowns
when origin or consumer cannot be established.
