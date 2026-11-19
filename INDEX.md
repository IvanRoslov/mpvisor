# marketplace-analytics Index

Read this whole. Each fact links one level down; follow only the branches your task touches. The rules for reading and writing the tree are in `CLAUDE.md`.

1. marketplace-analytics: <TODO: one sentence about what marketplace-analytics is.> What it is for, who uses it and how it ships. → [[docs/overview]]
2. app: <TODO: описание компонента> <TODO: the one fact an agent most needs about it.> → [[docs/app/README]]
3. The hard rules you must never break are a reference list outside the tree. → [[docs/invariants]]
4. Which tool to use to build, test and ship. → [[docs/agent-toolbox]]
5. Step-by-step runbooks for recurring operations, including the standing rules for proving a change and for running parallel workers. → [[docs/playbooks/README]]
6. What past runs taught us, until each lesson becomes a fact or a rule. → [[docs/lessons/README]]
7. How this knowledge base is organized and why it works. → [[docs/meta/knowledge-base]]
8. Docs and code share this repo: the vault is the root-level `*.md` files and `docs/`, and a leaf's `Code:` line links a directory of this repo. → [[CLAUDE]]

---

## Outside the tree

These are not facts to walk; a fact or a task sends you to them.

- [[docs/inbox/README]] — unprocessed notes, waiting to be triaged into the tree.
- [[docs/meta/replication-blueprint]] — why this structure works and how to roll it out elsewhere.
