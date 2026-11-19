#!/usr/bin/env python3
"""Lint the docs vault for structural invariants (the fact tree and its frame).

Usage (from repo root):  python3 scripts/lint_docs.py [vault_root]
Exits non-zero if any violation is found. Dependency-free (stdlib only).

This is the keystone of the knowledge base: green lint == the structure holds.
See docs/meta/knowledge-base.md for the architecture and README.md for how to adapt.
"""
import os, re, sys
from collections import defaultdict

WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)")
MD_LINK_RE = re.compile(r"\]\(([^)]+?\.md(?:#[^)]*)?)\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
ROOT_EXEMPT = {"INDEX", "REPOS", "CLAUDE", "AGENTS", "README"}  # repo-root docs may be orphans

# ---------------------------------------------------------------------------
# ADAPT THIS to your layout.
# MODE "docs": this repo holds only the knowledge base; code lives in other repos,
#   and a leaf's `Code:` line links GitHub repo roots.
# MODE "mono": docs and code share one repo; only root-level *.md and docs/** are
#   the vault, and a leaf's `Code:` line links directories of this repo.
MODE = "mono"
# A "component" is a direct child dir of COMPONENT_PARENT, each with a README.md
# hub. This template puts components directly under docs/ (small/medium projects).
# For a large project, set COMPONENT_PARENT = os.path.join("docs", "services").
COMPONENT_PARENT = "docs"
# Dirs directly under docs/ that are FRAMEWORK (not components) — exclude them:
FRAMEWORK_DIRS = {"meta", "playbooks", "lessons", "inbox"}
# Files in docs/playbooks/ exempt from playbook-shape / playbook-grounding rules:
PLAYBOOK_DIR = os.path.join("docs", "playbooks")
LESSON_DIR = os.path.join("docs", "lessons")
# ---------------------------------------------------------------------------

_PP = COMPONENT_PARENT.split(os.sep)


def find_md_files(vault):
    # Skip the gitignored agent working area, plus every dot-prefixed dir and file
    # (.git, .claude, .rocket/.rocket-prompt.md — agent tooling, never vault content).
    skip = {"superpowers"}
    out = []
    if MODE == "mono":
        # Code dirs (and their vendored READMEs) are not the vault: only root-level
        # *.md and docs/** are.
        for f in os.listdir(vault):
            if f.endswith(".md") and not f.startswith(".") and os.path.isfile(os.path.join(vault, f)):
                out.append(f)
        walk_root = os.path.join(vault, "docs")
        if not os.path.isdir(walk_root):
            return sorted(out)
    else:
        walk_root = vault
    for dirpath, dirs, files in os.walk(walk_root):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
        for f in files:
            if f.endswith(".md") and not f.startswith("."):
                out.append(os.path.relpath(os.path.join(dirpath, f), vault))
    return sorted(out)


def strip_code(text):
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def build_index(md_files):
    by_path, by_base = set(), {}
    for p in md_files:
        noext = p[:-3]
        by_path.add(noext)
        by_base.setdefault(os.path.basename(noext), []).append(noext)
    return by_path, by_base


def resolve(target, by_path, by_base):
    t = target.strip()
    if t in by_path:
        return t
    b = os.path.basename(t)
    if b in by_base:
        # NOTE: ambiguous basenames resolve to the first match by sort order.
        # Prefer full-path wikilinks to avoid silent mis-resolution.
        return by_base[b][0]
    return None


def read(vault, relpath):
    with open(os.path.join(vault, relpath), encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def _frontmatter_keys(text):
    m = FRONTMATTER_RE.match(text)
    keys = set()
    if m:
        for line in m.group(1).splitlines():
            km = re.match(r"([A-Za-z0-9_-]+):", line)
            if km:
                keys.add(km.group(1))
    return keys


def _is_component_readme(p):
    parts = p.split(os.sep)
    return (len(parts) == len(_PP) + 2
            and parts[:len(_PP)] == _PP
            and parts[len(_PP)] not in FRAMEWORK_DIRS
            and parts[-1] == "README.md")


def _is_component_dir(d):
    parts = d.split(os.sep)
    return (len(parts) > len(_PP)
            and parts[:len(_PP)] == _PP
            and parts[len(_PP)] not in FRAMEWORK_DIRS)


def _wikilink_targets(vault, relpath, by_path, by_base):
    body = strip_code(read(vault, relpath))
    return {resolve(m.group(1), by_path, by_base) for m in WIKILINK_RE.finditer(body)}


def check_broken_wikilinks(vault, md_files, by_path, by_base):
    out = []
    for p in md_files:
        body = strip_code(read(vault, p))
        for m in WIKILINK_RE.finditer(body):
            if resolve(m.group(1), by_path, by_base) is None:
                out.append(f"{p}: broken wikilink [[{m.group(1).strip()}]]")
    return out


def check_orphans(vault, md_files, by_path, by_base):
    inbound = {p[:-3]: 0 for p in md_files}
    for p in md_files:
        for r in _wikilink_targets(vault, p, by_path, by_base):
            if r is not None and r != p[:-3]:
                inbound[r] = inbound.get(r, 0) + 1
    out = []
    for p in md_files:
        noext = p[:-3]
        if os.path.dirname(noext) == "" and (MODE == "mono" or os.path.basename(noext) in ROOT_EXEMPT):
            continue
        if inbound.get(noext, 0) == 0:
            out.append(f"{p}: orphan (no inbound wikilinks)")
    return out


def check_markdown_doc_links(vault, md_files, by_path, by_base):
    out = []
    for p in md_files:
        body = strip_code(read(vault, p))
        for m in MD_LINK_RE.finditer(body):
            tgt = m.group(1)
            if tgt.startswith(("http://", "https://")):
                continue
            bracket = body.rfind("[", 0, m.start())  # skip image embeds ![..](..)
            if bracket > 0 and body[bracket - 1] == "!":
                continue
            out.append(f"{p}: markdown link to doc '{tgt}' — use [[wikilinks]]")
    return out


def check_no_plans_specs(vault, md_files, by_path, by_base):
    out = []
    for p in md_files:
        parts = p.split(os.sep)
        if parts[0] == "docs" and ("plans" in parts[1:] or "specs" in parts[1:]):
            out.append(f"{p}: plans/specs not allowed in the docs tree (use the gitignored working area)")
    return out


def check_component_readme_frontmatter(vault, md_files, by_path, by_base):
    required = {"component", "repo", "last-verified"}
    out = []
    for p in md_files:
        if _is_component_readme(p):
            missing = required - _frontmatter_keys(read(vault, p))
            if missing:
                out.append(f"{p}: component README missing frontmatter keys: {sorted(missing)}")
    return out


def check_lesson_frontmatter(vault, md_files, by_path, by_base):
    required = {"id", "date", "source", "status"}
    exempt = {"README.md", "_template.md"}
    out = []
    for p in md_files:
        if os.path.dirname(p) == LESSON_DIR and os.path.basename(p) not in exempt:
            missing = required - _frontmatter_keys(read(vault, p))
            if missing:
                out.append(f"{p}: lesson missing frontmatter keys: {sorted(missing)}")
    return out


def check_hub_completeness(vault, md_files, by_path, by_base):
    bydir = defaultdict(list)
    for p in md_files:
        bydir[os.path.dirname(p)].append(p)
    out = []
    for d, files in bydir.items():
        if not _is_component_dir(d) or len(files) < 3:
            continue
        hub = os.path.join(d, "README.md")
        if hub not in files:
            out.append(f"{d}: component dir with {len(files)} docs has no README hub")
            continue
        linked = _wikilink_targets(vault, hub, by_path, by_base)
        for f in files:
            if os.path.basename(f) != "README.md" and f[:-3] not in linked:
                out.append(f"{hub}: does not list child [[{f[:-3]}]]")
    return out


def _playbook_subject(p):
    return (os.path.dirname(p) == PLAYBOOK_DIR
            and os.path.basename(p) != "README.md"
            and not os.path.basename(p).startswith("_"))


def check_playbook_shape(vault, md_files, by_path, by_base):
    out = []
    for p in md_files:
        if not _playbook_subject(p):
            continue
        body = read(vault, p)
        missing = [h for h in ("## Steps", "## Verify")
                   if not re.search(rf"^{re.escape(h)}\b", body, re.MULTILINE)]
        if missing:
            out.append(f"{p}: playbook missing required headings: {', '.join(missing)}")
    return out


def collect_canonical_docs(vault, md_files):
    canonical = set()
    for p in md_files:
        m = FRONTMATTER_RE.match(read(vault, p))
        if m and any(re.match(r"canonical\s*:\s*true", line) for line in m.group(1).splitlines()):
            canonical.add(p[:-3])
    return canonical


def check_playbook_grounding(vault, md_files, by_path, by_base):
    canonical_docs = collect_canonical_docs(vault, md_files)
    out = []
    for p in md_files:
        if not _playbook_subject(p):
            continue
        targets = _wikilink_targets(vault, p, by_path, by_base)
        if not (targets & ({"docs/agent-toolbox"} | canonical_docs)):
            out.append(f"{p}: playbook has no wikilink to a canonical doc or docs/agent-toolbox")
    return out


# --- Fact tree ---------------------------------------------------------------
# Files with `kind:` in their frontmatter are tree files (see CLAUDE.md "Writing
# the tree"); the tree checks skip the rest, and `non-tree-docs` limits which
# files may lack it. INDEX.md is the root, checked by path: its facts are the
# numbered lines above the first `---` line; anything below it is not the tree.
TREE_ROOT, TREE_ROOT_MIN, TREE_ROOT_MAX = "INDEX.md", 8, 12
TREE_NODE_MIN, TREE_NODE_MAX, TREE_LEAF_MAX = 3, 7, 12
FACT_RE = re.compile(r"^\d+\. ")  # column 0 only: indented sub-items are not facts
UP_RE = re.compile(r"^\[\[([^\]\|#]+)(?:[|#][^\]]*)?\]\]$")
VERIFIED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\b")
LINK_URL_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
REPO_ROOT_RE = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")


def parse_frontmatter(text):
    """Return (dict of top-level `key: value` pairs, body after the frontmatter)."""
    text = text.replace("\r\n", "\n")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"([A-Za-z0-9_-]+):\s*(.*)$", line)
        if km:
            fm[km.group(1)] = km.group(2).strip()
    return fm, text[m.end():]


def body_lines_outside_fences(body):
    """Yield lines outside ``` fences, fence markers excluded."""
    in_fence = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line


def root_section(vault):
    """Body of INDEX.md above its first `---` line (outside fences): the root facts."""
    _, body = parse_frontmatter(read(vault, TREE_ROOT))
    kept = []
    for line in body_lines_outside_fences(body):
        if line.strip() == "---":
            break
        kept.append(line)
    return kept


def _unlinked_facts(p, facts):
    return [f"{p}: fact has no wikilink one level down: '{fact[:60]}'"
            for fact in facts if not WIKILINK_RE.search(INLINE_CODE_RE.sub("", fact))]


def _check_tree_root(vault):
    facts = [line for line in root_section(vault) if FACT_RE.match(line)]
    out = []
    if not TREE_ROOT_MIN <= len(facts) <= TREE_ROOT_MAX:
        out.append(f"{TREE_ROOT}: root has {len(facts)} facts (needs {TREE_ROOT_MIN}–{TREE_ROOT_MAX})")
    return out + _unlinked_facts(TREE_ROOT, facts)


def _check_up(vault, p, fm, by_path, by_base):
    um = UP_RE.match(fm.get("up", ""))
    if not um:
        return [f"{p}: frontmatter `up` must be a [[wikilink]] to the parent"]
    parent = resolve(um.group(1), by_path, by_base)
    if parent is None:
        return [f"{p}: `up` parent [[{um.group(1).strip()}]] does not exist"]
    if p[:-3] not in _wikilink_targets(vault, parent + ".md", by_path, by_base):
        return [f"{p}: `up` parent {parent}.md does not link back to it"]
    return []


def _check_local_code_link(vault, p, url):
    """Mono mode: a `Code:` link is a directory of this repo, never a file or a URL."""
    if "://" in url or url.startswith("/"):
        return [f"{p}: `Code:` link must be a directory of this repo, not '{url}'"]
    full = os.path.normpath(os.path.join(vault, url))
    if os.path.relpath(full, os.path.normpath(vault)).startswith(".."):
        return [f"{p}: `Code:` link leaves the repo: '{url}'"]
    if not os.path.exists(full):
        return [f"{p}: `Code:` link points at a missing path '{url}'"]
    if not os.path.isdir(full):
        return [f"{p}: `Code:` link must be a directory, not the file '{url}'"]
    return []


def _check_code_line(vault, p, lines):
    nonempty = [line for line in lines if line.strip()]
    last = nonempty[-1] if nonempty else ""
    if not last.startswith("Code:"):
        return [f"{p}: leaf must end with a `Code:` line linking where the code lives"]
    urls = LINK_URL_RE.findall(last)
    if not urls:
        return [f"{p}: `Code:` line has no link"]
    if MODE == "mono":
        return [x for url in urls for x in _check_local_code_link(vault, p, url)]
    return [f"{p}: `Code:` link must be a GitHub repo root, not '{url}'"
            for url in urls if not REPO_ROOT_RE.match(url)]


def check_tree_format(vault, md_files, by_path, by_base):
    out = _check_tree_root(vault) if TREE_ROOT in md_files else []
    for p in md_files:
        fm, body = parse_frontmatter(read(vault, p))
        kind = fm.get("kind")
        if kind is None:
            continue
        if kind not in ("node", "leaf"):
            out.append(f"{p}: unknown kind '{kind}' (node|leaf)")
            continue
        if not VERIFIED_RE.match(fm.get("verified", "")):
            out.append(f"{p}: frontmatter `verified` must start with a date YYYY-MM-DD")
        out += _check_up(vault, p, fm, by_path, by_base)
        lines = list(body_lines_outside_fences(body))
        facts = [line for line in lines if FACT_RE.match(line)]
        if kind == "node":
            if not TREE_NODE_MIN <= len(facts) <= TREE_NODE_MAX:
                out.append(f"{p}: node has {len(facts)} facts (needs {TREE_NODE_MIN}–{TREE_NODE_MAX})")
            out += _unlinked_facts(p, facts)
        else:
            if len(facts) > TREE_LEAF_MAX:
                out.append(f"{p}: leaf has {len(facts)} facts (max {TREE_LEAF_MAX})")
            out += _check_code_line(vault, p, lines)
    return out


def _is_tree_file(vault, noext):
    return "kind" in parse_frontmatter(read(vault, noext + ".md"))[0]


def _reached_from_root(vault, by_path, by_base):
    """Every doc reachable from the INDEX.md root section by following wikilinks
    through tree files only. A link from an old doc, a reference doc or anything
    below the root's `---` does not count: an agent walking the tree never reads it."""
    def targets(text):
        for m in WIKILINK_RE.finditer(strip_code(text)):
            r = resolve(m.group(1), by_path, by_base)
            if r is not None:
                yield r

    reached, queue = set(), list(targets("\n".join(root_section(vault))))
    while queue:
        cur = queue.pop()
        if cur in reached:
            continue
        reached.add(cur)
        if cur != TREE_ROOT[:-3] and _is_tree_file(vault, cur):
            queue.extend(targets(read(vault, cur + ".md")))
    return reached


def check_tree_reachability(vault, md_files, by_path, by_base):
    """Every tree file must be reachable from the root through tree files."""
    tree = [p for p in md_files if _is_tree_file(vault, p[:-3])]
    if TREE_ROOT not in md_files:
        return [f"{p}: tree file but {TREE_ROOT} is missing" for p in tree]
    reached = _reached_from_root(vault, by_path, by_base)
    return [f"{p}: tree file is not reachable from {TREE_ROOT} through tree files"
            for p in tree if p[:-3] not in reached]


def check_components_reachable(vault, md_files, by_path, by_base):
    """Every component hub (docs/<component>/README.md) must be reachable from the
    root through tree files, so an agent walking the tree can find the component."""
    if TREE_ROOT not in md_files:
        return [f"{TREE_ROOT}: missing"]
    reached = _reached_from_root(vault, by_path, by_base)
    return [f"{TREE_ROOT}: component [[{p[:-3]}]] is not reachable from the root through tree files"
            for p in md_files if _is_component_readme(p) and p[:-3] not in reached]


# Docs under docs/ that are deliberately not tree files: reference lists a fact
# sends an agent to, read whole, not walked. Everything else under docs/ carries
# `kind:` — there are no old docs in transition any more.
NON_TREE_DOCS = {"docs/invariants", "docs/agent-toolbox"}
# Directories with their own shape rules (lessons, playbooks) or no shape (inbox, meta).
NON_TREE_DIRS = {"docs/lessons", "docs/playbooks", "docs/inbox", "docs/meta"}


def check_non_tree_docs(vault, md_files, by_path, by_base):
    out = []
    for p in md_files:
        noext = p[:-3].replace(os.sep, "/")
        if not noext.startswith("docs/") or noext in NON_TREE_DOCS:
            continue
        if any(noext.startswith(d + "/") for d in NON_TREE_DIRS):
            continue
        if not _is_tree_file(vault, p[:-3]):
            out.append(f"{p}: no `kind:` frontmatter — rewrite it as a tree file or add it to NON_TREE_DOCS")
    return out


# The transition to the tree is over: no doc may still point at an old doc with
# the marker, or keep a hub section for one. Lessons are history and keep theirs.
TRANSITION_MARKER_RE = re.compile(r"not yet in tree format", re.IGNORECASE)


def check_no_transition_markers(vault, md_files, by_path, by_base):
    out = []
    for p in md_files:
        if p.replace(os.sep, "/").startswith(LESSON_DIR.replace(os.sep, "/") + "/"):
            continue
        if TRANSITION_MARKER_RE.search(strip_code(read(vault, p))):
            out.append(f"{p}: transitional 'not yet in tree format' marker — the tree is complete, link the tree file")
    return out


CHECKS = [
    ("broken-wikilinks", check_broken_wikilinks),
    ("orphans", check_orphans),
    ("markdown-doc-links", check_markdown_doc_links),
    ("plans-specs", check_no_plans_specs),
    ("component-readme-frontmatter", check_component_readme_frontmatter),
    ("lesson-frontmatter", check_lesson_frontmatter),
    ("hub-completeness", check_hub_completeness),
    ("components-reachable", check_components_reachable),
    ("non-tree-docs", check_non_tree_docs),
    ("no-transition-markers", check_no_transition_markers),
    ("playbook-shape", check_playbook_shape),
    ("playbook-grounding", check_playbook_grounding),
    ("tree-format", check_tree_format),
    ("tree-reachability", check_tree_reachability),
]


def lint(vault):
    md_files = find_md_files(vault)
    by_path, by_base = build_index(md_files)
    out = []
    for name, fn in CHECKS:
        for item in fn(vault, md_files, by_path, by_base):
            out.append(f"[{name}] {item}")
    return out


def main():
    vault = sys.argv[1] if len(sys.argv) > 1 else "."
    violations = lint(vault)
    if violations:
        print(f"docs lint: {len(violations)} violation(s)\n")
        for x in violations:
            print("  " + x)
        return 1
    print("docs lint: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
