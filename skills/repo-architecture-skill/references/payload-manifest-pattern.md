# Payload Manifest Pattern

Use a payload manifest only when an install, package, plugin, or release process
must assemble an artifact that differs from the canonical source tree. A static
skill already stored in its installable directory does not need a second tracked
copy or a sync script.

## Admission gate

Before adding a manifest, answer:

1. Which distribution consumer cannot use the canonical tree directly, and what
   artifact boundary does it require (runtime payload vs install/publish artifact)?
2. Is the output generated during packaging, or must it be tracked?
3. What proves the installed/packed artifact contains exactly the intended
   runtime payload (and excludes maintainer/control-plane material)?
4. Which file owns the artifact version, and what is the recovery path on drift?

If the only motivation is convenient browsing or copying, keep the payload
canonical and omit the manifest. Treat this pattern as context-dependent: do not
import release controls into repositories without a release artifact that
benefits from them.

## Manifest contract

The format may be ecosystem-native (`package.json` files, wheel metadata, plugin
manifest) or a small project manifest. It should declare exact runtime files by
category and, where relevant, distinguish runtime payload from adapter, package,
or maintainer artifacts, for example:

```json
{
  "entrypoints": ["SKILL.md"],
  "references": ["references/policy.md"],
  "scripts": ["scripts/check.py"]
}
```

Avoid a wildcard when the artifact is security-sensitive or separately
published. Exact inventories make additions reviewable and provide deterministic
evidence of declared contents (not runtime behavior or support status).

## Required checks

- Every declared source exists and is owned by the intended boundary.
- Every installed/packed file is declared; no declared runtime file is omitted.
- Generated files match their canonical sources (drift is detectable).
- Executable permissions are preserved when relevant.
- The artifact works from a staging directory without maintainer-only files.
- Version fields agree across manifests, tags, and release metadata when used.

Prefer generating artifacts into an ignored staging directory during tests.
Track generated replicas only when the downstream distribution mechanism
requires them in version control. Record check scope and skipped steps; an
inventory or staged-install check is structural/release evidence, not proof of
semantic correctness or client workflow behavior.

## Tool-backed skills

When a skill wraps a separately installable CLI, the package manifest should own
the executable inventory and the skill should describe how to locate it. Do not
copy the tool implementation into the skill directory merely to make the skill
self-contained. If an offline bundled mode is a real requirement, treat it as a
separate artifact and test it explicitly.

## Release integrity

Published artifacts may justify staged-install tests, version-alignment checks,
checksums, attestations/provenance, dependency audits, and immutable CI action
revisions. Apply these controls to the release lane and artifact, not
automatically to every static skill repository. For volatile release/catalog
or supply-chain guidance, prefer point-of-use primary-source verification and
record the checked date and recheck trigger.
