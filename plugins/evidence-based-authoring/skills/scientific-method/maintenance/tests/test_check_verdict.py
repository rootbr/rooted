"""check_verdict.py: the reader's verdict on one record, its shape and where each rule applies."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"
RECORD_FORMAT = SKILL / "references" / "record-format.md"
sys.path.insert(0, str(SCRIPTS))
import check_verdict as cv  # noqa: E402


def answer(rule, verdict="holds", quote="the words of the record", missing=""):
    return {"rule": rule, "verdict": verdict, "quote": quote, "missing": missing}


def not_applicable(rule):
    return answer(rule, "not-applicable", quote="")


def verdict(kind="claim", standing="supported", answers=None, **fields):
    obj = {"id": "H-03", "kind": kind, "standing": standing,
           "answers": answers if answers is not None else [answer(r) for r in cv.RULES]}
    obj.update(fields)
    return obj


def hypothesis(changes=None):
    """A valid verdict on a hypothesis: rules 1, 2, 7 hold and 3-6 are not applicable, with answers replaced by rule."""
    answers = {r: answer(r) if r in (1, 2, 7) else not_applicable(r) for r in cv.RULES}
    answers.update(changes or {})
    return verdict(standing="hypothesis", answers=list(answers.values()))


def norm(changes=None):
    answers = {r: answer(r) if r in (1, 4) else not_applicable(r) for r in cv.RULES}
    answers.update(changes or {})
    return verdict(kind="norm", answers=list(answers.values()))


def codes(obj):
    return [code for code, _ in cv.check(obj)]


class Valid(unittest.TestCase):
    def test_valid_verdicts_of_every_kind_pass(self):
        decision = verdict(kind="decision", answers=[answer(1)] + [not_applicable(r) for r in range(2, 8)])
        definition = dict(decision, kind="definition")
        del decision["standing"]
        for name, obj in {"supported": verdict(), "law": verdict(standing="law"), "hypothesis": hypothesis(),
                          "norm": norm(), "decision": decision, "definition": definition}.items():
            with self.subTest(name):
                self.assertEqual(cv.check(obj), [])

    def test_leading_takes_every_rule_as_a_claim_past_hypothesis(self):
        self.assertEqual(cv.check(verdict(standing="leading")), [])
        obj = verdict(standing="leading", answers=[answer(r) if r != 3 else not_applicable(3) for r in cv.RULES])
        self.assertEqual(codes(obj), ["APPLY"])

    def test_hypothesis_rules_3_to_6_take_any_verdict(self):
        obj = hypothesis({3: answer(3), 4: answer(4, "fails", quote="", missing="the test command"), 5: not_applicable(5)})
        self.assertEqual(cv.check(obj), [("FAILS", "rule 4 fails: the test command")])

    def test_the_example_of_the_description(self):
        text = RECORD_FORMAT.read_text(encoding="utf-8")
        example = json.loads(re.search(r"```json\n(.*?)```", text, re.S).group(1))
        self.assertEqual(codes(example), ["FAILS", "SHAPE", "SHAPE", "SHAPE", "SHAPE"])


class Shape(unittest.TestCase):
    def test_every_rejected_shape(self):
        no_id = verdict()
        del no_id["id"]
        no_kind = verdict()
        del no_kind["kind"]
        no_answers = verdict()
        del no_answers["answers"]
        no_standing = verdict()
        del no_standing["standing"]
        cases = {
            "not an object": [verdict()],
            "id absent": no_id,
            "kind absent": no_kind,
            "answers absent": no_answers,
            "a claim without standing": no_standing,
            "kind outside the vocabulary": verdict(kind="opinion"),
            "standing outside the vocabulary": verdict(standing="proven"),
            "a rule absent": verdict(answers=[answer(r) for r in range(1, 7)]),
            "a rule given twice": verdict(answers=[answer(r) for r in cv.RULES] + [answer(2)]),
            "a rule outside 1-7": verdict(answers=[answer(r) for r in cv.RULES] + [answer(8)]),
            "a rule that is not a number": verdict(answers=[answer(r) for r in cv.RULES] + [answer("1")]),
            "a verdict outside the three values": verdict(answers=[answer(r) for r in range(1, 7)] + [answer(7, "maybe")]),
            "answers not a list": verdict(answers={"1": "holds"}),
            "an answer not an object": verdict(answers=[answer(r) for r in cv.RULES] + ["holds"]),
            "a quote that is not a string": verdict(answers=[answer(r) for r in range(1, 7)] + [answer(7, quote=["q"])]),
        }
        for name, obj in cases.items():
            with self.subTest(name):
                found = codes(obj)
                self.assertIn("SHAPE", found)
                self.assertEqual(set(found) - {"SHAPE", "QUOTE"}, set(), found)

    def test_a_valid_object_has_no_shape_finding(self):
        self.assertNotIn("SHAPE", codes(verdict()))


class Answers(unittest.TestCase):
    def test_quote(self):
        self.assertEqual(codes(hypothesis({1: answer(1, quote="")})), ["QUOTE"])
        self.assertEqual(codes(hypothesis({1: answer(1, quote="  ")})), ["QUOTE"])
        self.assertEqual(codes(hypothesis({1: answer(1, quote="the line names its kind")})), [])

    def test_missing(self):
        self.assertEqual(codes(hypothesis({2: answer(2, "fails", quote="", missing="")})), ["MISSING", "FAILS"])
        self.assertEqual(codes(hypothesis({2: answer(2, "fails", quote="", missing="the refuting outcome")})), ["FAILS"])

    def test_apply(self):
        cases = {
            "rule 2 on a norm": norm({2: answer(2)}),
            "rule 4 not-applicable on a norm": norm({4: not_applicable(4)}),
            "rule 1 not-applicable on a hypothesis": hypothesis({1: not_applicable(1)}),
            "rule 7 not-applicable on a hypothesis": hypothesis({7: not_applicable(7)}),
            "rule 3 not-applicable on a supported claim": verdict(answers=[answer(r) if r != 3 else not_applicable(3) for r in cv.RULES]),
            "rule 7 fails on a definition": verdict(kind="definition", answers=[answer(1)] + [not_applicable(r) for r in range(2, 7)]
                                                    + [answer(7, "fails", quote="", missing="m")]),
        }
        for name, obj in cases.items():
            with self.subTest(name):
                self.assertEqual(codes(obj), ["APPLY"])
        self.assertEqual(codes(hypothesis({3: not_applicable(3), 6: answer(6)})), [])

    def test_fails(self):
        obj = verdict(answers=[answer(r) if r != 2 else answer(2, "fails", quote="", missing="the refuting outcome") for r in cv.RULES])
        self.assertEqual(cv.check(obj), [("FAILS", "rule 2 fails: the refuting outcome")])
        self.assertEqual(cv.check(verdict()), [])


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args, stdin=None):
        return subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_verdict.py"), *args],
                              input=stdin, capture_output=True, text=True, encoding="utf-8")

    def write(self, obj) -> str:
        path = self.dir / "verdict.json"
        path.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def test_every_applicable_rule_holds_exits_0(self):
        run = self.run_script(self.write(hypothesis()))
        self.assertEqual((run.returncode, run.stdout), (0, "0 finding(s)\n"), run.stderr)

    def test_a_fails_exits_1_with_one_line_per_finding(self):
        obj = hypothesis({2: answer(2, "fails", quote="", missing="what outcome refutes it — «ничего»")})
        run = self.run_script(self.write(obj))
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stdout.splitlines(), ["FAILS: rule 2 fails: what outcome refutes it — «ничего»", "1 finding(s)"])

    def test_standard_input(self):
        run = self.run_script("-", stdin=json.dumps(norm({2: answer(2)})))
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stdout.splitlines()[-1], "1 finding(s)")
        self.assertTrue(run.stdout.startswith("APPLY: rule 2 does not apply to a norm"))

    def test_unreadable_input_exits_2(self):
        for name, args in {"missing file": [str(self.dir / "absent.json")], "not JSON": [self.write("{not json")],
                           "no argument": []}.items():
            with self.subTest(name):
                run = self.run_script(*args)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, "")
                self.assertTrue(run.stderr)


if __name__ == "__main__":
    unittest.main()
