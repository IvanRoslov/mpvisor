---
last-verified: 2026-11-19
---

# Test the fact tree

## When to use

You rewrote an area of the tree, or you changed the root. Before the PR merges, prove that an agent with no context finds the answer by walking the tree from `INDEX.md` — fast, and without being misled by an old doc or a stale lesson.

The format is in `CLAUDE.md` ("Writing the tree") and is enforced by `make lint-docs`. The linter checks shape. This playbook checks that the tree answers questions. The tools a subagent may call are in [[docs/agent-toolbox]].

## Steps

1. Pick the questions: the golden set below, plus 2–3 questions derived from the lessons of the area you changed (see "Deriving questions from lessons").
2. For each question, start a **fresh** general-purpose subagent with no skills, in a clean checkout of the branch. It gets only this prompt, with nothing about the task, the area or the expected answer:

   ```text
   You are in the marketplace-analytics repo. Start at INDEX.md, follow wikilinks, list
   every file you open in order, answer, and name where the code lives. Do not
   open docs/playbooks/test-the-fact-tree.md or anything under docs/lessons/ or
   superpowers/.

   Question: <the question>
   ```

3. Record for each run: the files opened in order, the answer, where it said the code lives.
4. Score each run against the pass rule in "Verify".
5. A failed run points at a gap in the tree. Read the path it took:
   - It never found the branch: the fact one level up does not say what lies below. Reword that fact.
   - It found the leaf but answered wrong: a fact is missing or wrong. Fix it against the code.
   - It opened more than 4 tree files: the branch is too deep or a node fact is too vague. Merge or reword.
   - It answered from an old doc or a lesson: the tree fact is missing, so the old text won. Add the fact.
6. Fix the tree and rerun the failed question with a new fresh subagent. Do not reuse a subagent: it already knows the answer.
7. Put the table of runs (question, files opened, pass/fail) in the PR body, with the baseline (the same questions on `main` before your change) next to it.

## Deriving questions from lessons

Lessons in [[docs/lessons/README]] record what agents got wrong in practice. Each one is a question the tree must now answer.

1. List the open lessons whose topic falls in the area you changed.
2. Turn each lesson's situation into the question an agent would have asked at the time: a fix or a gotcha → "How do I X?"; a symptom → "Why does Y not work?"
3. The expected answer is the lesson's takeaway, checked against the code. A lesson can be stale.
4. Keep 2–3 questions per area that touch different leaves.

## Golden set

<TODO: 3–5 questions whose answers matter most, each with the expected answer checked against the code and the commit it was checked at. Run all of them after any change to the root, and each one after a change to an area it touches. Add them as the tree grows; an empty golden set means only lesson-derived questions run.>

## Verify

A run passes only if all three hold:

- the answer is correct (matches the expected answer in substance, and does not repeat a stale claim);
- the subagent opened **at most 4 tree files** (`INDEX.md` counts; files without `kind` and code do not count, but list them);
- it named where the code lives.

A run is **invalid** if the subagent opened or grepped this playbook (it holds the expected answers), anything under `docs/lessons/`, or `superpowers/`. Discard it and rerun with a new fresh subagent. A run that answers from a lesson or an old doc instead of a tree fact **fails**, even if the answer is right.

## Related

- [[docs/playbooks/consolidate-lessons]] — how lessons become facts
- [[docs/invariants]] — the hard rules, a reference doc outside the tree
