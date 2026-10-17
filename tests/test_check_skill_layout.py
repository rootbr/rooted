#!/usr/bin/env python3
"""Unit tests for check-skill-layout.py: one passing and one failing temporary skill tree per rule
(a to g), the exemption list, and the command line.

Run:  python3 -m unittest discover -s tests -p 'test_*.py'   (from the repository root)
"""
import contextlib
import importlib.util
import io
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("check_skill_layout", os.path.join(ROOT, "check-skill-layout.py"))
csl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(csl)

SKILL = "plugins/p/skills/s/"


class Tree(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.write(SKILL + "SKILL.md", "---\nname: s\n---\n\n# S\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, path, text):
        full = os.path.join(self.tmp, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def corpus(self, name):
        """A card corpus with its provenance map, the maintainer README and the layout table."""
        self.write(SKILL + f"maintenance/{name}-provenance.md", "")
        self.write(SKILL + "maintenance/README.md", "# M\n")
        self.write(SKILL + "README.md", "## Layout\n")

    def violations(self, sync_pairs=()):
        return csl.scan(self.tmp, sync_pairs=sync_pairs)

    def rules(self, **kwargs):
        return [line.split(": ")[1] for line in self.violations(**kwargs)]


class RuleA(Tree):
    def test_one_pointer_line_in_skill_md_passes(self):
        self.write(SKILL + "SKILL.md", "# S\n\n## Maintenance\n\n`maintenance/README.md` names what changes together.\n")
        self.assertEqual(self.violations(), [])

    def test_a_maintainer_path_in_a_reference_fails(self):
        self.write(SKILL + "references/guide.md", "Run `maintenance/scripts/validate.py` first.\n")
        self.assertEqual(self.violations(), [f"{SKILL}references/guide.md:1: a: a run-set file names \"maintenance/\""])

    def test_an_evals_path_in_skill_md_fails_and_a_second_pointer_line_fails(self):
        self.write(SKILL + "SKILL.md", "`maintenance/README.md`\nsee `evals/evals.json`\n`maintenance/README.md` again\n")
        self.assertEqual(self.violations(), [f"{SKILL}SKILL.md:2: a: a run-set file names \"evals/\"",
                                             f"{SKILL}SKILL.md:3: a: SKILL.md names \"maintenance/README.md\" on more than one line (lines 1, 3)"])

    def test_the_pointer_line_carries_no_other_maintainer_path(self):
        self.write(SKILL + "SKILL.md", "`maintenance/README.md` and `maintenance/map.md`\n")
        self.assertEqual(self.rules(), ["a"])

    def test_a_plugin_agent_naming_a_maintainer_path_fails(self):
        self.write("plugins/p/agents/dev.md", "Read `evals/grade.py`.\n")
        self.assertEqual(self.violations(), ["plugins/p/agents/dev.md:1: a: a run-set file names \"evals/\""])

    def test_the_maintainer_set_and_the_readme_may_name_each_other(self):
        self.write(SKILL + "maintenance/README.md", "`evals/evals.json` and `maintenance/map.md`\n")
        self.write(SKILL + "README.md", "## Layout\n\n`maintenance/README.md`\n")
        self.assertEqual(self.violations(), [])


class RuleB(Tree):
    def test_run_files_with_run_names_pass(self):
        self.write(SKILL + "scripts/render-reports.py", "")
        self.write(SKILL + "references/report-format.md", "")
        self.write(SKILL + "references/rule-cards/r-57--provenance-out-of-runtime.md", "")
        self.corpus("rule-cards")
        self.assertEqual(self.violations(), [])

    def test_a_maintainer_name_under_references_or_scripts_fails(self):
        self.write(SKILL + "references/corpus-taxonomy.md", "")
        self.write(SKILL + "scripts/validate-cards.py", "")
        self.assertEqual(self.violations(), [f"{SKILL}references/corpus-taxonomy.md: b: a maintainer file under references/",
                                             f"{SKILL}scripts/validate-cards.py: b: a maintainer file under scripts/"])

    def test_a_tests_directory_under_scripts_fails(self):
        tests_dir = os.path.join(SKILL + "scripts", "tests")
        self.write(os.path.join(tests_dir, "test_x.py"), "")
        self.assertEqual(self.violations(), [f"{tests_dir}/: b: a tests directory under scripts/"])


class RuleC(Tree):
    def test_a_run_file_without_the_phrases_passes(self):
        self.write(SKILL + "scripts/run.py", '"""Render the reports."""\n')
        self.assertEqual(self.violations(), [])

    def test_an_authoring_phrase_in_a_run_file_fails(self):
        self.write(SKILL + "scripts/run.py", '"""Harvest. Authoring time only; never part of a build or a review."""\n')
        self.assertEqual(self.rules(), ["c", "c"])


class RuleD(Tree):
    def readme(self):
        self.write(SKILL + "maintenance/README.md", "# M\n")
        self.write(SKILL + "README.md", "## Layout\n")

    def test_a_corpus_with_its_provenance_map_passes(self):
        self.readme()
        self.write(SKILL + "references/review-cards/cc-01--x.md", "")
        self.write(SKILL + "maintenance/review-cards-provenance.md", "")
        self.assertEqual(self.violations(), [])

    def test_a_corpus_without_its_provenance_map_fails(self):
        self.readme()
        self.write(SKILL + "references/craft-cards-python/py-01--x.md", "")
        self.assertEqual(self.violations(),
                         [f"{SKILL}maintenance/craft-cards-python-provenance.md: d: the provenance map of references/craft-cards-python/ is missing"])


class RuleE(Tree):
    def test_a_maintenance_directory_with_both_readmes_passes(self):
        self.write(SKILL + "maintenance/README.md", "# M\n")
        self.write(SKILL + "README.md", "# S\n\n## Layout\n\n| Path | Who | When |\n")
        self.assertEqual(self.violations(), [])

    def test_a_maintenance_directory_without_its_readme_or_layout_fails(self):
        self.write(SKILL + "maintenance/map.md", "")
        self.write(SKILL + "README.md", "# S\n\n### Layout\n")
        self.assertEqual(self.violations(), [f"{SKILL}maintenance/README.md: e: missing",
                                             f"{SKILL}README.md: e: no \"## Layout\" heading"])


class RuleF(Tree):
    PAIR = (("plugins/p/skills/s/references/spec.md", "plugins/p/skills/t/references/spec.md"),)

    def test_identical_copies_pass(self):
        self.write(self.PAIR[0][0], "spec\n")
        self.write(self.PAIR[0][1], "spec\n")
        self.assertEqual(self.violations(sync_pairs=self.PAIR), [])

    def test_a_drifted_or_missing_copy_fails(self):
        self.write(self.PAIR[0][0], "spec\n")
        self.write(self.PAIR[0][1], "spec, edited\n")
        self.assertEqual(self.rules(sync_pairs=self.PAIR), ["f"])
        os.remove(os.path.join(self.tmp, self.PAIR[0][1]))
        self.assertEqual(self.rules(sync_pairs=self.PAIR), ["f"])


class RuleG(Tree):
    def test_prose_without_provenance_notes_passes(self):
        self.write(SKILL + "references/rules.md",
                   "4. Does the answer change our work? (rule 14) The tag `[eval list E1]` sits in code.\n"
                   "Morphological analysis (Zwicky), a footnote[^1], a tag [cs.CR] and `https://api.example.org/v1` as code.\n"
                   "```\n[Rao 2018, arXiv:1805.04655] (fetched) https://example.org\n```\n"
                   "The bundling tax: a duplicated rule takes two attention slots (R-43).\n")
        self.assertEqual(self.violations(), [])

    def test_a_citation_bracket_an_eval_tag_and_a_fetch_marker_fail(self):
        self.write(SKILL + "references/rules.md",
                   "4. Does the answer change our work? [Rao 2018, arXiv:1805.04655; the rest untested]\n"
                   "5. Research first. [Kahneman 2011; Tversky 1974]\n"
                   "6. Decide by default. eval client-question-list E3 covers it.\n"
                   "The abstract was read (fetched); the full text is **unfetched**.\n")
        self.assertEqual(self.violations(), [
            f"{SKILL}references/rules.md:1: g: a source locator in a run-set file: arXiv:1805.04655",
            f"{SKILL}references/rules.md:1: g: a citation bracket in a run-set file: [Rao 2018, arXiv:1805.04655; the rest untested]",
            f"{SKILL}references/rules.md:2: g: a citation bracket in a run-set file: [Kahneman 2011; Tversky 1974]",
            f"{SKILL}references/rules.md:3: g: an eval expectation tag in a run-set file",
            f"{SKILL}references/rules.md:4: g: a fetch marker in a run-set file"])

    def test_a_locator_in_prose_fails_and_a_locator_in_code_passes(self):
        self.write(SKILL + "references/gotchas.md",
                   "G-01. Routers use full text; the gap is 31.8pp (SkillRouter 2603.22455 App. D).\n"
                   "G-02. See doi:10.1145/1028664.1028765 and https://example.org/paper.\n"
                   "Fetch `https://api.example.org/v1` and read Yang 2505 §3.\n")
        self.assertEqual(self.violations(), [
            f"{SKILL}references/gotchas.md:1: g: a source locator in a run-set file: 2603.22455",
            f"{SKILL}references/gotchas.md:2: g: a source locator in a run-set file: doi:10."])

    def test_a_script_and_the_maintainer_set_are_not_scanned(self):
        self.write(SKILL + "scripts/grade.py", 'TAG = "[Rao 2018, arXiv:1805.04655]"  # (fetched)\n')
        self.write(SKILL + "maintenance/rules-provenance.md", "- **R-1** · Rao 2018, arXiv:1805.04655 (fetched) · eval list E1\n")
        self.write(SKILL + "maintenance/README.md", "# M\n")
        self.write(SKILL + "README.md", "## Layout\n")
        self.assertEqual(self.violations(), [])


class CommandLine(Tree):
    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = csl.main(["--root", self.tmp, *argv])
        return code, out.getvalue()

    def test_the_table_lists_each_skill_by_set_and_a_violation_exits_1(self):
        original = csl.SYNC_PAIRS
        csl.SYNC_PAIRS = ()
        try:
            self.write(SKILL + "evals/evals.json", "{}")
            code, out = self.run_main("--table")
            self.assertEqual((code, out), (0, f"{SKILL.rstrip('/')}\n  run         SKILL.md\n  maintainer  evals/ 1 file\n"))
            self.write(SKILL + "references/x.md", "see evals/evals.json\n")
            code, out = self.run_main()
            self.assertEqual(code, 1)
            self.assertIn(": a: ", out)
        finally:
            csl.SYNC_PAIRS = original


if __name__ == "__main__":
    unittest.main()
