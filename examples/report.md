# A small, reproducible example

This synthetic example demonstrates the proposal format. It is not a run
against a real product and does not establish better model performance.

| Selected file | Characters | Estimated tokens |
| --- | ---: | ---: |
| [Before](before/AGENTS.md) | 465 | 117 |
| [After](after/AGENTS.md) | 314 | 79 |

**117 to 79 estimated tokens: 32.5% smaller by this estimate.**
Both protected lines are unchanged, in the same file and under the same heading.
The percentage uses the rounded file estimates, not a model tokenizer.

## Assumptions

The example owner has confirmed that the unconditional reading list and
fixed-count progress updates do not encode release gates or prior failures.
The three document paths exist in the fictional project, the test command
comes from the original file, and the intended scope is changed code packages.
The owner also confirms that the generic thinking prompt has no project-specific
purpose. Without those facts, the corresponding findings would remain HOLD.

The proposed text is an illustration of that owner's choices. No model trial
was performed to establish whether removing the thinking or progress prompts
helps. Model-specific recommendations require their own applicability check.

## Findings

| Original lines | Action | Reason | Catalog |
| --- | --- | --- | --- |
| 3 and 7 | REWRITE | Route architecture and schema reading by task; retain the contribution pointer | [U05](../skills/trim-instructions/references/rules.md) |
| 4 | DELETE, conditional | Owner-confirmed lack of project-specific purpose; no performance claim | [U02](../skills/trim-instructions/references/rules.md), advisory only |
| 5 | DELETE, conditional | Owner-confirmed fixed-count scaffolding; normal status communication remains outside this file | [U01](../skills/trim-instructions/references/rules.md), advisory only |
| 6 | REWRITE | Retain the provided command and state the package scope | [U08](../skills/trim-instructions/references/rules.md) |
| 9-10 | KEEP (constraint) | Preserve main-branch, production, spending, and secret boundaries verbatim | [U10](../skills/trim-instructions/references/rules.md) |

Sources checked October 3, 2026. The model-specific catalog entries support
reviewing a pattern; the fictional owner's stated requirements justify this
example's chosen edits.

## Reproduce

Run from the repository root:

```sh
python3 skills/trim-instructions/scripts/measure.py --root examples/before AGENTS.md --json
python3 skills/trim-instructions/scripts/measure.py --root examples/after AGENTS.md --json
git diff --no-index examples/before/AGENTS.md examples/after/AGENTS.md
```

`git diff --no-index` returns 1 when it finds this expected difference.
[measurements.json](measurements.json) stores the counts and exact-byte hashes;
`python3 scripts/validate.py` checks them against the current example files.

The validator also compares the two explicitly reviewed protected lines.
That comparison validates this fixture, not arbitrary safety-rule detection.
