---
last-verified: 2026-11-19
---

# Playbooks

Step-by-step runbooks for recurring operations the agent performs. Each playbook has `## Steps` and `## Verify`, and links a canonical doc (the linter enforces both). Ground every step in real docs — mark undocumented specifics "(confirm in repo)".

## Map

- [[docs/playbooks/verify-a-change]] — the standing rules for proving a claim or a change (what counts as evidence)
- [[docs/playbooks/run-parallel-workers]] — the standing rules for briefing, running and merging parallel workers
- [[docs/playbooks/test-the-fact-tree]] — prove the fact tree answers questions in ≤4 files (the golden set lives here)
- [[docs/playbooks/consolidate-lessons]] — distill open lessons into the tree and the playbooks (the episodic→semantic loop)
- [[docs/playbooks/_template]] — copy this to start a new playbook

<!-- Add a line per playbook as you write them (deploy, debug, release, …). -->

## Pillars

The procedural reference these runbooks build on: [[docs/agent-toolbox]] (which tool to use) and [[docs/invariants]] (hard rules).
