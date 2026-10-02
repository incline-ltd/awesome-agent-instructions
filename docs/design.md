# Design

The public name is **Awesome Agent Instructions**. The installable skill is
**trim-instructions**. The repository combines a curated reference with a
practical audit workflow, so someone can use it without installing anything.

The first version has three parts:

1. A source-backed pattern catalog with explicit exceptions and checked dates.
2. One portable skill that prepares a report and diff for review.
3. An offline helper that measures selected files reproducibly.

Instruction discovery and activation belong to the separate Agent Policy Map
project. This helper does not reproduce that engine. It does not load user
configuration, follow instruction imports, or claim to know a running
session's context.

The skill contains all its runtime references and code. The surrounding
repository contains examples, verification, and contribution guidance.
Installing it does not require npm, a plugin marketplace, a background
process, or a paid service.

Changes are judgment-based. No regex decides that a sentence is safe to delete.
The constraints that authorize an action are outside the cleanup scope.
Protected text, headings, and activation scope remain intact even when that
means retaining duplication or capitalized wording.

Validation has distinct layers: syntax and package checks, deterministic
measurement tests, behavioral smoke checks, live host invocation, and
controlled task evaluation. Passing one does not imply the others passed.
