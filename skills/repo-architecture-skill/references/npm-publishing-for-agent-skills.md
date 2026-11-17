# npm Publishing for Tool-Backed Skills

Use npm when the repository contains a Node.js tool that is useful outside the
agent runtime. Do not publish a Markdown-only skill to npm merely to gain another
installation command.

## Admission criteria

npm is a good fit when:

- a standalone CLI or library is the real runtime product;
- Node.js is an honest, documented prerequisite;
- users benefit from package-manager installation, `npx`, or programmatic use;
- the package has meaningful tests independent of agent activation;
- the project can maintain versions and releases as a software product.

Keep skill-catalog installation as the primary path when the payload is only
instructions, references, templates, or small agent-invoked scripts. Treat npm as
a separate distribution/artifact decision (source-family and product context
matter), not a default for all skill repositories.

## Artifact boundaries

A dual-use repository has at least two install/publish artifacts:

1. the npm tarball;
2. the agent skill directory/payload.

Declare and test each inventory independently. `package.json.files` should own
the npm tarball. The canonical skill directory or a dedicated skill manifest
should own the agent runtime payload. Do not use one ambiguous list when the
artifacts contain different files, and keep maintainer/control-plane material
(research, evidence, CI-only fixtures) out of runtime payloads.

Prefer one implementation source. The skill should invoke the installed CLI or
reference canonical package code; avoid copying the tool implementation into a
second tracked tree. If an offline bundled skill is required, treat it as a
separate generated artifact with a staged-install test and clear ownership.

## Package controls

For a published package, consider controls appropriate to the release artifact
and risk (evidence of what each check proves):

- an exact runtime `files` allowlist and artifact inventory checks;
- unit and integration tests for the CLI or library;
- `npm pack --dry-run` or an equivalent inventory assertion;
- installation and command smoke tests from the packed tarball (staged/install
  evidence for that artifact/version);
- version alignment among `package.json`, skill metadata when present, tags,
  and releases;
- a lockfile for development dependencies where reproducibility requires it;
- provenance/attestations and immutable CI actions appropriate to release risk;
- a prepublish gate that runs deterministic tests without network-dependent
  monitoring.

Zero runtime dependencies can simplify installation and supply-chain review, but
it is a product choice rather than a universal skill-repository requirement.

## Naming and discovery

Verify package-name availability at decision time through documented npm or
registry interfaces. Do not embed availability, popularity, download counts, or
competitor rankings in the runtime skill; those facts are volatile and decay.
For volatile registry/catalog guidance, record checked date/scope and a recheck
trigger.

The repository, package, CLI binary, and skill may have different names, but the
README must map them explicitly. Choose the CLI name for shell usability, the
package name for registry discovery, and the skill name for trigger clarity.

## Release separation

Keep external registry, download, or catalog monitoring in scheduled/manual jobs.
Keep package tests and artifact inventory in pull requests; keep publish actions
in an explicit release lane. Publish only from an explicit tag or release
workflow with least-privilege credentials. Separate deterministic evidence from
volatile monitoring and from runtime/support certification claims.
