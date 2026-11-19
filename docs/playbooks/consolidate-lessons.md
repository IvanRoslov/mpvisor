---
last-verified: 2026-11-19
---

# Consolidate lessons

Close the episodic→semantic/procedural loop: distill open lessons from [[docs/lessons/README]] into the fact tree and the playbooks, then mark each lesson consolidated. Run it with the `/consolidate-lessons` command.

## When to use

On demand, when `docs/lessons/` has accumulated `status: open` lessons whose takeaways have not yet been placed. The trigger is manual.

## Prerequisites

- A clean working tree on a branch; `make lint-docs` green at the start.
- Familiarity with [[docs/agent-toolbox]] (running `make lint-docs`, committing) and [[docs/meta/knowledge-base]] (where each layer lives).

## Steps

1. Find open lessons: every file under `docs/lessons/` with frontmatter `status: open`.
2. Group them by topic / affected component (use the `services:` frontmatter).
3. Verify each takeaway against the code on `main`. A part that no longer holds is stale: it gets a `note:` in the lesson's frontmatter, not a rule.
4. A lesson updates a fact. Place each half once:
   - a fact about the system → a new or corrected fact in the right node or leaf of the tree. Never append a paragraph; a full leaf gets a merge or a split, not a 13th fact.
   - a process rule → [[docs/playbooks/verify-a-change]] (proving a claim or change), [[docs/playbooks/run-parallel-workers]] (orchestration), the playbook of the operation it is about, or [[CLAUDE]] (writing these docs). Write a rule once; if it is already there, add the lesson to its Why line instead of a second copy.
   Each rule ends with a `Why:` line linking the lesson.
5. Mark the lesson `status: consolidated` only when every half is placed, and list in `consolidated-into` every doc that carries one. Update its row in the [[docs/lessons/README]] Map. Do not edit the lesson's body.
6. Run `make lint-docs` — it MUST print `docs lint: OK` before you commit. Also run `make test-lint`.
7. Commit. Everything stays in the git diff for review.

## Verify

- Every targeted lesson is now `status: consolidated` with `consolidated-into` filled.
- The tree carries each fact half, and each rule carries a `Why:` link back to the lesson.
- `grep -l '^status: open' docs/lessons/*.md` lists only `_template.md` once all are placed.
- `make lint-docs` → `docs lint: OK`; `make test-lint` passes.

## Rollback / if it goes wrong

It's all in git — revert the consolidation commit. The lessons remain the record; set their `status` back to `open` if needed.
