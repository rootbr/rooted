"""grade_cold_read.py: caught, not separated, missed, false alarm and unusable runs of the cold-read measurement."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

EVALS = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS))
import grade_cold_read as gcr  # noqa: E402


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


INTACT = """The task was to add a retry to the payment call. Two of three tests pass.
The gateway may already have charged a payment that timed out.
You decide whether the retry stays on for payments. Keep it?
"""
NO_DECISION = """The task was to add a retry to the payment call. Two of three tests pass.
The gateway may already have charged a payment that timed out.
"""
Q1, Q2, Q3 = "What was the task?", "How did it end?", "What do I have to decide?"
TASK = "The task was to add a retry to the payment call."
END = "Two of three tests pass."
GATEWAY = "The gateway may already have charged a payment that timed out."
DECIDE = "You decide whether the retry stays on for payments."


def answer(question, quote, found="yes", missing=""):
    return {"question": question, "found": found, "answer": "an answer", "quotes": [quote] if quote else [], "missing": missing}


def no(question, missing):
    return answer(question, "", found="no", missing=missing)


ALL = [answer(Q1, TASK), answer(Q2, END), answer(Q3, DECIDE)]
# Every question answered from sentences that stand in the variant without the decision.
ALL_IN_VARIANT = [answer(Q1, TASK), answer(Q2, END), answer(Q3, TASK)]
DECISION_MISSING = [answer(Q1, TASK), answer(Q2, END), no(Q3, "what the reader decides")]
GATEWAY_TERM = {"term": "the gateway", "quote": GATEWAY}


class Grading(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        fixtures = self.root / "fixtures"
        fixtures.mkdir()
        (fixtures / "intact.md").write_text(INTACT, encoding="utf-8")
        (fixtures / "no-decision.md").write_text(NO_DECISION, encoding="utf-8")
        (fixtures / "questions.json").write_text(json.dumps({"questions": [Q1, Q2, Q3]}), encoding="utf-8")
        self.plants = fixtures / "plants.json"
        self.write_plants({"question": 3, "terms": ["GATEWAY", "charge"]})
        self.runs = self.root / "runs"
        self.runs.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_plants(self, expect, cases=("retry",)):
        variant = {"variant": "no-decision", "report": "no-decision.md", "removed": "the decision"}
        if expect is not None:
            variant["expect"] = expect
        self.plants.write_text(json.dumps({"cases": [
            {"case": c, "report_intact": "intact.md", "questions": "questions.json", "variants": [variant]} for c in cases
        ]}), encoding="utf-8")

    def cold(self, run, answers, unexplained=()):
        (self.runs / run).mkdir()
        (self.runs / run / "cold.json").write_text(json.dumps({"answers": answers, "unexplained": list(unexplained)}), encoding="utf-8")

    def grade(self):
        return subprocess.run([sys.executable, "-I", str(EVALS / "grade_cold_read.py"), str(self.plants), str(self.runs)],
                              capture_output=True, text=True, encoding="utf-8")

    def graded(self):
        done = self.grade()
        self.assertEqual(done.returncode, 0, done.stderr)
        grading = json.loads((self.runs / "grading.json").read_text(encoding="utf-8"))
        return {r["run"]: r for r in grading["runs"]}, grading, done.stdout.splitlines()

    def test_caught_by_the_question_signal(self):
        self.cold("retry--intact", ALL)
        self.cold("retry--no-decision", DECISION_MISSING)
        runs, _, lines = self.graded()
        self.assertEqual((runs["retry--intact"]["outcome"], runs["retry--no-decision"]["outcome"]), (gcr.CLEAN, gcr.CAUGHT))
        self.assertEqual(runs["retry--no-decision"]["signal"], "question 3")
        self.assertIn("retry--no-decision: caught: question 3: missing", lines)

    def test_caught_by_the_terms_signal(self):
        self.write_plants({"terms": ["charge"]})
        self.cold("retry--intact", ALL)
        self.cold("retry--no-decision", ALL_IN_VARIANT, unexplained=[{"term": "charged", "quote": GATEWAY}])
        runs, _, lines = self.graded()
        self.assertEqual(runs["retry--intact"]["outcome"], gcr.CLEAN)
        self.assertEqual((runs["retry--no-decision"]["outcome"], runs["retry--no-decision"]["signal"]), (gcr.CAUGHT, gcr.TERMS))
        self.assertIn("retry--no-decision: caught: terms: 'charge' in the kept term 'charged'", lines)

    def test_terms_signal_fires_on_the_quote_of_a_kept_term(self):
        self.write_plants({"terms": ["charge"]})
        self.cold("retry--intact", ALL)
        self.cold("retry--no-decision", ALL_IN_VARIANT, unexplained=[{"term": "the timed-out payment", "quote": GATEWAY}])
        runs, _, _ = self.graded()
        self.assertEqual(runs["retry--no-decision"]["outcome"], gcr.CAUGHT)
        self.assertEqual(runs["retry--no-decision"]["detail"], "'charge' in the quote of the kept term 'the timed-out payment'")

    def test_signal_that_fires_in_both_runs_is_not_separated(self):
        self.write_plants({"terms": ["gateway"]})
        self.cold("retry--intact", ALL, unexplained=[GATEWAY_TERM])
        self.cold("retry--no-decision", ALL_IN_VARIANT, unexplained=[GATEWAY_TERM])
        runs, _, lines = self.graded()
        record = runs["retry--no-decision"]
        self.assertEqual((record["outcome"], record["signal"]), (gcr.NOT_SEPARATED, gcr.TERMS))
        self.assertIn("in the intact run too", record["detail"])
        self.assertTrue(any(line.startswith("retry--no-decision: not separated: terms: ") for line in lines), lines)
        # A kept term alone makes no false alarm: unexplained terms are advisory.
        self.assertEqual((runs["retry--intact"]["outcome"], runs["retry--intact"]["exit"]), (gcr.CLEAN, 0))

    def test_question_signal_in_both_runs_is_not_separated_and_the_intact_is_a_false_alarm(self):
        self.write_plants({"question": 3})
        self.cold("retry--intact", DECISION_MISSING)
        self.cold("retry--no-decision", DECISION_MISSING)
        runs, _, lines = self.graded()
        self.assertEqual(runs["retry--no-decision"]["outcome"], gcr.NOT_SEPARATED)
        self.assertEqual(runs["retry--intact"]["outcome"], gcr.FALSE_ALARM)
        self.assertIn("retry--intact: false alarm: question 3: missing: what the reader decides", lines)

    def test_one_separated_signal_suffices(self):
        """The terms signal fires in both runs, the question signal only in the variant's."""
        self.cold("retry--intact", ALL, unexplained=[GATEWAY_TERM])
        self.cold("retry--no-decision", DECISION_MISSING, unexplained=[GATEWAY_TERM])
        runs, _, _ = self.graded()
        self.assertEqual((runs["retry--no-decision"]["outcome"], runs["retry--no-decision"]["signal"]), (gcr.CAUGHT, "question 3"))

    def test_missed_when_no_signal_fires(self):
        self.cold("retry--intact", ALL)
        self.cold("retry--no-decision", [answer(Q1, TASK), no(Q2, "how it ended"), answer(Q3, TASK)],
                  unexplained=[{"term": "retry", "quote": TASK}])
        runs, _, lines = self.graded()
        self.assertEqual(runs["retry--no-decision"]["outcome"], gcr.MISSED)
        self.assertIsNone(runs["retry--no-decision"]["signal"])
        self.assertTrue(any(line.startswith("retry--no-decision: missed: no signal") for line in lines), lines)

    def test_unusable_when_its_own_or_the_intact_run_is_absent_or_exits_2(self):
        self.write_plants({"question": 3}, cases=("retry", "rename", "build"))
        self.cold("retry--no-decision", DECISION_MISSING)          # intact absent
        self.cold("rename--intact", ALL)                            # variant absent
        self.cold("build--intact", ALL)
        self.cold("build--no-decision", ALL[:2])                    # exits 2: question 3 without an answer
        runs, grading, _ = self.graded()
        self.assertEqual({k: r["outcome"] for k, r in runs.items()}, {
            "retry--intact": gcr.UNUSABLE, "retry--no-decision": gcr.UNUSABLE,
            "rename--intact": gcr.CLEAN, "rename--no-decision": gcr.UNUSABLE,
            "build--intact": gcr.CLEAN, "build--no-decision": gcr.UNUSABLE,
        })
        self.assertIn("the intact run is unusable", runs["retry--no-decision"]["detail"])
        self.assertEqual(runs["build--no-decision"]["exit"], 2)
        self.assertIsNone(runs["rename--no-decision"]["exit"])
        self.assertEqual(grading["summary"]["unusable"], 4)

    def test_summary_and_grading_json(self):
        self.write_plants({"question": 3}, cases=("retry", "rename", "build", "logformat"))
        for case in ("retry", "rename", "build", "logformat"):
            self.cold(f"{case}--intact", ALL)
        self.cold("retry--no-decision", DECISION_MISSING)                                    # caught
        self.cold("rename--no-decision", ALL_IN_VARIANT)                                      # missed
        self.cold("build--no-decision", [answer(Q1, TASK), answer(Q2, END), answer(Q3, "Invented.")])  # caught: unsupported
        runs, grading, lines = self.graded()
        self.assertEqual(grading["summary"], {
            "variants": {"no-decision": {"caught": 2, "not_separated": 0, "missed": 1, "planted": 4}},
            "false_alarms": 0, "intact": 4, "unusable": 1, "runs": 8,
        })
        self.assertEqual(lines[-3:], [
            "no-decision: 2 caught, 0 not separated, 1 missed of 4 planted",
            "false alarms: 0 of 4 intact",
            "unusable: 1 of 8 runs",
        ])
        self.assertEqual(len(lines), len(grading["runs"]) + 3)
        caught = runs["retry--no-decision"]
        self.assertEqual({k: caught[k] for k in ("kind", "variant", "removed", "exit", "outcome", "signal", "detail", "findings")}, {
            "kind": "planted", "variant": "no-decision", "removed": "the decision", "exit": 1, "outcome": gcr.CAUGHT,
            "signal": "question 3", "detail": "missing", "findings": ["question 3: missing: what the reader decides"],
        })
        self.assertEqual(runs["build--no-decision"]["detail"], "unsupported")

    def test_malformed_expect_exits_2(self):
        for expect in (None, {}, {"keywords": ["x"]}, {"question": 0}, {"question": 4}, {"question": True}, {"terms": []}, {"terms": "gateway"}):
            with self.subTest(expect=expect):
                self.write_plants(expect)
                done = self.grade()
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn("expect", done.stderr)
        self.assertFalse((self.runs / "grading.json").exists())

    def test_unreadable_input_exits_2(self):
        self.plants.write_text("not json", encoding="utf-8")
        self.assertEqual(self.grade().returncode, 2)
        self.plants.write_text(json.dumps({"cases": [{"case": "retry"}]}), encoding="utf-8")
        self.assertEqual(self.grade().returncode, 2)
        self.write_plants({"question": 1})
        (self.plants.parent / "questions.json").write_text("not json", encoding="utf-8")
        self.assertEqual(self.grade().returncode, 2)
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(gcr.main([str(self.plants), str(self.root / "absent")]), 2)
        self.assertIn("not a directory", err.getvalue())
        self.assertFalse((self.runs / "grading.json").exists())


if __name__ == "__main__":
    unittest.main()
