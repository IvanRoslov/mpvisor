---
last-verified: 2026-11-19
---

# Why this works — methodology & blueprint

The reasoning behind this template: what the structure is for, the principles that keep it healthy, how to roll it out (especially into an existing docs repo), and the pitfalls we already hit so you don't have to. For the layer model see [[docs/meta/knowledge-base]]; for the day-to-day rules see [[CLAUDE]].

## 1. The idea

Treat this repo as the **memory of an orchestrator agent**, not just human docs. The agent reads it by navigating files and following `[[wikilinks]]` — so structure, link integrity, and freshness are load-bearing. Because the docs are largely **written by agents**, the structure decays unless the discipline is enforced mechanically (that is what `scripts/lint_docs.py` + CI are for).

Memory has four layers (semantic / procedural / episodic / access) — see [[docs/meta/knowledge-base]]. The **consolidation loop** is the payoff: episodic lessons are periodically distilled back into the semantic and procedural layers ([[docs/playbooks/consolidate-lessons]]), so the agent improves run over run.

## 2. Principles (the non-negotiables)

1. **Semantic layer stays file-native and hand-curated.** Do NOT replace the wikilink graph with a vector/RAG index. The curated graph is the well-formed top of the pyramid; an index re-derives a worse copy and loses multi-hop traversal, determinism, and reviewability. (Vector / managed-memory tools are candidates ONLY for the episodic layer, and ONLY once it grows large — Stage 4.)
2. **A tree of short facts, read top-down.** The root ([[INDEX]]) holds 8–12 facts; each links one level down to a node (3–7 facts) or a leaf (up to 12 facts, ending in a `Code:` line). An agent reads the root whole and descends only the branches its task touches, so it finds a fact in 2–4 small files instead of reading whole hubs. Facts say what is true and why it matters; the code says how.
3. **Just-in-time over pre-load.** Give the agent lightweight identifiers (paths, wikilinks) it follows on demand — don't front-load everything.
4. **Self-maintaining over hand-maintained.** Every index/link must be enforced by the linter or generated. Hand-maintained links rot — that is exactly how graphs break (markdown links instead of wikilinks → unreachable orphan docs).
5. **Traceability.** A consolidated fact points back to its source (a lesson, a PR, a verified section).
6. **One canonical home per concept.** Cross-cutting topics get ONE canonical doc (`canonical: true`); everywhere else is a one-line digest + a wikilink. No silent duplication.
7. **Inflow discipline.** Agent-generated transient artifacts (plans, specs) never get committed into the docs tree; they live in the gitignored `superpowers/` working area. Only durable knowledge is promoted in.
8. **Don't invent.** When authoring grounded docs (playbooks especially), every concrete command/fact comes from a real source or is marked "(confirm in repo)". A confidently-stated unverified command is worse than a gap.

## 3. The linter (the keystone)

`scripts/lint_docs.py` (dependency-free, run via `make lint-docs`) encodes the structural invariants. Green lint == the structure holds. It is the test for the whole base, and it runs in CI on every PR. The rules:

| Rule tag | What it enforces |
|----------|------------------|
| `broken-wikilinks` | every `[[link]]` resolves to a real file |
| `orphans` | every non-root doc has ≥1 inbound wikilink |
| `markdown-doc-links` | forbids `](file.md)` between docs — wikilinks only |
| `plans-specs` | no `plans/`/`specs/` in the docs tree (catches inflow leaks) |
| `component-readme-frontmatter` | each component hub has `component`/`repo`/`last-verified` |
| `lesson-frontmatter` | each lesson has `id`/`date`/`source`/`status` |
| `hub-completeness` | a component dir with ≥3 docs has a README that links all its children |
| `components-reachable` | every component hub is reachable from the root through tree files |
| `non-tree-docs` | every doc under `docs/` carries `kind`, except the reference docs and the lessons/playbooks/inbox/meta folders |
| `no-transition-markers` | no leftover `*(not yet in tree format)*` marker after a rewrite |
| `playbook-shape` | each playbook has `## Steps` and `## Verify` |
| `playbook-grounding` | each playbook links a `canonical: true` doc or `agent-toolbox` |
| `tree-format` | root/node/leaf fact counts, a wikilink in every root and node fact, `kind`/`up`/`verified` frontmatter, `up` links back, a leaf ends with a valid `Code:` line |
| `tree-reachability` | every tree file is reachable from the root through tree files |

Extend it the same way it was built: **test-first**, one rule per commit (see `scripts/test_lint_docs.py`).

## 4. Adapting the layout

`MODE` near the top of `scripts/lint_docs.py` says where the code lives:

- `docs` — this repo is only the knowledge base; code lives in other repos listed in `REPOS.md`. A leaf's `Code:` line links GitHub repo roots, never file paths. The linter scans the whole repo.
- `mono` — docs and code share one repo. Only root-level `*.md` and `docs/**` are the vault, so code READMEs and vendored docs are never linted. A leaf's `Code:` line links directories of this repo (or `.` for the root); the linter checks that each exists and is a directory, so moving code without fixing the tree fails CI. CI runs on every PR for that reason, and `.gitignore` ignores only `superpowers/` — a broad `**/specs/` rule would hide code directories such as test specs.

A "component" is a direct child dir of `COMPONENT_PARENT` with a `README.md` hub. The default is `COMPONENT_PARENT = "docs"`; for a large system with many components, set it to `os.path.join("docs", "services")`. `FRAMEWORK_DIRS` marks the dirs under `docs/` that are framework, not components — keep it in sync if you rename them.

## 5. Rolling it out (into an existing docs repo)

A fresh copy of this template already passes lint, so most of "Stage 1" is done for you. When **retrofitting an existing repo**, do it in stages — each ends with a PR, green lint, and CI:

- **Stage 0 — Audit.** Run the linter against the existing docs to measure the starting state: orphan count, markdown-vs-wikilink links, duplicated concepts, oversized files, committed transient artifacts. This is your baseline to drive to zero.
- **Stage 1 — Semantic.** Drop in the linter (test-first), fix `.gitignore`, remove leaked transient files, convert markdown doc-links → wikilinks, rewrite each area as a fact tree (root → node → leaf, every line becomes a fact, is covered by the `Code:` link, or is dropped on purpose; mark each not-yet-rewritten link with the `*(not yet in tree format)*` marker and drive them to zero), test each area with fresh agents ([[docs/playbooks/test-the-fact-tree]]), write the authoring rules into CLAUDE.md, add the knowledge-base tracker.
- **Stage 2 — Procedural.** Mark the toolbox `canonical: true`; add the playbook rules and the standing-rule playbooks (`verify-a-change`, `run-parallel-workers`); write `docs/playbooks/` runbooks for your recurring operations, GROUNDED in real docs.
- **Stage 3 — Episodic.** Add `docs/lessons/` + the lesson rule; the consolidate-lessons playbook + `/consolidate-lessons` command; seed a few REAL lessons and dogfood one consolidation cycle.
- **Stage 4 — Hybrid retrieval (gated).** Only when `docs/lessons/` grows to a few hundred records. BM25+embeddings or an off-the-shelf engine, scoped to `docs/lessons/` only. Don't build it early.

Execution that worked for us: brainstorm → umbrella spec → staged plans (kept in the gitignored working area) → subagent-driven execution with two-stage review (spec-compliance, then quality), the lint as the objective gate. Always work on a branch; gate every PR on CI.

## 6. Pitfalls we hit (real)

- **The graph died at hop 2.** Component READMEs used markdown links `](file.md)`, so the graph stopped at INDEX→README and deep docs were unreachable orphans. Fix: wikilinks only (`orphans` + `markdown-doc-links` rules).
- **Transient artifacts leaked into git.** The ignore covered only the working area, but the planning skill wrote plans/specs INTO component dirs, which the ignore didn't cover. Fix: ignore `**/plans/ **/specs/`; the `plans-specs` rule blocks recurrence.
- **Mechanical link conversion mis-resolved silently.** When a relative target didn't exist, the basename fallback picked the FIRST same-named file by sort order — a valid-but-wrong link. Lint stayed green. Fix: prefer full-path wikilinks.
- **Hubs grew into catalogs nobody read.** Component READMEs listed every doc with a summary, and agents read whole hubs to find one fact. Fix: the fact tree — a short root read whole, one branch walked down, `Code:` links for HOW.
- **A lesson appended a paragraph instead of fixing a fact.** Facts and their corrections drifted apart in one doc. Fix: a lesson updates a fact; its process half becomes a rule written once in a playbook.
- **A fact corrected in one doc, stale in siblings.** Consolidating a lesson fixed one README but left sibling docs contradicting it. Scope consolidation to the whole component; record every doc touched in the lesson's `consolidated-into`.
- **`.claude/` and `__pycache__/` linted/committed by accident.** `find_md_files` skips `.claude`; gitignore covers `__pycache__/`/`*.pyc`.

## 7. Checklist (adopting in a repo)

- [ ] `scripts/lint_docs.py` (`MODE` and `COMPONENT_PARENT` set) + `scripts/test_lint_docs.py`
- [ ] `Makefile` + `.github/workflows/docs-lint.yml`
- [ ] `.gitignore` ignores the working area (`docs` mode also `**/plans/ **/specs/`)
- [ ] `INDEX.md` root holds 8–12 facts; every doc under `docs/` is a tree file or in an allowed folder
- [ ] Every tree file reachable from the root; zero orphans; wikilinks only
- [ ] Golden questions written; the tree passes [[docs/playbooks/test-the-fact-tree]]
- [ ] Toolbox is `canonical: true`; playbooks written + grounded; `verify-a-change` and `run-parallel-workers` hold the standing rules
- [ ] `docs/lessons/` + consolidate-lessons playbook + `/consolidate-lessons` command
- [ ] `CLAUDE.md` and `AGENTS.md`; `docs/meta/knowledge-base.md`
- [ ] `make lint-docs` → OK; CI green
