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

### Dependabot-aware architecture audit

When a repository uses Dependabot, inventory dependency manifests, lockfiles,
workflow action references, and their directories before recommending changes.
Declare the update ecosystems from that inventory rather than guessing from the
primary language. Treat scheduled version updates, vulnerability alerts, and
security-update pull requests as separate controls: they have different
triggers, grouping choices, and queue limits.

For a monorepo, use multiple directories and cross-directory grouping only when
the packages share an ecosystem and a dependency version must move together.
Otherwise, keep proposals scoped to the affected package boundary. Record the
owner and review rule for any `ignore`, `allow`, security-grouping, or
auto-merge setting. Do not recommend auto-merge merely because updates are
grouped or CI is green.

Make the maintenance lane observable. A repository with an unreviewed bot queue
can pause Dependabot updates or stop rebasing stale pull requests; the
maintainer routine should therefore inspect open Dependabot pull requests and
the paused state, not only failed CI.

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
Distinguish **selection/activation** evidence (should-trigger / should-not-trigger
or non-activation boundaries) from **in-procedure behavior** evidence (correct
classification, boundary mapping, recommendations, and prohibited actions for a
given profile). A compact contract should include:

- positive and negative trigger prompts or scenarios (including non-activation
  boundaries);
- representative observed profiles and source context;
- expected route/archetype and boundary assignments (for in-procedure cases);
- required recommendations and prohibited recommendations/unsafe actions;
- evidence expectations (paths/claims) and, when recorded, environment/context
  needed to interpret results (named runtime/model/version, constraints).

Validate fixture shape and grading contracts in the deterministic lane. Shape
and deterministic grading do not prove model behavior; they make intended
behavior reviewable. Keep routine CI model-free where possible. Run model
regression only after material trigger/workflow changes or on a schedule, grade
observable outputs against the contract, and record limitations; do not require
model availability for ordinary repository changes or treat a single run as a
reliability baseline.

## Evidence recording for volatile recommendations

When a recommendation depends on volatile guidance, external contracts, or
time-sensitive repo/platform facts (CI/runner, Actions permissions/trust,
Dependabot semantics, client discovery/install/activation, release/catalog
state, compatibility), record:

- the **decision question** and relevant scope/surface;
- **evidence basis** with type and checked date/revision/runtime identity (or
  explicit “unverified/point-in-time” status), and what it proves/does not prove;
- a concrete **recheck trigger** (event, change, or due condition).

Prefer point-of-use primary-source verification before changing behavior or
claims. Label comparative inputs as *observed* (source + pinned revision or URL
+ checked date) separately from *recommended* (with limits/transfer context).

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
