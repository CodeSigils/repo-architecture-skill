# Skill Repository Structure Snapshot

> Observed at pinned commits: 2026-07-22
>
> Integrity re-verified: 2026-10-30
>
> Evidence type: dated repository-tree observation, not a compatibility claim

## Method

This snapshot resolved each pinned commit through the GitHub REST commit API,
then queried that commit's tree through the REST tree API with recursive
traversal. Every returned tree reported `truncated: false`. A skill count
includes blobs named `SKILL.md` at any depth.

Repository layouts and counts are volatile. The pinned commits below and their
resolved trees are the authority for this snapshot; current default branches
may differ.

## Snapshot

| Repository | Commit SHA | Skills | Observed skill layout | Root shared support | Explicit sync paths |
| --- | --- | ---: | --- | --- | --- |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills/tree/2fbfa004a0192529bc997d103fc12f19a3804aab) | `2fbfa00` | 24 | `skills/<name>/SKILL.md` | `references/`, `scripts/` | None found by name |
| [`openai/skills`](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431) | `49f948f` | 44 | `skills/.curated/<name>/SKILL.md` and `skills/.system/<name>/SKILL.md` | None | One reference filename containing `sync`; no payload-sync script |
| [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/5770185ea302bab23fbcf58ff818fd73e626c708) | `5770185` | 30 | `plugins/<plugin>/skills/<name>/SKILL.md` and `external_plugins/...` | None | None found by name |
| [`wondelai/skills`](https://github.com/wondelai/skills/tree/ed2930cf8496336641441eef513ad2ad857b65a1) | `ed2930c` | 62 | `<name>/SKILL.md` at repository root | `scripts/` | Two sync scripts and one sync workflow |

The OpenAI total is 39 curated plus 5 system skills. The Anthropic total is 24
under `plugins/` plus 6 under `external_plugins/`.

## Observed Patterns

### Entrypoints follow the distribution unit

None of these four multi-skill collections has a root `SKILL.md`. That is useful
evidence for collection repositories, not a universal prohibition: a standalone
skill can still be repository-rooted when the repository itself is the install
artifact.

Three collection layouts appear:

1. a `skills/<name>/` collection;
2. skills nested inside a plugin boundary;
3. flat skill directories at repository root.

The correct choice depends on the consumer. A generic count or popularity
ranking does not establish a canonical layout.

### Shared directories need shared consumers

Addy Osmani's repository has root `references/` and `scripts/` alongside a
`plugin.json` and several platform-facing directories. OpenAI keeps support
files inside individual skills. Wondelai has root scripts because repository
automation operates across many flat skills. These are ownership decisions,
not evidence for a preferred script-to-skill or reference-to-skill ratio.

### Sync infrastructure is distribution-specific

Only Wondelai exposes clearly named synchronization infrastructure in this
sample:

- `.github/workflows/sync-marketplace-version.yml`;
- `scripts/sync-ide-skills.sh`;
- `scripts/sync-marketplace-versions.sh`.

That repository also carries multiple platform adapter directories. The other
three trees do not show a comparable payload-sync script. This supports adding
sync only when a distinct generated or published consumer exists.

### Manifests are platform contracts, not universal skill files

No repository in the sample uses a generic root payload manifest for all skill
content. Plugin-oriented repositories do contain platform-specific manifests or
marketplace metadata. A manifest is justified when a plugin, package, registry,
or generated artifact consumes it; it is not implied merely by the presence of
`SKILL.md`.

### Adapter density does not prove portability

Observed top-level platform markers include:

- Addy Osmani: `.agents/`, `.claude/`, `.claude-plugin/`, `.codex-plugin/`,
  `.gemini/`, and `.opencode/`;
- Anthropic: `.claude-plugin/` and plugin trees;
- Wondelai: `.agents/`, `.claude/`, `.claude-plugin/`, `.cursor/`, `.pi/`,
  `.windsurf/`, and `.cursorrules`;
- OpenAI: no top-level client-adapter directory in the observed tree.

These markers show intended integrations. They do not establish successful
installation or behavior on a named runtime version.

## Architectural Implications

1. Classify the repository before recommending a layout.
2. Declare authoring source, runtime payload, install artifact, and maintainer
   infrastructure independently.
3. Keep support files with their narrowest real consumer.
4. Add synchronization only for a separate consumer that cannot read the
   canonical source directly.
5. Treat plugin manifests and marketplace metadata as adapter contracts.
6. Record a repository tree or commit SHA and runtime evidence before making compatibility
   claims.

## Limitations

- The sample is small and intentionally includes large, visible collections.
- File names reveal structure, not whether every path is actively consumed.
- GitHub stars and current head counts were excluded because they add volatility
  without improving the architectural conclusion.
- No runtime installation or workflow test was performed for this snapshot.

## Retention and review

This is immutable historical evidence, not a generated cache. Retain it while
active documentation or runtime guidance relies on its conclusions. The
freshness checker emits a non-blocking review reminder after 400 days for active
unmonitored pinned snapshots. At review, retain the snapshot, record a newer
dated observation, or mark its evidence-manifest entry `retired` with
`monitor: false` once no active guidance depends on it. Do not delete a pinned
snapshot automatically.
