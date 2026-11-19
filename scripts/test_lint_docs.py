import os, tempfile, unittest
import lint_docs as L


def write(root, rel, body):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(body)


class _Pinned:
    """Pin the linter's configuration for one test, whatever the scaffolder set:
    the tests use components directly under docs/ and the mode named by the class."""
    PIN_MODE = "docs"

    def setUp(self):
        self._saved = (L.MODE, L.COMPONENT_PARENT, L._PP)
        L.MODE, L.COMPONENT_PARENT, L._PP = self.PIN_MODE, "docs", ["docs"]

    def tearDown(self):
        L.MODE, L.COMPONENT_PARENT, L._PP = self._saved


class MonoMode(_Pinned):
    """Run a test body with the linter switched to mono mode (docs + code in one repo)."""
    PIN_MODE = "mono"


class DocsMode(_Pinned):
    """The tests below were written for docs mode; pin it so they hold in a mono repo too."""
    PIN_MODE = "docs"


class ScaffoldTest(DocsMode, unittest.TestCase):
    def test_find_resolve_and_strip(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/a/README.md", "see [[docs/a/child]] and `[[ignored]]`")
            write(root, "docs/a/child.md", "x")
            write(root, "docs/superpowers/specs/local.md", "x")  # excluded
            write(root, ".claude/x.md", "x")                     # excluded
            md = L.find_md_files(root)
            self.assertIn("docs/a/child.md", md)
            self.assertNotIn("docs/superpowers/specs/local.md", md)
            self.assertNotIn(".claude/x.md", md)
            bp, bb = L.build_index(md)
            self.assertEqual(L.resolve("docs/a/child", bp, bb), "docs/a/child")
            self.assertEqual(L.resolve("child", bp, bb), "docs/a/child")
            self.assertIsNone(L.resolve("nope", bp, bb))
            self.assertNotIn("[[ignored]]", L.strip_code("`[[ignored]]`"))


class BrokenWikilinksTest(DocsMode, unittest.TestCase):
    def test_flags_unresolved_only(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/a.md", "[[docs/b]] and [[ghost]] and `[[fenced]]`")
            write(root, "docs/b.md", "x")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_broken_wikilinks(root, md, bp, bb)
            self.assertTrue(any("ghost" in x for x in v))
            self.assertFalse(any("docs/b" in x for x in v))
            self.assertFalse(any("fenced" in x for x in v))


class OrphansTest(DocsMode, unittest.TestCase):
    def test_flags_unreferenced_nonroot(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "INDEX.md", "[[docs/a/README]]")
            write(root, "docs/a/README.md", "[[docs/a/child]]")
            write(root, "docs/a/child.md", "x")
            write(root, "docs/a/lonely.md", "x")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_orphans(root, md, bp, bb)
            self.assertTrue(any("lonely" in x for x in v))
            self.assertFalse(any("INDEX" in x for x in v))
            self.assertFalse(any("a/child" in x for x in v))

    def test_root_agents_md_is_an_entry_point_not_an_orphan(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "INDEX.md", "x")
            write(root, "AGENTS.md", "read CLAUDE.md")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            self.assertEqual(L.check_orphans(root, md, bp, bb), [])


class MdLinkTest(DocsMode, unittest.TestCase):
    def test_flags_md_links_not_http_or_images(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/a.md", "[doc](architecture.md) [ok](https://x.com) ![img](d.md)")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_markdown_doc_links(root, md, bp, bb)
            self.assertTrue(any("architecture.md" in x for x in v))
            self.assertFalse(any("x.com" in x for x in v))
            self.assertFalse(any("d.md" in x for x in v))


class PlansSpecsTest(DocsMode, unittest.TestCase):
    def test_flags_plans_specs_in_docs(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/svc/plans/x.md", "x")
            write(root, "docs/svc/domain/ok.md", "x")
            write(root, "docs/superpowers/specs/fine.md", "x")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_no_plans_specs(root, md, bp, bb)
            self.assertTrue(any("svc/plans" in x for x in v))
            self.assertFalse(any("domain/ok" in x for x in v))
            self.assertFalse(any("superpowers" in x for x in v))


class ComponentFrontmatterTest(DocsMode, unittest.TestCase):
    def test_requires_keys(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/svc/README.md", "---\ncomponent: Svc\nrepo: r\n---\nbody")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_component_readme_frontmatter(root, md, bp, bb)
            self.assertTrue(any("last-verified" in x for x in v))

    def test_complete_frontmatter_ok(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/svc/README.md", "---\ncomponent: Svc\nrepo: r\nlast-verified: 2026-01-01\n---\nbody")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            self.assertEqual(L.check_component_readme_frontmatter(root, md, bp, bb), [])

    def test_framework_dir_not_a_component(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/meta/README.md", "no frontmatter")  # framework, not a component
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            self.assertEqual(L.check_component_readme_frontmatter(root, md, bp, bb), [])


class LessonFrontmatterTest(DocsMode, unittest.TestCase):
    def test_missing_status_flagged_template_exempt(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/lessons/2026-01-01-x.md", "---\nid: x\ndate: 2026-01-01\nsource: u\n---\nb")
            write(root, "docs/lessons/_template.md", "---\n---\nb")
            write(root, "docs/lessons/README.md", "hub")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_lesson_frontmatter(root, md, bp, bb)
            self.assertTrue(any("2026-01-01-x" in x and "status" in x for x in v))
            self.assertFalse(any("_template" in x for x in v))
            self.assertFalse(any("README" in x for x in v))


class HubCompletenessTest(DocsMode, unittest.TestCase):
    def test_component_hub_must_list_children(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/svc/README.md", "Map: [[docs/svc/a]]")  # misses b
            write(root, "docs/svc/a.md", "x")
            write(root, "docs/svc/b.md", "x")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_hub_completeness(root, md, bp, bb)
            self.assertTrue(any("svc/b" in x for x in v))
            self.assertFalse(any("svc/a" in x for x in v))

    def test_framework_dir_exempt(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/meta/a.md", "x")
            write(root, "docs/meta/b.md", "x")
            write(root, "docs/meta/c.md", "x")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            self.assertEqual(L.check_hub_completeness(root, md, bp, bb), [])


class PlaybookShapeTest(DocsMode, unittest.TestCase):
    def test_missing_verify_flagged_exemptions(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/playbooks/op.md", "## Steps\n1. do")
            write(root, "docs/playbooks/full.md", "## Steps\n1.\n## Verify\nok")
            write(root, "docs/playbooks/_template.md", "skeleton")
            write(root, "docs/playbooks/README.md", "hub")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_playbook_shape(root, md, bp, bb)
            self.assertTrue(any("op.md" in x and "Verify" in x for x in v))
            self.assertFalse(any("full.md" in x for x in v))
            self.assertFalse(any("_template" in x for x in v))
            self.assertFalse(any("README" in x for x in v))


class PlaybookGroundingTest(DocsMode, unittest.TestCase):
    def test_requires_canonical_or_toolbox_link(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/agent-toolbox.md", "---\ncanonical: true\n---\ntoolbox")
            write(root, "docs/playbooks/grounded.md", "## Steps\n## Verify\nsee [[docs/agent-toolbox]]")
            write(root, "docs/playbooks/floating.md", "## Steps\n## Verify\nno link")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            v = L.check_playbook_grounding(root, md, bp, bb)
            self.assertTrue(any("floating.md" in x for x in v))
            self.assertFalse(any("grounded.md" in x for x in v))


# --- Fact tree ---------------------------------------------------------------

GH = "https://github.com/lepsto/x"


def node(facts, up="up: [[docs/a/README]]\n", extra=""):
    lines = "\n".join(f"{i}. Fact {i} links down. -> [[docs/a/b/l{i}]]" for i in range(1, facts + 1))
    return f"---\nkind: node\n{up}verified: 2026-10-01\n---\n# N\n\n{lines}\n{extra}"


def leaf(facts, code=f"Code: [lepsto/x]({GH})", up="up: [[docs/a/README]]\n",
         verified="verified: 2026-10-01 against x@abc\n", kind="leaf"):
    lines = "\n".join(f"{i}. Fact {i}." for i in range(1, facts + 1))
    return f"---\nkind: {kind}\n{up}{verified}---\n# L\n\n{lines}\n\n{code}\n"


PARENT = "---\nkind: node\nup: [[INDEX]]\nverified: 2026-10-01\n---\n1. a -> [[docs/a/leaf]]\n2. b -> [[docs/a/x]]\n3. c -> [[docs/a/y]]\n"


def root(facts, extra="", link=True):
    lines = "\n".join(f"{i}. Root fact {i}." + (" -> [[docs/a/README]]" if link else "") for i in range(1, facts + 1))
    return f"# Mail Index\n\nRead this whole.\n\n{lines}\n{extra}\n---\n\n## Catalog (until the tree covers it)\n\n1. old catalog line\n"


ROOT = root(8)


def run_check(fn, files):
    with tempfile.TemporaryDirectory() as r:
        for rel, body in files.items():
            write(r, rel, body)
        md = L.find_md_files(r); bp, bb = L.build_index(md)
        return fn(r, md, bp, bb)


class TreeFormatTest(DocsMode, unittest.TestCase):
    def run_tree(self, files):
        return run_check(L.check_tree_format, files)

    def leaf_vault(self, body):
        return self.run_tree({"INDEX.md": ROOT, "docs/a/README.md": PARENT, "docs/a/leaf.md": body})

    def node_vault(self, body):
        return [x for x in self.leaf_vault(body) if "docs/a/README.md" not in x]

    def test_node_with_2_facts_fails(self):
        v = self.node_vault(node(2))
        self.assertTrue(any("docs/a/leaf.md" in x and "node" in x and "2 facts" in x for x in v), v)

    def test_node_with_8_facts_fails(self):
        v = self.node_vault(node(8))
        self.assertTrue(any("8 facts" in x for x in v), v)

    def test_node_with_5_facts_passes(self):
        self.assertEqual(self.node_vault(node(5)), [])

    def test_node_fact_without_wikilink_fails(self):
        v = self.node_vault(node(3, extra="4. A fact with no link down.\n"))
        self.assertEqual(len(v), 1, v)
        self.assertIn("no wikilink", v[0])

    def test_node_fact_with_link_only_in_inline_code_fails(self):
        v = self.node_vault(node(3, extra="4. Mentions `[[docs/a/b/l1]]` only.\n"))
        self.assertEqual(len(v), 1, v)

    def test_leaf_with_13_facts_fails(self):
        v = self.leaf_vault(leaf(13))
        self.assertTrue(any("13 facts" in x for x in v), v)

    def test_leaf_with_12_facts_passes(self):
        self.assertEqual(self.leaf_vault(leaf(12)), [])

    def test_leaf_without_code_line_fails(self):
        v = self.leaf_vault(leaf(3, code="Some closing words."))
        self.assertTrue(any("Code:" in x for x in v), v)

    def test_leaf_code_line_not_last_fails(self):
        v = self.leaf_vault(leaf(3, code=f"Code: [x]({GH})\n\nTrailing prose."))
        self.assertTrue(any("Code:" in x for x in v), v)

    def test_leaf_code_link_to_file_fails(self):
        v = self.leaf_vault(leaf(3, code="Code: [a](https://github.com/lepsto/x/blob/main/a.ts)"))
        self.assertTrue(any("blob/main/a.ts" in x for x in v), v)

    def test_leaf_code_link_to_tree_path_fails(self):
        v = self.leaf_vault(leaf(3, code=f"Code: [x]({GH}), [y](https://github.com/lepsto/y/tree/main/src)"))
        self.assertEqual(len(v), 1, v)

    def test_leaf_code_non_github_link_fails(self):
        v = self.leaf_vault(leaf(3, code="Code: [x](https://example.invalid/lepsto/x)"))
        self.assertEqual(len(v), 1, v)

    def test_leaf_code_line_without_link_fails(self):
        v = self.leaf_vault(leaf(3, code="Code: lepsto-mail-toolkit"))
        self.assertEqual(len(v), 1, v)

    def test_leaf_code_repo_roots_pass(self):
        code = f"Code: [x]({GH}), [y](https://github.com/lepsto/y/) (mail part)"
        self.assertEqual(self.leaf_vault(leaf(3, code=code)), [])

    def test_missing_up_fails(self):
        v = self.leaf_vault(leaf(3, up=""))
        self.assertTrue(any("up" in x for x in v), v)

    def test_missing_verified_fails(self):
        v = self.leaf_vault(leaf(3, verified=""))
        self.assertTrue(any("verified" in x for x in v), v)

    def test_verified_without_date_fails(self):
        v = self.leaf_vault(leaf(3, verified="verified: recently\n"))
        self.assertTrue(any("verified" in x for x in v), v)

    def test_up_not_a_wikilink_fails(self):
        v = self.leaf_vault(leaf(3, up="up: docs/a/README\n"))
        self.assertTrue(any("up" in x for x in v), v)

    def test_up_unresolvable_fails(self):
        v = self.leaf_vault(leaf(3, up="up: [[docs/a/ghost]]\n"))
        self.assertTrue(any("ghost" in x for x in v), v)

    def test_up_parent_without_backlink_fails(self):
        parent = "---\nkind: node\nverified: 2026-10-01\n---\n1. a -> [[docs/a/x]]\n2. b -> [[docs/a/y]]\n3. c -> [[docs/a/z]]\n"
        v = self.run_tree({"docs/a/README.md": parent, "docs/a/leaf.md": leaf(3)})
        self.assertTrue(any("docs/a/leaf.md" in x and "does not link back" in x for x in v), v)

    def test_root_index_needs_no_up(self):
        v = self.run_tree({"INDEX.md": ROOT, "docs/a/README.md":
                           "---\nkind: node\nup: [[INDEX]]\nverified: 2026-10-01\n---\n1. a [[x]]\n2. b [[y]]\n3. c [[z]]\n"})
        self.assertEqual(v, [])

    def test_fenced_and_indented_numbered_lines_not_counted(self):
        body = leaf(12, code=f"```\n13. not a fact\n14. nor this\n```\n   15. indented sub-item\n\nCode: [x]({GH})")
        self.assertEqual(self.leaf_vault(body), [])

    def test_nested_list_items_under_a_node_fact_not_counted(self):
        body = node(7, extra="   1. a nested step\n   2. another\n")
        self.assertEqual(self.node_vault(body), [])

    def test_code_line_inside_fence_does_not_count(self):
        v = self.leaf_vault(leaf(3, code=f"```\nCode: [x]({GH})\n```"))
        self.assertTrue(any("Code:" in x for x in v), v)

    def test_file_without_kind_is_ignored(self):
        v = self.run_tree({"docs/a/old.md": "---\nlast-verified: 2026-01-01\n---\n1. one\n2. two\n"})
        self.assertEqual(v, [])

    def test_component_hub_keeps_its_keys_alongside_kind(self):
        hub = ("---\ncomponent: Mail\nrepo: lepsto-mail-toolkit\nlast-verified: 2026-10-01\n"
               "kind: node\nup: [[INDEX]]\nverified: 2026-10-01\n---\n1. a [[x]]\n2. b [[y]]\n3. c [[z]]\n")
        self.assertEqual(self.run_tree({"INDEX.md": ROOT, "docs/a/README.md": hub}), [])

    def test_unknown_kind_fails(self):
        v = self.leaf_vault(leaf(3, kind="hub"))
        self.assertTrue(any("kind" in x and "hub" in x for x in v), v)

    def test_crlf_frontmatter_parsed(self):
        self.assertEqual(self.leaf_vault(leaf(3).replace("\n", "\r\n")), [])

    def test_root_with_7_facts_fails(self):
        v = self.run_tree({"INDEX.md": root(7)})
        self.assertTrue(any("INDEX.md" in x and "7 facts" in x for x in v), v)

    def test_root_with_13_facts_fails(self):
        v = self.run_tree({"INDEX.md": root(13)})
        self.assertTrue(any("INDEX.md" in x and "13 facts" in x for x in v), v)

    def test_root_with_10_facts_passes(self):
        self.assertEqual(self.run_tree({"INDEX.md": root(10)}), [])

    def test_root_fact_without_wikilink_fails(self):
        v = self.run_tree({"INDEX.md": root(8, extra="9. A root fact with no link.")})
        self.assertEqual(len(v), 1, v)
        self.assertIn("no wikilink", v[0])

    def test_root_lines_below_separator_not_counted(self):
        body = root(10) + "".join(f"{i}. catalog {i}\n" for i in range(2, 20))
        self.assertEqual(self.run_tree({"INDEX.md": body}), [])

    def test_registered_in_lint(self):
        self.assertIn("tree-format", [name for name, _ in L.CHECKS])


class TreeReachabilityTest(DocsMode, unittest.TestCase):
    def run_reach(self, files):
        return run_check(L.check_tree_reachability, files)

    def test_leaf_reached_through_node_passes(self):
        v = self.run_reach({"INDEX.md": ROOT, "docs/a/README.md": PARENT, "docs/a/leaf.md": leaf(3)})
        self.assertEqual(v, [])

    def test_tree_file_with_no_path_from_root_fails(self):
        v = self.run_reach({"INDEX.md": ROOT, "docs/a/README.md": PARENT, "docs/a/leaf.md": leaf(3),
                            "docs/b/lost.md": leaf(3, up="up: [[docs/a/README]]\n")})
        self.assertEqual(len(v), 1, v)
        self.assertIn("docs/b/lost", v[0])

    def test_link_from_non_tree_doc_does_not_count(self):
        v = self.run_reach({"INDEX.md": root(8).replace("[[docs/a/README]]", "[[docs/invariants]]"),
                            "docs/invariants.md": "see [[docs/a/README]]",
                            "docs/a/README.md": PARENT})
        self.assertTrue(any("docs/a/README" in x for x in v), v)

    def test_link_only_from_catalog_below_separator_does_not_count(self):
        body = root(8).replace("[[docs/a/README]]", "[[docs/invariants]]") + "- [[docs/a/README]]\n"
        v = self.run_reach({"INDEX.md": body, "docs/invariants.md": "x", "docs/a/README.md": PARENT})
        self.assertTrue(any("docs/a/README" in x for x in v), v)

    def test_unlinked_non_tree_file_is_ignored(self):
        v = self.run_reach({"INDEX.md": ROOT, "docs/a/README.md": PARENT, "docs/old.md": "1. old"})
        self.assertEqual(v, [])

    def test_missing_index_with_tree_files_fails(self):
        v = self.run_reach({"docs/a/README.md": PARENT})
        self.assertTrue(v, v)

    def test_registered_in_lint(self):
        self.assertIn("tree-reachability", [name for name, _ in L.CHECKS])


class ComponentsReachableTest(DocsMode, unittest.TestCase):
    """Replaces index-lists-components: a component hub must be reachable from the
    root through tree files, not merely linked from anywhere in INDEX.md."""
    def run_cr(self, files):
        return run_check(L.check_components_reachable, files)

    def test_hub_linked_from_root_passes(self):
        self.assertEqual(self.run_cr({"INDEX.md": ROOT, "docs/a/README.md": PARENT}), [])

    def test_hub_not_reached_fails(self):
        v = self.run_cr({"INDEX.md": ROOT, "docs/a/README.md": PARENT, "docs/b/README.md": "x"})
        self.assertEqual(len(v), 1, v)
        self.assertIn("docs/b/README", v[0])

    def test_hub_reached_through_a_node_passes(self):
        files = {"INDEX.md": ROOT,
                 "docs/a/README.md": PARENT.replace("[[docs/a/x]]", "[[docs/b/README]]"),
                 "docs/b/README.md": "x"}
        self.assertEqual(self.run_cr(files), [])

    def test_hub_linked_only_below_separator_fails(self):
        v = self.run_cr({"INDEX.md": ROOT + "- [[docs/b/README]]\n",
                         "docs/a/README.md": PARENT, "docs/b/README.md": "x"})
        self.assertEqual(len(v), 1, v)

    def test_framework_dir_hub_not_required(self):
        self.assertEqual(self.run_cr({"INDEX.md": ROOT, "docs/a/README.md": PARENT,
                                      "docs/playbooks/README.md": "x"}), [])

    def test_missing_index_reported(self):
        self.assertEqual(self.run_cr({"docs/a/README.md": "x"}), ["INDEX.md: missing"])

    def test_registered_in_lint(self):
        names = [name for name, _ in L.CHECKS]
        self.assertIn("components-reachable", names)
        self.assertNotIn("index-lists-components", names)


class NonTreeDocsTest(DocsMode, unittest.TestCase):
    def run_nt(self, files):
        return run_check(L.check_non_tree_docs, files)

    def test_kindless_doc_under_docs_fails(self):
        v = self.run_nt({"docs/a/old.md": "---\nlast-verified: 2026-01-01\n---\nold"})
        self.assertEqual(len(v), 1, v)
        self.assertIn("docs/a/old.md", v[0])

    def test_kindless_doc_directly_under_docs_fails(self):
        self.assertEqual(len(self.run_nt({"docs/roadmap.md": "old"})), 1)

    def test_tree_doc_passes(self):
        self.assertEqual(self.run_nt({"docs/a/new.md": leaf(3)}), [])

    def test_allowlisted_reference_docs_pass(self):
        self.assertEqual(self.run_nt({d + ".md": "reference" for d in L.NON_TREE_DOCS}), [])

    def test_allowlist_is_exactly_the_two_reference_docs(self):
        self.assertEqual(L.NON_TREE_DOCS, {"docs/invariants", "docs/agent-toolbox"})

    def test_excluded_dirs_pass(self):
        self.assertEqual(self.run_nt({d + "/x.md": "x" for d in L.NON_TREE_DIRS}), [])

    def test_maps_dir_is_not_excluded(self):
        self.assertEqual(len(self.run_nt({"docs/maps/README.md": "x"})), 1)

    def test_files_outside_docs_pass(self):
        self.assertEqual(self.run_nt({"INDEX.md": "x", "REPOS.md": "x", "other/x.md": "x"}), [])

    def test_root_level_entry_points_pass(self):
        files = {f: "no kind here" for f in ("INDEX.md", "REPOS.md", "README.md", "CLAUDE.md", "AGENTS.md")}
        self.assertEqual(self.run_nt(files), [])

    def test_meta_docs_linked_from_a_root_fact_stay_valid(self):
        """Root fact 7 links docs/meta/client-docs, a kindless doc: no check may flag it."""
        files = {"INDEX.md": root(8).replace("[[docs/a/README]]", "[[docs/meta/client-docs]]"),
                 "docs/meta/client-docs.md": "---\nlast-verified: 2026-10-01\n---\n# Client docs\n",
                 "docs/meta/knowledge-base.md": "see [[docs/meta/client-docs]]"}
        for fn in (L.check_non_tree_docs, L.check_broken_wikilinks, L.check_tree_format,
                   L.check_tree_reachability, L.check_components_reachable, L.check_no_transition_markers):
            self.assertEqual(run_check(fn, files), [], fn.__name__)

    def test_registered_in_lint(self):
        self.assertIn("non-tree-docs", [name for name, _ in L.CHECKS])


class TransitionMarkersTest(DocsMode, unittest.TestCase):
    def run_tm(self, files):
        return run_check(L.check_no_transition_markers, files)

    def test_inline_marker_fails(self):
        v = self.run_tm({"docs/a/leaf.md": "see [[docs/x]] *(not yet in tree format)*"})
        self.assertEqual(len(v), 1, v)
        self.assertIn("docs/a/leaf.md", v[0])

    def test_hub_heading_fails(self):
        self.assertEqual(len(self.run_tm({"docs/a/README.md": "## Not yet in tree format\n"})), 1)

    def test_marker_in_root_and_claude_fails(self):
        self.assertEqual(len(self.run_tm({"INDEX.md": "*(not yet in tree format)*",
                                          "CLAUDE.md": "Not yet in tree format"})), 2)

    def test_lessons_are_history_and_pass(self):
        self.assertEqual(self.run_tm({"docs/lessons/x.md": "*(not yet in tree format)*"}), [])

    def test_marker_in_inline_code_passes(self):
        self.assertEqual(self.run_tm({"docs/meta/kb.md": "the old `*(not yet in tree format)*` marker"}), [])

    def test_clean_file_passes(self):
        self.assertEqual(self.run_tm({"docs/a.md": "nothing here"}), [])

    def test_registered_in_lint(self):
        self.assertIn("no-transition-markers", [name for name, _ in L.CHECKS])


class ModeConfigTest(unittest.TestCase):
    def test_mode_is_docs_or_mono(self):
        self.assertIn(L.MODE, ("docs", "mono"))


class MonoScanScopeTest(MonoMode, unittest.TestCase):
    def test_only_root_md_and_docs_are_scanned(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "INDEX.md", "x")
            write(root, "CHANGELOG.md", "x")
            write(root, "docs/a.md", "x")
            write(root, "apps/api/README.md", "code readme")
            write(root, "node_modules/pkg/README.md", "vendored")
            self.assertEqual(L.find_md_files(root), ["CHANGELOG.md", "INDEX.md", "docs/a.md"])

    def test_any_root_md_is_an_entry_point_not_an_orphan(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "INDEX.md", "x")
            write(root, "CHANGELOG.md", "x")
            write(root, "CONTRIBUTING.md", "x")
            md = L.find_md_files(root); bp, bb = L.build_index(md)
            self.assertEqual(L.check_orphans(root, md, bp, bb), [])


class DocsModeScanScopeTest(DocsMode, unittest.TestCase):
    def test_docs_mode_keeps_scanning_the_whole_repo(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "other/x.md", "x")
            self.assertIn("other/x.md", L.find_md_files(root))


class MonoCodeLineTest(MonoMode, unittest.TestCase):
    def vault(self, code, dirs=("apps/api",), files=("apps/api/main.ts",)):
        with tempfile.TemporaryDirectory() as r:
            for d in dirs:
                os.makedirs(os.path.join(r, d), exist_ok=True)
            for f in files:
                write(r, f, "x")
            for rel, body in {"INDEX.md": ROOT, "docs/a/README.md": PARENT,
                              "docs/a/leaf.md": leaf(3, code=code)}.items():
                write(r, rel, body)
            md = L.find_md_files(r); bp, bb = L.build_index(md)
            return L.check_tree_format(r, md, bp, bb)

    def test_existing_code_dir_passes(self):
        self.assertEqual(self.vault("Code: [api](apps/api)"), [])

    def test_trailing_slash_passes(self):
        self.assertEqual(self.vault("Code: [api](apps/api/)"), [])

    def test_repo_root_dot_passes(self):
        self.assertEqual(self.vault("Code: [repo root](.)"), [])

    def test_several_dirs_pass(self):
        self.assertEqual(self.vault("Code: [api](apps/api), [web](apps/web)",
                                    dirs=("apps/api", "apps/web")), [])

    def test_missing_dir_fails(self):
        v = self.vault("Code: [web](apps/web)")
        self.assertEqual(len(v), 1, v)
        self.assertIn("apps/web", v[0])

    def test_file_path_fails(self):
        v = self.vault("Code: [main](apps/api/main.ts)")
        self.assertEqual(len(v), 1, v)
        self.assertIn("directory", v[0])

    def test_github_url_fails_in_mono(self):
        self.assertEqual(len(self.vault(f"Code: [x]({GH})")), 1)

    def test_path_escaping_the_repo_fails(self):
        self.assertEqual(len(self.vault("Code: [up](../elsewhere)")), 1)

    def test_absolute_path_fails(self):
        self.assertEqual(len(self.vault("Code: [abs](/etc)")), 1)


if __name__ == "__main__":
    unittest.main()
