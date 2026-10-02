# Read-only public Guidelines audit

Source: https://github.com/incline-ltd/coding-agent-guidelines
Checked: 2026-10-03. Local public-source revision: 115970688831472c8dbef9a9d6275a7e2c572b1b; working tree clean on main. This is an audit of public product source, not personal runtime guidance.
No source file was edited and no replacement policy is proposed without owner review.

## Selected-file measurement

The packaged measure.py helper was run on AGENTS.md, CLAUDE.md, root SKILL.md and the two packaged SKILL.md copies. Method: ceil(characters / 4), separately per file.

| File | Characters | Estimated tokens |
| --- | ---: | ---: |
| AGENTS.md | 14,194 | 3,549 |
| CLAUDE.md | 13,883 | 3,471 |
| Each of three SKILL.md copies | 3,975 | 994 |

Do not present the sum as an always-loaded or live session total. Different users install different formats. Skill body and metadata are not loaded identically, and host behavior was not exercised here.

## Findings

| Source | Disposition | Evidence and recommended next step |
| --- | --- | --- |
| docs/ARCHITECTURE.md:43-57; three SKILL.md copies | KEEP intentional distribution copies | Architecture explicitly documents separate installation formats and validates byte equality. Equal text across install paths is not evidence that one live session loads all copies. All three measured hashes match. Do not delete copies merely to reduce a repository total. |
| AGENTS.md:141-143; SKILL.md:50-53 | HOLD inconsistent retry policy | Full instructions say to stop after three repeated failures, while skill form says after two. Ask the owner for the intended threshold or a single observable failure rule before synchronizing. This is a concrete local inconsistency, not evidence either threshold is wrong. |
| SKILL.md:3-10 | HOLD broad activation; U07 review candidate | Metadata covers essentially every coding or review task. That may be intentional for a behavioral package, so narrowing it is a product decision. Consider whether the intended installation is persistent baseline guidance or an opt-in review skill before changing activation. |
| AGENTS.md:33-35 and 111-113 | HOLD overlapping reading guidance | One says relevant files in full before edits; another says targeted ranges once the relevant code is known. These can be reconciled by phase, but wording does not make the boundary crisp. Clarify the intended ownership/call-site evidence requirement rather than automatically deleting either instruction. |
| AGENTS.md:146-172; SKILL.md:56-62 | HOLD host-specific subagent assertions | Portable product text contains specific Task behavior and final-message-only claims. Exact present host/version applicability is not established in this audit. Move or rewrite only after checking current host documentation and retaining useful delegation constraints. |
| AGENTS.md:300-328; SKILL.md:82-92 | HOLD model-specific defaults | Portable guidance embeds provider/model routing defaults and cost claims. No evaluation or present host capability was checked here. A later scoped review can separate durable selection principles from version-specific operational instructions. |
| CONTRIBUTING.md:22-39; .github/workflows/validate.yml | KEEP verified repository commands | node scripts/validate.mjs is an actual local/CI check; Ruby is required for YAML checks, and Claude plugin validation is conditional on tool availability. Preserve these commands in repository-specific guidance. They should not replace generic requirements shipped for arbitrary consumer repositories. |

## Outcome

No deletion percentage or speed/quality claim is justified. This first pass found one concrete synchronization discrepancy and several review candidates that require product intent or host evidence. It deliberately retained distribution copies and generic consumer testing requirements.
