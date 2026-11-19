# marketplace-analytics

<TODO: one sentence about what marketplace-analytics is.>

Docs and code share this repo. The vault is the root-level `*.md` files and `docs/`; everything else is code. A leaf's `Code:` line links the directory of this repo that holds the code for its facts.

## Where to start

- **Agents and humans:** read the top of `INDEX.md` — the root of a tree of short facts — then `CLAUDE.md` for the rules. Non-Claude agents start at `AGENTS.md`.
- **What you get:** four memory layers (see `docs/meta/knowledge-base.md`) — the fact tree (semantic), the toolbox, invariants and playbooks (procedural), lessons and the `/consolidate-lessons` loop (episodic), and `INDEX.md` + `[[wikilinks]]` (access).

## Keep it green

```
make lint-docs     # structure of the fact tree → "docs lint: OK"
make test-lint     # unit tests for the linter
```

CI (`.github/workflows/docs-lint.yml`) runs both. The linter enforces the tree format, reachability from the root, wikilinks only, playbook and lesson shape, and no plans/specs in `docs/`. The methodology behind it is in `docs/meta/replication-blueprint.md`.

## Fill it in

The scaffold ships `<TODO:` markers where content must be written by hand: the root facts in `INDEX.md`, the prime frame in `CLAUDE.md`, `docs/overview.md`, each component leaf, `docs/invariants.md`, `docs/agent-toolbox.md`, and the golden questions in `docs/playbooks/test-the-fact-tree.md`. Write only what is true today; leave the rest as `<TODO:`.
