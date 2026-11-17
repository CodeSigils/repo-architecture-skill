# Development Workflow and Canonical-Source Patterns

Use this reference when a repository has copied payloads, several install paths,
or unclear maintainer ownership.

## Prefer direct-source development

When a client can discover a repository's canonical `skills/` directory, use
that directory during development. Direct discovery eliminates installed-copy
staleness, but exposes uncommitted changes; use a dedicated clone or stable
branch for production sessions.

Treat every discovered directory as a trust boundary. Before pointing a client
at canonical source, inspect its owner, group, permissions, and the client's
ability to write, update, or uninstall content there. A writable external skill
directory can let a client or its maintenance commands mutate the authoring
source. Use direct discovery only for development unless the source is protected
against unintended writes; otherwise install a reviewed copy and record who
owns updates.

Manual installation creates a separate drift class from generated-payload drift:

| Drift                    | Cause                                               | Remedy                             |
| ------------------------ | --------------------------------------------------- | ---------------------------------- |
| Generated-payload drift  | Canonical source changed without regeneration       | Regenerate and verify the artifact |
| Installed-copy staleness | A previously installed copy predates source changes | Reinstall or use direct discovery  |

Do not add repository sync tooling to solve installed-copy staleness.

## Choose one canonical source

For each concept, declare the single file maintainers edit. Common valid models:

- The tracked runtime payload is canonical and copied directly during install.
- Root source is canonical and a required package artifact is generated.
- A package source tree is canonical and the skill wrapper references the
  installed tool rather than duplicating its implementation.

Tracked source and tracked payload copies are justified only when a real
distribution consumer requires both. The copy must have a generator, drift
check, and installed-artifact smoke test.

## Keep ownership instructions layered

Use a short repository instruction file only when multiple sources could compete
for authority. It should route maintainers to owning documents, not duplicate
their contents. A typical ownership map is:

- `SKILL.md`: runtime trigger and procedure;
- runtime references: conditional execution detail;
- maintainer guide or README: contribution and verification commands;
- fixtures: intended behavior;
- research: evidence, not runtime authority.

If one `SKILL.md` is the repository's only meaningful source, an instruction
file usually adds no value.

## Keep installation documentation separate from portability

README sections may describe client-specific installation paths. Runtime
instructions should depend only on the declared portability tier. An install
example does not make a portable skill platform-specific; a runtime command or
required client API does.

Test commands against the actual tracked layout and name the produced artifact.
For several distribution paths, maintain one inventory per artifact rather than
one ambiguous global file list. Keep runtime payload distinct from maintainer
control-plane/evidence artifacts (research, evidence manifests, compatibility
reports) and do not treat install docs or maintainer records as runtime/support
proof.

Client-specific metadata, hooks, or dynamic commands belong in a thin adapter,
not the portable core. Review such adapters as executable or privileged input:
identify commands, network access, writable paths, credentials, and approval
behavior before enabling them. For volatile install/discovery guidance, record
the checked source/date and recheck trigger rather than assuming stability.

## Change-admission questions

Before adding a script, manifest, adapter, schema, or shared abstraction, ask:

1. Which observed failure or repeated cost motivates it?
2. Which boundary owns it and which consumer uses it?
3. Can an existing mechanism solve the problem?
4. Is this the smallest sufficient change?
5. What evidence will show success or justify later removal?
