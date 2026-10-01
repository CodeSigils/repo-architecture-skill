# Platform Skill Support Snapshot

> Refreshed: 2026-10-01
>
> Evidence type: official documentation review retrieved 2026-10-01

## Sources and Scope

This dated snapshot separates the portable Agent Skills format from client
discovery, activation, security, and distribution behavior. Its 2026-10-01
review uses official documentation for:

- [Agent Skills specification](https://agentskills.io/specification);
- [OpenAI Codex manual](https://developers.openai.com/codex/codex-manual.md),
  especially its Build skills, plugin structure, and `AGENTS.md` sections;
- [Claude Code skills](https://code.claude.com/docs/en/skills);
- [Gemini CLI skill management](https://geminicli.com/docs/cli/using-agent-skills/);
- [Hermes skills system](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

Documentation describes intended product behavior. It does not replace a
recorded installation and workflow test against a named client version.

## Portable Format Baseline

The Agent Skills specification defines a skill as a directory containing
`SKILL.md`, with optional `scripts/`, `references/`, and `assets/` directories.
`name` and `description` are required. Optional standard fields include
`license`, `compatibility`, `metadata`, and experimental `allowed-tools`.

The standard defines the artifact format, not one universal installation path.
It recommends progressive disclosure, relative file references, shallow
reference routing, and a `SKILL.md` under 500 lines.

This repository deliberately enforces a narrower baseline of only `name` and
`description` for its own portable payload. That is repository policy, not a
claim that the standard forbids other fields.

## Client Matrix (reviewed 2026-10-01)

| Client | Native authoring/discovery paths | `.agents/skills` status | Distribution path | Notable behavior |
| --- | --- | --- | --- | --- |
| OpenAI Codex | Repository ancestors, user, admin, and system skill locations | Native for repository and user scopes | Plugins for reusable installation; skill installer for local curated skills | Explicit and implicit invocation; progressive disclosure; optional `agents/openai.yaml` |
| Claude Code | `~/.claude/skills/`, `.claude/skills/`, and plugin `skills/` | Not documented on the reviewed skills page | Claude plugins or direct skill directories | Live change detection, parent and nested discovery, Claude-specific frontmatter and dynamic context |
| Gemini CLI | `~/.gemini/skills/`, `.gemini/skills/`, built-ins, and extensions | Native alias at user and workspace scopes | `gemini skills install`, link, or extension | Install confirmation and activation consent; reload without restart |
| Hermes Agent | `~/.hermes/skills/` plus configured external directories | Supported when added to `skills.external_dirs` | Skills Hub, direct URL/GitHub install, or tap | Quarantined install scanning, provenance lock data, bundles, mutable external directories |

## OpenAI Codex

The previous draft's statement that Codex lacked a documented skills system was
incorrect. The current Codex manual documents skills in the ChatGPT desktop app,
Codex CLI, and IDE extension.

Codex scans `.agents/skills` from the current directory through repository
ancestors and also supports `$HOME/.agents/skills`. It loads skill metadata
first, then the full `SKILL.md` when explicitly mentioned or implicitly matched.
Codex supports symlinked skill directories.

For distribution, OpenAI distinguishes a direct skill directory from a plugin.
A plugin requires `.codex-plugin/plugin.json` and may bundle skills, hooks, MCP
configuration, app mappings, and presentation assets. Optional
`agents/openai.yaml` inside a skill provides UI metadata, invocation policy, and
tool dependencies.

`AGENTS.md` remains a different surface: Codex loads it as durable repository
guidance before work, with nearer files overriding broader guidance. Use it for
repository conventions and verification commands, not as a duplicate skill
payload.

## Claude Code

Claude Code documents personal, project, enterprise, and plugin skill scopes.
It follows the Agent Skills format while extending it with invocation controls,
forked subagent context, arguments, dynamic command injection, and tool approval
fields.

Project discovery walks from the starting directory to the repository root and
can discover nested `.claude/skills/` directories when work enters a
subdirectory. Existing watched directories update live; creating a new top-level
skills directory may require restart. The reviewed page does not document
`.agents/skills` as an alias.

Claude-specific extensions are not automatically portable. In particular,
dynamic command injection and permission fields require an explicit target and
security review.

## Gemini CLI

Gemini CLI documents built-in, extension, user, and workspace tiers. Both user
and workspace tiers accept `.agents/skills` as an alias for the corresponding
`.gemini/skills` path.

The CLI can install a remote Git repository, link a local skill for development,
uninstall skills, and reload discovery in-session. Its documentation states that
remote installation requires source confirmation and every activation requires
consent before the skill gains access to its resources.

## Hermes Agent

Hermes uses `~/.hermes/skills/` as its primary source of truth and can scan
additional directories configured under `skills.external_dirs`. The official
example explicitly includes `~/.agents/skills`.

External directories are integration points, not write-protection boundaries:
Hermes can update a discovered skill in place when the directory is writable.
Hub and direct installs use quarantine scanning and record source and content
provenance. Tap repositories default to a `skills/` collection layout.

This corrects the previous draft's claim that Hermes did not support an
`.agents/skills` workflow. Support is explicit but configured, rather than an
automatic alias.

## Cross-Platform Findings

1. **Format portability is not workflow certification.** Shared `SKILL.md`
   structure does not guarantee identical frontmatter, tools, permissions, or
   activation semantics.
2. **`.agents/skills` has meaningful adoption.** Codex and Gemini discover it
   natively; Hermes documents it as an external-directory example; Claude's
   reviewed documentation uses `.claude/skills` instead.
3. **Static skills need no build step.** Plugins, marketplaces, generated
   adapters, or package wrappers may still require assembly and validation.
4. **Client extensions belong behind explicit adapters.** Preserve a portable
   core and isolate dynamic commands, invocation policy, or client UI metadata.
5. **Trust controls differ.** Record install source, review executable support
   files, preserve host approvals, and do not infer safety from a common format.
6. **Distribution mechanisms differ.** Codex and Claude use plugins, Gemini can
   install or link skills, and Hermes provides Hub and tap workflows.

## Maintenance Rule

Refresh this document when a portability claim depends on client behavior. Keep
the retrieval date, distinguish absence of documentation from lack of support,
and record a client version plus installation and workflow evidence before
upgrading this repository's portability status.
