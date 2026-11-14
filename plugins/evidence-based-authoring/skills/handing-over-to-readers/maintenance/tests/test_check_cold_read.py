"""check_cold_read.py: an answer of the cold read counts only when its quotes stand in the report."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_cold_read as cc  # noqa: E402


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


REPORT = """# Retry for payments

The task was to add a retry to the payment call. The retry is in, and two of three tests pass.
The payments team's test fails, because it expects “one attempt” — it sees four.

## What you decide

```text
delay: 200 ms -> 400 ms -> 800 ms
```

You decide whether the retry stays on for payments. Keep it?
"""

Q1, Q2, Q3 = "What was the task?", "How did it end?", "What do I have to decide?"


def answer(question, found="yes", quotes=(), text="an answer", missing=""):
    return {"question": question, "found": found, "answer": text, "quotes": list(quotes), "missing": missing}


def all_answered(**extra):
    cold = {"answers": [
        answer(Q1, quotes=["The task was to add a retry to the payment call."], text="Add a retry to the payment call."),
        answer(Q2, quotes=["The retry is in, and two of three tests pass."], text="Two of three tests pass."),
        answer(Q3, quotes=["You decide whether the retry stays on for payments."], text="Whether the retry stays on."),
    ]}
    cold.update(extra)
    return cold


class Files:
    """The three input files in a temporary directory."""

    def __init__(self, tmp: Path, cold, questions=None, report=REPORT):
        self.report = tmp / "report.md"
        self.questions = tmp / "questions.json"
        self.answers = tmp / "cold.json"
        self.report.write_text(report, encoding="utf-8")
        self.questions.write_text(json.dumps(questions if questions is not None else {"questions": [Q1, Q2, Q3]}, ensure_ascii=False), encoding="utf-8")
        self.answers.write_text(cold if isinstance(cold, str) else json.dumps(cold, ensure_ascii=False), encoding="utf-8")

    def args(self):
        return ["--report", str(self.report), "--questions", str(self.questions), "--answers", str(self.answers)]


class TempDir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, files, *extra):
        cmd = [sys.executable, "-I", str(SCRIPTS / "check_cold_read.py"), *files.args(), *extra]
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    def result(self, cold, questions=None, report=REPORT):
        f = Files(self.dir, cold, questions, report)
        return cc.check_files(f.report, f.questions, f.answers)

    def verdicts(self, cold, **kw):
        return [r["verdict"] for r in self.result(cold, **kw)["questions"]]


class Verdicts(TempDir):
    def test_answered_needs_yes_and_a_standing_quote(self):
        result = self.result(all_answered())
        self.assertEqual([r["verdict"] for r in result["questions"]], [cc.ANSWERED] * 3)
        self.assertEqual(cc.exit_code(result), 0)

    def test_yes_without_a_standing_quote_is_unsupported(self):
        cold = all_answered()
        cold["answers"][0]["quotes"] = ["The task was to make payments faster."]
        self.assertEqual(self.verdicts(cold)[0], cc.UNSUPPORTED)

    def test_yes_without_any_quote_is_unsupported(self):
        cold = all_answered()
        cold["answers"][0]["quotes"] = []
        self.assertEqual(self.verdicts(cold)[0], cc.UNSUPPORTED)

    def test_partly_without_a_standing_quote_is_unsupported(self):
        cold = all_answered()
        cold["answers"][1] = answer(Q2, found="partly", quotes=["All tests pass."], missing="which test fails")
        self.assertEqual(self.verdicts(cold)[1], cc.UNSUPPORTED)

    def test_partly_with_a_standing_quote_is_partly(self):
        cold = all_answered()
        cold["answers"][1] = answer(Q2, found="partly", quotes=["The retry is in, and two of three tests pass."], missing="why the third test fails")
        result = self.result(cold)
        self.assertEqual(result["questions"][1]["verdict"], cc.PARTLY)
        self.assertEqual(cc.exit_code(result), 1)

    def test_no_is_missing_even_with_a_standing_quote(self):
        cold = all_answered()
        cold["answers"][2] = answer(Q3, found="no", quotes=["You decide whether the retry stays on for payments."], missing="the options")
        self.assertEqual(self.verdicts(cold)[2], cc.MISSING)

    def test_one_standing_quote_of_several_suffices(self):
        cold = all_answered()
        cold["answers"][0]["quotes"] = ["Invented sentence.", "The task was to add a retry to the payment call."]
        row = self.result(cold)["questions"][0]
        self.assertEqual(row["verdict"], cc.ANSWERED)
        self.assertEqual(row["quotes_found"], ["The task was to add a retry to the payment call."])
        self.assertEqual(row["quotes_absent"], ["Invented sentence."])


class Normalisation(unittest.TestCase):
    def setUp(self):
        self.report = cc.normalise(REPORT + "\nThe *payment*  call\n\tuses `retry_policy` — see “the gateway’s” limit.\n")

    def assert_stands(self, quote):
        self.assertTrue(cc.stands(quote, self.report), quote)

    def test_white_space_runs(self):
        self.assert_stands("The payment call uses retry_policy")

    def test_line_break_inside_a_sentence(self):
        self.assert_stands("two of three tests pass. The payments team's test fails")

    def test_curly_and_straight_quotes(self):
        self.assert_stands('see "the gateway\'s" limit')
        self.assert_stands("expects \"one attempt\"")
        self.assert_stands("The payments team’s test fails")

    def test_dashes_of_every_kind(self):
        self.assert_stands('expects "one attempt" - it sees four')
        self.assert_stands('expects "one attempt" – it sees four')
        self.assert_stands("uses retry_policy ― see")

    def test_emphasis_and_backticks(self):
        self.assert_stands("The payment call uses `retry_policy`")
        self.assert_stands("The **payment** call uses retry_policy")

    def test_case(self):
        self.assert_stands("THE TASK WAS TO ADD A RETRY")

    def test_trailing_period_question_mark_and_ellipsis(self):
        self.assert_stands("Keep it?")
        self.assert_stands("The retry is in, and two of three tests pass…")
        self.assert_stands("The retry is in...")
        self.assert_stands("You decide whether the retry stays on for payments?")

    def test_quote_inside_a_fenced_block(self):
        self.assert_stands("delay: 200 ms -> 400 ms -> 800 ms")

    def test_absent_and_empty_quotes_do_not_stand(self):
        self.assertFalse(cc.stands("The task was to remove the retry.", self.report))
        self.assertFalse(cc.stands("", self.report))
        self.assertFalse(cc.stands(" ... ", self.report))
        self.assertFalse(cc.stands("**", self.report))


class Unexplained(TempDir):
    def test_term_with_a_standing_quote_is_kept_and_changes_no_exit_code(self):
        cold = all_answered(unexplained=[{"term": "the payments team's test", "quote": "The payments team’s test fails, because it expects “one attempt”"}])
        result = self.result(cold)
        self.assertEqual(result["unexplained"], [cold["unexplained"][0]])
        self.assertEqual(result["dropped"], [])
        self.assertEqual(cc.exit_code(result), 0)

    def test_all_answered_with_a_kept_term_exits_0_and_prints_the_term(self):
        cold = all_answered(unexplained=[{"term": "the payments team's test", "quote": "The payments team's test fails"}])
        run = self.run_script(Files(self.dir, cold))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout.splitlines()[-2:], [
            "unexplained: the payments team's test: \"The payments team's test fails\"",
            "3 of 3 questions answered from the text, 1 unexplained term(s)",
        ])

    def test_term_with_an_absent_quote_is_dropped_and_changes_no_exit_code(self):
        cold = all_answered(unexplained=[{"term": "idempotency key", "quote": "The idempotency key is reused."}])
        result = self.result(cold)
        self.assertEqual(result["unexplained"], [])
        self.assertEqual(result["dropped"], [cold["unexplained"][0]])
        self.assertEqual(cc.exit_code(result), 0)


class InputDefects(TempDir):
    def assert_exit_2(self, files, *expected):
        run = self.run_script(files)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertEqual(run.stdout, "")
        lines = run.stderr.splitlines()
        for fragment in expected:
            self.assertTrue(any(fragment in line for line in lines), f"{fragment!r} not in {lines}")
        return lines

    def test_unreadable_file(self):
        files = Files(self.dir, all_answered())
        files.report.unlink()
        self.assert_exit_2(files, "report: cannot read")

    def test_malformed_json(self):
        self.assert_exit_2(Files(self.dir, "not json"), "answers:", "is not JSON")

    def test_malformed_shape(self):
        self.assert_exit_2(Files(self.dir, all_answered(), questions=["What was the task?"]), "questions: expected an object")

    def test_found_outside_the_three_values(self):
        cold = all_answered()
        cold["answers"][0]["found"] = "maybe"
        self.assert_exit_2(Files(self.dir, cold), "answer 1: \"found\" is 'maybe'")

    def test_answer_to_a_question_that_was_not_asked(self):
        cold = all_answered()
        cold["answers"].append(answer("What did it cost?", quotes=["Keep it?"]))
        self.assert_exit_2(Files(self.dir, cold), "answer 4: answers a question that QUESTIONS.json does not hold: What did it cost?")

    def test_question_without_an_answer(self):
        cold = all_answered()
        del cold["answers"][1]
        self.assert_exit_2(Files(self.dir, cold), "question 2 has no answer: How did it end?")

    def test_one_line_per_defect(self):
        cold = all_answered()
        cold["answers"][0]["found"] = "maybe"
        del cold["answers"][2]
        lines = self.assert_exit_2(Files(self.dir, cold), "\"found\" is 'maybe'", "question 3 has no answer")
        self.assertEqual(len(lines), 2, lines)

    def test_input_error_from_the_module(self):
        files = Files(self.dir, {"answers": []})
        with self.assertRaises(cc.InputError) as raised:
            cc.check_files(files.report, files.questions, files.answers)
        self.assertEqual(len(raised.exception.defects), 3)


class Output(TempDir):
    def cold(self):
        cold = all_answered(unexplained=[
            {"term": "the payments team's test", "quote": "The payments team's test fails"},
            {"term": "gateway", "quote": "The gateway rejects it."},
        ])
        cold["answers"][1] = answer(Q2, found="partly", quotes=["two of three tests pass"], text="Two of three pass.", missing="which test fails and why")
        cold["answers"][2] = answer(Q3, found="no", text="", missing="the options and their costs")
        return cold

    def test_lines_in_question_order_then_terms_then_summary(self):
        run = self.run_script(Files(self.dir, self.cold()))
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stdout.splitlines(), [
            "question 1: answered: Add a retry to the payment call.",
            "question 2: partly: which test fails and why",
            "question 3: missing: the options and their costs",
            "unexplained: the payments team's test: \"The payments team's test fails\"",
            "dropped: gateway: \"The gateway rejects it.\"",
            "1 of 3 questions answered from the text, 1 unexplained term(s)",
        ])

    def test_all_answered_exits_0(self):
        run = self.run_script(Files(self.dir, all_answered()))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout.splitlines()[-1], "3 of 3 questions answered from the text, 0 unexplained term(s)")

    def test_json(self):
        run = self.run_script(Files(self.dir, self.cold()), "--json")
        self.assertEqual(run.returncode, 1, run.stderr)
        data = json.loads(run.stdout)
        self.assertEqual(set(data), {"questions", "unexplained", "dropped", "answered", "total"})
        self.assertEqual((data["answered"], data["total"]), (1, 3))
        self.assertEqual(data["questions"][1], {
            "n": 2, "question": Q2, "verdict": "partly", "answer": "Two of three pass.",
            "missing": "which test fails and why", "quotes_found": ["two of three tests pass"], "quotes_absent": [],
        })
        self.assertEqual([t["term"] for t in data["unexplained"]], ["the payments team's test"])
        self.assertEqual([t["term"] for t in data["dropped"]], ["gateway"])

    def test_report_is_left_unchanged(self):
        files = Files(self.dir, self.cold())
        before = files.report.read_bytes()
        self.run_script(files)
        self.assertEqual(files.report.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["cold.json", "questions.json", "report.md"])


class StreamEncoding(TempDir):
    def test_report_and_quotes_outside_ascii_under_cp1252_streams(self):
        """Quotes and answers outside ASCII reach stdout intact although the process's streams are cp1252."""
        report = "Die Aufgabe war, die Zahlung zu wiederholen. Das Ergebnis: zwei von drei Tests grün.\n"
        questions = {"questions": ["Was war die Aufgabe?"]}
        cold = {"answers": [answer("Was war die Aufgabe?", quotes=["Das Ergebnis: zwei von drei Tests grün"], text="Zahlung wiederholen — „grün“ ✓")],
                "unexplained": [{"term": "Prüfsumme", "quote": "Die Prüfsumme fehlt."}]}
        files = Files(self.dir, cold, questions=questions, report=report)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONIOENCODING": "cp1252", "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]}
        run = subprocess.run([sys.executable, str(SCRIPTS / "check_cold_read.py"), *files.args()], capture_output=True, env=env)
        out = run.stdout.decode("utf-8")
        self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8", "replace"))
        self.assertIn("question 1: answered: Zahlung wiederholen — „grün“ ✓", out)
        self.assertIn("dropped: Prüfsumme: \"Die Prüfsumme fehlt.\"", out)


if __name__ == "__main__":
    unittest.main()
