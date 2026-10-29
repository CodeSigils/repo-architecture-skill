# Automation Bots and Workflow Boundaries

> Reviewed: 2026-10-29
>
> Evidence type: repository configuration, GitHub runner-image announcements,
> and official GitHub documentation

This note records what automation can do in this repository and what remains a
human decision. It is maintainer guidance, not runtime skill content.

## Repository actors

| Actor | Current use here | Effective boundary |
| --- | --- | --- |
| `dependabot[bot]` | Proposes UV and GitHub Actions dependency updates | Creates branches and pull requests; does not merge them |
| `github-actions[bot]` | Runs `validate` and GitHub-managed Dependabot update workflows | Current repository workflow token is read-only; no PR, branch, release, or issue mutation |
| Human maintainer | Reviews dependency changes and policy exceptions | Merges changes and changes repository settings |

The `github-actions[bot]` identity is the execution identity for workflow jobs,
not evidence that a workflow has broad write authority. Effective permissions
come from the workflow `permissions` block and any job-level override.

## Dependabot services and current posture

GitHub exposes three related Dependabot services with different evidence and
controls:

| Service | Trigger and purpose | Current repository posture |
| --- | --- | --- |
| Alerts | GitHub detects a known vulnerable dependency | Review from the Security tab; an alert is evidence to investigate, not a merge instruction. |
| Security updates | An alert can produce a pull request that moves to the minimum version that resolves the vulnerability | Enabled and not paused, checked through the repository API on 2026-10-29. Review the advisory, the resulting lockfile, and the tests. |
| Version updates | A scheduled `dependabot.yml` check proposes newer allowed versions | Enabled for `github-actions` and `uv`; the configuration below is authoritative for schedule, grouping, labels, and the version-update PR cap. |

Security and version updates both appear as Dependabot pull requests, but they
are not interchangeable. Version updates aim to keep dependencies current;
security updates address known vulnerabilities and normally choose the minimum
non-vulnerable release. The three-day version-update cooldown and the
`open-pull-requests-limit` described below do not govern security updates.
Security updates instead have GitHub's separate fixed limit of ten open pull
requests.

## Version updates and security updates

Ordinary Dependabot version updates follow this repository's weekly schedule,
ecosystem-specific grouping, labels, and two-PR cap. They keep the pinned
maintainer toolchain current but do not by themselves indicate a vulnerability.

Dependabot security updates are advisory-driven responses to known vulnerable
dependencies. Do not assume they arrive on the weekly schedule or are governed
by the same configuration as ordinary version updates. Treat the advisory,
affected dependency, lockfile change, and test result as separate review
evidence. This repository does not auto-merge either type: a maintainer still
reviews the diff and green checks before merging.

## Current configuration

Dependabot checks both ecosystems weekly:

- both checks run Monday at 08:00 UTC, giving maintainers a predictable review
  window;
- GitHub Actions updates are grouped under `actions-maintenance`, which accepts
  minor and patch updates;
- UV patch updates are grouped under `uv-maintenance`;
- UV minor updates for Ruff and ty are isolated under `ruff-minor-review` and
  `ty-minor-review`, because their zero-major minor releases are the ones that
  break the locked toolchain contract;
- major updates remain separate for manual review;
- each ecosystem is capped at two open pull requests;
- labels identify dependency, Python/UV, and GitHub Actions changes.

`validate.py` enforces the complete reviewed `dependabot.yml` shape: the two
root directories, Monday schedule, queue caps, labels, and version-update group
rules. It rejects unreviewed filters, target branches, registries, cooldowns,
multi-ecosystem groups, and security-update groups. Any of those can be valid
in a different repository, but here each changes the maintenance or security
policy and needs an intentional validator and documentation update.

The groups in this file apply to version updates. A security-update group would
need an explicit `applies-to: security-updates` rule or a repository/organization
security-update setting; neither should be inferred from the version groups.
If grouped security updates are considered later, decide first whether combining
multiple fixes would make advisory review harder, then document the setting and
its owner here.

GitHub now applies a three-day cooldown to ordinary Dependabot version updates
by default. Security updates remain immediate. This repository intentionally
uses that platform default rather than duplicating it in `dependabot.yml`.

The UV groups partition the update types rather than relying on group order:
every group accepts a disjoint set of `update-types`, so a given update matches
at most one group. GitHub assigns an update that could match several groups to
the first matching group. Keeping the rules disjoint makes that ordering
irrelevant here and preserves the intended isolated review of Ruff and ty
minor releases.

`exclude-patterns` is deliberately unused. Excluding a dependency from a group
does not skip it: the dependency becomes ungrouped and still receives its own
pull request, including for major updates, which bypass the group's
`update-types` filter entirely. Exclusion would therefore have doubled the
review load instead of reducing it.

The two-pull-request cap bounds concurrent version-update pull requests, not
the rate at which they arrive. Each ecosystem entry carries its own cap, shared
across its grouped and ungrouped version-update pull requests; a group consumes
one slot. When the cap is reached, Dependabot does not open another version
update until capacity becomes available. Security updates use a separate,
fixed limit of ten open pull requests. Review both queues rather than assuming
that a quiet week means all dependencies are current.

For GitHub Actions, Dependabot checks action references and reusable-workflow
references. The immutable SHA pin is therefore maintained as a reviewed
dependency update: inspect the version comment, changed SHA, release notes,
and resulting workflow behavior together. The `UV_VERSION` environment value
is different because it is an ordinary workflow scalar, not a recognized
dependency reference; Dependabot will not maintain it.

The repository's `validate` workflow has two lanes:

1. `deterministic` runs on pushes and pull requests. It uses read-only
   permissions, pinned actions, a pinned UV version, the locked environment,
   custom repository validation, `skills-ref`, fixture tests, lint, format, and
   type checks. It runs for the `requires-python` floor and one newer release,
   currently 3.13 and 3.14, and a matrix cell reports independently instead of
   cancelling its siblings. Environment sync, lint, format, type checks, and
   canonical validation are contiguous so a preflight failure fails fast, and
   the live `skills-ref` clone retries bounded transient failures while still
   failing persistent drift.
2. `monitor-external-contracts` runs only on the weekly schedule or manual
   dispatch. It checks external evidence URLs and freshness markers. Its URL
   checker retries bounded transient failures but still fails persistent drift.

## Runner image and bootstrap-tool policy

Both CI jobs explicitly use `ubuntu-26.04`. `ubuntu-latest` is a moving label:
GitHub announced its transition from Ubuntu 24.04 to 26.04 in November 2026.
Pinning the supported 26.04 label makes that operating-system baseline visible
in review and prevents a future `ubuntu-latest` transition from changing CI
without a repository change. This is an OS-release pin, not an immutable VM
image pin; GitHub continues to update the 26.04 image. The workflow still
installs the tested Python and uv versions explicitly rather than relying on
the runner's preinstalled tools.

The `validate.py` contract enforces `ubuntu-26.04` for every CI job. When the
runner line changes, update the workflow, this contract, and this note together
after testing the exact proposed runner label. Do not choose a runner solely
because its cached tools happen to make a job faster.

The sibling [repo-health-scan automation policy](https://github.com/CodeSigils/repo-health-scan/blob/main/docs/automation-identities.md)
records the same general least-privilege and review principles. Its exact
workflow permissions, update limits, and branch-cleanup behavior are specific
to that repository, so this note remains the authoritative maintenance record
for `repo-architecture-skill`.

The explicit `UV_VERSION` pin remains a separate manual review boundary.
Dependabot can update the `setup-uv` action reference, but not an arbitrary
workflow environment value. Review a new uv release, update the pin, and run
the locked suite before changing it. The same distinction applies to the
Python baseline: package metadata owns the minimum supported version, while
the workflow matrix proves that floor and one newer release.

Merged source branches are deleted by the repository setting. No repository
workflow creates, approves, merges, rebases, closes, or deletes pull requests.
Repository rules require every change to `main` to arrive through a pull request
with the `deterministic (3.13)` and `deterministic (3.14)` checks passing. The
repository-wide auto-merge feature is disabled. The ruleset deliberately
requires no approving review count because this is a small maintainer project,
but a human still decides whether and when to merge each reviewed pull request.

## Important GitHub behavior

- A workflow's `GITHUB_TOKEN` is short-lived and scoped to the job. Unspecified
  permissions are not granted when the workflow sets a restrictive permission
  block.
- Events caused by `GITHUB_TOKEN` generally do not recursively trigger new
  workflow runs. `workflow_dispatch` and `repository_dispatch` are explicit
  exceptions.
- Dependabot pull-request workflows should be treated as untrusted dependency
  changes. They must not receive ordinary repository secrets by default.
- `allow` rules narrow which dependencies are considered and `ignore` rules
  take precedence when both match. Neither is present here: adding either is a
  policy decision that must name the excluded maintenance responsibility.
- Grouping reduces review and CI volume; it does not establish that an update
  is safe. Review the diff and green checks before merging.
- If maintainers leave Dependabot pull requests untouched, GitHub can pause
  updates after 90 days; it also stops rebasing inactive Dependabot pull
  requests after 30 days. The paused state and stale queue are operational
  signals, not evidence that dependencies are current.
- A successful workflow proves only the checks it actually ran. A skipped
  external-monitor job on a pull request is expected because that lane is
  schedule/manual-only.

## Maintainer routine

1. Review Dependabot pull requests weekly.
2. Classify each proposal as an alert follow-up, security update, or version
   update before applying the corresponding review standard.
3. Merge narrow, green dependency-only updates after inspecting the diff,
   advisory or release notes, and lockfile effect.
4. Close stale or unneeded proposals deliberately; do not assume the cap
   represents a complete or queued update inventory.
5. Check the repository's Dependabot paused state and stale pull-request queue;
   interact deliberately before the 90-day inactivity threshold.
6. Confirm merged branches are removed automatically.
7. Investigate failed or ambiguous checks; do not bypass protection merely to
   clear a queue.
8. Re-check this note when adding a workflow that writes issues, releases,
   attestations, pull requests, branches, or repository settings.

## Official references

- [GITHUB_TOKEN security](https://docs.github.com/en/actions/concepts/security/github_token)
- [Workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Triggering workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run)
- [Dependabot pull-request grouping](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/optimizing-pr-creation-version-updates)
- [Dependabot services quickstart](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/dependabot-quickstart)
- [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates)
- [Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates)
- [Configuring Dependabot security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates)
- [Dependabot pull-request limits and errors](https://docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-errors)
- [Dependabot inactivity and automatic pause](https://docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-updates-stopped)
- [Dependabot configuration options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
- [Dependabot on GitHub Actions](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions)
- [GitHub-hosted runner images](https://github.com/actions/runner-images)
- [Ubuntu 26.04 availability announcement](https://github.com/actions/runner-images/issues/14747)
- [ubuntu-latest transition announcement](https://github.com/actions/runner-images/issues/14748)
