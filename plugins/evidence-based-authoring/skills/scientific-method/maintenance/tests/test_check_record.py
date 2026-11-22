"""check_record.py: the records of rule lines, in plain mode and against a base state in git."""
from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"
RECORD_FORMAT = SKILL / "references" / "record-format.md"
sys.path.insert(0, str(SCRIPTS))
import check_record as cr  # noqa: E402

FINDING = re.compile(r"^(?P<path>.+?):(?P<line>\d+): (?P<code>[A-Z]+): (?P<message>.*)$")


def setUpModule():
    """Git in this module reads no configuration of the user or the system, and HOME is a temporary directory."""
    home = tempfile.TemporaryDirectory(prefix="check-record-home-")
    unittest.addModuleCleanup(home.cleanup)
    environment = mock.patch.dict(os.environ, {
        "HOME": home.name, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
    })
    environment.start()
    unittest.addModuleCleanup(environment.stop)


PREDICTION = (("measure", "share of runs that read the file first"), ("against", "the same prompt without the paragraph"),
              ("scope", "coding agents on one model"), ("refuter", "the share is under ten points higher"),
              ("threshold", "ten points"))
OWN_RESULT = (("runs", "ten per arm"), ("test", "own evals/a.json"), ("result", "eight of ten against two of ten"),
              ("bounds", "one model, one repository"), ("fit", "direct"), ("validity", "direct: the share"))
EVENT_PREDICTION = (("measure", "the lock wait time in the database log during the outage"), ("against", "a lock in the database"),
                    ("event", "the outage of 2026-10-14, incident 412"),
                    ("refuter", "the lock wait time rises above its usual level before the queue fills"))
LEADING_TAIL = (("test", "own evals/a.json"), ("result", "the lock wait time stayed at its usual level"),
                ("bounds", "the database log of the outage"))


def line(rid: str, *fields: tuple[str, str], free: str = "free text · with: a colon") -> str:
    head = f"- **{rid}**" + (f" · {free}" if free else "")
    return " · ".join([head, *(f"{k}: {v}" for k, v in fields)])


def claim(rid: str, standing: str, *extra: tuple[str, str], prediction=PREDICTION) -> str:
    return line(rid, ("kind", "claim"), ("standing", standing), *prediction, *extra)


def replace(fields, key, value):
    return tuple((k, value if k == key else v) for k, v in fields)


NORM = line("N-1", ("kind", "norm"), ("issuer", "IEEE"), ("version", "1003.1-2024"), ("locator", "§2.8.2 Exit Status"))
DEFINITION = line("D-1", ("kind", "definition"), ("term", "card"))
DECISION = line("C-1", ("kind", "decision"), ("owner", "the operator"), ("goal", "calm figures"), ("hypothesis", "H-1"))
HYPOTHESIS = claim("H-1", "hypothesis", ("runs", "ten per arm"), ("test", "own evals/a.json"))
SUPPORTED = claim("H-1", "supported", *OWN_RESULT)
FIRST_HAND = "external doi:10.1/x §4 first-hand"
RELAY = "external a blog post relay"
ABSTRACT = "external doi:10.3/z abstract"
LAW = claim("L-1", "law", *replace(OWN_RESULT, "test", f"own evals/a.json; {FIRST_HAND}"))
CONTESTED = claim("X-1", "contested", ("test", f"{FIRST_HAND}; external doi:10.2/y first-hand"), ("result", "one for, one against"))
REFUTED = claim("F-1", "refuted", ("test", FIRST_HAND), ("result", "no difference in 40 runs"), ("bounds", "one model"))
UNRECORDED = "- **U-1** · a source and its words, no record"
EVENT_HYPOTHESIS = claim("E-1", "hypothesis", ("test", "own evals/a.json"), prediction=EVENT_PREDICTION)
LEADING = claim("E-1", "leading", *LEADING_TAIL, prediction=EVENT_PREDICTION)
TRIED = claim("H-2", "hypothesis", ("runs", "ten per arm"), ("test", "own evals/a.json"),
              ("result", "one run went against; it waits for its repetition"))


class Root(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        (self.root / "evals").mkdir(parents=True)
        (self.root / "evals" / "a.json").write_text("{}\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, *rules: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Map\n\n" + "".join(r + "\n" for r in rules), encoding="utf-8")
        return path

    def run_main(self, *args: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cr.main(["--root", str(self.root), *args])
            except SystemExit as usage:
                code = usage.code
        return code, out.getvalue().splitlines(), err.getvalue()

    def findings(self, *args: str):
        """The findings of one run; a DUE line is no finding and counts in neither the errors nor the exit status."""
        code, lines, err = self.run_main(*args)
        self.assertNotEqual(code, 2, err)
        found = [m.groupdict() for l in lines if (m := FINDING.match(l)) and m["code"] != "DUE"]
        self.assertEqual(lines[-1], f"{len(found)} error(s)")
        self.assertEqual(code, 1 if found else 0)
        return found

    def notices(self, *args: str):
        """The DUE lines of one run, as (path, line, message)."""
        code, lines, err = self.run_main(*args)
        self.assertNotEqual(code, 2, err)
        return [(m["path"], m["line"], m["message"]) for l in lines if (m := FINDING.match(l)) and m["code"] == "DUE"]

    def codes(self, *args: str) -> list[str]:
        return [f["code"] for f in self.findings(*args)]

    def check_lines(self, *rules: str, require: bool = False) -> list[str]:
        """The codes of one provenance map holding the rules, in plain mode."""
        self.write("rules-provenance.md", *rules)
        return self.codes(*(["--require"] if require else []))


class Passing(Root):
    def test_a_valid_record_of_every_kind_and_standing_passes(self):
        self.assertEqual(self.check_lines(NORM, DEFINITION, DECISION, HYPOTHESIS, claim("S-1", "supported", *OWN_RESULT),
                                          LAW, CONTESTED, REFUTED), [])

    def test_free_text_before_kind_is_not_read(self):
        self.assertEqual(self.check_lines(line("D-2", ("kind", "definition"), ("term", "card"), free="colour: red · loose words")), [])

    def test_the_example_lines_of_the_description_pass(self):
        shutil.copy(RECORD_FORMAT, self.root / "record-format.md")
        target = self.root / "checks" / "read-before-edit" / "cases.json"
        target.parent.mkdir(parents=True)
        target.write_text("{}\n", encoding="utf-8")
        code, lines, err = self.run_main("--stats", str(self.root / "record-format.md"))
        self.assertEqual(code, 0, "\n".join(lines) + err)
        self.assertIn("records by kind: claim 2, decision 0, definition 0, norm 1", lines)
        self.assertEqual(lines[-1], "0 error(s)")

    def test_the_example_hypothesis_needs_its_own_test_file(self):
        shutil.copy(RECORD_FORMAT, self.root / "record-format.md")
        self.assertEqual(self.codes(str(self.root / "record-format.md")), ["OWN"])


class PlainCodes(Root):
    def test_kind(self):
        self.assertEqual(self.check_lines(line("K-1", ("kind", "opinion"), ("term", "x"))), ["KIND"])
        self.assertEqual(self.check_lines(line("K-2", ("kind", ""))), ["KIND"])
        self.assertEqual(self.check_lines(line("K-3", ("kind", "definition"), ("term", "x"))), [])

    def test_field(self):
        cases = {
            "a required field absent": line("F-1", ("kind", "norm"), ("issuer", "IEEE"), ("version", "2024")),
            "a key outside the tables": line("F-2", ("kind", "definition"), ("term", "x"), ("colour", "red")),
            "an empty value": line("F-3", ("kind", "definition"), ("term", "")),
            "a key written twice": line("F-4", ("kind", "definition"), ("term", "x"), ("term", "y")),
            "a field its kind does not take": line("F-5", ("kind", "definition"), ("term", "x"), ("owner", "me")),
            "a segment that is not key: value": DEFINITION + " · loose words",
            "a key that is not lowercase": DEFINITION + " · Term: x",
            "a field its standing adds": claim("F-6", "refuted", ("test", FIRST_HAND), ("result", "none")),
            "threshold of a supported claim with an own test": claim("F-7", "supported", *OWN_RESULT, prediction=PREDICTION[:4]),
            "threshold of a hypothesis with an own test": claim("F-9", "hypothesis", ("runs", "ten per arm"), ("test", "own evals/a.json"),
                                                               prediction=PREDICTION[:4]),
            "runs of a hypothesis with an own test": claim("F-10", "hypothesis", ("test", "own evals/a.json")),
        }
        for name, rule in cases.items():
            with self.subTest(name):
                self.assertEqual(self.check_lines(rule), ["FIELD"])
        with self.subTest("a hypothesis with an own test, its threshold and its runs passes"):
            self.assertEqual(self.check_lines(HYPOTHESIS), [])
        with self.subTest("a hypothesis with sources beside it or no test needs no threshold or runs"):
            self.assertEqual(self.check_lines(claim("F-11", "hypothesis", ("beside", RELAY), prediction=PREDICTION[:4]),
                                              claim("F-12", "hypothesis", prediction=PREDICTION[:4])), [])
        with self.subTest("a supported claim on a first-hand test needs no threshold or runs"):
            self.assertEqual(self.check_lines(claim("F-8", "supported", ("test", FIRST_HAND), ("result", "r"),
                                                    ("bounds", "b"), ("fit", "direct"), prediction=PREDICTION[:4])), [])

    def test_standing(self):
        self.assertEqual(self.check_lines(claim("S-1", "proven")), ["STANDING"])
        self.assertEqual(self.check_lines(claim("S-2", "maybe")), ["STANDING"])
        self.assertEqual(self.check_lines(replace_line(REFUTED, "result", "the test Proved the opposite")), ["STANDING"])
        self.assertEqual(self.check_lines(replace_line(REFUTED, "result", "the share improved; provenance kept")), [])

    def test_test(self):
        self.assertEqual(self.check_lines(replace_line(REFUTED, "test", "a paper I read")), ["TEST"])
        self.assertEqual(self.check_lines(replace_line(REFUTED, "test", "external doi:10.1/x second-hand")), ["TEST"])
        self.assertEqual(self.check_lines(replace_line(LAW, "test", "own evals/a.json")), ["TEST"])
        self.assertEqual(self.check_lines(replace_line(CONTESTED, "test", FIRST_HAND)), ["TEST"])
        self.assertEqual(self.check_lines(LAW, CONTESTED), [])

    def test_support(self):
        relay_only = claim("P-1", "supported", ("test", RELAY), ("result", "r"), ("bounds", "b"), ("fit", "direct"))
        self.assertEqual(self.check_lines(relay_only), ["SUPPORT"])
        self.assertEqual(self.check_lines(replace_line(relay_only, "test", f"{RELAY}; {FIRST_HAND}")), [])

    def test_a_peer_reviewed_source_read_by_its_abstract_supports(self):
        abstract_only = claim("P-2", "supported", ("test", ABSTRACT), ("result", "r"), ("bounds", "b"), ("fit", "direct"))
        self.assertEqual(self.check_lines(abstract_only), [])
        self.assertEqual(self.check_lines(replace_line(LAW, "test", f"{ABSTRACT}; {RELAY}")), [])
        self.write("rules-provenance.md", replace_line(abstract_only, "test", RELAY))
        self.assertIn("it needs a test that is own, first-hand or abstract", self.findings()[0]["message"])

    def test_own(self):
        (self.root.parent / "outside.json").write_text("{}\n", encoding="utf-8")
        self.assertEqual(self.check_lines(replace_line(HYPOTHESIS, "test", "own evals/absent.json")), ["OWN"])
        self.assertEqual(self.check_lines(replace_line(HYPOTHESIS, "test", "own ../outside.json")), ["OWN"])
        self.assertEqual(self.check_lines(HYPOTHESIS), [])

    def test_fit(self):
        supported = claim("T-1", "supported", *OWN_RESULT)
        self.assertEqual(self.check_lines(replace_line(supported, "fit", "partial")), ["FIT"])
        self.assertEqual(self.check_lines(replace_line(supported, "fit", "transfer")), ["FIT"])
        self.assertEqual(self.check_lines(replace_line(supported, "fit", "transfer") + " · transfer: a newer model"), [])

    def test_dup(self):
        self.write("a-provenance.md", DEFINITION)
        self.write("pending-evidence.md", line("D-1", ("kind", "definition"), ("term", "other")))
        found = self.findings()
        self.assertEqual([(f["path"], f["code"]) for f in found], [("a-provenance.md", "DUP"), ("pending-evidence.md", "DUP")])
        self.assertIn("also stands on pending-evidence.md:3", found[0]["message"])

    def test_dup_needs_a_recorded_line(self):
        self.write("a-provenance.md", DEFINITION, UNRECORDED)
        self.write("pending-evidence.md", line("D-1", free="no record"), UNRECORDED)
        self.assertEqual([(f["path"], f["code"]) for f in self.findings()], [("a-provenance.md", "DUP")])

    def test_one_id_in_two_directories_passes(self):
        self.write("skill-a/maintenance/rules-provenance.md", DEFINITION)
        self.write("skill-b/maintenance/pending-evidence.md", DEFINITION)
        self.assertEqual(self.codes(), [])

    def test_distinct_ids_pass(self):
        self.write("a-provenance.md", DEFINITION)
        self.write("pending-evidence.md", NORM)
        self.assertEqual(self.codes(), [])

    def test_norecord_only_under_require(self):
        self.assertEqual(self.check_lines(UNRECORDED, DEFINITION), [])
        self.assertEqual(self.check_lines(UNRECORDED, DEFINITION, require=True), ["NORECORD"])


class OneEvent(Root):
    def test_a_claim_takes_scope_or_event(self):
        cases = {
            "neither": (claim("E-2", "hypothesis", prediction=EVENT_PREDICTION[:2] + EVENT_PREDICTION[3:]), ["FIELD"]),
            "both": (claim("E-3", "hypothesis", prediction=EVENT_PREDICTION + (("scope", "one model"),)), ["FIELD"]),
            "event alone": (EVENT_HYPOTHESIS, []),
            "scope alone": (HYPOTHESIS, []),
        }
        for name, (rule, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(self.check_lines(rule), expected)

    def test_against_names_the_rivals(self):
        for value in ("none", "None"):
            with self.subTest(value):
                self.assertEqual(self.check_lines(replace_line(EVENT_HYPOTHESIS, "against", value)), ["FIELD"])
        self.assertEqual(self.check_lines(EVENT_HYPOTHESIS), [])

    def test_the_standings_of_a_claim_about_one_event(self):
        two_tests = ("test", f"{FIRST_HAND}; external doi:10.2/y first-hand")
        for standing in ("supported", "law"):
            with self.subTest(standing):
                rule = claim("E-4", standing, two_tests, ("result", "r"), ("bounds", "b"), ("fit", "direct"), prediction=EVENT_PREDICTION)
                self.assertEqual(self.check_lines(rule), ["STANDING"])
        for standing, extra in (("hypothesis", ()), ("leading", LEADING_TAIL), ("contested", (two_tests, ("result", "r"))),
                                ("refuted", (("test", FIRST_HAND), ("result", "r"), ("bounds", "b")))):
            with self.subTest(standing):
                self.assertEqual(self.check_lines(claim("E-5", standing, *extra, prediction=EVENT_PREDICTION)), [])

    def test_an_own_test_adds_no_threshold_or_runs(self):
        self.assertEqual(self.check_lines(EVENT_HYPOTHESIS, LEADING.replace("E-1", "E-6")), [])

    def test_leading(self):
        self.assertEqual(self.check_lines(LEADING), [])
        self.assertEqual(self.check_lines(replace_line(LEADING, "test", FIRST_HAND)), [])
        cases = {
            "scope in place of event": (claim("E-7", "leading", *LEADING_TAIL, prediction=PREDICTION[:4]), ["FIELD"]),
            "no result": (claim("E-8", "leading", LEADING_TAIL[0], LEADING_TAIL[2], prediction=EVENT_PREDICTION), ["FIELD"]),
            "an abstract test alone": (replace_line(LEADING, "test", ABSTRACT), ["SUPPORT"]),
            "a relay test alone": (replace_line(LEADING, "test", RELAY), ["SUPPORT"]),
        }
        for name, (rule, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(self.check_lines(rule), expected)


class Validity(Root):
    def test_a_supported_claim_or_law_on_an_own_test_says_what_checked_its_measure(self):
        bare = tuple(field for field in OWN_RESULT if field[0] != "validity")
        cases = {
            "supported without validity": claim("V-1", "supported", *bare),
            "law without validity": claim("V-2", "law", *replace(bare, "test", f"own evals/a.json; {FIRST_HAND}")),
            "supported, unchecked": claim("V-3", "supported", *bare, ("validity", "unchecked")),
        }
        for name, rule in cases.items():
            with self.subTest(name):
                self.assertEqual(self.check_lines(rule), ["VALIDITY"])
        for value in ("direct: the claim is about the count the measure reports",
                      "probe: a planted defect raised the count by one", "labels: two people marked 40 runs and agreed on 38"):
            with self.subTest(value):
                self.assertEqual(self.check_lines(claim("V-4", "supported", *bare, ("validity", value))), [])
        with self.subTest("a hypothesis and a claim on someone else's test may leave it out"):
            self.assertEqual(self.check_lines(HYPOTHESIS, claim("V-5", "supported", ("test", FIRST_HAND), ("result", "r"),
                                                                ("bounds", "b"), ("fit", "direct"), prediction=PREDICTION[:4])), [])

    def test_the_four_forms(self):
        for value in ("maybe", "direct", "direct:", "probe:  ", "labels:x", "Unchecked"):
            with self.subTest(value):
                self.assertEqual(self.check_lines(claim("V-6", "hypothesis", ("validity", value), prediction=PREDICTION[:4])),
                                 ["VALIDITY"])
        self.assertEqual(self.check_lines(claim("V-7", "hypothesis", ("validity", "unchecked"), prediction=PREDICTION[:4])), [])


NEIGHBOUR = (("beside", f"{FIRST_HAND}; {RELAY}"), ("beside-result", "a neighbouring question pointing the claim's way"),
             ("beside-bounds", "students reading pairs of sentences"))


class Beside(Root):
    def test_a_hypothesis_keeps_its_sources_beside_its_planned_test(self):
        self.assertEqual(self.check_lines(claim("B-1", "hypothesis", ("runs", "ten per arm"), ("test", "own evals/a.json"),
                                                *NEIGHBOUR), require=True), [])
        self.assertEqual(self.check_lines(claim("B-2", "hypothesis", *NEIGHBOUR, prediction=PREDICTION[:4]), require=True), [])

    def test_the_forms_of_a_beside_entry(self):
        cases = {
            "an entry in none of the forms": ("beside", "a paper I read"),
            "a reading outside the three": ("beside", "external doi:10.1/x second-hand"),
            "a test of our own": ("beside", "own evals/a.json"),
            "a test of our own among published ones": ("beside", f"{FIRST_HAND}; own evals/a.json"),
        }
        for name, entry in cases.items():
            with self.subTest(name):
                self.assertEqual(self.check_lines(claim("B-3", "hypothesis", entry, prediction=PREDICTION[:4])), ["BESIDE"])
        self.write("rules-provenance.md", claim("B-3", "hypothesis", ("beside", "own evals/a.json"), prediction=PREDICTION[:4]))
        self.assertIn("is a test of our own; it stands in test", self.findings()[0]["message"])

    def test_its_result_and_bounds_take_beside(self):
        for key in ("beside-result", "beside-bounds"):
            with self.subTest(key):
                self.assertEqual(self.check_lines(claim("B-4", "hypothesis", (key, "r"), prediction=PREDICTION[:4])), ["BESIDE"])
        self.assertEqual(self.check_lines(claim("B-5", "hypothesis", ("beside", ""), ("beside-result", "r"),
                                                prediction=PREDICTION[:4])), ["FIELD"])

    def test_only_a_claim_takes_beside(self):
        self.assertEqual(self.check_lines(DECISION + f" · beside: {FIRST_HAND}"), ["FIELD"])

    def test_a_hypothesis_with_a_published_test_is_held_where_a_record_is(self):
        published = claim("B-6", "hypothesis", ("test", f"{FIRST_HAND}; {ABSTRACT}"), ("result", "r"), ("bounds", "b"),
                          prediction=PREDICTION[:4])
        self.assertEqual(self.check_lines(published), [])
        self.assertEqual(self.check_lines(published, require=True), ["BESIDE"])
        self.assertIn("names 2 published source(s) in test", self.findings("--require")[0]["message"])
        relay = claim("B-7", "hypothesis", ("runs", "ten per arm"), ("test", f"own evals/a.json; {RELAY}"))
        self.assertEqual(self.check_lines(relay, require=True), ["BESIDE"])
        event = claim("B-8", "hypothesis", ("test", f"own evals/a.json; {FIRST_HAND}"), prediction=EVENT_PREDICTION)
        self.assertEqual(self.check_lines(event, require=True), ["BESIDE"])

    def test_a_relayed_source_in_the_test_of_a_claim_is_held_where_a_record_is(self):
        relayed = claim("B-14", "supported", ("test", f"{FIRST_HAND}; {RELAY}"), ("result", "r"), ("bounds", "b"),
                        ("fit", "direct"), prediction=PREDICTION[:4])
        self.assertEqual(self.check_lines(relayed), [])
        self.assertEqual(self.check_lines(relayed, require=True), ["BESIDE"])
        self.assertIn("names 1 relayed source(s) in test", self.findings("--require")[0]["message"])
        beside = claim("B-15", "supported", ("test", FIRST_HAND), ("beside", RELAY), ("result", "r"), ("bounds", "b"),
                       ("fit", "direct"), prediction=PREDICTION[:4])
        self.assertEqual(self.check_lines(beside, require=True), [])

    def test_beside_counts_for_nothing_in_the_standing(self):
        cases = {
            "SUPPORT: a supported claim on a relay, a first-hand source beside it":
                (claim("B-9", "supported", ("test", RELAY), ("beside", FIRST_HAND), ("result", "r"), ("bounds", "b"),
                       ("fit", "direct"), prediction=PREDICTION[:4]), ["SUPPORT"]),
            "TEST: a law on one test, a second beside it":
                (claim("B-10", "law", *replace(OWN_RESULT, "test", "own evals/a.json"), ("beside", FIRST_HAND)), ["TEST"]),
            "TEST: a contested claim on one test, a second beside it":
                (claim("B-11", "contested", ("test", FIRST_HAND), ("beside", "external doi:10.2/y first-hand"), ("result", "r")),
                 ["TEST"]),
            "VALIDITY: a supported claim on an own test, its validity unchecked":
                (claim("B-12", "supported", *replace(OWN_RESULT, "validity", "unchecked"), *NEIGHBOUR), ["VALIDITY"]),
            "FIELD: a supported claim with sources beside it and no test":
                (claim("B-13", "supported", *NEIGHBOUR, ("result", "r"), ("bounds", "b"), ("fit", "direct"),
                       prediction=PREDICTION[:4]), ["FIELD"]),
        }
        for name, (rule, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(self.check_lines(rule), expected)
        with self.subTest("a supported claim with a source beside it passes on its own test"):
            self.assertEqual(self.check_lines(claim("B-14", "supported", *OWN_RESULT, *NEIGHBOUR)), [])


VERSIONS_LIST = """# Versions

Free text, and a line that names no version: - Model A 5.5 in prose.

- **Model A 5.5** · id: model-a-5-5
- **Model A 5** · id: model-a-5
- **Model B 4.5** · id: model-b-4-5-20250929 · retired: 2026-11-30 · source: `https://example.invalid/deprecations`
"""
TODAY = ("--today", "2026-11-22")
EXTERNAL_RESULT = (("test", FIRST_HAND), ("result", "r"), ("bounds", "b"), ("fit", "direct"))


def on_model(scope: str):
    """The prediction of a claim with no threshold and the given scope."""
    return replace(PREDICTION[:4], "scope", scope)


class Review(Root):
    def setUp(self):
        super().setUp()
        self.versions = self.root / "versions.md"
        self.versions.write_text(VERSIONS_LIST, encoding="utf-8")
        self.listed = ("--versions", str(self.versions))

    def review_codes(self, *rules: str, require: bool = False) -> list[str]:
        self.write("rules-provenance.md", *rules)
        return self.codes(*self.listed, *TODAY, *(["--require"] if require else []))

    def supported(self, rid: str, *review: tuple[str, str], scope: str = "agents on Model A 5.5 at effort high",
                  standing: str = "supported") -> str:
        extra = replace(EXTERNAL_RESULT, "test", f"{FIRST_HAND}; external doi:10.2/y first-hand") if standing == "law" else EXTERNAL_RESULT
        return claim(rid, standing, *extra, *review, prediction=on_model(scope))

    def test_the_two_forms_pass(self):
        for value in ("retirement of Model A 5.5", "retirement of model-b-4-5-20250929", "retirement of  model a 5.5",
                      "2027-11-24"):
            with self.subTest(value):
                self.assertEqual(self.review_codes(self.supported("V-1", ("review", value)), require=True), [])

    def test_a_review_outside_the_two_forms(self):
        for value in ("soon", "2027-02-30", "27-11-24", "2027-11-24 or later", "retirement of", "retirement of Model C 1",
                      "retirement of Model A 5.55"):
            with self.subTest(value):
                self.assertEqual(self.review_codes(self.supported("V-2", ("review", value))), ["REVIEW"])
        self.write("rules-provenance.md", self.supported("V-3", ("review", "retirement of Model C 1")))
        self.assertIn("'Model C 1', which no line of versions.md names", self.findings(*self.listed)[0]["message"])

    def test_an_empty_review_is_a_field_defect(self):
        self.assertEqual(self.review_codes(self.supported("V-4", ("review", ""))), ["FIELD"])

    def test_only_a_claim_takes_review(self):
        self.assertEqual(self.review_codes(DECISION + " · review: 2027-11-24"), ["FIELD"])

    def test_a_claim_whose_scope_names_a_listed_version_carries_review_under_require(self):
        bare = self.supported("V-5")
        self.assertEqual(self.review_codes(bare), [])
        self.assertEqual(self.review_codes(bare, require=True), ["REVIEW"])
        self.assertEqual(self.review_codes(self.supported("V-6", standing="law"), require=True), ["REVIEW"])
        self.assertEqual(self.review_codes(self.supported("V-7", scope="agents on MODEL-A-5-5"), require=True), ["REVIEW"])
        self.write("rules-provenance.md", self.supported("V-8", scope="agents on Model A 5, and Model A 5.5 later"))
        self.assertIn("scope names Model A 5.5 needs review", self.findings(*self.listed, "--require")[0]["message"])

    def test_a_scope_that_names_no_listed_version_needs_none(self):
        for scope in ("agents on Model A 5.55", "agents on Model A 50", "agents on a 2026 model", "humans reading Model A-5.5x"):
            with self.subTest(scope):
                self.assertEqual(self.review_codes(self.supported("V-9", scope=scope), require=True), [])
        with self.subTest("a hypothesis"):
            self.assertEqual(self.review_codes(claim("V-10", "hypothesis", prediction=on_model("agents on Model A 5.5")),
                                               require=True), [])

    def test_none_declares_no_term_and_is_never_due(self):
        people = self.supported("V-11", ("review", "none"), scope="engineers reading reports Model A 5.5 wrote")
        self.assertEqual(self.review_codes(people, require=True), [])
        self.assertEqual(self.notices(*self.listed, "--today", "2099-01-01"), [])
        for value in ("None", "none yet"):
            with self.subTest(value):
                self.assertEqual(self.review_codes(self.supported("V-12", ("review", value))), ["REVIEW"])

    def test_a_term_that_has_come_is_due_and_fails_nothing(self):
        self.write("rules-provenance.md", self.supported("D-1", ("review", "2026-11-22")),
                   self.supported("D-2", ("review", "2026-11-25")),
                   self.supported("D-3", ("review", "retirement of Model B 4.5")),
                   self.supported("D-4", ("review", "retirement of Model A 5.5")))
        self.assertEqual(self.codes(*self.listed, *TODAY), [])
        self.assertEqual(self.notices(*self.listed, *TODAY),
                         [("rules-provenance.md", "3", "D-1 is due to be read again: its review date 2026-11-22 has come")])
        self.assertEqual(self.notices(*self.listed, "--today", "2026-11-30"), [
            ("rules-provenance.md", "3", "D-1 is due to be read again: its review date 2026-11-22 has come"),
            ("rules-provenance.md", "4", "D-2 is due to be read again: its review date 2026-11-25 has come"),
            ("rules-provenance.md", "5", "D-3 is due to be read again: Model B 4.5 is retired on 2026-11-30")])

    def test_due_lines_follow_the_findings_and_change_no_exit_status(self):
        self.write("rules-provenance.md", self.supported("D-5", ("review", "2026-01-01")), line("K-1", ("kind", "opinion")))
        code, lines, err = self.run_main(*self.listed, *TODAY, "--stats")
        self.assertEqual(code, 1, err)
        self.assertEqual([l.split(": ")[1] for l in lines[:2]], ["KIND", "DUE"])
        self.assertEqual(lines[-1], "1 error(s)")

    def test_a_malformed_list_exits_2(self):
        cases = {
            "a retired date that is no date": "- **X** · retired: 2026-11-31 · source: s",
            "retired without source": "- **X** · retired: 2026-11-30",
            "a key outside the list's keys": "- **X** · colour: red",
            "a key written twice": "- **X** · id: x · id: y",
            "words glued to the name": "- **X** soon",
            "a name given twice": "- **X**\n- **x**",
            "an id that is another name": "- **X** · id: y\n- **Y**",
        }
        for name, text in cases.items():
            with self.subTest(name):
                self.versions.write_text(text + "\n", encoding="utf-8")
                self.write("rules-provenance.md", DEFINITION)
                code, lines, err = self.run_main(*self.listed)
                self.assertEqual((code, lines), (2, []))
                self.assertIn("versions.md:", err)
        code, lines, err = self.run_main("--versions", str(self.root / "absent.md"))
        self.assertEqual((code, lines), (2, []))
        self.assertIn("cannot read", err)

    def test_today_takes_a_date(self):
        code, lines, err = self.run_main("--today", "2026-13-01")
        self.assertEqual((code, lines), (2, []))
        self.assertIn("is not a date YYYY-MM-DD", err)

    def test_the_shipped_list_parses(self):
        versions = cr.parse_versions("model-versions.md", cr.VERSIONS.read_text(encoding="utf-8"))
        self.assertTrue(versions.entries)


class FilesAndOutput(Root):
    def test_discovery_passes_over_the_skipped_directories(self):
        bad = line("K-1", ("kind", "opinion"))
        self.write("skill/maintenance/rules-provenance.md", bad)
        self.write("skill/maintenance/pending-evidence-java.md", bad.replace("K-1", "K-2"))
        for skipped in ("tmp", "trash", "node_modules", "worktrees", "__pycache__", "run-workspace", ".git"):
            self.write(f"{skipped}/rules-provenance.md", bad.replace("K-1", f"K-{skipped}"))
        self.write("skill/notes.md", bad.replace("K-1", "K-9"))
        found = self.findings()
        self.assertEqual([f["path"] for f in found],
                         ["skill/maintenance/pending-evidence-java.md", "skill/maintenance/rules-provenance.md"])

    def test_output_line_and_exit_under_python_isolated(self):
        self.write("rules-provenance.md", UNRECORDED, line("K-1", ("kind", "opinion")))
        run = subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_record.py"), "--root", str(self.root)],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stdout.splitlines(), [
            "rules-provenance.md:4: KIND: kind 'opinion' is outside claim, decision, definition, norm", "1 error(s)"])

    def test_stats(self):
        self.write("rules-provenance.md", NORM, DEFINITION, HYPOTHESIS, REFUTED, UNRECORDED, line("U-2"))
        code, lines, err = self.run_main("--stats")
        self.assertEqual(code, 0, err)
        self.assertEqual(lines, [
            "records by kind: claim 2, decision 0, definition 1, norm 1",
            "claims by standing: contested 0, hypothesis 1, law 0, leading 0, refuted 1, supported 0",
            "rule lines without a record: 2",
            "0 error(s)",
        ])

    def test_stats_change_no_exit_status(self):
        self.write("rules-provenance.md", line("K-1", ("kind", "opinion")))
        self.assertEqual(self.run_main("--stats")[0], 1)
        self.assertIn("records by kind: claim 0, decision 0, definition 0, norm 0, opinion 1", self.run_main("--stats")[1])

    def test_missing_file_exits_2(self):
        run = subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_record.py"), "--root", str(self.root),
                              str(self.root / "absent-provenance.md")], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")
        self.assertIn("cannot read", run.stderr)

    def test_non_utf8_file_exits_2(self):
        (self.root / "rules-provenance.md").write_bytes(b"- **R-1** \xff\n")
        self.assertEqual(self.run_main()[0], 2)


def replace_line(rule: str, key: str, value: str) -> str:
    """The rule line with the value of one field replaced."""
    segments = rule.split(" · ")
    return " · ".join(f"{key}: {value}" if s.startswith(f"{key}: ") else s for s in segments)


class GitModes(Root):
    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.write("rules-provenance.md", NORM, UNRECORDED)
        self.write("pending-evidence.md")
        self.commit("base")

    def git(self, *args: str) -> str:
        run = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", message)

    def test_a_new_line_without_a_record_is_norecord(self):
        self.write("rules-provenance.md", NORM, UNRECORDED, "- **U-2** · new words")
        found = self.findings("--changed")
        self.assertEqual([(f["line"], f["code"]) for f in found], [("5", "NORECORD")])

    def test_an_edited_line_without_a_record_is_norecord(self):
        self.write("rules-provenance.md", NORM, UNRECORDED + ", edited")
        self.assertEqual(self.codes("--changed"), ["NORECORD"])

    def test_an_unchanged_line_without_a_record_passes(self):
        self.write("rules-provenance.md", NORM, UNRECORDED, DEFINITION)
        self.assertEqual(self.codes("--changed"), [])

    def test_unchanged_records_still_pass_the_plain_codes(self):
        self.write("rules-provenance.md", NORM, UNRECORDED, line("K-1", ("kind", "opinion")))
        self.commit("bad record")
        self.assertEqual(self.codes("--changed"), ["KIND"])

    def test_a_result_after_its_committed_hypothesis_passes(self):
        self.write("pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.write("rules-provenance.md", NORM, UNRECORDED, SUPPORTED)
        self.write("pending-evidence.md")
        self.assertEqual(self.codes("--changed"), [])

    def test_a_result_without_a_hypothesis_at_the_base_is_prediction(self):
        self.write("rules-provenance.md", NORM, UNRECORDED, SUPPORTED)
        found = self.findings("--changed")
        self.assertEqual([f["code"] for f in found], ["PREDICTION"])
        self.assertIn("H-1 has no record in . at HEAD", found[0]["message"])

    def test_a_changed_refuter_is_prediction(self):
        self.write("pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.write("pending-evidence.md", replace_line(SUPPORTED, "refuter", "the share is not higher"))
        found = self.findings("--changed")
        self.assertEqual([f["code"] for f in found], ["PREDICTION"])
        self.assertTrue(found[0]["message"].endswith("in refuter"), found[0]["message"])

    def test_prediction_fields_compare_with_white_space_collapsed(self):
        self.write("pending-evidence.md", replace_line(HYPOTHESIS, "measure", "share  of runs   that read the file first"))
        self.commit("hypothesis")
        self.write("pending-evidence.md", SUPPORTED)
        self.assertEqual(self.codes("--changed"), [])

    def test_an_explicit_base(self):
        self.write("pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.commit("later")
        self.write("pending-evidence.md", SUPPORTED)
        self.assertEqual(self.codes("--changed", "--base", "HEAD~1"), [])
        self.assertEqual(self.codes("--changed", "--base", "HEAD~2"), ["PREDICTION"])
        self.assertEqual(self.codes("--changed"), [])

    def test_base_takes_changed(self):
        for args in (["--staged", "--base", "HEAD"], ["--base", "HEAD"]):
            with self.subTest(args):
                code, lines, err = self.run_main(*args)
                self.assertEqual((code, lines), (2, []))
                self.assertIn("--base takes --changed", err)

    def test_a_line_moved_from_the_list_of_hypotheses_to_the_map_passes(self):
        self.write("pending-evidence.md", DEFINITION, HYPOTHESIS)
        self.commit("hypothesis")
        self.write("pending-evidence.md", DEFINITION)
        self.write("rules-provenance.md", NORM, UNRECORDED, SUPPORTED)
        self.assertEqual(self.codes("--changed"), [])

    def test_the_base_is_the_union_of_the_checked_files_alone(self):
        self.write("pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.write("pending-evidence.md")
        self.write("rules-provenance.md", NORM, UNRECORDED, SUPPORTED)
        self.assertEqual(self.codes("--changed", str(self.root / "rules-provenance.md")), ["PREDICTION"])

    def test_a_hypothesis_in_another_directory_is_prediction(self):
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.write("skill-a/maintenance/pending-evidence.md")
        self.write("skill-b/maintenance/rules-provenance.md", SUPPORTED)
        found = self.findings("--changed")
        self.assertEqual([(f["path"], f["code"]) for f in found], [("skill-b/maintenance/rules-provenance.md", "PREDICTION")])

    def test_a_hypothesis_in_the_same_directory_passes(self):
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.write("skill-a/maintenance/pending-evidence.md")
        self.write("skill-a/maintenance/rules-provenance.md", SUPPORTED)
        self.assertEqual(self.codes("--changed"), [])

    def test_a_refuted_id_kept_only_in_another_directory_is_erased(self):
        self.write("skill-a/maintenance/pending-evidence.md", REFUTED)
        self.commit("refuted")
        self.write("skill-a/maintenance/pending-evidence.md")
        self.write("skill-b/maintenance/pending-evidence.md", REFUTED)
        found = self.findings("--changed")
        self.assertEqual([(f["path"], f["code"]) for f in found], [("skill-a/maintenance/pending-evidence.md", "ERASED")])

    def test_a_deleted_map_with_a_refuted_record_is_erased(self):
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS, REFUTED)
        self.commit("refuted")
        (self.root / "skill-a" / "maintenance" / "pending-evidence.md").unlink()
        expected = [("skill-a/maintenance/pending-evidence.md", "4", "ERASED")]
        found = self.findings("--changed")
        self.assertEqual([(f["path"], f["line"], f["code"]) for f in found], expected)
        self.git("add", "-A")
        found = self.findings("--staged")
        self.assertEqual([(f["path"], f["line"], f["code"]) for f in found], expected)

    def test_a_deleted_map_without_a_refuted_record_passes(self):
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS)
        self.write("tmp/pending-evidence.md", REFUTED)
        self.commit("hypothesis")
        (self.root / "skill-a" / "maintenance" / "pending-evidence.md").unlink()
        (self.root / "tmp" / "pending-evidence.md").unlink()
        self.assertEqual(self.codes("--changed"), [])
        self.git("add", "-A")
        self.assertEqual(self.codes("--staged"), [])

    def test_a_deleted_refuted_line_is_erased_at_its_base_position(self):
        self.write("pending-evidence.md", DEFINITION, REFUTED, CONTESTED)
        self.commit("refuted")
        self.write("pending-evidence.md", DEFINITION)
        found = self.findings("--changed")
        self.assertEqual([(f["path"], f["line"], f["code"]) for f in found],
                         [("pending-evidence.md", "4", "ERASED"), ("pending-evidence.md", "5", "ERASED")])

    def test_a_refuted_line_kept_passes(self):
        self.write("pending-evidence.md", DEFINITION, REFUTED)
        self.commit("refuted")
        self.write("pending-evidence.md", REFUTED, DEFINITION)
        self.assertEqual(self.codes("--changed"), [])

    def test_a_deleted_record_that_carries_a_result_is_erased(self):
        self.write("pending-evidence.md", DEFINITION, TRIED, SUPPORTED)
        self.commit("results")
        self.write("pending-evidence.md", DEFINITION)
        found = self.findings("--changed")
        self.assertEqual([(f["line"], f["code"]) for f in found], [("4", "ERASED"), ("5", "ERASED")])
        self.assertIn("H-2, which carries a result at HEAD, has no rule line", found[0]["message"])

    def test_a_moved_directory_keeps_a_record_that_carries_a_result(self):
        self.write("skill-a/maintenance/pending-evidence.md", SUPPORTED, REFUTED, TRIED)
        self.commit("results")
        self.git("mv", "skill-a", "skill-b")
        self.assertEqual(self.codes("--staged"), [])
        self.write("skill-b/maintenance/pending-evidence.md", SUPPORTED, REFUTED)
        self.git("add", "-A")
        found = self.findings("--staged")
        self.assertEqual([(f["path"], f["line"], f["code"]) for f in found], [("skill-b/maintenance/pending-evidence.md", "5", "ERASED")])

    def test_a_leading_record_after_its_committed_hypothesis_passes(self):
        self.write("pending-evidence.md", EVENT_HYPOTHESIS)
        self.commit("hypothesis")
        self.write("pending-evidence.md", LEADING)
        self.assertEqual(self.codes("--changed"), [])
        self.write("pending-evidence.md", replace_line(LEADING, "event", "the outage of 2026-10-15"))
        found = self.findings("--changed")
        self.assertEqual([f["code"] for f in found], ["PREDICTION"])
        self.assertTrue(found[0]["message"].endswith("in event"), found[0]["message"])

    def test_a_leading_record_without_its_hypothesis_at_the_base_is_prediction(self):
        self.write("pending-evidence.md", LEADING)
        self.assertEqual(self.codes("--changed"), ["PREDICTION"])

    def test_a_deleted_hypothesis_line_passes(self):
        self.write("pending-evidence.md", DEFINITION, HYPOTHESIS)
        self.commit("hypothesis")
        self.write("pending-evidence.md", DEFINITION)
        self.assertEqual(self.codes("--changed"), [])

    def test_staged_reads_the_index(self):
        self.write("rules-provenance.md", NORM, UNRECORDED, "- **U-2** · new words")
        self.git("add", "rules-provenance.md")
        self.write("rules-provenance.md", NORM, UNRECORDED, DEFINITION)
        self.assertEqual(self.codes("--staged"), ["NORECORD"])
        self.assertEqual(self.codes("--changed"), [])

    def test_staged_erasure_and_prediction(self):
        self.write("pending-evidence.md", HYPOTHESIS, REFUTED)
        self.commit("hypothesis and refuted")
        self.write("pending-evidence.md", replace_line(SUPPORTED, "threshold", "five points"))
        self.git("add", "pending-evidence.md")
        self.assertEqual(sorted(self.codes("--staged")), ["ERASED", "PREDICTION"])

    def test_staged_reads_a_path_absent_from_the_index_as_empty(self):
        self.write("new-provenance.md", "- **U-3** · words")
        self.assertEqual(self.codes("--staged"), [])
        self.assertEqual(self.codes("--changed"), ["NORECORD"])

    def move_skill_a_with_its_result(self) -> None:
        """skill-a holds a supported claim after its hypothesis, a refuted claim and an unrecorded line; git mv names it skill-b."""
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS, REFUTED)
        self.write("skill-a/maintenance/rules-provenance.md", NORM, UNRECORDED)
        self.commit("hypothesis")
        self.write("skill-a/maintenance/pending-evidence.md", SUPPORTED, REFUTED)
        self.commit("result")
        self.git("mv", "skill-a", "skill-b")

    def test_a_moved_directory_keeps_the_history_of_its_records(self):
        self.move_skill_a_with_its_result()
        self.assertEqual(self.codes("--staged"), [])
        self.assertEqual(self.codes("--changed"), [])
        self.assertEqual(self.codes("--staged", str(self.root / "skill-b" / "maintenance" / "pending-evidence.md")), [])

    def test_a_moved_directory_is_compared_with_the_base_that_registered_its_hypothesis(self):
        self.move_skill_a_with_its_result()
        self.assertEqual(self.codes("--changed", "--base", "HEAD~1"), [])
        self.write("skill-b/maintenance/pending-evidence.md", replace_line(SUPPORTED, "threshold", "five points"), REFUTED)
        found = self.findings("--changed", "--base", "HEAD~1")
        self.assertEqual([(f["path"], f["code"]) for f in found], [("skill-b/maintenance/pending-evidence.md", "PREDICTION")])

    def test_a_refuted_line_dropped_in_the_move_is_erased_at_the_current_path(self):
        self.move_skill_a_with_its_result()
        self.write("skill-b/maintenance/pending-evidence.md", SUPPORTED)
        self.write("skill-b/maintenance/rules-provenance.md", NORM, UNRECORDED, "- **U-2** · new words")
        self.git("add", "-A")
        found = self.findings("--staged")
        self.assertEqual([(f["path"], f["line"], f["code"]) for f in found],
                         [("skill-b/maintenance/pending-evidence.md", "4", "ERASED"),
                          ("skill-b/maintenance/rules-provenance.md", "5", "NORECORD")])

    def test_a_moved_directory_keeps_its_history_when_a_map_is_rewritten_beyond_half(self):
        self.move_skill_a_with_its_result()
        added = [claim(f"H-{n}", "hypothesis") for n in range(2, 9)]
        self.write("skill-b/maintenance/pending-evidence.md", SUPPORTED, REFUTED, *added)
        self.git("add", "-A")
        status = self.git("diff", "--cached", "-M", "--name-status", "HEAD")
        self.assertIn("A\tskill-b/maintenance/pending-evidence.md", status)
        self.assertIn("\tskill-a/maintenance/rules-provenance.md\tskill-b/maintenance/rules-provenance.md", status)
        self.assertEqual(self.codes("--staged"), [])
        self.assertEqual(self.codes("--changed"), [])

    def test_a_rewritten_map_whose_neighbours_did_not_move_starts_without_history(self):
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS)
        self.write("skill-a/maintenance/rules-provenance.md", NORM)
        self.commit("hypothesis")
        added = [claim(f"H-{n}", "hypothesis") for n in range(2, 9)]
        self.git("rm", "-q", "skill-a/maintenance/pending-evidence.md")
        self.write("skill-b/maintenance/pending-evidence.md", SUPPORTED, *added)
        self.git("add", "-A")
        found = self.findings("--staged")
        self.assertEqual([(f["path"], f["code"]) for f in found], [("skill-b/maintenance/pending-evidence.md", "PREDICTION")])

    def test_a_map_copied_to_another_directory_starts_without_history(self):
        self.write("skill-a/maintenance/pending-evidence.md", HYPOTHESIS)
        self.commit("hypothesis")
        self.write("skill-b/maintenance/pending-evidence.md", SUPPORTED)
        self.git("add", "-A")
        found = self.findings("--staged")
        self.assertEqual([(f["path"], f["code"]) for f in found], [("skill-b/maintenance/pending-evidence.md", "PREDICTION")])

    def test_review_is_held_on_a_changed_line_and_a_due_term_fails_no_commit(self):
        versions = self.root / "versions.md"
        versions.write_text(VERSIONS_LIST, encoding="utf-8")
        listed = ("--versions", str(versions), *TODAY)
        bare = claim("R-1", "supported", *EXTERNAL_RESULT, prediction=on_model("agents on Model A 5.5"))
        self.write("rules-provenance.md", NORM, UNRECORDED, bare)
        self.commit("a supported claim before the field")
        self.assertEqual(self.codes("--changed", *listed), [])
        self.write("rules-provenance.md", NORM, UNRECORDED, replace_line(bare, "result", "r, read again"))
        self.assertEqual(self.codes("--changed", *listed), ["REVIEW"])
        self.write("rules-provenance.md", NORM, UNRECORDED, bare + " · review: 2026-01-01")
        self.git("add", "-A")
        self.assertEqual(self.codes("--staged", *listed), [])
        self.assertEqual([n[2] for n in self.notices("--staged", *listed)],
                         ["R-1 is due to be read again: its review date 2026-01-01 has come"])

    def test_a_hypothesis_with_a_published_test_is_held_on_a_changed_line_alone(self):
        published = claim("B-1", "hypothesis", ("test", FIRST_HAND), ("result", "r"), prediction=PREDICTION[:4])
        self.write("pending-evidence.md", published)
        self.commit("a hypothesis before the field")
        self.assertEqual(self.codes("--changed"), [])
        self.write("pending-evidence.md", replace_line(published, "result", "r, read again"))
        self.assertEqual(self.codes("--changed"), ["BESIDE"])
        self.write("pending-evidence.md", replace_line(published, "test", "unused").replace("test: unused", f"beside: {FIRST_HAND}")
                   .replace("result: r", "beside-result: r"))
        self.git("add", "-A")
        self.assertEqual(self.codes("--staged"), [])

    def test_an_unknown_base_exits_2(self):
        code, lines, err = self.run_main("--changed", "--base", "no-such-revision")
        self.assertEqual((code, lines), (2, []))
        self.assertIn("no-such-revision is not a revision", err)


class OutsideGit(Root):
    def test_a_comparing_mode_outside_a_repository_exits_2(self):
        self.write("rules-provenance.md", NORM)
        top = Path(self.tmp.name)
        ceiling = os.pathsep.join({str(top), str(top.resolve())})
        for mode in ("--changed", "--staged"):
            with self.subTest(mode), mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": ceiling}):
                run = subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_record.py"), "--root", str(self.root), mode],
                                     capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(run.returncode, 2, run.stdout)
                self.assertEqual(run.stdout, "")
                self.assertIn("git rev-parse --show-toplevel failed", run.stderr)


if __name__ == "__main__":
    unittest.main()
