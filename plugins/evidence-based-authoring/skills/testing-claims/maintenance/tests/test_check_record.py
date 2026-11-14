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
              ("bounds", "one model, one repository"), ("fit", "direct"))


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
LAW = claim("L-1", "law", *replace(OWN_RESULT, "test", f"own evals/a.json; {FIRST_HAND}"))
CONTESTED = claim("X-1", "contested", ("test", f"{FIRST_HAND}; external doi:10.2/y first-hand"), ("result", "one for, one against"))
REFUTED = claim("F-1", "refuted", ("test", FIRST_HAND), ("result", "no difference in 40 runs"), ("bounds", "one model"))
UNRECORDED = "- **U-1** · a source and its words, no record"


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
        code, lines, err = self.run_main(*args)
        self.assertNotEqual(code, 2, err)
        found = [FINDING.match(l).groupdict() for l in lines if FINDING.match(l)]
        self.assertEqual(lines[-1], f"{len(found)} error(s)")
        self.assertEqual(code, 1 if found else 0)
        return found

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
        self.assertIn("records by kind: claim 1, decision 0, definition 0, norm 1", lines)
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
        with self.subTest("a hypothesis with external tests only or no test needs no threshold or runs"):
            self.assertEqual(self.check_lines(claim("F-11", "hypothesis", ("test", RELAY), prediction=PREDICTION[:4]),
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
            "claims by standing: contested 0, hypothesis 1, law 0, refuted 1, supported 0",
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
