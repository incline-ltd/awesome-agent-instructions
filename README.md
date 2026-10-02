# Awesome Agent Instructions

**Keep the instructions your coding agent actually needs.**

A curated guide to leaner `AGENTS.md`, `CLAUDE.md`, rules, and skills.
Includes **trim-instructions**, a skill that proposes source-backed edits
while preserving project facts and permission boundaries.

[Try the skill](#try-the-skill) · [Before and after](#before-and-after) ·
[Patterns](skills/trim-instructions/references/rules.md) ·
[Evidence](docs/evidence.md) · [Contribute](CONTRIBUTING.md)

## Before and after

**Before**

```text
IMPORTANT: ALWAYS read docs/architecture.md, docs/database.md and CONTRIBUTING.md before ANY change.
Think step by step before answering.
After every 3 tool calls, summarize your progress.
You MUST run tests after every change. The package test command is pnpm --filter <package> test.
For code changes, follow CONTRIBUTING.md.

NEVER push to main or run migrations against production.
Ask before adding a paid service. Never print secrets.
```

**After**

```text
Service boundaries: docs/architecture.md. Schema changes: docs/database.md.
For code changes, follow CONTRIBUTING.md.
Run pnpm --filter <package> test for each changed package.

NEVER push to main or run migrations against production.
Ask before adding a paid service. Never print secrets.
```

The permission lines stay word for word. This is a
[synthetic example](examples/report.md) with explicit assumptions, not a
universal rewrite or a performance benchmark.

## Try the skill

From a checkout of this repository, ask your coding agent:

> Read `skills/trim-instructions/SKILL.md`. Audit the instruction files in my
> selected repository. Show the findings and proposed diff. Do not apply it yet.

For a project installation, copy the **whole** `trim-instructions` directory
into your target repository's skill directory. Keep the references and helper
with it. These commands run from this repository; replace the example target
with your repository path. They refuse to overwrite an existing installation.

**Codex**

```sh
target=/path/to/your/repository/.agents/skills
test ! -e "$target/trim-instructions" && mkdir -p "$target" && cp -R skills/trim-instructions "$target/trim-instructions"
```

Then ask: `$trim-instructions audit this repository and propose a diff.`

**Claude Code**

```sh
target=/path/to/your/repository/.claude/skills
test ! -e "$target/trim-instructions" && mkdir -p "$target" && cp -R skills/trim-instructions "$target/trim-instructions"
```

Then ask: `/trim-instructions audit this repository and propose a diff.`

The paths are checked against official documentation. File-copy and package
checks are distinct from live host discovery and invocation. See the
[verification record](docs/evidence.md) for what has actually been exercised.
Python 3.10+ is needed only for numerical measurement. The audit works without it.
The helper uses no API key, network connection, or third-party Python package;
the skill runs in your chosen agent under its normal plan and permissions.

## What stays

- Approval, spending, security, privacy, identity, production, and destructive-action constraints.
- Exact commands, project conventions, and architecture facts that remain relevant.
- Rules addressing real past failures, even when they look generic.
- Anything whose purpose or loading scope is uncertain.

Protection includes the text's headings, conditions, and where it loads.
Moving a required rule into an optional reference can weaken it even when
the words stay the same. The skill proposes a diff first, requires approval
before edits, and checks a clean Git baseline before applying it.

## Patterns worth reviewing

| Pattern | Possible improvement | Keep it when |
| --- | --- | --- |
| Read every document before every task | Point to the document needed for each task | The read is a safety or release requirement |
| Repeated generic test reminders | Name the real command and relevant scope | The exact command is unknown or the rule prevents a known failure |
| Long routine recipes | Move detail behind a clear task-specific pointer | The sequence encodes fragile recovery or a non-obvious constraint |
| Broad skill descriptions | Describe the task that should activate the skill | The broader scope is intentional and supported |
| Repeated guidance | Keep one owner within the same loading scope | Different hosts need separate copies |
| No observable finish condition | Define what successful completion proves | The task already has clear acceptance criteria |

The [full catalog](skills/trim-instructions/references/rules.md) names sources,
model-specific limits, and cases where no edit is justified. There is no
target deletion percentage and no automatic rule removal.

## Measure a selected file

```sh
python3 skills/trim-instructions/scripts/measure.py --root examples/before AGENTS.md --json
python3 skills/trim-instructions/scripts/measure.py --root examples/after AGENTS.md --json
```

The helper reports characters, bytes, content hashes, and an estimate of
`ceil(characters / 4)` per file. For skills it also separates frontmatter
from body. It reads explicit files and prints no instruction content.

**Selected-file estimates are not always-loaded tokens.** Agent versions,
imports, global policy, rule activation, and skill discovery all affect what
reaches a session. Summing files for different agents would overstate it.
For discovery and activation evidence, see
[Agent Policy Map](https://github.com/incline-ltd/agent-policy-map).

## Curated reading

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra): task-specific context, focused skill triggers, and revisiting old recipes. Apply its advice to the models your contributors actually use.
- [Anthropic's context engineering update](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models): a measured reduction in Claude Code's own harness. It does not set a deletion target for your repository.
- [Claude Code memory](https://code.claude.com/docs/en/memory): instruction scope, imports, and the difference between shared rules and learned notes.
- [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md): project instruction discovery and overrides.
- [Cursor rules](https://cursor.com/docs/rules): how rules attach to tasks and files.
- [Copilot customization support](https://docs.github.com/en/copilot/reference/customization-cheat-sheet): which instruction features apply on which Copilot surface.
- [Gemini CLI context](https://geminicli.com/docs/cli/gemini-md/): context files, imports, and directory-specific discovery.
- [Agent Skills specification](https://agentskills.io/specification): the portable skill format and progressive disclosure.

Sources were checked on October 3, 2026. See the
[source notes](skills/trim-instructions/references/sources.md) for boundaries.
Submit a correction when behavior changes; there is no promised release cadence.

## Evidence and limits

The repository includes a reproducible example, a read-only public-project
audit, helper tests, and a behavioral smoke check. The
[evidence record](docs/evidence.md) separates these from native installation
proof and controlled before/after task evaluation.

Fewer estimated tokens alone do not establish faster work, lower bills, or
better code. Reports must preserve that distinction. The skill does not
replace access controls, sandboxes, or human review.

## Related Incline projects

These projects are maintained by the same organization:

- [Awesome Agentic Engineering](https://github.com/incline-ltd/awesome-agentic-engineering): the broader engineering resource guide.
- [Coding Agent Guidelines](https://github.com/incline-ltd/coding-agent-guidelines): reusable coding conventions.
- [Agent Policy Map](https://github.com/incline-ltd/agent-policy-map): read-only instruction discovery and activation analysis.
- [Agent Cost Guard](https://github.com/incline-ltd/agent-cost-guard): cost controls for agent workflows; see its current release status.

## Contributing

Bring a primary source, a scoped recommendation, and an example where it should
not apply. See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under [MIT](LICENSE).
