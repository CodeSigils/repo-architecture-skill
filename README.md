# Repo Architecture Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CodeSigils/repo-architecture-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/repo-architecture-skill/actions/workflows/ci.yml)
[![Skill format](https://img.shields.io/badge/skill%20format-agentskills.io-blue)](https://agentskills.io/specification)
[![skills.sh](https://skills.sh/b/codesigils/repo-architecture-skill)](https://skills.sh/codesigils/repo-architecture-skill/repo-architecture-skill)

**Architecture follows the artifact.** This methodology helps an agent design,
review, and tighten skill repositories without forcing the same structure onto a
static Markdown skill, routed skill pack, CLI-backed skill, and published plugin.

It classifies what the repository ships, separates authoring source, runtime
payload, install artifact, and maintainer infrastructure, then recommends only
the validation and release controls justified by those boundaries.

## What it covers

- Five repository archetypes: Markdown-only, multi-skill, tool-backed,
  operational, and distribution monorepo.
- Four explicit boundaries: authoring source, runtime payload, install/publish
  artifact, and maintainer infrastructure.
- Progressive disclosure and portable runtime instructions.
- Canonical-source, generated-payload, and installed-copy drift decisions.
- Deterministic validation, behavioral fixtures, volatile monitoring, and
  release-only controls.
- File-swamp diagnosis based on ownership and consumers rather than universal
  script or reference ratios.

Use `repo-health-and-sync-skill` for general repository health and
`skill-discovery` for finding third-party skills. This skill focuses specifically
on the architecture of repositories that create or distribute skills.

## What it does in practice

Suppose you ask an agent:

> Review this repository. It contains a CLI, an npm package, and a `SKILL.md`.
> Tell me what should ship, whether it needs a payload manifest, and which checks
> belong in pull requests.

The methodology guides the agent to:

1. classify the repository as a tool-backed skill rather than a Markdown-only
   skill;
2. identify the CLI source as authoring source, the activated instructions and
   invoked code as runtime payload, the npm tarball and skill directory as
   separate install artifacts, and tests or release scripts as maintainer
   infrastructure;
3. inspect each artifact inventory independently instead of applying a raw
   script-to-skill ratio;
4. keep deterministic package, link, unit, and staged-install checks in pull
   requests while moving registry monitoring outside that lane; and
5. report the smallest changes needed, with evidence and skipped checks.

For a Markdown-only skill, the result is deliberately smaller: keep one
canonical skill directory, avoid a generated mirror, validate its structure and
references, and add behavioral fixtures only when the procedure makes meaningful
decisions.

## Scope

| Use this skill for                                             | Use another workflow for                       |
| -------------------------------------------------------------- | ---------------------------------------------- |
| Designing or auditing a skill repository                       | General repository-health audits               |
| Declaring source, runtime, artifact, and maintainer boundaries | Domain-specific skill content authoring        |
| Choosing payload, adapter, validation, and release patterns    | Finding or installing third-party skills       |
| Reducing unowned files or unnecessary generated copies         | Ordinary feature implementation or code review |

## Install

The canonical payload is
[`skills/repo-architecture-skill/`](skills/repo-architecture-skill/). There is no
build or generated mirror.

The generic installation shape is to copy that directory into a client-supported
skill location:

```bash
cp -R skills/repo-architecture-skill <your-skills-directory>/
```

For development, point clients that support external skill directories at this
repository's `skills/` directory so edits are immediately visible.

Documented candidate paths are installation hints, not support claims:

| Client | Candidate path or mechanism |
| --- | --- |
| OpenAI Codex CLI | project `.agents/skills/` |
| Gemini CLI | project `.agents/skills/` |
| Claude Code | project `.claude/skills/` |
| Hermes Agent | copy under `$HERMES_HOME/skills/` or configure `skills.external_dirs` |

An external directory or symlink is a development adapter and a trust boundary.
Check ownership, permissions, targets, and whether the client can mutate the
canonical source before enabling it.

Client discovery locations change independently of the payload format. Verify
the named client's current documentation and record its version and installation
result before claiming support.

## Support status

Deterministic checks establish that the canonical payload has valid baseline
frontmatter, resolvable references, and no known platform-only runtime markers.
Named-runtime claims are narrower:

| Runtime | Tested version | Status |
| --- | --- | --- |
| OpenAI Codex CLI | 0.133.0 | `workflow_verified` |
| Hermes Agent | 0.19.0 | `workflow_verified` with a recorded shutdown-warning limitation |
| Claude Code | 2.1.159 | `candidate`; certification was inconclusive |
| Gemini CLI | not installed | `candidate` |

See [the portability contract](docs/portability-contract.md) and
[dated compatibility report](docs/compatibility/2026-07-22.md) for evidence,
prompts, grading, and limitations. These results do not imply universal or
future-version compatibility.

## Use

1. Make `repo-architecture-skill` discoverable to the agent.
2. Ask it to design or audit a skill repository, naming any active distribution
   targets or portability requirements.
3. Expect an archetype classification, four-boundary map, artifact-specific
   controls, prioritized recommendations, and an exact record of checks run or
   skipped.

Typical requests include:

- “Design a repository for a portable Markdown-only skill.”
- “Audit this skill pack's router and standalone loading behavior.”
- “Does this CLI-backed skill need a generated payload manifest?”
- “Extract a portable core from these platform-specific instructions.”

The reviewable behavior contract lives in
[`evals/cases/architecture-audit.json`](evals/cases/architecture-audit.json).
The optional executable evaluation, retained-artifact contract, and model-free
grader tests are documented in
[`docs/behavioral-evaluation.md`](docs/behavioral-evaluation.md).

## Runtime payload

Only [`skills/repo-architecture-skill/`](skills/repo-architecture-skill/) ships.
It contains one `SKILL.md`, eight conditionally loaded references, the bundled
MIT `LICENSE.txt`, and no runtime scripts or configuration:

| Reference                            | Load when                                                   |
| ------------------------------------ | ----------------------------------------------------------- |
| `skill-repo-audit-procedure.md`      | Running a complete architecture audit                       |
| `file-swamp-patterns.md`             | File ownership, consumers, or growth is unclear             |
| `portability-patterns.md`            | Selecting portability tier or bounding compatibility claims |
| `payload-manifest-pattern.md`        | A real install or publication artifact must be assembled    |
| `dev-workflow-patterns.md`           | Choosing canonical source, adapters, or drift handling      |
| `operational-patterns.md`            | Designing CI lanes and behavioral evaluation                |
| `npm-publishing-for-agent-skills.md` | The skill wraps a publishable Node.js tool                  |
| `portability-migration.md`           | Extracting a portable core from platform coupling           |

The payload is authored in place. There is no root reference mirror, generated
payload, runtime dependency, or synchronization step.

## Security model

The installed artifact is an allowlisted payload: one `SKILL.md`, eight direct
references, and its MIT notice, with no symlinks, executables, nested directories,
scripts, configuration, or dependencies. Deterministic validation also checks
for high-confidence secret patterns and unsafe runtime instructions without
printing matched values. See [SECURITY.md](SECURITY.md) for the trust contract
and private reporting route.

## Architecture

```text
repo-architecture-skill/
├── AGENTS.md                    # maintainer routing; not shipped
├── CITATION.cff
├── LICENSE
├── README.md
├── SECURITY.md
├── pyproject.toml               # non-package maintainer environment
├── uv.lock                      # exact transitive dependency lock
├── .github/
│   ├── dependabot.yml           # uv and action update automation
│   └── workflows/ci.yml
├── docs/
│   ├── behavioral-evaluation.md    # evaluation methodology and adoption evidence
│   ├── compatibility/              # named-runtime reports; not shipped
│   ├── evaluation-adoption-ledger.yaml  # evaluation tracking
│   ├── evidence-urls.json          # external monitoring contract
│   ├── portability-contract.md     # compatibility evidence levels and status
│   └── research/                   # dated maintainer evidence; not shipped
├── evals/
│   ├── cases/                       # shared behavioral fixture contracts
│   └── codex/                       # optional model-regression prompts and schema
├── scripts/
│   ├── check-expiry.py             # Scans for expired doc and config references
│   ├── evaluation_contract.py       # Validates shared Codex evaluation contracts
│   ├── evidence_manifest.py         # Shared validated evidence-urls manifest loader
│   ├── grade-codex-regression.py   # Grades Codex regression artifacts
│   ├── run-codex-regression.py     # Runs isolated Codex skill regressions
│   ├── validate.py                 # deterministic schema/link/fixture checks
│   └── verify-urls.py             # scheduled external monitoring
└── skills/
    └── repo-architecture-skill/ # canonical runtime payload
        ├── SKILL.md
        ├── LICENSE.txt
        └── references/
```

The tracked payload is both authoring source and install artifact. CI, fixtures,
evidence contracts, and repository documentation are maintainer infrastructure.

## Design examples behind the methodology

| Repository shape               | Architectural lesson                                                            |
| ------------------------------ | ------------------------------------------------------------------------------- |
| Small discovery methodology    | Keep runtime guidance compact and monitor external contracts separately.        |
| Routed Python review pack      | Test routing and preserve standalone safety for every focused skill.            |
| Markdown formatter CLI         | Let the package manifest own executable payload and test staged installation.   |
| Operational health methodology | Pair structural validation with explicit behavioral fixtures.                   |
| Reproducible build repository  | Import provenance and release controls only when a real artifact warrants them. |

These are transfer patterns, not templates. The skill asks whether the same
artifact and failure mode exist before recommending the corresponding control.

## Research provenance

Maintainer research is preserved as dated evidence, not runtime authority:

- [repository structure snapshot](docs/research/repository-structure-snapshot.md)
  records four public repositories at pinned Git tree objects;
- [platform skill support snapshot](docs/research/platform-skill-support-snapshot.md)
  compares current official Agent Skills, Codex, Claude Code, Gemini CLI, and
  Hermes documentation.
- [automation bots and workflows](docs/research/automation-bots-and-workflows.md)
  records the repository's Dependabot, workflow-token, trigger, and manual
  maintainer boundaries.

Refresh volatile claims before using them to change compatibility status or
runtime guidance. Pinned repository snapshots remain historical provenance; a
non-blocking reminder requests review after 400 days rather than deleting them.

## Verify

Sync the isolated maintainer environment from the committed lockfile:

```bash
uv sync --locked
```

`uv` is used instead of raw `pip` because this repository has several Python
maintainer checks and benefits from a locked transitive environment plus native
Dependabot updates. It remains maintainer infrastructure; the skill itself has
no Python or uv runtime dependency.

Run the deterministic suite:

```bash
uv run --locked ruff check scripts .github/scripts
uv run --locked ruff format --check scripts .github/scripts
uv run --locked python scripts/validate.py
uvx --from git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref skills-ref validate skills/repo-architecture-skill
uv run --locked python scripts/validate.py --self-test
uv run --locked python scripts/run-codex-regression.py --self-test
uv run --locked python scripts/grade-codex-regression.py --self-test
uv run --locked python .github/scripts/check-portability.py
uv run --locked python scripts/verify-urls.py --self-test
uv run --locked python scripts/check-expiry.py --self-test
uv run --locked python scripts/check-expiry.py
```

Lint and format checks run first so a style failure surfaces in seconds
instead of after the full suite. CI repeats this suite on every Python release
that `requires-python` admits, so pass an explicit interpreter to reproduce a
specific matrix cell locally:

```bash
uv run --locked --python 3.13 ruff check scripts .github/scripts
```

External URL checks are intentionally separate because they depend on network
and provider state:

```bash
uv run --locked python scripts/verify-urls.py
```

CI runs deterministic checks on pull requests across a Python matrix that covers
every release admitted by `requires-python`, freshness checks on every lane,
and live external monitoring only on schedule or manual dispatch.
Runtime-specific behavior remains a separate, non-blocking certification
activity.

## Maintainer ownership

- `skills/repo-architecture-skill/SKILL.md` owns runtime procedure and triggers.
- Runtime references own conditional detail and examples.
- `evals/` owns intended classification and recommendation behavior.
- `README.md` owns installation, repository layout, and verification commands.
- `docs/` and any research notes are evidence, not runtime authority.
- `AGENTS.md` routes maintainers to these sources without repeating them.

## See also

- [`skill-discovery`](https://github.com/CodeSigils/skill-discovery) — find and
  assess reusable skills.
- [`repo-health-and-sync-skill`](https://github.com/CodeSigils/repo-health-and-sync-skill)
  — audit general repository health and release readiness.
- [`py-review-skill`](https://github.com/CodeSigils/py-review-skill) — review
  Python code with focused routing and rules.

## License

MIT — see [LICENSE](LICENSE).
