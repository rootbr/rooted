#!/usr/bin/env python3
"""Unit tests for the one-line source pointer of a finding: render-reports.py reads it from the
provenance map beside a card's directory (cardlib.source_pointer), on a fixture map in a
temporary directory.

Run:  python3 -m unittest discover -s scripts/tests -p 'test_*.py'   (from the skill directory)
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("render_reports", os.path.join(SCRIPTS, "render-reports.py"))
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

LINES = [
    "- **CC-01** · `java.util.concurrent` package Javadoc, Java SE 21, \"Memory Consistency Properties\" — \"The results of a "
    "write by one thread are guaranteed to be visible to a read by another thread only if the write operation happens-before "
    "the read operation\" (fetched); jcstress BasicJMM_06_Causality · concurrency §1.1 · formulation: none · notes: high",
    "- **CC-02** · JLS §8.3.1.1 static Fields — \"If a field is declared static, there exists exactly one incarnation of the "
    "field\" — **unfetched** · concurrency §1.2 · formulation: none · notes: moderate",
]


class RenderedRuleLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        cards = os.path.join(self.tmp, "references", "review-cards")
        os.makedirs(cards)
        with open(os.path.join(self.tmp, "references", "review-cards-provenance.md"), "w", encoding="utf-8") as handle:
            handle.write("# Review-cards provenance map\n\n---\n\n## CC — concurrency\n\n" + "\n".join(LINES) + "\n")
        self.cards = {rid: {"rule_id": rid, "title": f"Title of {rid}", "path": os.path.join(cards, f"{rid.lower()}--card.md")}
                      for rid in ("CC-01", "CC-02", "CC-09")}
        rr.provenance_lines.cache_clear()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def finding(self, rule_id):
        return {"rule_id": rule_id, "id": f"{rule_id}.1", "severity": "major", "file": "A.java", "symbol": "A#f",
                "code": "private boolean done;", "problem": "p", "fix": "private volatile boolean done;", "rationale": "r"}

    def test_a_major_finding_carries_the_first_citation_of_its_provenance_line(self):
        report, _rejections, _summary = rr.render([self.finding("CC-01")], {"cards": list(self.cards.values())}, "T", "")
        self.assertIn("- **Rule**: `CC-01` — `java.util.concurrent` package Javadoc, Java SE 21, \"Memory Consistency Properties\"",
                      report)

    def test_the_pointer_stops_before_the_statement_after_a_dash(self):
        self.assertEqual(rr.rule_line(self.finding("CC-02"), self.cards), "`CC-02` — JLS §8.3.1.1 static Fields")

    def test_a_card_without_a_provenance_line_shows_its_id_alone(self):
        self.assertEqual(rr.rule_line(self.finding("CC-09"), self.cards), "`CC-09`")


if __name__ == "__main__":
    unittest.main()
