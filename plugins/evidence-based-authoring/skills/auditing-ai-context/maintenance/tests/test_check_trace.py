"""check_trace.py: the verdicts of each reading on a trace list, their refusal codes and the disposition."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_trace as ct  # noqa: E402

OLD = """# Retry policy

Some clients retry on every error.

A citation names its source.

The client sends each request once.
"""

# Lines 3 and 5 stand in both texts; lines 7, 9 and 11 are the candidates c001, c002 and c003;
# line 13 is added but carries no cue and no term.
NEW = """# Retry policy

Some clients retry on every error.

A citation names its source.

The client retries idempotent requests only, instead of retrying on every error.

The job does not write outside its directory.

The method is neither a sequence of steps nor a demand for a citation.

Each request carries a budget per minute.
"""

LICENCE = "Some clients retry on every error."


def rewrite(id_, target="the old rule"):
    return {"id": id_, "target": target, "verdict": "rewrite", "reason": "it argues with the deleted rule"}


def licensed(id_, quote=LICENCE, target="retrying on every error"):
    return {"id": id_, "target": target, "verdict": "licensed", "quote": quote, "reason": "the text names it earlier"}


def plain(id_, question="Does the job write outside its directory?", target="writing outside the directory"):
    return {"id": id_, "target": target, "verdict": "plain", "question": question, "reason": "a reader asks it"}


def keeping_all():
    """A reading that keeps every candidate of the fixture by a valid verdict."""
    return [licensed("c001"), plain("c002"), licensed("c003", quote="A citation names its source.",
                                                       target="a demand for a citation")]


class Fixture(unittest.TestCase):
    """A document and its list, built by trace_list.py from OLD and NEW under a temporary directory."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "old.md").write_text(OLD, encoding="utf-8")
        (self.dir / "new.md").write_text(NEW, encoding="utf-8")
        built = subprocess.run([sys.executable, "-I", str(SCRIPTS / "trace_list.py"), "--old", "old.md", "--new",
                                "new.md", "--out", "list.json"],
                               cwd=self.dir, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(built.returncode, 0, built.stderr)
        self.listing = json.loads((self.dir / "list.json").read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, *readings):
        return ct.check(self.listing, list(readings), self.dir)

    def settled(self, readings, id_):
        """[(outcome, code)] of the candidate, one per reading."""
        entry = next(entry for entry in self.check(*readings)["candidates"] if entry["id"] == id_)
        return [(outcome["outcome"], outcome["code"]) for outcome in entry["outcomes"]]

    def refusal(self, verdict):
        """(code, message) of the one finding a single reading with this verdict on its candidate produces."""
        findings = self.check([verdict])["findings"]
        mine = [(item["code"], item["message"]) for item in findings if item["id"] == verdict["id"]]
        self.assertEqual(len(mine), 1, findings)
        return mine[0]


class List(Fixture):
    def test_the_fixture_lists_the_three_candidates(self):
        found = [(c["id"], c["line"], c["cues"]) for c in self.listing["candidates"]]
        self.assertEqual(found, [("c001", 7, ["instead"]), ("c002", 9, ["not"]), ("c003", 11, ["neither", "nor"])])


class Valid(Fixture):
    def test_one_valid_verdict_of_each_kind(self):
        cases = {"rewrite": (rewrite("c001"), ("rewrite", "")),
                 "licensed by a word of the target": (licensed("c001"), ("keep", "")),
                 "licensed on a later candidate": (keeping_all()[2], ("keep", "")),
                 "plain": (plain("c002"), ("keep", "")),
                 "plain on any candidate": (plain("c003", question="Does the method demand a citation?",
                                                  target="a demand for a citation"), ("keep", ""))}
        for name, (verdict, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(self.settled([[verdict]], verdict["id"]), [expected])

    def test_a_reading_that_keeps_everything_has_no_finding(self):
        result = self.check(keeping_all())
        self.assertEqual(result["findings"], [])
        self.assertEqual([entry["disposition"] for entry in result["candidates"]], ["keep"] * 3)

    def test_the_quote_is_compared_normalised(self):
        verdict = licensed("c001", quote="  Some clients   retry on every error.\n")
        self.assertEqual(self.settled([[verdict]], "c001"), [("keep", "")])


class Refusals(Fixture):
    def test_missing(self):
        verdicts = [verdict for verdict in keeping_all() if verdict["id"] != "c002"]
        findings = self.check(verdicts)["findings"]
        self.assertEqual([(item["code"], item["id"]) for item in findings], [("MISSING", "c002")])
        self.assertEqual(self.settled([verdicts], "c002"), [("rewrite", "MISSING")])

    def test_shape(self):
        no_target = licensed("c001")
        del no_target["target"]
        no_question = plain("c002")
        del no_question["question"]
        cases = {"a verdict outside the three": dict(rewrite("c001"), verdict="keep"),
                 "no target": no_target,
                 "an empty target": licensed("c001", target="  "),
                 "plain without a question": no_question,
                 "plain with an empty question": plain("c002", question=" ")}
        for name, verdict in cases.items():
            with self.subTest(name):
                self.assertEqual(self.refusal(verdict)[0], "SHAPE")
                self.assertEqual(self.settled([[verdict]], verdict["id"]), [("rewrite", "SHAPE")])

    def test_each_quote_condition_separately(self):
        cases = {
            "shorter than 12 characters": (licensed("c001", quote="Some clients"[:11]), "shorter than 12"),
            "absent from the text": (licensed("c001", quote="Some servers retry on every error."),
                                     "does not occur in new.md"),
            "after the candidate": (licensed("c001", quote="Each request carries a budget per minute.",
                                             target="retrying every request"), "ends after the candidate"),
            "inside a candidate to rewrite": (licensed("c003", quote="The job does not write outside its directory.",
                                                       target="writing outside the directory"),
                                              "lies in a candidate to rewrite: c002"),
            "no shared word": (licensed("c001", target="the old budget"), "shares no word"),
        }
        for name, (verdict, message) in cases.items():
            with self.subTest(name):
                code, found = self.refusal(verdict)
                self.assertEqual(code, "QUOTE")
                self.assertIn(message, found)
                self.assertEqual(self.settled([[verdict]], verdict["id"]), [("rewrite", "QUOTE")])

    def test_a_shared_word_has_four_letters_and_matches_by_its_ending(self):
        self.assertTrue(ct.shares_word("Every rule cites a source.", "the cited rules"))
        self.assertFalse(ct.shares_word("Every rule cites a source.", "a demand"))
        self.assertFalse(ct.shares_word("We use it on a day.", "the uses of days"))

    def test_unknown_has_no_effect(self):
        result = self.check(keeping_all() + [rewrite("c099")])
        self.assertEqual([(item["code"], item["id"]) for item in result["findings"]], [("UNKNOWN", "c099")])
        self.assertEqual([entry["disposition"] for entry in result["candidates"]], ["keep"] * 3)

    def test_duplicate_the_first_counts(self):
        result = self.check(keeping_all() + [rewrite("c001")])
        self.assertEqual([(item["code"], item["id"]) for item in result["findings"]], [("DUPLICATE", "c001")])
        self.assertEqual(result["candidates"][0]["disposition"], "keep")
        result = self.check([rewrite("c001")] + keeping_all())
        self.assertEqual(result["candidates"][0]["disposition"], "rewrite")


class Disposition(Fixture):
    def test_three_readings_all_keep(self):
        result = self.check(keeping_all(), keeping_all(), keeping_all())
        self.assertEqual([entry["disposition"] for entry in result["candidates"]], ["keep"] * 3)
        self.assertEqual(result["candidates"][0]["quotes"], [LICENCE])

    def test_three_readings_one_rewrite(self):
        second = [rewrite("c001")] + keeping_all()[1:]
        result = self.check(keeping_all(), second, keeping_all())
        self.assertEqual([entry["disposition"] for entry in result["candidates"]], ["rewrite", "keep", "keep"])
        self.assertEqual([o["outcome"] for o in result["candidates"][0]["outcomes"]], ["keep", "rewrite", "keep"])
        self.assertEqual(result["candidates"][0]["quotes"], [])

    def test_a_quote_from_an_earlier_candidate_holds_while_that_candidate_is_kept(self):
        leaning = keeping_all()[:2] + [licensed("c003", quote="The job does not write outside its directory.",
                                                 target="writing outside the directory")]
        result = self.check(leaning, keeping_all())
        self.assertEqual([entry["disposition"] for entry in result["candidates"]], ["keep"] * 3)
        self.assertEqual(result["findings"], [])

    def test_a_quote_from_an_earlier_candidate_falls_with_that_candidate(self):
        leaning = keeping_all()[:2] + [licensed("c003", quote="The job does not write outside its directory.",
                                                 target="writing outside the directory")]
        other = [keeping_all()[0], rewrite("c002"), keeping_all()[2]]
        result = self.check(leaning, other)
        self.assertEqual([entry["disposition"] for entry in result["candidates"]], ["keep", "rewrite", "rewrite"])
        self.assertEqual(self.settled([leaning, other], "c003"), [("rewrite", "QUOTE"), ("keep", "")])
        self.assertEqual([(item["code"], item["reading"], item["id"]) for item in result["findings"]],
                         [("QUOTE", 1, "c003")])

    def test_the_findings_of_a_reading_follow_the_order_of_the_list(self):
        result = self.check([rewrite("c099"), licensed("c003", target="  "), licensed("c001", target="  ")])
        self.assertEqual([(item["code"], item["id"]) for item in result["findings"]],
                         [("UNKNOWN", "c099"), ("SHAPE", "c001"), ("MISSING", "c002"), ("SHAPE", "c003")])

    def test_a_reading_given_as_an_array_of_objects(self):
        payload = [{"verdicts": keeping_all()[:1]}, {"verdicts": keeping_all()[1:]}]
        verdicts = ct.reading_verdicts(payload, "reading.json")
        self.assertEqual(verdicts, keeping_all())
        self.assertEqual(self.check(verdicts)["findings"], [])

    def test_a_shape_that_is_no_reading_is_refused(self):
        for payload in ({"verdict": []}, [{"verdicts": []}, "x"], "text"):
            with self.subTest(payload):
                with self.assertRaises(ct.InputError):
                    ct.reading_verdicts(payload, "reading.json")


class CommandLine(Fixture):
    def write(self, name, payload):
        path = self.dir / name
        path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
        return str(path)

    def run_script(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_trace.py"), "--list",
                               str(self.dir / "list.json"), "--root", str(self.dir), *args],
                              capture_output=True, text=True, encoding="utf-8")

    def test_every_candidate_kept_exits_0(self):
        run = self.run_script(self.write("r1.json", {"verdicts": keeping_all()}))
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.splitlines(), [
            f'new.md:7: KEEP c001 [licensed ×1] quote: "{LICENCE}"',
            "new.md:9: KEEP c002 [plain ×1]",
            'new.md:11: KEEP c003 [licensed ×1] quote: "A citation names its source."',
            "3 candidates: 3 kept, 0 to rewrite; readings: 1"])

    def test_a_candidate_to_rewrite_exits_1_with_its_line_and_findings(self):
        second = [licensed("c001", quote="Some servers retry on every error.")] + keeping_all()[1:]
        third = [rewrite("c001")] + keeping_all()[1:] + [rewrite("c099")]
        readings = [self.write("r1.json", {"verdicts": keeping_all()}), self.write("r2.json", {"verdicts": second}),
                    self.write("r3.json", [{"verdicts": third}])]
        run = self.run_script(*readings)
        self.assertEqual(run.returncode, 1, run.stderr)
        lines = run.stdout.splitlines()
        self.assertEqual(lines[0], "new.md:7: REWRITE c001 [reading 1: licensed; reading 2: QUOTE; reading 3: rewrite] "
                                   "The client retries idempotent requests only, instead of …")
        self.assertEqual(lines[1], "new.md:9: KEEP c002 [plain ×3]")
        self.assertEqual(lines[3:], ["QUOTE: reading 2: c001: the quote does not occur in new.md",
                                     "UNKNOWN: reading 3: c099: the list holds no candidate with this id",
                                     "3 candidates: 2 kept, 1 to rewrite; readings: 3"])

    def test_json_shape(self):
        out = self.dir / "out.json"
        second = [plain("c001")] + keeping_all()[1:]
        run = self.run_script("--json", str(out), self.write("r1.json", {"verdicts": keeping_all()}),
                              self.write("r2.json", {"verdicts": second}))
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(set(result), {"readings", "candidates", "findings"})
        self.assertEqual(result["readings"], 2)
        self.assertEqual(result["candidates"][0], {
            "id": "c001", "file": "new.md", "line": 7,
            "sentence": "The client retries idempotent requests only, instead of retrying on every error.",
            "disposition": "keep",
            "outcomes": [{"reading": 1, "verdict": "licensed", "outcome": "keep", "code": ""},
                         {"reading": 2, "verdict": "plain", "outcome": "keep", "code": ""}],
            "quotes": [LICENCE]})
        self.assertEqual(result["findings"], [])
        missing = self.dir / "missing.json"
        run = self.run_script("--json", str(missing), self.write("r3.json", {"verdicts": keeping_all()[1:]}))
        self.assertEqual(run.returncode, 1, run.stderr)
        result = json.loads(missing.read_text(encoding="utf-8"))
        self.assertEqual(result["candidates"][0]["outcomes"],
                         [{"reading": 1, "verdict": "", "outcome": "rewrite", "code": "MISSING"}])
        self.assertEqual(result["findings"],
                         [{"code": "MISSING", "reading": 1, "id": "c001", "message": "no verdict for the candidate"}])

    def test_a_changed_document_exits_2(self):
        reading = self.write("r1.json", {"verdicts": keeping_all()})
        (self.dir / "new.md").write_text(NEW + "\nOne more line.\n", encoding="utf-8")
        run = self.run_script(reading)
        self.assertEqual((run.returncode, run.stdout), (2, ""))
        self.assertIn("the document changed since the list was built", run.stderr)

    def test_too_few_readings_exits_2(self):
        reading = self.write("r1.json", {"verdicts": keeping_all()})
        for name, args in {"none": [], "two of three": ["--min-readings", "3", reading, reading]}.items():
            with self.subTest(name):
                run = self.run_script(*args)
                self.assertEqual((run.returncode, run.stdout), (2, ""))
                self.assertIn("--min-readings", run.stderr)

    def test_unreadable_input_exits_2(self):
        cases = {"an absent reading": [str(self.dir / "absent.json")],
                 "a reading that is not JSON": [self.write("bad.json", "{not json")],
                 "a reading of another shape": [self.write("other.json", {"answers": []})],
                 "a list that is no trace list": ["--list", self.write("nolist.json", {"files": []})]}
        for name, args in cases.items():
            with self.subTest(name):
                run = self.run_script(*args, self.write("r1.json", {"verdicts": keeping_all()}))
                self.assertEqual((run.returncode, run.stdout), (2, ""))
                self.assertTrue(run.stderr.startswith("check_trace: "), run.stderr)

    def test_help_exits_0(self):
        run = self.run_script("--help")
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
