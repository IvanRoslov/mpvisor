# CLAUDE.md — marketplace-analytics

You are working in **marketplace-analytics**. Its docs are the source of truth for how the system is built, how parts connect, and what rules govern it. They are the **memory of the orchestrator agent**, not just human documentation.

<TODO: one sentence about what marketplace-analytics is.>

> **PRIME FRAME — <TODO: the one thing that governs every decision here>.**
> <TODO: state the project's governing frame in 3-6 lines: what this system is for, what
> it must never become, and the practical test to apply to any change. If there is no
> such frame yet, delete this block rather than leaving it vague.>

## Start here — read the fact tree

The docs are a tree of short facts. `INDEX.md` is the root.

1. Read the top of `INDEX.md` whole — always, before anything else. The root facts sit above its first `---` line.
2. Go down only the facts that touch your task. Each fact links one level down: a node (more facts, each linking down) or a leaf (facts ending in a `Code:` line).
3. Stop when you have your answer. Do not read a whole folder.
4. Need to know HOW something works? The leaf's `Code:` line says where the code is — read it there. The docs say what is true, not how it is implemented.
5. A few reference docs sit outside the tree: the hard-rule list (`docs/invariants.md`) and the agent toolbox (`docs/agent-toolbox.md`). A fact sends you there; read only what you need.
6. Before proposing to build something, check the tree for what already exists.

For how this base is organized, see `docs/meta/knowledge-base.md`.

## Repository structure

- `INDEX.md` — root of the fact tree, the entry point for agents and humans
- `AGENTS.md` — entry point for non-Claude agents; it points back here
- `docs/` — the knowledge vault (Obsidian-style; `[[wikilinks]]`)
- `docs/overview.md` and `docs/<component>/` — the tree: what the system is, then one dir per component
- `docs/invariants.md` and `docs/agent-toolbox.md` — reference docs outside the tree: the hard rules, and which tool to use
- `docs/playbooks/` — step-by-step runbooks (procedural memory), including the standing process rules in `verify-a-change.md` and `run-parallel-workers.md`
- `docs/lessons/` — episodic memory (what past runs taught us)
- `docs/meta/` — how this base is organized and why
- `docs/inbox/` — unprocessed notes; triage into the tree
- `scripts/lint_docs.py` — the structural linter (run `make lint-docs`)

## Working on the code

Docs and code live in this one repo, so one PR carries both.

- You changed behaviour? Fix the fact in the same PR. A PR that changes what the tree says and leaves the fact stale is not done.
- A leaf's `Code:` line links a directory of this repo. Moving or renaming that directory breaks the leaf; `make lint-docs` catches it, and CI runs the docs lint on every PR, code-only ones included.
- Read the tree for what is true, the code for how. Do not copy code mechanics into facts.
- Code layout: <TODO: where the code lives (for example `apps/api`, `apps/web`, `packages/*`) once it exists. Until then the tree links the repo root.>
- Code conventions: <TODO: language, formatter, linter, test runner, and the commands for each — or a link to where they live.> Build, run and test commands are in `docs/agent-toolbox.md`.
- Keep the `lint-docs` and `test-lint` targets when you add code targets to the `Makefile`.

## Authoring rules (enforced by `make lint-docs`)

- Internal links are `[[wikilinks]]`, never markdown relative links between docs.
- Every component dir with ≥3 docs has a `README.md` hub that lists all its docs.
- Agent-generated plans/specs go ONLY to the gitignored `superpowers/` working area. Never into the docs tree. Promote durable knowledge into the tree instead.
- Tree files (`kind: node|leaf`) follow the format in "Writing the tree" below, and every tree file is reachable from the root through tree files.
- Run `make lint-docs` before committing docs changes.

## Writing the tree

Format (enforced by `make lint-docs`):

- The root (`INDEX.md`) holds 8–12 numbered facts above its first `---` line; each fact links one file down.
- A node (`kind: node`) holds 3–7 numbered facts; each fact contains a `[[wikilink]]` one level down.
- A leaf (`kind: leaf`) holds up to 12 numbered facts (subheading groups are fine). It ends with a line starting `Code:` that says where the code lives. Its links are directories of this repo (`[api](apps/api)`, or `[repo root](.)`), never files or URLs; the linter checks that each directory exists.
- Every tree file has `kind`, `up` (a wikilink to the parent, which links back) and `verified` (a date) frontmatter. A component hub README keeps `component`, `repo` and `last-verified` too.
- A fact is a numbered line at column 0. Numbered lines inside code fences and indented sub-items are not facts.

Content:

- A fact is one or two sentences: what is true and why it matters. No mechanics, no ports, no env listings.
- Open a new file only when its expansion answers a separate question and has ≥3 facts. Merge a file with 1–2 facts into its parent. Split a leaf over 12 facts by question, not by layer. Usual depth: root → area → leaf.
- Every doc under `docs/` is a tree file, except the two reference docs (`docs/invariants.md`, `docs/agent-toolbox.md`) and the folders with their own shape: `docs/lessons/`, `docs/playbooks/`, `docs/inbox/`, `docs/meta/`. The linter rejects any other doc without `kind`.
- A fact that is not true yet is not a fact. Plans live in `superpowers/` or in the task tracker; the tree describes what `main` does, and says so when production differs.

Verification:

- Verify every fact against the code on `main` of this repo (`git fetch && git show origin/main:<path>`), never against an old doc or an unpushed branch.
- The tree describes the behaviour of `main`, without judgements like "this is a bug". Code that does not do what was intended is reported to whoever owns the task, not fixed silently from a docs change.
- Cite a count from the file that holds it, not from a summary of it.
- Rewriting an old doc: every line becomes a fact, is covered by the `Code:` link, or is dropped on purpose. List what you dropped in the PR.
- Test a rewritten area, and any change to the root, with `docs/playbooks/test-the-fact-tree.md`.

## Writing lessons (episodic memory)

- After a non-trivial run that surfaced a gotcha, contradiction, or non-obvious fix, write a lesson from `docs/lessons/_template.md` into `docs/lessons/`. Lessons are TRACKED (committed), unlike plans/specs. Name the file after the takeaway, not the date.
- Write a lesson when: docs/expectation contradicted reality; a root cause was non-obvious; a workaround future runs would repeat; a decision made under ambiguity. Do NOT write one for routine success or already-documented facts.
- A lesson updates a fact: its product half becomes a fact in the right node or leaf, or corrects an existing one, and never adds a paragraph. Its process half becomes a rule, written once, in `docs/playbooks/verify-a-change.md` (proving a change), `docs/playbooks/run-parallel-workers.md` (orchestration), the playbook of the operation it is about, or this file (writing the docs); the rule links the lesson as its Why.
- A lesson is closed (`status: consolidated`) only when every half is placed, and `consolidated-into` lists every doc that carries one. A stale part gets a `note:` in the frontmatter saying what no longer holds.
- A lesson is a record: do not rewrite its body later, not even for a rename.
- Run the `/consolidate-lessons` command (or `docs/playbooks/consolidate-lessons.md`) to distill open lessons.

## Don't invent

Every concrete command, path, or fact comes from a real source (the code, a run, a linked doc) or is marked "(confirm in repo)". A `<TODO:` marker is a correct answer; a plausible fabrication is not.

## Writing style

Plain English. Short sentences. Lead with the point. No emojis in prose. Link to related docs rather than duplicating content. One concept per file.
