#!/usr/bin/env python3
"""Unit tests for write-topic-result.py: per-prefix numbering of a language corpus whose
cards span several domains, and the card path the research note links.

Run:  python3 -m unittest discover -s scripts/tests -p 'test_*.py'   (from the skill directory)
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("write_topic_result", os.path.join(SCRIPTS, "write-topic-result.py"))
wtr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wtr)


class PythonPrefixNumbering(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for name in ("py-01--an-error-card.md", "py-02--a-test-card.md", "py-03--a-design-card.md", "err-07--universal.md"):
            open(os.path.join(self.tmp, name), "w").close()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_existing_max_counts_the_prefix_across_domains(self):
        self.assertEqual(wtr.existing_max(self.tmp, "PY"), 3)

    def test_existing_max_reads_a_three_digit_id(self):
        open(os.path.join(self.tmp, "py-100--three-digits.md"), "w").close()
        self.assertEqual(wtr.existing_max(self.tmp, "PY"), 100)

    def test_existing_max_of_an_absent_directory_is_zero(self):
        self.assertEqual(wtr.existing_max(os.path.join(self.tmp, "absent"), "PY"), 0)

    def test_renumber_follows_the_id_the_markdown_carries(self):
        card = {"rule_id": "PY-16", "filename": "py-16--x.md",
                "markdown": "---\nrule_id: PY-60\n---\n# t\n(`rule_id: PY-60`)"}
        md, fn = wtr.renumber(card, "PY-16", "PY-70")
        self.assertEqual(md.count("PY-70"), 2)
        self.assertNotIn("PY-60", md)
        self.assertEqual(fn, "py-70--x.md")

    def test_renumber_replaces_the_id_in_markdown_and_filename(self):
        card = {"markdown": "rule_id: PY-90\n\n`rule_id: PY-90`", "filename": "py-90--a-tooling-card.md"}
        md, fn = wtr.renumber(card, "PY-90", "PY-04")
        self.assertEqual(md, "rule_id: PY-04\n\n`rule_id: PY-04`")
        self.assertEqual(fn, "py-04--a-tooling-card.md")


class CardsDerivedTable(unittest.TestCase):
    def test_a_python_card_is_linked_where_it_lies(self):
        result = {"topic": {"slug": "py-errors", "title": "Errors", "group": "G", "domain": "errors", "prefix": "PY"},
                  "spine": {}, "sources": []}
        path = os.path.join(wtr.SKILL, "references", "craft-cards-python", "py-04--a-card.md")
        written = [{"rule_id": "PY-04", "title": "A card", "filename": "py-04--a-card.md", "path": path,
                    "verification": "accepted on the first verdict"}]
        note = wtr.note_markdown(result, "verified", "agents run: 1", written, [])
        self.assertIn("| PY-04 | A card | `references/craft-cards-python/py-04--a-card.md` | accepted on the first verdict |", note)


if __name__ == "__main__":
    unittest.main()
