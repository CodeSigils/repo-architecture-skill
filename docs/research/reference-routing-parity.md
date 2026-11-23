# Reference Routing Parity (C-036 Differentiation)

- **Date:** 2026-11-23
- **Status:** local implementation evidence / maintainer note
- **Scope:** `skills/repo-architecture-skill/` reference routing contract
- **Related evidence:** skill-catalogue C-036 `docs/research/2026-11-23-shared-routing-method-contract.md`, C-037 `docs/research/2026-11-23-c036-counterexample-pass.md` (checked 2026-11-23)

## Observed problem

`skills/repo-architecture-skill/SKILL.md` routes nine independent conditional references through `## Reference Routing` as backtick `Read \`references/...\`` entries. `scripts/validate.py` already enforced an `EXPECTED_REFERENCES` allowlist, payload inventory, required sections, 500-line budget, and markdown local-link checks. It also failed when an observed reference file name was not present in SKILL body text. It did **not** fail when `## Reference Routing` named a `references/*.md` file that did not exist, because markdown link resolution only inspects markdown links.

## Decision

Implement **bidirectional reference-routing parity** in `scripts/validate.py`:

- Parse reference names from the `## Reference Routing` section (`references/<name>.md`).
- Compare against observed top-level payload `references/*.md` files.
- Fail on unrouted reference files and dangling routed references.
- Add `--self-test` fixtures for ok/unrouted/dangling.

Also make shape-first inspection explicit in `SKILL.md` Procedure/checklist. No new anchor+delta+guard contract was added.

## Why different from C-036 anchor+delta+guard

C-036/C-037 (skill-catalogue, 2026-11-23) found the anchor+delta+guard pattern viable for multi-reference shared-method prose-drift cases, but found **no portable normative anchor/link-contract mandate**; counterexamples showed multiple viable enforcement shapes.

Repo-architecture-skill references are **independent conditional concerns**, not routed deltas narrowing one shared method. The proportional invariant is routing completeness/discoverability, not shared-method ownership. Therefore this repo uses bidirectional parity inside the existing validator/allowlist model instead of C-036 anchor/delta markers.

## Recheck trigger

Revisit if reference files become shared-method deltas with prose-drift risk, if routing moves to generated/manifest-driven form, or if a non-markdown reference type is introduced.
