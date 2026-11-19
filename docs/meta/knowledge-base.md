---
last-verified: 2026-11-19
---

# Knowledge base

This repo's docs are the memory of the orchestrator agent. They are organized in four layers.

| Layer | What it holds | Where it lives |
|-------|---------------|----------------|
| **Semantic** | Facts about the system — what is true and why it matters | the fact tree: [[INDEX]] → `docs/` |
| **Procedural** | How the agent operates — tool selection, hard rules, standing process rules, step-by-step playbooks | [[docs/agent-toolbox]], [[docs/invariants]], [[docs/playbooks/README]] |
| **Episodic** | What happened in past runs, distilled | [[docs/lessons/README]] + consolidation loop |
| **Access / retrieval** | How the agent finds the right memory | [[INDEX]] + wikilinks now; optional hybrid search later (gated on lesson volume) |

The semantic layer is a **fact tree** rooted at [[INDEX]]. The root holds 8–12 short facts, each linking one level down to a node (more facts) or a leaf (facts ending in a `Code:` line). An agent reads the root whole and descends only the branches its task touches, so it finds a fact in 2–4 small files. The tree describes `main`, every fact is verified against the code, and the linter enforces the format and reachability. The rules are in [[CLAUDE]] ("Start here — read the fact tree", "Writing the tree"); [[docs/playbooks/test-the-fact-tree]] tests it. Every doc under `docs/` is a tree file except the two reference docs and the lessons, playbooks, inbox and meta folders; the linter enforces that too.

The **consolidation loop** is the point: episodic lessons are distilled back into the semantic and procedural layers, so the agent improves run over run. A lesson updates a fact: its product half becomes or corrects a fact in the tree, never an appended paragraph, and its process half becomes a rule written once in a playbook ([[docs/playbooks/verify-a-change]], [[docs/playbooks/run-parallel-workers]]) or in [[CLAUDE]], with the lesson as its Why. Run it with the `/consolidate-lessons` command (see [[docs/playbooks/consolidate-lessons]]).

## How the tree stays fresh

- The linter rejects a tree file in the wrong shape, a tree file or component the root cannot reach, a doc under `docs/` without `kind`, and a `Code:` line that points at the wrong kind of target.
- A change to behaviour fixes its fact in the same feature.
- Deployment facts are re-checked where deployment state lives, never repeated from memory.
- A rewritten area, and any change to the root, is tested with fresh agents ([[docs/playbooks/test-the-fact-tree]]).

## Internal memory vs client-facing docs

This is **internal memory**. If the project also publishes documentation for people outside the team, that lives in its own place and is written differently. The test: does someone outside the team need this to use the system? Yes → the public docs. No → here. The tree may state where the public docs live, as a fact; it never rewrites them.

## Why this works

New to this approach? Read [[docs/meta/replication-blueprint]] — the principles, the reasoning, how to roll it out into an existing repo, and the pitfalls already hit.

## How docs stay healthy

Run `make lint-docs` before committing docs changes. The linter (`scripts/lint_docs.py`) enforces: wikilinks only, no orphans, hub completeness, component README frontmatter, no plans/specs in the docs tree, playbook shape and grounding, lesson frontmatter, fact-tree format, reachability of every tree file and component from the root, `kind` on every doc under `docs/` outside the allowed folders, and no leftover transition markers. The same checks run in CI on every pull request via the `docs-lint` workflow, so a violation blocks merge.
