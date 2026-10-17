#!/usr/bin/env python3
"""Unit tests for brief-gate.py: a brief in the shape SKILL.md §Phase 3 states passes; each
shape defect — a section missing, repeated, out of order or empty, a solution without a
`path:Symbol` anchor, a missing or malformed `### Decisions`, a step without its kind or its
file, a failure path over several lines, a test entry without a location, a task without a
write-zone path, a stack fact without a named file — is reported on one line; the JSON
output and the exit statuses, through the script as a subprocess.

Run:  python3 -m unittest discover -s maintenance/tests -p 'test_*.py'   (from the skill directory)
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
GATE = os.path.join(SCRIPTS, "brief-gate.py")
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location("brief_gate", GATE)
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)

BRIEF = """# Design brief

## Task
Add a token-bucket rate limiter to the public API. Write zone: `src/api/limits.py`, `tests/test_limits.py`.

## Stack
- pytest with plain asserts (`tests/test_orders.py`); ruff and mypy --strict from `pyproject.toml`.
- Errors are raised as subclasses of `ApiError` (`src/api/errors.py`).

## Design
- `src/api/limits.py:TokenBucket` — holds the tokens of one client and refills them by the clock it is given; hides the refill arithmetic.
  Operations: `try_acquire(n: int) -> bool`, n >= 1; `tokens_at(now: float) -> float`.
- Data flow: the middleware calls `try_acquire` once per request.
- Invariant: the token count never exceeds the capacity.

### Decisions
1. Where the clock comes from — chosen: the constructor takes a `clock` callable, because the tests of `tests/test_orders.py` inject time the same way; alternative: reading `time.monotonic()` inside the bucket — blocked by the test suite, which runs with no sleep.

## Failure paths
- `n < 1` raises `ValueError` naming n.
- A clock that goes backwards keeps the last reading and refills nothing.

## Tests
- `tests/test_limits.py::test_refill_after_interval` — a bucket emptied at t refills at t + interval.
- `tests/test_limits.py::test_rejects_zero` — `try_acquire(0)` raises.

## Steps
1. implement — `src/api/limits.py`: the `TokenBucket` type with `try_acquire` and `tokens_at`.
2. handle-errors — `src/api/limits.py`: the two failure paths.
3. test — `tests/test_limits.py`: the two behaviours above.

## Out of scope
none
"""


def section(title):
    """The text of one `##` section of BRIEF, heading included."""
    start = BRIEF.index("## " + title)
    end = BRIEF.find("\n## ", start + 1)
    return BRIEF[start:] if end == -1 else BRIEF[start:end + 1]


def replaced(title, body):
    return BRIEF.replace(section(title), "## %s\n%s\n\n" % (title, body))


def messages(text):
    return [message for _, message in bg.defects(text)]


class Shape(unittest.TestCase):
    def test_a_brief_in_the_contract_shape_has_no_defect(self):
        self.assertEqual(bg.defects(BRIEF), [])

    def test_a_missing_section_is_named(self):
        text = BRIEF.replace(section("Tests"), "")
        self.assertIn("section `## Tests` is missing", messages(text))

    def test_a_section_outside_the_seven_is_named(self):
        text = BRIEF + "\n## Notes\nsome\n"
        self.assertIn("section `## Notes` is not one of the seven", messages(text))

    def test_sections_out_of_order_are_reported(self):
        text = BRIEF.replace(section("Steps"), "").replace("## Tests", section("Steps") + "## Tests")
        self.assertTrue(any(m.startswith("sections are out of order") for m in messages(text)), messages(text))

    def test_a_repeated_section_is_counted(self):
        text = BRIEF + "\n" + section("Tests")
        self.assertIn("section `## Tests` appears 2 times", messages(text))

    def test_an_empty_section_is_reported_and_none_is_accepted(self):
        self.assertIn("the section is empty; an empty one says none", messages(replaced("Failure paths", "")))
        self.assertEqual(messages(replaced("Failure paths", "none")), [])

    def test_a_fenced_heading_is_not_a_section(self):
        text = replaced("Stack", "```\n## Not a section\n```\nruff from `pyproject.toml`.")
        self.assertEqual(messages(text), [])


class Sections(unittest.TestCase):
    def test_a_task_without_a_write_zone_path_is_reported(self):
        self.assertIn("no write-zone path is named", messages(replaced("Task", "Add a limiter.")))

    def test_a_stack_without_a_named_file_is_reported(self):
        self.assertIn("no fact is read from a named file", messages(replaced("Stack", "pytest and ruff.")))

    def test_a_design_without_an_anchor_is_reported(self):
        text = replaced("Design", "A bucket type.\n\n### Decisions\nnone")
        self.assertIn("no module or type is anchored by `path:Symbol`", messages(text))

    def test_a_design_without_decisions_is_reported(self):
        text = replaced("Design", "- `src/api/limits.py:TokenBucket` — the bucket.")
        self.assertIn("`### Decisions` is missing", messages(text))

    def test_decisions_may_say_none(self):
        text = replaced("Design", "- `src/api/limits.py:TokenBucket` — the bucket.\n\n### Decisions\nnone")
        self.assertEqual(messages(text), [])

    def test_a_decision_without_its_two_parts_is_reported(self):
        text = replaced("Design", "- `src/api/limits.py:TokenBucket` — the bucket.\n\n### Decisions\n"
                                  "1. the clock — chosen: injected, because the tests inject time.\n"
                                  "2. the store — in memory.")
        self.assertEqual([m for m in messages(text) if m.startswith("decision")],
                         ["decision 1 lacks alternative:", "decision 2 lacks chosen: and alternative:"])

    def test_decisions_that_are_not_items_are_reported(self):
        text = replaced("Design", "- `src/api/limits.py:TokenBucket` — the bucket.\n\n### Decisions\nthe clock is injected")
        self.assertIn("`### Decisions` holds text that is not a numbered item", messages(text))

    def test_a_subsection_after_decisions_is_reported(self):
        text = replaced("Design", "- `src/api/limits.py:TokenBucket` — the bucket.\n\n### Decisions\nnone\n\n### Flow\nmore")
        self.assertIn("`### Flow` sits after `### Decisions`", messages(text))

    def test_a_failure_path_over_several_lines_is_reported(self):
        text = replaced("Failure paths", "- `n < 1` raises `ValueError`\n  naming n.\n- a second path, one line.")
        self.assertEqual(messages(text), ["path 1 spans 2 lines"])

    def test_a_test_entry_without_a_location_is_reported(self):
        text = replaced("Tests", "- a bucket refills.\n- `tests/test_limits.py::test_rejects_zero` — rejects zero.")
        self.assertEqual(messages(text), ["entry 1 names no test location"])

    def test_a_step_without_a_kind_or_a_file_is_reported(self):
        text = replaced("Steps", "1. write the bucket in `src/api/limits.py`.\n2. test — the behaviours.")
        self.assertEqual(messages(text), ["step 1 names no kind (implement, handle-errors, test, refactor, document)",
                                          "step 2 names no file"])

    def test_a_step_may_run_over_several_lines(self):
        text = replaced("Steps", "1. implement —\n   `src/api/limits.py`: the type.")
        self.assertEqual(messages(text), [])

    def test_steps_that_are_bullets_are_reported(self):
        text = replaced("Steps", "- implement — `src/api/limits.py`: the type.")
        self.assertEqual(messages(text), ["the steps are not numbered items"])

    def test_an_empty_steps_section_is_reported(self):
        self.assertEqual(messages(replaced("Steps", "none")), ["no step is listed"])

    def test_the_kind_is_a_whole_word(self):
        text = replaced("Steps", "1. the tests of `tests/test_limits.py`.")
        self.assertEqual(messages(text), ["step 1 names no kind (implement, handle-errors, test, refactor, document)"])


class Script(unittest.TestCase):
    def run_gate(self, text, *flags):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "design.md")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            return subprocess.run([sys.executable, GATE, path, *flags], capture_output=True, text=True), path

    def test_a_passing_brief_exits_zero_and_prints_nothing(self):
        result, _ = self.run_gate(BRIEF)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_a_failing_brief_exits_one_with_one_line_per_defect(self):
        result, path = self.run_gate(replaced("Steps", "none"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "%s: Steps: no step is listed\n" % path)

    def test_json_output_carries_the_defects(self):
        result, path = self.run_gate(replaced("Steps", "none"), "--json")
        self.assertEqual(json.loads(result.stdout),
                         {"path": path, "defects": [{"section": "Steps", "message": "no step is listed"}]})

    def test_a_missing_file_exits_two(self):
        result = subprocess.run([sys.executable, GATE, "/nonexistent/design.md"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)


if __name__ == "__main__":
    unittest.main()
