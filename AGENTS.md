# AGENTS.md — marketplace-analytics agent entry point

These instructions apply throughout this repository. Docs and code share this repo. The vault is the root-level `*.md` files and `docs/`; everything else is code. A leaf's `Code:` line links the directory of this repo that holds the code for its facts.

## Start here

1. Read the top of `INDEX.md` whole. It is the root of a tree of short facts;
   the reading rule is in `CLAUDE.md` ("Start here — read the fact tree").
2. Read `CLAUDE.md` in full and follow its repository rules. Despite its name,
   it is the shared contract for every agent, Claude or not. Keep those rules
   there rather than maintaining a second copy here.
3. Read `docs/invariants.md` before you change behaviour. Use
   `docs/agent-toolbox.md` to choose tools for operational tasks.
4. For the task's topic, descend from `INDEX.md` fact by fact: follow only the
   facts that touch your task, stop when you have the answer, and read the code
   a leaf links for HOW. Check `docs/playbooks/README.md` for a runbook; the
   standing process rules are in `docs/playbooks/verify-a-change.md` and
   `docs/playbooks/run-parallel-workers.md`.

## Working with the existing tooling

- Tool names in `docs/agent-toolbox.md` describe the required capability.
  Discover the tools actually available in the current session; Claude's
  `ToolSearch` syntax and MCP prefixes are not portable API contracts. If a
  required connection is missing, report the specific limitation without
  inventing tool calls or claiming an operation succeeded.
- Claude slash commands are convenience entry points. Other agents run the
  underlying playbook directly. For lesson consolidation, read
  `docs/playbooks/consolidate-lessons.md`.

## Validation and delivery

Run checks from the repository root. The docs checks need only Python 3 and Make.

```sh
make lint-docs
make test-lint
git diff --check
```

Check the baseline before editing. Fix issues introduced by the task and report
pre-existing failures separately. Review the final diff and report changed
files, verification results, and any checks that could not run. Keep temporary
plans and specs under the gitignored `superpowers/` directory, as `CLAUDE.md`
requires; durable knowledge belongs in the tree.
