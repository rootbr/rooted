#!/usr/bin/env python3
"""Unit tests for craft-cards.py: --provenance, the lookup of a card's provenance line in the map
of each --cards-dir (the skill's maintainer directory), and --domain over a domain only a
language card takes, on a fixture skill in a temporary directory.

Run:  python3 -m unittest discover -s maintenance/tests -p 'test_*.py'   (from the skill directory)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts", "craft-cards.py")
UNIVERSAL = "- **ERR-01** · RFC 9110 §15.5.1, fetched — \"a statement\" · topic: errors (research/software-craft/errors.md)"
PYTHON = "- **PY-01** · Ruff B006 mutable-argument-default, fetched — \"a statement\" · topic: idioms (research/x.md)"


class Provenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dirs = []
        os.makedirs(os.path.join(self.tmp, "maintenance"))
        for name, line in (("craft-cards", UNIVERSAL), ("craft-cards-python", PYTHON)):
            os.makedirs(os.path.join(self.tmp, "references", name))
            with open(os.path.join(self.tmp, "maintenance", f"{name}-provenance.md"), "w", encoding="utf-8") as handle:
                handle.write(f"# map\n\n---\n\n{line}\n")
            self.dirs += ["--cards-dir", os.path.join(self.tmp, "references", name)]

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, *argv):
        out = subprocess.run([sys.executable, SCRIPT, *argv], capture_output=True, text=True)
        return out.returncode, out.stdout, out.stderr

    def test_each_named_id_prints_its_line_from_the_map_of_its_cards_directory(self):
        code, out, err = self.run_script(*self.dirs, "--provenance", "PY-01", "--provenance", "ERR-01")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.splitlines(), [PYTHON, UNIVERSAL])

    def test_an_id_no_map_holds_is_named_and_fails(self):
        code, out, err = self.run_script(*self.dirs[:2], "--provenance", "PY-01")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("no provenance line for PY-01 in craft-cards-provenance.md", err)

    def test_a_filter_beside_provenance_is_refused(self):
        code, _out, err = self.run_script(*self.dirs, "--provenance", "ERR-01", "--step", "design")
        self.assertEqual(code, 1)
        self.assertIn("--provenance takes no filter", err)


class DomainFilter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        with open(os.path.join(self.tmp, "java-01--counter.md"), "w", encoding="utf-8") as handle:
            handle.write("---\ntitle: A shared counter changes atomically\nrule_id: JAVA-01\ndomain: concurrency\n"
                         "step: [implement]\napplies_to: [java]\ntriggers: []\nscope: hunk\ncheck_kind: semantic\n"
                         "severity_default: critical\n---\n# A shared counter changes atomically\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_a_language_only_domain_lists_its_cards(self):
        out = subprocess.run([sys.executable, SCRIPT, "--cards-dir", self.tmp, "--domain", "concurrency"],
                             capture_output=True, text=True)
        self.assertEqual((out.returncode, out.stderr), (0, ""))
        self.assertEqual(out.stdout.splitlines()[0].split(" · ")[:2], ["JAVA-01", "A shared counter changes atomically"])


if __name__ == "__main__":
    unittest.main()
