# Portability and Compatibility Evidence

Use this reference when choosing a portability tier, documenting installation,
or making compatibility claims for a named agent runtime.

## Portability tier

Classify what the payload requires before discussing client support:

| Tier              | Runtime content                                      | Structural claim                                  |
| ----------------- | ---------------------------------------------------- | ------------------------------------------------- |
| Fully portable    | Markdown and baseline metadata; no tool assumptions  | Plausible for runtimes supporting that skill form |
| Tool-portable     | General executables such as `git`, `python3`, `node` | Requires those tools and usable execution access  |
| Platform-specific | One client's APIs, hooks, commands, or paths         | Requires the named platform                       |

Portable text is not the same as verified client behavior. Shell availability,
sandboxing, authentication, discovery, and instruction adherence vary by
runtime.

## Frontmatter policy

Use only `name` and `description` for the broadest baseline unless an active
distribution or runtime target requires another field. Validate optional fields
against that target's current parser; do not assume unknown fields are ignored.

Keep platform-only metadata in a thin adapter when possible. An adapter may
point at the canonical payload or add required packaging metadata, but it should
not duplicate runtime instructions.

## Three evidence levels

| Claim             | Minimum evidence                                                                                         | Proves / does not prove |
| ----------------- | -------------------------------------------------------------------------------------------------------- | ----------------------- |
| Payload portable  | Canonical files parse under the claimed format and contain no known platform-only runtime dependency     | Structure/known markers only; not installation or workflow behavior. |
| Install verified  | A named runtime and version locates or installs the exact canonical payload through a recorded procedure | Discovery/installation for that runtime+version; not workflow behavior or broader compatibility. |
| Workflow verified | That runtime completes representative positive and negative tasks against the behavioral contract        | Observed behavior for recorded cases/runtime/context; not universal or future-version compatibility. |

A schema/shape check, deterministic validator, URL/anchor/freshness pass,
directory convention, marketplace listing, or successful copy does not establish
semantic correctness or workflow behavior. Platform documentation is intended
behavior, not runtime certification. Record checked dates/versions, scope, and
limitations; treat point-in-time or volatile claims as needing re-verification.

## Compatibility states

Use the narrowest state supported by current evidence:

| State               | Meaning                                                        |
| ------------------- | -------------------------------------------------------------- |
| `candidate`         | Payload appears structurally suitable; runtime is untested     |
| `install_verified`  | Discovery or installation succeeded; behavior remains untested |
| `workflow_verified` | Representative behavior passed for the recorded runtime        |
| `limited`           | Testing found a documented constraint                          |
| `unsupported`       | A known incompatibility prevents the workflow                  |

Record the runtime name and version, date, installation path, explicit and
implicit selection results, positive and negative scenarios, evidence or grading
criteria, and tool or sandbox limitations. A material payload, prompt, grader,
or schema change starts a new evidence baseline.

## Runtime-content scan

Search the canonical payload for platform commands, APIs, paths, hooks, and
metadata. Treat a scan as detection of known markers, not proof that no coupling
exists. Educational platform examples should be conditional and isolated from
the core procedure.

For tool-portable skills, test the actual runtime commands on each supported
operating system. Running a Markdown parser or maintainer validator on several
operating systems does not establish cross-platform workflow behavior.

## Adapter decision

Create an adapter only after selecting a platform as an active target and
identifying a concrete requirement. Prefer a path, import, symlink, or manifest
that points to canonical content. Avoid copied prose and avoid claiming that an
adapter proves runtime selection or instruction adherence.

An external discovery symlink can be a valid development adapter when the
client supports it and the target's ownership and mutability are understood.
That does not justify symlinks inside a shipped payload: copied or packaged
artifacts should remain self-contained unless their distribution contract
explicitly preserves and verifies links.

## Automation boundary

Keep deterministic payload checks in normal CI. Keep model-backed runtime
certification non-blocking and scoped to a named compatibility report. Reuse the
fixture vocabulary first; build a generic cross-runtime harness only after at
least two concrete uses share the same lifecycle and grading contract.
