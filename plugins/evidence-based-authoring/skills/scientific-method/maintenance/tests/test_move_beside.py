"""move_beside.py: the published sources of every hypothesis moved from `test` to `beside`."""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "maintenance" / "scripts" / "move_beside.py"
sys.path[:0] = [str(SCRIPT.parent), str(SKILL / "scripts")]
import check_record as cr  # noqa: E402
import move_beside as mb  # noqa: E402

CLAIM = ("kind: claim · standing: hypothesis · measure: share of runs · against: the same prompt without the paragraph"
         " · scope: one model · refuter: under ten points")
FIRST_HAND = "external doi:10.1/x §4 first-hand"
ABSTRACT = "external doi:10.2/y abstract"
RELAY = "external a blog post relay"
OWN = "own evals/a.json"


def hypothesis(rid: str, *fields: str, free: str = "a claim · with: a colon") -> str:
    return " · ".join([f"- **{rid}**", free, CLAIM, *fields])


PUBLISHED = hypothesis("H-1", f"test: {FIRST_HAND}; {ABSTRACT}", "result: one way; the other", "bounds: students", "review: none")
MOVED = hypothesis("H-1", f"beside: {FIRST_HAND}; {ABSTRACT}", "beside-result: one way; the other", "beside-bounds: students",
                   "review: none")


class Root(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "evals").mkdir()
        (self.root / "evals" / "a.json").write_text("{}\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, *lines: str, ending: str = "\n") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(("# Hypotheses" + ending + ending + "".join(l + ending for l in lines)).encode("utf-8"))
        return path

    def run_main(self, *args: str) -> tuple[int, list[str], str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = mb.main(["--root", str(self.root), *args])
            except SystemExit as usage:
                code = usage.code
        return code, out.getvalue().splitlines(), err.getvalue()

    def moved(self, *lines: str) -> tuple[list[str], list[str]]:
        """The list's rule lines after one run, and the run's output."""
        path = self.write("pending-evidence.md", *lines)
        code, out, err = self.run_main()
        self.assertNotEqual(code, 2, err)
        return path.read_text(encoding="utf-8").splitlines()[2:], out


class Moving(Root):
    def test_the_published_sources_result_and_bounds_move_in_place(self):
        lines, out = self.moved(PUBLISHED)
        self.assertEqual(lines, [MOVED])
        self.assertEqual(out, [
            "pending-evidence.md:3: MOVED H-1: 2 to beside",
            "pending-evidence.md: 1 moved, 0 left; test entries 2 -> 0, beside entries 0 -> 2",
            "1 moved, 0 left in 1 file(s)",
        ])

    def test_a_test_of_our_own_stays_beside_follows_it_and_result_moves_whole(self):
        line = hypothesis("H-2", "threshold: ten points", "runs: ten per arm", f"test: {RELAY}; {OWN}; {FIRST_HAND}",
                          "result: what the sources showed", "bounds: other readers")
        lines, out = self.moved(line)
        self.assertEqual(lines, [hypothesis("H-2", "threshold: ten points", "runs: ten per arm", f"test: {OWN}",
                                            f"beside: {RELAY}; {FIRST_HAND}", "beside-result: what the sources showed",
                                            "beside-bounds: other readers")])
        self.assertEqual(out[0], "pending-evidence.md:3: MOVED H-2: 2 to beside, 1 own kept in test")

    def test_the_measure_check_of_a_source_stays_on_the_moved_line(self):
        line = hypothesis("H-3", "validity: labels: two raters, r = .95", f"test: {FIRST_HAND}", "result: r", "bounds: b")
        lines, out = self.moved(line)
        self.assertEqual(lines, [hypothesis("H-3", "validity: labels: two raters, r = .95", f"beside: {FIRST_HAND}",
                                            "beside-result: r", "beside-bounds: b")])
        self.assertEqual(out[0], "pending-evidence.md:3: MOVED H-3: 1 to beside")

    def test_every_other_byte_stays(self):
        free = "a source · test: external doi:10.9/z first-hand · in free text"
        path = self.write("pending-evidence.md", "Prose · test: x", hypothesis("H-3", f"test:  {FIRST_HAND}", free=free) + "  ",
                          PUBLISHED, ending="\r\n")
        path.write_bytes(path.read_bytes() + b"- **H-4** \xc2\xb7 no record")
        self.run_main()
        self.assertEqual(path.read_bytes().decode("utf-8"),
                         "# Hypotheses\r\n\r\nProse · test: x\r\n"
                         + hypothesis("H-3", f"beside:  {FIRST_HAND}", free=free) + "  \r\n"
                         + MOVED + "\r\n- **H-4** · no record")

    def test_a_second_run_moves_nothing(self):
        path = self.write("pending-evidence.md", PUBLISHED)
        self.run_main()
        after = path.read_bytes()
        code, out, _ = self.run_main()
        self.assertEqual((code, out), (0, ["0 moved, 0 left in 0 file(s)"]))
        self.assertEqual(path.read_bytes(), after)

    def test_the_moved_list_passes_the_record_check_under_require(self):
        self.write("pending-evidence.md", PUBLISHED, hypothesis("H-2", "runs: ten per arm", "threshold: t",
                                                                f"test: {OWN}; {FIRST_HAND}", "bounds: b"))
        before = io.StringIO()
        with contextlib.redirect_stdout(before):
            self.assertEqual(cr.main(["--root", str(self.root), "--require"]), 1)
        self.assertEqual([l.split(": ")[1] for l in before.getvalue().splitlines()[:-1]], ["BESIDE", "BESIDE"])
        self.run_main()
        after = io.StringIO()
        with contextlib.redirect_stdout(after):
            self.assertEqual(cr.main(["--root", str(self.root), "--require"]), 0, after.getvalue())


class NotMoved(Root):
    def test_lines_that_are_no_candidate_stay_unreported(self):
        lines = [
            hypothesis("H-1", f"test: {OWN}", "threshold: t", "runs: r"),
            hypothesis("H-2", "result: a run of our own that failed its checks"),
            hypothesis("H-3"),
            hypothesis("H-4", f"beside: {FIRST_HAND}", "beside-result: r"),
            PUBLISHED.replace("H-1", "S-1").replace("standing: hypothesis", "standing: refuted"),
            "- **D-1** · kind: decision · owner: the owner · goal: g · test: external x first-hand",
            "- **U-1** · " + f"test: {FIRST_HAND} · standing: hypothesis",
        ]
        after, out = self.moved(*lines)
        self.assertEqual(after, lines)
        self.assertEqual(out, ["0 moved, 0 left in 0 file(s)"])

    def test_a_line_whose_fields_need_judgement_is_left_and_reported(self):
        cases = {
            "fit": ("fit: direct", "carries fit, a field that describes a test"),
            "fit and transfer": ("fit: transfer · transfer: t", "carries fit, transfer, fields that describe a test"),
            "beside already": (f"beside: {ABSTRACT}", "carries beside already"),
            "an entry outside the forms": (None, "its test holds an entry outside the four forms"),
            "a key twice": ("bounds: again", "writes bounds twice"),
        }
        lines = {
            "an entry outside the forms": hypothesis("H-1", f"test: {FIRST_HAND}; a paper I read", "result: r"),
        }
        for name, (extra, reason) in cases.items():
            with self.subTest(name):
                line = lines.get(name) or f"{PUBLISHED} · {extra}"
                path = self.write("pending-evidence.md", line)
                code, out, _ = self.run_main()
                self.assertEqual(code, 1)
                self.assertEqual(out[0], f"pending-evidence.md:3: LEFT H-1: {reason}")
                self.assertEqual(out[-1], "0 moved, 1 left in 1 file(s)")
                self.assertEqual(path.read_text(encoding="utf-8").splitlines()[2], line)

    def test_a_left_line_does_not_stop_the_others(self):
        lines, out = self.moved(f"{PUBLISHED} · fit: direct", PUBLISHED.replace("H-1", "H-2"))
        self.assertEqual(lines, [f"{PUBLISHED} · fit: direct", MOVED.replace("H-1", "H-2")])
        self.assertEqual(out[-2:], ["pending-evidence.md: 1 moved, 1 left; test entries 4 -> 2, beside entries 0 -> 2",
                                    "1 moved, 1 left in 1 file(s)"])


class FilesAndOutput(Root):
    def test_discovery_takes_the_maps_and_passes_over_the_skipped_directories(self):
        self.write("skill/maintenance/pending-evidence-java.md", PUBLISHED)
        self.write("skill/maintenance/rules-provenance.md", PUBLISHED.replace("H-1", "H-2"))
        self.write("skill/notes.md", PUBLISHED)
        self.write("tmp/pending-evidence.md", PUBLISHED)
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual([l for l in out if " MOVED " in l],
                         ["skill/maintenance/pending-evidence-java.md:3: MOVED H-1: 2 to beside",
                          "skill/maintenance/rules-provenance.md:3: MOVED H-2: 2 to beside"])
        self.assertIn("test: ", (self.root / "skill" / "notes.md").read_text(encoding="utf-8"))
        self.assertIn("test: ", (self.root / "tmp" / "pending-evidence.md").read_text(encoding="utf-8"))

    def test_a_named_file_alone_is_moved(self):
        named = self.write("a/pending-evidence.md", PUBLISHED)
        other = self.write("b/pending-evidence.md", PUBLISHED)
        self.run_main(str(named))
        self.assertIn("beside: ", named.read_text(encoding="utf-8"))
        self.assertNotIn("beside: ", other.read_text(encoding="utf-8"))

    def test_dry_run_writes_nothing(self):
        path = self.write("pending-evidence.md", PUBLISHED)
        before = path.read_bytes()
        code, out, _ = self.run_main("--dry-run")
        self.assertEqual((code, out[0]), (0, "pending-evidence.md:3: MOVED H-1: 2 to beside"))
        self.assertEqual(path.read_bytes(), before)

    def test_unreadable_input_exits_2_and_writes_nothing(self):
        good = self.write("a/pending-evidence.md", PUBLISHED)
        (self.root / "b").mkdir()
        (self.root / "b" / "pending-evidence.md").write_bytes(b"- **H-1** \xff\n")
        code, out, err = self.run_main()
        self.assertEqual((code, out), (2, []))
        self.assertIn("cannot read", err)
        self.assertIn("test: ", good.read_text(encoding="utf-8"))
        code, out, err = self.run_main(str(self.root / "absent-provenance.md"))
        self.assertEqual((code, out), (2, []))
        code, out, err = self.run_main("--root", str(self.root / "absent"))
        self.assertEqual(code, 2)

    def test_the_script_runs_under_python_isolated(self):
        path = self.write("pending-evidence.md", PUBLISHED)
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root)],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.splitlines()[-1], "1 moved, 0 left in 1 file(s)")
        self.assertEqual(path.read_text(encoding="utf-8").splitlines()[2], MOVED)


if __name__ == "__main__":
    unittest.main()
