# Operational, CI, and Evaluation Patterns

Use this reference when deciding which controls belong in pull requests,
scheduled monitoring, model regression, or release automation.

## Control admission record

For each proposed control, record:

| Field       | Question                                            |
| ----------- | --------------------------------------------------- |
| Invariant   | What exact property must remain true?               |
| Evidence    | Which observed failure or costly risk justifies it? |
| Owner       | Which boundary owns the checked files?              |
| Determinism | Does identical local input produce the same result? |
| Recovery    | What should a maintainer do after failure?          |
| Lane        | PR, scheduled, manual, or release-only?             |

Reject a control whose invariant or recovery cannot be stated clearly.

## Automation and bot boundaries

Treat Dependabot and workflow bots as actors with narrowly scoped authority, not
as maintainers. Before recommending automation, record which identity can create
branches or pull requests, what its `GITHUB_TOKEN` or equivalent permissions
are, whether secrets are available, and whether its events can trigger another
workflow. Keep merge, approval, release, branch deletion, and repository-setting
changes behind explicit policy and human approval unless a separate threat-model
review justifies otherwise. Grouping dependency updates reduces review volume;
it does not establish that an update is safe.

## Execution lanes

### Deterministic pull-request lane

Use for frontmatter parsing, name/path agreement, local-link resolution,
portability scans, unit and integration tests, fixture-schema validation,
generated-payload drift, and formatting or linting owned by the repository.

Keep repository-owned checks fast and deterministic. A pinned validation-tool
bootstrap may require network access when it cannot be packaged locally; cache
it where practical, bound retries, fail closed, and keep volatile external
contract checks out of this lane. Add path filters only when they do not create
unvalidated gaps. Use concurrency cancellation for superseded runs.

### Scheduled or manual monitoring lane

Use for URL reachability, marketplace/catalog contracts, dependency freshness,
external release state, and model regression. A network outage or provider
change should not make an unrelated documentation pull request nondeterministic.

### Release lane

Use for staged installation, artifact inventory, version alignment, checksums,
provenance, publication credentials, and post-package smoke tests. Apply this
lane only when the repository publishes an artifact beyond a directly copied
static skill directory.

## Behavioral fixture contract

Decision-heavy skills need explicit examples in addition to structural checks.
A compact contract should include:

- positive and negative trigger prompts;
- representative observed profiles;
- expected archetype or route;
- required boundary assignments;
- required recommendations;
- prohibited recommendations or unsafe actions.

Validate the contract's schema in the deterministic lane. The contract does not
prove model behavior, but it makes intended behavior reviewable and supports a
future model runner without embedding provider-specific execution in the skill.

Run model regression only after material trigger or workflow changes, or on a
schedule. Grade observable outputs against the fixture contract. Do not require
model availability for ordinary repository changes.

## Policy tests

Prefer a test of the relationship that can drift over a test that merely checks
file presence. Examples:

- every package-manifest runtime file appears in the installed artifact;
- every router destination names an existing independently valid skill;
- every workflow-created label is accepted by the label policy;
- every README install command targets the declared payload directory;
- every external contract is monitored in the volatile lane, not the PR lane.

## Dependency and action integrity

Pin validation dependencies and CI actions according to the repository's threat
and reproducibility requirements. Published or security-sensitive projects
should prefer immutable action revisions and lockfiles. A static skill with one
trivial check can use a short exact development-requirements file. When several
maintainer tools share a Python environment, a non-package uv project plus a
committed lockfile gives deterministic sync and native dependency automation
without adding a runtime dependency.
