---
last-verified: 2026-11-19
---

# Run parallel workers

## When to use

You orchestrate several workers (agent sessions, subagents) that build features at the same time, or you are one of those workers. These are the standing rules for briefing them, keeping them alive, merging their PRs and triaging review. Each rule came from a run that went wrong; the line under each rule is its why.

The starting rules were distilled from lessons in another knowledge base of ours and link there; add this project's lessons to the Why lines as they come (see [[docs/playbooks/consolidate-lessons]]). The rules for proving a single change are in [[docs/playbooks/verify-a-change]]. The tools are in [[docs/agent-toolbox]].

## Steps

1. Before you spawn, plan subtasks and briefs with "Briefing and subtasks".
2. While workers run, follow "Workers on a shared machine".
3. When their PRs land, follow "Merging parallel work" and "Review findings".

## Briefing and subtasks

**One PR, one subtask.** Work owed after a merge (a second PR, a live staging pass, a browser check) gets its own subtask up front, with a fresh worker spawned when its dependency merges: a worker is often reaped the moment its PR merges, whatever its brief said.
Why: [two-PR work needs two subtasks](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/two-pr-work-needs-two-subtasks.md)

**Send a brief as a durable doc, not only as a message.** A message can be lost, and a session reaped or respawned; a brief stored on the task survives all three. Check that it is stored.
Why: [two-PR work needs two subtasks](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/two-pr-work-needs-two-subtasks.md)

**Write the cross-feature semantic into the brief.** "Independent" in a dependency graph means no build order, not disjoint files. When two features extend the same path, the orchestrator decides how they combine and says so in both briefs; a mechanical conflict resolution must not decide it.
Why: [parallel phases collide at merge](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/parallel-phases-collide-at-merge.md)

**A rename brief states intent, not the result.** Resolve each old name through its redirect or the consumer's manifest before you write it as current, and brief workers with the resolved names, not the pattern. Leave history (version pins, past PR links, lessons) alone.
Why: [a rename brief is not the rename map](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/a-rename-brief-is-not-the-rename-map.md)

## Workers on a shared machine

**Write every brief, answer and PR body into the session scratchpad, and pass markdown as a file.** A shared `/tmp` can deliver somebody else's brief under a generic file name, and a double-quoted shell argument runs its backticks as commands.
Why: [orchestrator scratch files and shell quoting](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/orchestrator-scratch-files-and-shell-quoting.md)

**Never wrap a non-idempotent call in a retry loop.** A client timeout can follow a committed write. On a timeout, read the recorded state and decide from it; before a deliberate retry, check that no old loop still runs.
Why: [a timeout is not a failed delivery](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/a-timeout-is-not-a-failed-delivery.md)

**After a spawn, look at the session screen before you send anything.** A fresh agent may sit on a trust prompt whose preselected answer exits; a keystroke or a delivered message picks it.
Why: [a timeout is not a failed delivery](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/a-timeout-is-not-a-failed-delivery.md)

**Share nothing a parallel run can break.** Give each browser run its own profile. Never kill by process name (`pkill`, `killall`): it takes down other runs. On a loaded machine CI is the gate.
Why: [a timeout is not a failed delivery](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/a-timeout-is-not-a-failed-delivery.md)

## Merging parallel work

**Treat the integration files as a contended resource.** Module registries, schema barrels and migration journals collide under parallel work. Brief workers to expect a conflict there and to merge `origin/main` and resolve, keeping both sides. <TODO: list this project's integration files once they exist.>
Why: [concurrent features collide on migrations](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/concurrent-features-collide-on-migrations-and-send-path.md)

**Regenerate a migration on rebase, never hand-edit it.** Parallel branches claim the same next index. Drop your migration and its journal entry, rebase, merge any widened schema first, then generate again.
Why: [concurrent features collide on migrations](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/concurrent-features-collide-on-migrations-and-send-path.md)

**Merge isolated PRs first and serialize the rest.** The last feature in absorbs the reconciliation of a shared path; drive it to rebase and re-verify.
Why: [rebase and re-verify before merge](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/rebase-and-reverify-before-merge-main-moves-fast.md)

## Review findings

**Triage each finding: real, then in your diff.** A reviewer that scans the whole tree reports old bugs against every PR. Real and in the diff: fix it here. Real but pre-existing: annotate the PR and route it to a standalone fix or to the worker that owns the file.
Why: [a reviewer scans the whole tree](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/ao-reviewer-scans-whole-tree-triage-preexisting.md)

**Close a review cycle by decision.** When every in-diff finding is fixed and only routed pre-existing findings remain, declare the review complete.
Why: [a reviewer scans the whole tree](https://github.com/lepsto/lepsto-mail-docs/blob/main/docs/lessons/ao-reviewer-scans-whole-tree-triage-preexisting.md)

## Verify

- Every worker that owes post-merge work has its own subtask.
- Every brief is stored on its subtask.
- Each merged PR was rebased on current `origin/main` and re-tested before merge.

## Related

- [[docs/playbooks/verify-a-change]] — rules for proving a change
- [[docs/playbooks/consolidate-lessons]] — how a lesson becomes a rule here or a fact in the tree
