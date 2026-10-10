#!/usr/bin/env python3
"""Unit tests for the one-line source pointer of a finding: cardlib.source_pointer on provenance
lines of each shape, and render-reports.py reading it from the provenance map of a card's
directory, on a fixture skill in a temporary directory; and the severity layout of the review
report: critical findings beside major ones, their count, and the recommendation each sets.

Run:  python3 -m unittest discover -s maintenance/tests -p 'test_*.py'   (from the skill directory)
"""
import importlib.util
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
sys.path.insert(0, SCRIPTS)
import cardlib  # noqa: E402

spec = importlib.util.spec_from_file_location("render_reports", os.path.join(SCRIPTS, "render-reports.py"))
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

TAIL = " · topic: errors (research/software-craft/errors.md) · formulation: none · reception: not contested · notes: confidence high"
LINES = {
    "ERR-01": ("- **ERR-01** · RFC 9110 §15.5.1 (https://www.rfc-editor.org/rfc/rfc9110#section-15.5.1), fetched — "
               "\"The 400 (Bad Request) status code indicates that the server cannot or will not process the request\"; "
               "CWE-20, fetched — \"The product receives input\"" + TAIL),
    "ERR-02": ("- **ERR-02** · Go project, \"Keeping Your Modules Compatible\" (golang/website _content/blog/module-compatibility.md) "
               "(fetched): \"add, don't change or remove\"" + TAIL),
    "ERR-03": ("- **ERR-03** · Soto, J.; McCall, J., SE-0117 \"Allow distinguishing between public access and public overridability\", "
               "**relayed** — \"a statement\"; Ruff B006" + TAIL),
    "ERR-04": "- **ERR-04** · " + "Python documentation, `Doc/library/" + "x" * 200 + ".rst`, fetched — \"a statement\"" + TAIL,
    "ERR-05": ("- **ERR-05** · SEI CERT Oracle Coding Standard for Java, LCK09-J \"Do not perform operations that can block "
               "while holding a lock\" — **unfetched** (wiki.sei.cmu.edu blocked); SpotBugs SWL_SLEEP_WITH_LOCK_HELD" + TAIL),
}


class SourcePointer(unittest.TestCase):
    def test_the_first_citation_is_cut_before_its_quoted_statement(self):
        self.assertEqual(cardlib.source_pointer(LINES["ERR-01"]),
                         "RFC 9110 §15.5.1 (https://www.rfc-editor.org/rfc/rfc9110#section-15.5.1)")

    def test_a_quoted_title_stays_and_a_statement_after_a_colon_is_cut(self):
        self.assertEqual(cardlib.source_pointer(LINES["ERR-02"]),
                         "Go project, \"Keeping Your Modules Compatible\" (golang/website _content/blog/module-compatibility.md)")

    def test_an_author_list_is_one_citation(self):
        self.assertEqual(cardlib.source_pointer(LINES["ERR-03"]),
                         "Soto, J.; McCall, J., SE-0117 \"Allow distinguishing between public access and public overridability\"")

    def test_a_status_set_off_by_a_dash_ends_the_pointer_and_the_quoted_title_stays(self):
        self.assertEqual(cardlib.source_pointer(LINES["ERR-05"]),
                         "SEI CERT Oracle Coding Standard for Java, LCK09-J \"Do not perform operations that can block while holding a lock\"")

    def test_a_long_citation_is_cut_at_160_characters_with_its_code_span_closed(self):
        pointer = cardlib.source_pointer(LINES["ERR-04"])
        self.assertEqual(len(pointer), 161)
        self.assertTrue(pointer.endswith("x…`"), pointer)

    def test_the_map_path_sits_in_the_maintainer_directory_of_the_skill(self):
        self.assertEqual(cardlib.provenance_map_path("references/craft-cards-python/"),
                         os.path.join("maintenance", "craft-cards-python-provenance.md"))
        self.assertEqual(cardlib.provenance_map_path("/s/skill/references/craft-cards"),
                         os.path.join("/s/skill", "maintenance", "craft-cards-provenance.md"))


class RenderedRuleLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        cards = os.path.join(self.tmp, "references", "craft-cards")
        os.makedirs(cards)
        os.makedirs(os.path.join(self.tmp, "maintenance"))
        with open(os.path.join(self.tmp, "maintenance", "craft-cards-provenance.md"), "w", encoding="utf-8") as handle:
            handle.write("# Craft-cards provenance map\n\n---\n\n## ERR — errors\n\n" + "\n".join(LINES.values()) + "\n")
        self.cards = {rid: {"rule_id": rid, "title": f"Title of {rid}", "path": os.path.join(cards, f"{rid.lower()}--card.md")}
                      for rid in ("ERR-01", "ERR-09")}
        rr.provenance_lines.cache_clear()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def finding(self, rule_id):
        return {"rule_id": rule_id, "id": f"{rule_id}.1", "severity": "major", "file": "app.py", "symbol": "f",
                "code": "raise ValueError()", "problem": "p", "fix": "raise ValueError(text)", "rationale": "r"}

    def test_a_major_finding_carries_the_pointer_of_its_provenance_line(self):
        report, _rejections, _summary = rr.render([self.finding("ERR-01")], {"cards": list(self.cards.values())}, "T", "", "", "")
        self.assertIn("- **Rule**: `ERR-01` — RFC 9110 §15.5.1 (https://www.rfc-editor.org/rfc/rfc9110#section-15.5.1)", report)

    def test_a_card_without_a_provenance_line_shows_its_id_alone(self):
        self.assertEqual(rr.rule_line(self.finding("ERR-09"), self.cards), "`ERR-09`")


class SeverityLayout(unittest.TestCase):
    def logic_finding(self, severity):
        return {"rule_id": "LOGIC", "id": "LOGIC.1", "severity": severity, "file": "app.py", "symbol": "save",
                "code": "store.write(row)", "problem": "the row is written twice", "fix": "store.write_once(row)",
                "rationale": "a retry repeats the write", "verdict": {"verdict": "confirmed", "final_severity": severity}}

    def test_a_confirmed_critical_finding_blocks_and_is_shown_in_full(self):
        report, _rejections, summary = rr.render([self.logic_finding("critical")], {"cards": []}, "T", "", "", "")
        self.assertIn("- Findings: 1 (1 critical, 0 major, 0 minor, 0 suggestion)", report)
        self.assertIn("- Recommendation: Block", summary)
        marks = ["## Critical & Major Findings", "### LOGIC.1: ", "- **Severity**: Critical", "## Minor & Suggestions"]
        positions = [report.index(mark) for mark in marks]
        self.assertEqual(positions, sorted(positions))

    def test_the_gravest_severity_shown_sets_the_recommendation(self):
        expected = {"critical": "Block", "major": "Fix before merge", "minor": "Merge with fixes", "suggestion": "Merge"}
        for severity, recommendation in expected.items():
            with self.subTest(severity=severity):
                report, _rejections, _summary = rr.render([self.logic_finding(severity)], {"cards": []}, "T", "", "", "")
                self.assertIn(f"- Recommendation: {recommendation}", report)


if __name__ == "__main__":
    unittest.main()
