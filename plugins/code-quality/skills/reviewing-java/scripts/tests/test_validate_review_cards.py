#!/usr/bin/env python3
"""Unit tests for validate-review-cards.py: the body-block check — six blocks pass, a `## Source`
block or any other H2 is an error — and the practitioner-text check over the whole card, on
cards built in a temporary directory.

Run:  python3 -m unittest discover -s scripts/tests -p 'test_*.py'   (from the skill directory)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR = os.path.join(os.path.dirname(HERE), "validate-review-cards.py")


def card_text(tail=""):
    title = "A shared field is volatile, atomic, final or guarded by a lock"
    return f"""---
title: {title}
rule_id: CC-01
domain: concurrency
triggers: ['\\bprivate\\s+boolean\\b']
scope: file
check_kind: semantic
severity_default: major
---

# {title}

## Thesis
A field written by one thread and read by another is volatile, atomic, final or read and written under one lock.

## Rationale
Without a happens-before edge between the write and the read, the reader may observe a stale value.

## Example
```java
bad:  private boolean done;
good: private volatile boolean done;
```

## Limits
A field confined to one thread needs no edge.

## Validator
Open the class and trace each field's writers and readers. Validator question: **Is a field written and read on different threads with no happens-before edge?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-01`, severity major, `file`, `symbol`, `code` = the field, `fix` = the volatile field, `rationale` = the missing edge).
{tail}"""


class ValidateBodyBlocks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_on(self, tail=""):
        with open(os.path.join(self.tmp, "cc-01--shared-field.md"), "w", encoding="utf-8") as fh:
            fh.write(card_text(tail))
        out = subprocess.run([sys.executable, VALIDATOR, self.tmp], capture_output=True, text=True)
        return out.returncode, out.stdout + out.stderr

    def test_six_blocks_pass(self):
        rc, out = self.run_on()
        self.assertEqual(rc, 0, out)
        self.assertIn(", 0 error(s)", out)

    def test_a_source_block_fails(self):
        rc, out = self.run_on("\n## Source\n- JLS §17.4.5 happens-before order\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("error: a `## Source` block is present; a card carries no citation", out)
        self.assertIn(", 1 error(s)", out)

    def test_another_h2_fails(self):
        rc, out = self.run_on("\n## Notes\nA maintainer note.\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("error: H2 ['Notes'] outside the body blocks", out)

    def test_a_practitioner_text_outside_the_six_blocks_fails(self):
        rc, out = self.run_on("\n## Source\n- Java Concurrency in Practice, chapter 3\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("error: attribution 'Java Concurrency in Practice' in the card", out)


if __name__ == "__main__":
    unittest.main()
