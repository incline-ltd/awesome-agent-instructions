# Verification record

Checked October 3, 2026. This record separates what was exercised from what
remains unverified. No separately billed provider API, paid evaluation service, or public
instruction corpus was used.

| Layer | Evidence | Limit |
| --- | --- | --- |
| Skill format | Skill Creator validator passed; YAML parsed | Format checks do not establish behavior |
| Measurement helper | 24 unit tests passed on Python 3.10.21 and 3.12.11; CLI smoke checks passed | Estimates use characters / 4, not a tokenizer |
| Example | [Stored counts and hashes](../examples/measurements.json), checked by the package validator | Synthetic owner-approved choices; no task comparison |
| Behavioral smoke | [One isolated audit](behavior/README.md), 13 fixture checks passed | Direct skill reading in a Codex session; no native discovery test |
| Public project audit | [Coding Agent Guidelines](audits/coding-agent-guidelines.md) at a pinned public revision | Read-only findings; no instructions changed |
| Installation package | Full-directory copies and helper invocation in temporary Codex/Claude project paths | Claude Code file placement only; native Codex verification is separate |
| Native Codex invocation | [Project discovery and an explicit CLI audit](behavior/native-codex.md) completed with exit code 0; targets unchanged | One host version, read-only sandbox, proposal-only; no implicit-trigger or apply-phase proof |
| Native Claude Code invocation | Not verified | No Claude Code invocation receipt |
| Comparative task evaluation | Not run | No pass-rate, latency, cost, or quality improvement claim |
| Broad corpus study | Not run | No prevalence, median savings, or ecosystem-wide claim |

## Reproduce the local checks

From the repository root with Python 3.10+:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
python3 skills/trim-instructions/scripts/measure.py --root examples/before AGENTS.md --json
python3 skills/trim-instructions/scripts/measure.py --root examples/after AGENTS.md --json
git diff --check
```

The CI workflow is configured for Python 3.10 and 3.13 on Linux. A configured
workflow is not a successful hosted run; remote CI will have its own result
after publication. The local test environment is macOS.

The file reader rejects selected symlinks, path traversal, known secret-like
names, invalid UTF-8, and oversized input. It accepts at most 64 selected paths,
1 MiB per file, and 8 MiB total. Content and absolute root paths are omitted
from reports. Filename checks are not a secret scanner: sensitive content
can still be inside a valid instruction file. Select only authorized files.
Root-relative names remain visible, so choose a scope without private identifiers
before sharing a report. No report is published automatically.

Unix platforms with directory-relative, no-follow opens receive additional
protection against path replacement during reads. Windows runtime behavior
has not been verified. Do not use the helper as a security boundary for
concurrently attacker-controlled filesystems.

## Before claiming a performance result

Use the same pinned source, task, model, effort, tools, permissions, and clean
starting state for original and trimmed instructions. Randomize trial order,
record failures as well as successes, and keep expected answers outside the
agent's context. Record at least five trials per condition as an initial
check, then justify a larger sample before drawing strong conclusions.

Record correctness, elapsed time, context/token measurement method, and any
protected-constraint violation separately. Include trial artifacts and
uncertainty. Fewer characters are not a substitute for this evaluation.
Use existing authorized resources; an API-based run needs its own cost approval.

## Before claiming native installation support

On each named host and version, install the complete directory in a temporary
project, confirm discovery, explicitly invoke the skill on synthetic targets,
and check that it returns a proposal before any edit. Record the host's
visible result and preserve all protected spans. File-copy checks alone do
not satisfy this test.
