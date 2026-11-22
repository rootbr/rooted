"""grade_retelling.py: caught, not separated, missed, false alarm and unusable runs of the retelling measurement in its two
arms, and the comparison of their caught shares."""
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
import grade_retelling as gr  # noqa: E402


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


SEND = "The client sends the request."
WAIT = "Without an answer the client waits for the pause."
DOUBLE = "After each wait the pause doubles."
FAIL = "After the fourth try the client reports a failure."
INTACT = "\n".join([SEND, WAIT, DOUBLE, FAIL]) + "\n"
NO_STEP = "\n".join([SEND, WAIT, FAIL]) + "\n"
Q1, Q2 = "What is the mechanism for?", "By which steps does it reach its result?"
CASE = {"case": "retry", "report_intact": "intact.md", "steps": 4,
        "variants": [{"variant": "no-step", "report": "no-step.md", "removed": "the doubling of the pause"}]}
GAP = "how the pause grows between two tries"


def answer(question, quote, found="yes", missing=""):
    return {"question": question, "found": found, "answer": "an answer", "quotes": [quote] if quote else [], "missing": missing}


def no(question, missing):
    return answer(question, "", found="no", missing=missing)


def step(quote):
    return {"step": "a step", "quotes": [quote]}


ANSWERED = [answer(Q1, SEND), answer(Q2, WAIT)]
Q2_MISSING = [answer(Q1, SEND), no(Q2, "how the pause grows")]
FULL = [step(SEND), step(WAIT), step(DOUBLE), step(FAIL)]
SHORT = [step(SEND), step(WAIT), step(FAIL)]
# Four steps that stand in the report without the doubling: the reader split the wait in two.
SPLIT = [step(SEND), step("Without an answer the client waits"), step("for the pause"), step(FAIL)]


class Grading(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fixtures = self.root / "fixtures"
        self.fixtures.mkdir()
        (self.fixtures / "intact.md").write_text(INTACT, encoding="utf-8")
        (self.fixtures / "no-step.md").write_text(NO_STEP, encoding="utf-8")
        self.write_arm_questions()
        self.plants = self.fixtures / "plants.json"
        self.write_plants(CASE)
        self.iteration = self.root / "iteration-1"
        self.iteration.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_questions(self, name, payload):
        (self.fixtures / name).write_text(json.dumps(payload), encoding="utf-8")

    def write_arm_questions(self):
        """The well-formed questions of both arms: the same questions, and "retell" in the arm retell's alone."""
        self.write_questions(gr.QUESTIONS_FILE[gr.QUESTIONS], {"questions": [Q1, Q2]})
        self.write_questions(gr.QUESTIONS_FILE[gr.RETELL], {"questions": [Q1, Q2], "retell": "the mechanism, by its steps"})

    def write_plants(self, case):
        self.plants.write_text(json.dumps({"cases": [case]}), encoding="utf-8")

    def cold(self, arm, round_no, run, answers, retelling=None, gaps=()):
        """Write a run's cold.json; a retelling of None leaves the key out."""
        payload = {"answers": answers, "unexplained": [], "gaps": list(gaps)}
        if retelling is not None:
            payload["retelling"] = retelling
        run_dir = self.iteration / arm / f"round-{round_no}" / run
        run_dir.mkdir(parents=True)
        (run_dir / "cold.json").write_text(json.dumps(payload), encoding="utf-8")

    def empty_round(self, arm):
        """An arm the test does not look at still needs a round; its runs are absent and come out unusable."""
        (self.iteration / arm / "round-1").mkdir(parents=True)

    def grade(self):
        return subprocess.run([sys.executable, "-I", str(EVALS / "grade_retelling.py"), str(self.plants), str(self.iteration)],
                              capture_output=True, text=True, encoding="utf-8")

    def graded(self):
        done = self.grade()
        self.assertEqual(done.returncode, 0, done.stderr)
        grading = json.loads((self.iteration / "grading.json").read_text(encoding="utf-8"))
        return {r["run"]: r for r in grading["runs"]}, grading, done.stdout.splitlines()

    def test_retell_steps_signal_fires_on_too_few_an_unsupported_or_no_step(self):
        rows = [  # (round, the planted run's retelling, the evidence of the steps signal)
            (1, SHORT, "3 of 3 steps stand, 4 expected"),
            (2, SPLIT + [step(DOUBLE)], "4 of 5 steps stand, 4 expected"),
            (3, None, "0 of 0 steps stand, 4 expected"),
        ]
        for round_no, retelling, _ in rows:
            self.cold(gr.RETELL, round_no, "retry--intact", ANSWERED, FULL)
            self.cold(gr.RETELL, round_no, "retry--no-step", ANSWERED, retelling)
        self.empty_round(gr.QUESTIONS)
        runs, _, lines = self.graded()
        for round_no, _, evidence in rows:
            with self.subTest(round=round_no):
                planted = runs[f"retell/round-{round_no}/retry--no-step"]
                self.assertEqual(runs[f"retell/round-{round_no}/retry--intact"]["outcome"], gr.CLEAN)
                self.assertEqual((planted["outcome"], planted["signal"], planted["detail"]), (gr.CAUGHT, gr.STEPS, evidence))
                self.assertIn(f"retell/round-{round_no}/retry--no-step: caught: steps: {evidence}", lines)

    def test_retell_gap_alone_catches_nothing_and_is_counted_apart(self):
        self.cold(gr.RETELL, 1, "retry--intact", ANSWERED, FULL)
        self.cold(gr.RETELL, 1, "retry--no-step", ANSWERED, SPLIT, gaps=[GAP])
        self.empty_round(gr.QUESTIONS)
        runs, grading, lines = self.graded()
        planted = runs["retell/round-1/retry--no-step"]
        self.assertEqual((planted["outcome"], planted["signals"], planted["gaps"]), (gr.MISSED, {}, [GAP]))
        retell = grading["summary"]["arms"][gr.RETELL]
        self.assertEqual((retell["gaps_planted"], retell["usable_planted"], retell["gaps_intact"], retell["usable_intact"]),
                         (1, 1, 0, 1))
        self.assertIn("retell: a gap listed in 1 of 1 usable planted and 0 of 1 usable intact", lines)

    def test_retell_missed_when_the_steps_stand_and_no_gap_is_listed_whatever_the_answers(self):
        """As many standing steps as the case's steps fire nothing, and a question left without an answer is no signal."""
        self.cold(gr.RETELL, 1, "retry--intact", ANSWERED, FULL)
        self.cold(gr.RETELL, 1, "retry--no-step", Q2_MISSING, SPLIT)
        self.empty_round(gr.QUESTIONS)
        runs, _, lines = self.graded()
        planted = runs["retell/round-1/retry--no-step"]
        self.assertEqual((planted["outcome"], planted["signal"], planted["signals"], planted["exit"]), (gr.MISSED, None, {}, 1))
        self.assertIn("retell/round-1/retry--no-step: missed: no signal fired", lines)

    def test_retell_signal_in_both_runs_is_not_separated_and_the_intact_is_a_false_alarm(self):
        self.cold(gr.RETELL, 1, "retry--intact", ANSWERED, SHORT)
        self.cold(gr.RETELL, 1, "retry--no-step", ANSWERED, SHORT)
        self.empty_round(gr.QUESTIONS)
        runs, _, lines = self.graded()
        planted = runs["retell/round-1/retry--no-step"]
        self.assertEqual((planted["outcome"], planted["signal"]), (gr.NOT_SEPARATED, gr.STEPS))
        self.assertEqual(planted["detail"], "3 of 3 steps stand, 4 expected; in the intact run too: 3 of 3 steps stand, 4 expected")
        self.assertEqual(runs["retell/round-1/retry--intact"]["outcome"], gr.FALSE_ALARM)
        self.assertIn("retell/round-1/retry--intact: false alarm: steps: 3 of 3 steps stand, 4 expected", lines)

    def test_retell_gap_on_an_intact_text_is_no_false_alarm(self):
        """A gap is listed in both runs; the steps signal fires in the planted one alone."""
        self.cold(gr.RETELL, 1, "retry--intact", ANSWERED, FULL, gaps=[GAP])
        self.cold(gr.RETELL, 1, "retry--no-step", ANSWERED, SHORT, gaps=[GAP])
        self.empty_round(gr.QUESTIONS)
        runs, grading, lines = self.graded()
        self.assertEqual((runs["retell/round-1/retry--no-step"]["outcome"], runs["retell/round-1/retry--no-step"]["signal"]),
                         (gr.CAUGHT, gr.STEPS))
        self.assertEqual((runs["retell/round-1/retry--intact"]["outcome"], runs["retell/round-1/retry--intact"]["gaps"]),
                         (gr.CLEAN, [GAP]))
        self.assertEqual(grading["summary"]["arms"][gr.RETELL]["false_alarms"], 0)
        self.assertIn("retell: a gap listed in 1 of 1 usable planted and 1 of 1 usable intact", lines)

    def test_questions_caught_by_a_question_not_answered(self):
        self.cold(gr.QUESTIONS, 1, "retry--intact", ANSWERED)
        self.cold(gr.QUESTIONS, 1, "retry--no-step", Q2_MISSING)
        self.empty_round(gr.RETELL)
        runs, _, lines = self.graded()
        planted = runs["questions/round-1/retry--no-step"]
        self.assertEqual(runs["questions/round-1/retry--intact"]["outcome"], gr.CLEAN)
        self.assertEqual((planted["outcome"], planted["signal"], planted["detail"]), (gr.CAUGHT, "question 2", "missing"))
        self.assertIn("questions/round-1/retry--no-step: caught: question 2: missing", lines)

    def test_questions_signal_in_both_runs_is_not_separated_and_the_intact_is_a_false_alarm(self):
        self.cold(gr.QUESTIONS, 1, "retry--intact", Q2_MISSING)
        self.cold(gr.QUESTIONS, 1, "retry--no-step", Q2_MISSING)
        self.empty_round(gr.RETELL)
        runs, _, lines = self.graded()
        self.assertEqual(runs["questions/round-1/retry--no-step"]["outcome"], gr.NOT_SEPARATED)
        self.assertIn("questions/round-1/retry--intact: false alarm: question 2: missing", lines)

    def test_questions_missed_and_a_retelling_there_is_not_read(self):
        self.cold(gr.QUESTIONS, 1, "retry--intact", ANSWERED)
        self.cold(gr.QUESTIONS, 1, "retry--no-step", ANSWERED, SHORT, gaps=[GAP])
        self.empty_round(gr.RETELL)
        runs, _, _ = self.graded()
        planted = runs["questions/round-1/retry--no-step"]
        self.assertEqual((planted["outcome"], planted["signals"], planted["gaps"], planted["exit"]), (gr.MISSED, {}, [], 0))

    def test_unusable_when_its_own_or_the_intact_run_is_absent_or_exits_2(self):
        self.cold(gr.RETELL, 1, "retry--no-step", ANSWERED, SHORT)                                # intact absent
        self.cold(gr.RETELL, 2, "retry--intact", ANSWERED, FULL)                                  # planted absent
        self.cold(gr.RETELL, 3, "retry--intact", ANSWERED, FULL)
        self.cold(gr.RETELL, 3, "retry--no-step", ANSWERED, [{"quotes": [SEND]}])                 # exits 2: a step without "step"
        self.empty_round(gr.QUESTIONS)
        runs, grading, _ = self.graded()
        self.assertEqual({k: r["outcome"] for k, r in runs.items() if r["arm"] == gr.RETELL}, {
            "retell/round-1/retry--intact": gr.UNUSABLE, "retell/round-1/retry--no-step": gr.UNUSABLE,
            "retell/round-2/retry--intact": gr.CLEAN, "retell/round-2/retry--no-step": gr.UNUSABLE,
            "retell/round-3/retry--intact": gr.CLEAN, "retell/round-3/retry--no-step": gr.UNUSABLE,
        })
        self.assertIn("the intact run is unusable", runs["retell/round-1/retry--no-step"]["detail"])
        self.assertIsNone(runs["retell/round-2/retry--no-step"]["exit"])
        self.assertEqual(runs["retell/round-3/retry--no-step"]["exit"], 2)
        retell = grading["summary"]["arms"][gr.RETELL]
        self.assertEqual((retell["unusable"], retell["planted"], retell["intact"]), (3, 3, 3))

    def test_no_comparison_when_an_arm_has_no_usable_planted_run(self):
        self.cold(gr.RETELL, 1, "retry--intact", ANSWERED, FULL)                                  # planted absent
        self.cold(gr.QUESTIONS, 1, "retry--intact", ANSWERED)
        self.cold(gr.QUESTIONS, 1, "retry--no-step", Q2_MISSING)                                  # caught
        _, grading, lines = self.graded()
        comparison = grading["summary"]["comparison"]
        self.assertEqual(comparison["caught_share"], {gr.RETELL: {"caught": 0, "usable": 0, "share": None},
                                                      gr.QUESTIONS: {"caught": 1, "usable": 1, "share": 1.0}})
        self.assertEqual((comparison["difference_points"], comparison["p_one_sided"]), (None, None))
        self.assertEqual(lines[-1], ("caught of usable planted: retell 0 of 0, questions 1 of 1 (100.0 %); "
                                     "no comparison: an arm has no usable planted run"))

    def test_summary_comparison_and_grading_json(self):
        for round_no, retelling in ((1, SHORT), (2, None), (3, SPLIT)):                          # caught, caught, missed
            self.cold(gr.RETELL, round_no, "retry--intact", ANSWERED, FULL)
            self.cold(gr.RETELL, round_no, "retry--no-step", ANSWERED, retelling)
        for round_no, intact, planted in ((1, ANSWERED, Q2_MISSING), (2, ANSWERED, ANSWERED),     # caught, missed
                                          (3, Q2_MISSING, Q2_MISSING)):                           # not separated
            self.cold(gr.QUESTIONS, round_no, "retry--intact", intact)
            self.cold(gr.QUESTIONS, round_no, "retry--no-step", planted)
        self.cold(gr.QUESTIONS, 4, "retry--intact", ANSWERED)                                     # the planted run absent: unusable
        runs, grading, lines = self.graded()
        summary = grading["summary"]
        self.assertEqual(summary["arms"], {
            gr.RETELL: {"caught": 2, "not_separated": 0, "missed": 1, "unusable": 0, "planted": 3, "false_alarms": 0, "intact": 3,
                        "gaps_planted": 0, "usable_planted": 3, "gaps_intact": 0, "usable_intact": 3},
            gr.QUESTIONS: {"caught": 1, "not_separated": 1, "missed": 1, "unusable": 1, "planted": 4, "false_alarms": 1, "intact": 4,
                           "gaps_planted": 0, "usable_planted": 3, "gaps_intact": 0, "usable_intact": 4},
        })
        comparison = summary["comparison"]
        self.assertEqual({arm: (s["caught"], s["usable"]) for arm, s in comparison["caught_share"].items()},
                         {gr.RETELL: (2, 3), gr.QUESTIONS: (1, 3)})
        self.assertAlmostEqual(comparison["caught_share"][gr.RETELL]["share"], 2 / 3, places=12)
        self.assertAlmostEqual(comparison["difference_points"], 100 / 3, places=9)
        # (C(3,2)·C(3,1) + C(3,3)·C(3,0)) / C(6,3) = (9 + 1) / 20
        self.assertAlmostEqual(comparison["p_one_sided"], 0.5, places=12)
        self.assertEqual(lines[-4:], [
            "retell: 2 caught, 0 not separated, 1 missed, 0 unusable of 3 planted; 0 false alarms of 3 intact",
            "questions: 1 caught, 1 not separated, 1 missed, 1 unusable of 4 planted; 1 false alarms of 4 intact",
            "retell: a gap listed in 0 of 3 usable planted and 0 of 3 usable intact",
            ("caught of usable planted: retell 2 of 3 (66.7 %), questions 1 of 3 (33.3 %); "
             "difference 33.3 points; one-sided Fisher exact p = 0.5"),
        ])
        self.assertEqual(len(grading["runs"]), 14)
        self.assertEqual(len(lines), len(grading["runs"]) + 4)
        caught = runs["retell/round-1/retry--no-step"]
        self.assertEqual(caught, {
            "run": "retell/round-1/retry--no-step", "arm": gr.RETELL, "round": 1, "case": "retry", "kind": "planted",
            "variant": "no-step", "removed": "the doubling of the pause", "exit": 1, "outcome": gr.CAUGHT,
            "signal": gr.STEPS, "detail": "3 of 3 steps stand, 4 expected", "signals": {gr.STEPS: "3 of 3 steps stand, 4 expected"},
            "gaps": [],
        })

    def test_malformed_plants_exits_2(self):
        without_steps = {k: v for k, v in CASE.items() if k != "steps"}
        for case in (without_steps, {**CASE, "steps": 0}, {**CASE, "steps": True}, {**CASE, "steps": "4"}, {**CASE, "steps": 2.5}):
            with self.subTest(steps=case.get("steps")):
                self.write_plants(case)
                done = self.grade()
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn("\"steps\"", done.stderr)
        for case in ({**CASE, "report_intact": None}, {**CASE, "variants": "no-step"}, {**CASE, "variants": [{"variant": "no-step"}]}):
            with self.subTest(case=case):
                self.write_plants(case)
                self.assertEqual(self.grade().returncode, 2)
        self.plants.write_text("not json", encoding="utf-8")
        self.assertEqual(self.grade().returncode, 2)
        self.assertFalse((self.iteration / "grading.json").exists())

    def test_malformed_questions_exits_2(self):
        rows = [
            (gr.RETELL, {"questions": [Q1, Q2]}, "needs \"retell\""),
            (gr.RETELL, {"questions": [Q1, Q2], "retell": " "}, "needs \"retell\""),
            (gr.QUESTIONS, {"questions": [Q1, Q2], "retell": "the mechanism"}, "\"retell\" must be absent"),
            (gr.QUESTIONS, {"questions": "What is the mechanism for?"}, "list of strings"),
        ]
        self.empty_round(gr.RETELL)
        self.empty_round(gr.QUESTIONS)
        for arm, payload, message in rows:
            with self.subTest(arm=arm, payload=payload):
                self.write_arm_questions()
                self.write_questions(gr.QUESTIONS_FILE[arm], payload)
                done = self.grade()
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn(message, done.stderr)
        self.assertFalse((self.iteration / "grading.json").exists())

    def test_an_arm_without_rounds_exits_2(self):
        self.empty_round(gr.RETELL)
        done = self.grade()                                                                       # the arm questions is absent
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("no round-<r> directory", done.stderr)
        for name in ("round-0", "round-01", "round-x"):
            (self.iteration / gr.QUESTIONS / name).mkdir(parents=True)
        (self.iteration / gr.QUESTIONS / "round-2").write_text("a file, not a round", encoding="utf-8")
        self.assertEqual(self.grade().returncode, 2)
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(gr.main([str(self.plants), str(self.root / "absent")]), 2)
        self.assertIn("not a directory", err.getvalue())
        self.assertFalse((self.iteration / "grading.json").exists())


class FisherExact(unittest.TestCase):
    def test_one_sided_p_value_on_hand_checked_tables(self):
        rows = [  # (caught and runs of the first arm, caught and runs of the second, the exact tail)
            # 9 of 12 against 3 of 12: (C(12,9)·C(12,3) + C(12,10)·C(12,2) + C(12,11)·C(12,1) + C(12,12)·C(12,0)) / C(24,12)
            ((9, 12, 3, 12), (220 * 220 + 66 * 66 + 12 * 12 + 1) / 2704156),
            ((12, 12, 0, 12), 1 / 2704156),
            ((3, 12, 9, 12), 1 - (1 + 12 * 12 + 66 * 66) / 2704156),
            ((0, 12, 0, 12), 1.0),
            ((2, 3, 1, 3), 0.5),
        ]
        for table, expected in rows:
            with self.subTest(table=table):
                self.assertAlmostEqual(gr.fisher_one_sided(*table), expected, delta=expected * 1e-12)
        self.assertAlmostEqual(gr.fisher_one_sided(9, 12, 3, 12), 0.020, delta=0.0005)


if __name__ == "__main__":
    unittest.main()
