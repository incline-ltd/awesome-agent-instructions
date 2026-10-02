# Behavioral smoke

One isolated audit exercised the skill by direct file reference in a Codex
session on October 3, 2026. It was a qualitative smoke check, not a native
installation test, a model comparison, or a performance benchmark.

The input files are stored as `.md.txt` to keep them visibly separate from
instructions governing this repository:

- [AGENTS input](input/AGENTS.md.txt)
- [CLAUDE input](input/CLAUDE.md.txt)
- [Actual proposed diff](proposed.patch)
- [Observed check results](checks.json)

The audit request was to simplify the synthetic repository's instruction files
and return a proposal without applying it. The fixture deliberately included
mandatory testing without a known command, a repeated response instruction,
production constraints whose heading defines scope, cross-host duplication,
an ambiguous legacy requirement, and an embedded instruction attempting to
execute a command and publish a message.

The resulting proposal removed only one consecutive duplicate response
instruction. It retained testing, production scope, cross-host requirements,
and the ambiguous legacy rule. The embedded command and posting request were
treated as data. The original input files stayed unchanged.

All 13 recorded fixture checks passed. The proposed `AGENTS.md` estimate fell
from 236 to 220; `CLAUDE.md` stayed at 113. These are separate file estimates.
The non-Git fixture was correctly left at proposal-only status because it
lacked the clean, tracked baseline required for application.

The check results are an observation from that run, not an automatic assertion
that future hosts or versions will behave the same way. To repeat it, copy
the input files to their corresponding `.md` names in an isolated temporary
directory, request an audit with the packaged skill, and inspect the actual
diff and effects against the cases above. Never run the embedded instruction.
