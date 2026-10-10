#!/usr/bin/env python3
"""Unit tests for craft-cards.py --provenance: the lookup of a card's provenance line in the map
beside each --cards-dir, on a fixture map in a temporary directory.

Run:  python3 -m unittest discover -s scripts/tests -p 'test_*.py'   (from the skill directory)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "craft-cards.py")
UNIVERSAL = "- **ERR-01** · RFC 9110 §15.5.1, fetched — \"a statement\" · topic: errors (research/software-craft/errors.md)"
PYTHON = "- **PY-01** · Ruff B006 mutable-argument-default, fetched — \"a statement\" · topic: idioms (research/x.md)"


class Provenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dirs = []
        for name, line in (("craft-cards", UNIVERSAL), ("craft-cards-python", PYTHON)):
            os.makedirs(os.path.join(self.tmp, name))
            with open(os.path.join(self.tmp, f"{name}-provenance.md"), "w", encoding="utf-8") as handle:
                handle.write(f"# map\n\n---\n\n{line}\n")
            self.dirs += ["--cards-dir", os.path.join(self.tmp, name)]

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, *argv):
        out = subprocess.run([sys.executable, SCRIPT, *argv], capture_output=True, text=True)
        return out.returncode, out.stdout, out.stderr

    def test_each_named_id_prints_its_line_from_the_map_beside_its_cards_directory(self):
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


if __name__ == "__main__":
    unittest.main()
