# Contributing

Add a pattern when it helps someone decide what an instruction file should
contain. Prefer a small, useful collection over a large directory.

For a new rule, include a primary source, the date checked, the agent or model
it applies to, a short before/after example, and a case where the rule should
**not** be applied. Distinguish the source's recommendation from our
interpretation. Preserve constraint text and its loading scope in examples.

For resources, explain the concrete use, prefer official documentation or
maintained projects, and disclose ownership or affiliation. No paid placement,
star requirements, referral links, or unsupported performance claims.

For code, use Python 3.10+ and the standard library. The helper measures
explicitly selected files; discovery and activation modeling belong in
[Agent Policy Map](https://github.com/incline-ltd/agent-policy-map).

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
git diff --check
```

Use synthetic fixtures. Do not attach private instructions, environment files,
credentials, personal identifiers, or screenshots of account settings.
Report a reproducible issue with redacted inputs and the exact command used.
