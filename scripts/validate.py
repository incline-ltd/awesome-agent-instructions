#!/usr/bin/env python3
"""Check this package's metadata, local links, and reproducible example."""

import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/trim-instructions"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    # This package deliberately uses only three plain, single-line YAML scalars.
    # Reject richer syntax instead of pretending to implement a general YAML parser.
    require(text.startswith("---\n"), "Missing skill frontmatter")
    header, body = text[4:].split("\n---\n", 1)
    fields = {}
    for line in header.splitlines():
        key, value = line.split(": ", 1)
        require(key not in fields and value and ": " not in value,
                "Use unique plain scalar fields in skill frontmatter")
        require(not value.startswith(tuple("{[&*!|>'\"%@`")), "Unsupported YAML scalar syntax")
        fields[key] = value
    require(set(fields) == {"name", "description", "license"}, "Unexpected metadata fields")
    require(fields["name"] == SKILL.name, "Skill name must match directory")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"]) is not None,
            "Invalid skill name")
    require(len(fields["name"]) <= 64 and 0 < len(fields["description"]) <= 1024,
            "Invalid metadata length")
    require(fields["license"] == "MIT" and body.strip(), "License or skill body missing")
    require((SKILL / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes(),
            "Installed skill must carry the same license")

    count = 0
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        content = path.read_text(encoding="utf-8")
        require(not any(line.rstrip() != line for line in content.splitlines()),
                f"Trailing whitespace: {path.relative_to(ROOT)}")
        require(not re.search(r"/Users/|/home/|[A-Z]:\\\\Users\\\\", content),
                f"Personal path in public documentation: {path.relative_to(ROOT)}")
        require(not re.search(r"co-authored-by:|(?:generated|designed|assisted) by (?:an? )?(?:agent|codex|claude|chatgpt)",
                              content, re.I), "Unexpected authorship credit")
        prose = re.sub(r"```.*?```", "", content, flags=re.S)
        for link in re.findall(r"\]\(([^\s)]+)\)", prose):
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            require(target.is_relative_to(ROOT) and target.is_file(),
                    f"Missing local link in {path.relative_to(ROOT)}: {link}")
        count += 1

    spec = importlib.util.spec_from_file_location("measure", SKILL / "scripts/measure.py")
    measure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(measure)
    expected = json.loads((ROOT / "examples/measurements.json").read_text(encoding="utf-8"))
    for side in ("before", "after"):
        actual = measure.measure_files(ROOT / "examples" / side, ["AGENTS.md"])
        require(expected[side] == actual, f"Stale {side} example measurements")
    before = (ROOT / "examples/before/AGENTS.md").read_bytes()
    after = (ROOT / "examples/after/AGENTS.md").read_bytes()
    protected = (b"NEVER push to main or run migrations against production.\n"
                 b"Ask before adding a paid service. Never print secrets.\n")
    require(before.endswith(protected) and after.endswith(protected), "Protected example spans changed")
    require(before.startswith(b"# Project instructions\n") and after.startswith(b"# Project instructions\n"),
            "Example scope heading changed")
    print(f"Package metadata, license, {count} Markdown files, local links, measurements, and protected example spans passed.")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, OSError, KeyError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
