#!/usr/bin/env python3
"""Unit tests for validate-craft-cards.py: the language-corpus mode (--language python)
against the universal mode, and the body-block check of both modes — six blocks, no `## Source`,
no other H2 — with the practitioner-text check over the whole card, on cards built in a
temporary directory.

Run:  python3 -m unittest discover -s scripts/tests -p 'test_*.py'   (from the skill directory)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR = os.path.join(os.path.dirname(HERE), "validate-craft-cards.py")

UNIVERSAL_THESIS = "An error names the operation that failed and the values that caused it."
PYTHON_EXAMPLE = """bad:  def parse_port(text):
          raise ValueError("invalid input")
good: def parse_port(text):
          raise ValueError(f"parse port: {text!r} is not a number")"""


CARD_DEFAULTS = {"domain": "errors", "applies_to": "[python]", "fence": "python", "thesis": UNIVERSAL_THESIS,
                 "limits": "A predeclared sentinel compared by identity carries no operand.", "tail": ""}


def card_text(rule_id, **overrides):
    """A card valid in the python corpus; each override replaces one of CARD_DEFAULTS."""
    fields = {**CARD_DEFAULTS, **overrides}
    domain, applies_to, fence = fields["domain"], fields["applies_to"], fields["fence"]
    thesis, limits, tail = fields["thesis"], fields["limits"], fields["tail"]
    title = f"An error names the failed operation and its values {rule_id.lower()}"
    return f"""---
title: {title}
rule_id: {rule_id}
domain: {domain}
step: [implement, handle-errors]
applies_to: {applies_to}
triggers: ['\\braise\\b']
scope: hunk
check_kind: semantic
severity_default: minor
---

# {title}

## Thesis
{thesis}

## Rationale
An error is read after the frame that held the operands is gone, so its message is the only record of them.

## Example
```{fence}
{PYTHON_EXAMPLE}
```

## Limits
{limits}

## Validator
Grep the added lines for a raise. Validator question: **Does the raised error leave out the operand the site holds?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: {rule_id}`, severity minor, `file`, `symbol`, `code` = the raise, `fix` = the raise with the operand, `rationale` = the missing operand).
{tail}"""


class CardDirectory(unittest.TestCase):
    """A temporary cards directory and the validator run over it."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, rule_id, **kw):
        prefix, num = rule_id.split("-")
        path = os.path.join(self.tmp, f"{prefix.lower()}-{num}--card-{num}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(card_text(rule_id, **kw))
        return path

    def run_validator(self, *flags):
        out = subprocess.run([sys.executable, VALIDATOR, *flags, self.tmp], capture_output=True, text=True)
        return out.returncode, out.stdout + out.stderr

    def assert_passes(self, *flags):
        rc, out = self.run_validator(*flags)
        self.assertEqual(rc, 0, out)
        self.assertIn(", 0 error(s)", out)

    def assert_fails_with(self, fragment, *flags):
        rc, out = self.run_validator(*flags)
        self.assertEqual(rc, 1, out)
        self.assertIn(fragment, out)


class ValidateLanguageCorpus(CardDirectory):
    def test_python_card_of_a_non_code_domain_passes_with_language(self):
        self.write("PY-01", domain="errors")
        self.write("PY-02", domain="tests")
        self.assert_passes("--language", "python")

    def test_three_digit_id_passes_once_a_prefix_passes_99_cards(self):
        self.write("PY-99")
        self.write("PY-100")
        self.assert_passes("--language", "python")

    def test_four_digit_id_fails(self):
        self.write("PY-1000")
        self.assert_fails_with("is not <PREFIX>-NN", "--language", "python")

    def test_java_fence_fails_with_language(self):
        self.write("PY-01", fence="java")
        self.assert_fails_with("Example fence must be tagged python in the python corpus, found ```java", "--language", "python")

    def test_python_in_thesis_passes_with_language(self):
        self.write("PY-01", thesis="A Python error names the operation that failed and the values that caused it.")
        self.assert_passes("--language", "python")

    def test_java_in_thesis_fails_with_language(self):
        self.write("PY-01", thesis="A Java error names the operation that failed and the values that caused it.")
        self.assert_fails_with("Thesis names a language ('Java'); the python corpus names no other language", "--language", "python")

    def test_applies_to_without_the_language_first_fails(self):
        self.write("PY-01", applies_to="[universal]")
        self.assert_fails_with("must begin with 'python' in the python corpus", "--language", "python")

    def test_python_card_without_language_fails(self):
        self.write("PY-01")
        self.assert_fails_with("rule_id prefix PY belongs to the python corpus; the universal corpus takes no language card")

    def test_universal_card_passes_without_language(self):
        self.write("ERR-01", applies_to="[universal]")
        self.assert_passes()

    def test_universal_card_fails_with_language(self):
        self.write("ERR-01", applies_to="[python]")
        self.assert_fails_with("rule_id prefix ERR is a universal prefix; a python card takes PY", "--language", "python")

    def test_sibling_ids_are_caught_in_a_python_card(self):
        self.write("PY-01", limits="PY-02 and ERR-03 own the neighbouring cases.")
        self.assert_fails_with("names sibling rule id(s) ['ERR-03', 'PY-02']", "--language", "python")

    def test_example_language_distribution_is_not_reported_with_language(self):
        for n in range(1, 11):
            self.write(f"PY-{n:02d}")
        rc, out = self.run_validator("--language", "python")
        self.assertEqual(rc, 0, out)
        self.assertIn(", 0 warning(s)", out)
        self.assertNotIn("the floor is a tenth", out)

    def test_unknown_language_is_refused(self):
        self.write("PY-01")
        rc, out = self.run_validator("--language", "cobol")
        self.assertNotEqual(rc, 0)
        self.assertIn("--language 'cobol' names no language corpus (known: python)", out)


class ValidateBodyBlocks(CardDirectory):
    """The body is the six blocks: a `## Source` block or any other H2 is an error in both modes, and a
    practitioner text is an error anywhere in the card."""

    def test_six_blocks_pass_in_both_modes(self):
        self.write("PY-01")
        self.assert_passes("--language", "python")
        shutil.rmtree(self.tmp)
        os.makedirs(self.tmp)
        self.write("ERR-01", applies_to="[universal]")
        self.assert_passes()

    def test_a_source_block_fails_in_both_modes(self):
        tail = "\n## Source\n- DOI 10.1109/SBES.2014.19, §Results\n"
        self.write("PY-01", tail=tail)
        self.assert_fails_with("error: a `## Source` block is present; a card carries no citation", "--language", "python")
        shutil.rmtree(self.tmp)
        os.makedirs(self.tmp)
        self.write("ERR-01", applies_to="[universal]", tail=tail)
        self.assert_fails_with("error: a `## Source` block is present; a card carries no citation")

    def test_another_h2_fails(self):
        self.write("ERR-01", applies_to="[universal]", tail="\n## Notes\nA maintainer note.\n")
        self.assert_fails_with("error: H2 ['Notes'] outside the body blocks")

    def test_a_practitioner_text_outside_the_six_blocks_fails(self):
        self.write("ERR-01", applies_to="[universal]", tail="\n## Source\n- Clean Code, chapter 7\n")
        self.assert_fails_with("error: attribution 'Clean Code' in the card")


if __name__ == "__main__":
    unittest.main()
