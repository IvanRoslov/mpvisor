---
description: Consolidate open lessons (docs/lessons/) into the fact tree and the playbooks — the episodic→semantic loop.
argument-hint: "[lesson-id | all]   (default: all open lessons)"
allowed-tools: Read, Edit, Write, Grep, Glob, Bash
---

Run the lessons consolidation loop for this docs vault. The authoritative procedure is `docs/playbooks/consolidate-lessons.md` — read it first and follow it exactly.

## Scope
- If the argument below is empty or `all`: consolidate every lesson under `docs/lessons/` whose frontmatter has `status: open`.
- Otherwise treat it as a lesson `id` (or filename) and consolidate only that one.

Argument: `$ARGUMENTS`

## Guardrails (from the playbook — do not deviate)
- A lesson updates a fact. Its product half becomes a new or corrected fact in the right node or leaf of the fact tree — never an appended paragraph. Its process half becomes a rule written once in `docs/playbooks/verify-a-change.md`, `docs/playbooks/run-parallel-workers.md`, the playbook of the operation, or `CLAUDE.md`, ending with a `Why:` line linking the lesson.
- Mark a lesson `status: consolidated` only when every half is placed, and list every doc that carries one in `consolidated-into`. Never edit a lesson's body.
- Do NOT invent facts. Verify each takeaway against the code on `main`; a part that no longer holds gets a `note:` in the lesson's frontmatter.
- Before committing, run `make lint-docs` — it MUST print `docs lint: OK`. Also run `make test-lint`. The green lint is the gate.
- Commit the result with a clear message. Everything stays in the git diff for review.

## Report when done
Which lessons were consolidated (id → which canonical docs), anything left `open` and why, and the final `make lint-docs` / `make test-lint` output.
