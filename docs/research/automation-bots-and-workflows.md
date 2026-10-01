# Automation Bots and Workflow Boundaries

> Reviewed: 2026-09-08
>
> Evidence type: repository configuration plus official GitHub documentation

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

## Version updates and security updates

Ordinary Dependabot version updates follow this repository's weekly schedule,
ecosystem-specific grouping, labels, and two-PR cap. They keep the pinned
maintainer toolchain current but do not by themselves indicate a vulnerability.

Dependabot security updates are advisory-driven responses to known vulnerable
dependencies. Do not assume they arrive on the weekly schedule or are governed
by the same grouping behavior as ordinary version updates. Treat the advisory,
affected dependency, lockfile change, and test result as separate review
evidence. This repository does not auto-merge either type: a maintainer still
reviews the diff and green checks before merging.

## Current configuration

Dependabot checks both ecosystems weekly:

- GitHub Actions updates are grouped under `actions-maintenance`, which accepts
  minor and patch updates;
- UV patch updates are grouped under `uv-maintenance`;
- UV minor updates for Ruff and ty are isolated under `ruff-minor-review` and
  `ty-minor-review`, because their zero-major minor releases are the ones that
  break the locked toolchain contract;
- major updates remain separate for manual review;
- each ecosystem is capped at two open pull requests;
- labels identify dependency, Python/UV, and GitHub Actions changes.

The UV groups partition the update types rather than relying on group
resolution order: every group accepts a disjoint set of `update-types`, so a
given update matches at most one group no matter which group Dependabot
considers first. That matters because the official documentation states that a
dependency joins the first group it matches, while the updater implements
most-specific-match. Disjoint update types make the documented and the
implemented behavior indistinguishable for this configuration.

`exclude-patterns` is deliberately unused. Excluding a dependency from a group
does not skip it: the dependency becomes ungrouped and still receives its own
pull request, including for major updates, which bypass the group's
`update-types` filter entirely. Exclusion would therefore have doubled the
review load instead of reducing it.

The two-pull-request cap bounds concurrent open pull requests, not the rate at
which they arrive. Each ecosystem entry carries its own cap, shared across its
grouped and ungrouped pull requests; a group consumes one slot. When the cap is
reached Dependabot opens nothing further and re-evaluates on the next
scheduled run, so there is no backlog. A newer release arriving while a pull
request is open supersedes it, closing the old pull request and opening a new
one at the same count, which is why a tool that releases weekly can still leave
a pull request waiting indefinitely.

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

Merged source branches are deleted by the repository setting. No repository
workflow creates, approves, merges, rebases, closes, or deletes pull requests.
Native Dependabot auto-merge is disabled.

## Important GitHub behavior

- A workflow's `GITHUB_TOKEN` is short-lived and scoped to the job. Unspecified
  permissions are not granted when the workflow sets a restrictive permission
  block.
- Events caused by `GITHUB_TOKEN` generally do not recursively trigger new
  workflow runs. `workflow_dispatch` and `repository_dispatch` are explicit
  exceptions.
- Dependabot pull-request workflows should be treated as untrusted dependency
  changes. They must not receive ordinary repository secrets by default.
- Grouping reduces review and CI volume; it does not establish that an update
  is safe. Review the diff and green checks before merging.
- A successful workflow proves only the checks it actually ran. A skipped
  external-monitor job on a pull request is expected because that lane is
  schedule/manual-only.

## Maintainer routine

1. Review Dependabot pull requests weekly.
2. Merge narrow, green dependency-only updates after inspecting the diff.
3. Close superseded or stale proposals when a newer grouped update replaces
   them.
4. Confirm merged branches are removed automatically.
5. Investigate failed or ambiguous checks; do not bypass protection merely to
   clear a queue.
6. Re-check this note when adding a workflow that writes issues, releases,
   attestations, pull requests, branches, or repository settings.

## Official references

- [GITHUB_TOKEN security](https://docs.github.com/en/actions/concepts/security/github_token)
- [Workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Triggering workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run)
- [Dependabot pull-request grouping](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/optimizing-pr-creation-version-updates)
- [Dependabot configuration options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
- [Dependabot on GitHub Actions](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions)
