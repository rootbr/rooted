"""apply_records.py: the records and hypotheses of result files carried into a provenance map and its list of hypotheses."""
from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "maintenance" / "scripts" / "apply_records.py"
sys.path.insert(0, str(SCRIPT.parent))
import apply_records as ar  # noqa: E402

MAP = ("# Provenance of a skill\n"
       "\n"
       "Each line names what its rule rests on — § Lines and files.  \n"
       "\n"
       "- **R-1** · the first rule · Smith 2024 §3\n"
       "- **R-10** · the tenth rule\n"
       "- **R-2** · the second rule · kind: norm · issuer: IEEE · version: 1003.1-2024 · locator: §2.8.2\n"
       "- **R-3** · the third rule\n")
LIST = ("# Hypotheses\n"
        "\n"
        "- **H-01** · an old hypothesis · kind: claim · standing: hypothesis\n")
NORM = "kind: norm · issuer: IEEE · version: 1003.1-2024 · locator: §2.8.2"
FOURTH = ("- **R-4**, and R-5 by the same source · the fourth rule"
          " · kind: norm · issuer: IETF · version: RFC 9110 · locator: §15\n")
REWORDED_H01 = "- **H-01** · the same id, reworded · kind: claim · standing: hypothesis"
SUMMARY_CODES = ("recorded", "replaced", "reworded", "kept", "added", "missing", "bad")


def record(rule_id: str) -> str:
    return f"kind: decision · owner: the repository owner · goal: {rule_id} is kept"


def hypothesis(hypothesis_id: str) -> str:
    return f"- **{hypothesis_id}** · a claim behind the rule · kind: claim · standing: hypothesis"


def rule(rule_id: str, record_text: str | None = None, **fields: object) -> dict:
    """A result rule with the record of record(), no hypotheses, sources or corrections and no note; `fields` replace them."""
    return {"id": rule_id, "kind": "decision", "record": record(rule_id) if record_text is None else record_text,
            "hypotheses": [], "sources": [], "corrections": [], "notes": "", **fields}


def worded(rule_id: str, text: str, **fields: object) -> dict:
    """A result rule of rule() that carries `text` and no record."""
    carried = rule(rule_id, text=text, **fields)
    del carried["record"]
    return carried


def summary(**counts: int) -> str:
    """The summary line with the given counts and 0 for every other code."""
    return ", ".join(f"{counts.get(code, 0)} {code}" for code in SUMMARY_CODES)


def recorded(text: str, rule_id: str) -> str:
    """The text with the record of rule() appended to the line of `rule_id`."""
    lines = text.split("\n")
    index = next(i for i, line in enumerate(lines) if line.startswith(f"- **{rule_id}**"))
    lines[index] += f" · {record(rule_id)}"
    return "\n".join(lines)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="apply-records-")
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.map = self.dir / "method-provenance.md"
        self.list = self.dir / "pending-evidence.md"
        self.reset()

    def reset(self, map_text: str = MAP, list_text: str = LIST) -> None:
        self.map.write_bytes(map_text.encode("utf-8"))
        self.list.write_bytes(list_text.encode("utf-8"))

    def result(self, name: str, *rules: dict, unopened: tuple[str, ...] = ()) -> str:
        path = self.dir / name
        path.write_text(json.dumps({"rules": list(rules), "unopened": list(unopened)}, ensure_ascii=False),
                        encoding="utf-8")
        return str(path)

    def run_main(self, *args: str) -> tuple[int, list[str], str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = ar.main(list(args))
            except SystemExit as usage:
                code = usage.code
        return code, out.getvalue().splitlines(), err.getvalue()

    def apply(self, *results: str, options: tuple[str, ...] = ()) -> tuple[int, list[str], str]:
        return self.run_main("--map", str(self.map), "--hypotheses", str(self.list), *options, *results)

    def files(self) -> tuple[str, str]:
        return self.map.read_text(encoding="utf-8"), self.list.read_text(encoding="utf-8")

    def assertUntouched(self) -> None:
        self.assertEqual(self.files(), (MAP, LIST))


class Recording(Base):
    def test_a_record_is_appended_to_its_line_and_every_other_byte_stays(self):
        code, lines, err = self.apply(self.result("a.json", rule("R-1")))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(lines, ["RECORDED R-1", "1 recorded, 0 replaced, 0 reworded, 0 kept, 0 added, 0 missing, 0 bad"])
        self.assertEqual(self.map.read_bytes(), recorded(MAP, "R-1").encode("utf-8"))
        self.assertEqual(self.list.read_bytes(), LIST.encode("utf-8"))

    def test_a_line_with_crlf_endings_takes_its_record_before_the_cr(self):
        self.reset(map_text=MAP.replace("\n", "\r\n"))
        self.assertEqual(self.apply(self.result("a.json", rule("R-3")))[0], 0)
        self.assertEqual(self.map.read_bytes(), recorded(MAP, "R-3").replace("\n", "\r\n").encode("utf-8"))

    def test_a_line_that_carries_a_record_is_kept_and_a_second_run_writes_nothing(self):
        path = self.result("a.json", rule("R-1"), rule("R-2"))
        self.assertEqual(self.apply(path)[1], ["RECORDED R-1", "KEPT R-2",
                                               "1 recorded, 0 replaced, 0 reworded, 1 kept, 0 added, 0 missing, 0 bad"])
        first = self.files()
        self.assertEqual(first[0], recorded(MAP, "R-1"))
        inodes = (self.map.stat().st_ino, self.list.stat().st_ino)
        code, lines, _ = self.apply(path)
        self.assertEqual((code, lines), (0, ["KEPT R-1", "KEPT R-2",
                                             "0 recorded, 0 replaced, 0 reworded, 2 kept, 0 added, 0 missing, 0 bad"]))
        self.assertEqual(self.files(), first)
        self.assertEqual((self.map.stat().st_ino, self.list.stat().st_ino), inodes)

    def test_a_segment_opening_kind_after_a_separator_is_a_record(self):
        for tail in (" · kind: norm", " · kind:norm", " · free text · kind: decision · owner: x"):
            with self.subTest(tail=tail):
                text = MAP.replace("- **R-3** · the third rule\n", f"- **R-3** · the third rule{tail}\n")
                self.reset(map_text=text)
                self.assertEqual(self.apply(self.result("a.json", rule("R-3")))[1][0], "KEPT R-3")
                self.assertEqual(self.map.read_text(encoding="utf-8"), text)

    def test_a_missing_id_is_reported_and_the_other_rules_of_the_file_are_applied(self):
        path = self.result("a.json", rule("R-9"), rule("R-1"), rule("R-3"))
        code, lines, err = self.apply(path)
        self.assertEqual(code, 1)
        self.assertEqual(lines, ["MISSING R-9", "RECORDED R-1", "RECORDED R-3",
                                 "2 recorded, 0 replaced, 0 reworded, 0 kept, 0 added, 1 missing, 0 bad"])
        self.assertEqual(self.map.read_text(encoding="utf-8"), recorded(recorded(MAP, "R-1"), "R-3"))
        self.assertEqual(err, f"MISSING R-9: no rule line of the map opens `- **R-9**` ({path})\n")

    def test_a_malformed_record_is_bad_and_nothing_is_written_for_its_rule(self):
        no_kind, line_break = "the record does not open with `kind: `", "the record holds a line break"
        records = {
            "no kind": ("decision · owner: the repository owner", no_kind),
            "kind with no space": ("kind:decision · owner: the repository owner", no_kind),
            "a line feed": ("kind: decision\n · owner: the repository owner", line_break),
            "a line separator": ("kind: decision · owner: the repository\u2028owner", line_break),
        }
        for name, (text, reason) in records.items():
            with self.subTest(name):
                self.reset()
                path = self.result("a.json", rule("R-1", text, hypotheses=(hypothesis("H-R-1"),)), rule("R-3"))
                code, lines, err = self.apply(path)
                self.assertEqual(code, 1)
                self.assertEqual(lines, ["BAD R-1", "RECORDED R-3",
                                         "1 recorded, 0 replaced, 0 reworded, 0 kept, 0 added, 0 missing, 1 bad"])
                self.assertEqual(self.files(), (recorded(MAP, "R-3"), LIST))
                self.assertEqual(err, f"BAD R-1: {reason} ({path})\n")

    def test_an_id_on_two_rule_lines_of_the_map_is_bad_and_nothing_is_written_for_it(self):
        text = MAP + "- **R-3** · the third rule, a second source\n"
        self.reset(map_text=text)
        path = self.result("a.json", rule("R-3", hypotheses=(hypothesis("H-R-3"),)))
        code, lines, err = self.apply(path)
        self.assertEqual((code, lines), (1, ["BAD R-3", "0 recorded, 0 replaced, 0 reworded, 0 kept, 0 added, 0 missing, 1 bad"]))
        self.assertEqual(self.files(), (text, LIST))
        self.assertEqual(err, f"BAD R-3: the id stands on the rule lines 8, 9 of the map ({path})\n")


class Hypotheses(Base):
    def test_a_hypothesis_is_appended_once_and_kept_on_the_second_run(self):
        path = self.result("a.json", rule("R-1", hypotheses=(hypothesis("H-R-1"),)))
        code, lines, _ = self.apply(path)
        self.assertEqual((code, lines), (0, ["RECORDED R-1", "ADDED H-R-1",
                                             "1 recorded, 0 replaced, 0 reworded, 0 kept, 1 added, 0 missing, 0 bad"]))
        self.assertEqual(self.list.read_text(encoding="utf-8"), f"{LIST}\n{hypothesis('H-R-1')}\n")
        first = self.files()
        code, lines, _ = self.apply(path)
        self.assertEqual((code, lines), (0, ["KEPT R-1", "KEPT H-R-1",
                                             "0 recorded, 0 replaced, 0 reworded, 2 kept, 0 added, 0 missing, 0 bad"]))
        self.assertEqual(self.files(), first)

    def test_a_hypothesis_whose_id_the_list_holds_is_kept_as_the_list_words_it(self):
        reworded = "- **H-01** · the same id, reworded · kind: claim · standing: hypothesis"
        code, lines, _ = self.apply(self.result("a.json", rule("R-1", hypotheses=(reworded,))))
        self.assertEqual((code, lines), (0, ["RECORDED R-1", "KEPT H-01",
                                             "1 recorded, 0 replaced, 0 reworded, 1 kept, 0 added, 0 missing, 0 bad"]))
        self.assertEqual(self.list.read_text(encoding="utf-8"), LIST)

    def test_hypotheses_are_appended_in_the_order_of_the_results_and_an_id_appended_before_is_kept(self):
        first = self.result("a.json", rule("R-3", hypotheses=(hypothesis("H-R-3"), hypothesis("H-shared"))))
        second = self.result("b.json", rule("R-1", hypotheses=(hypothesis("H-R-1"), hypothesis("H-shared"))))
        code, lines, _ = self.apply(first, second)
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["RECORDED R-3", "RECORDED R-1", "ADDED H-R-3", "ADDED H-shared", "ADDED H-R-1",
                                 "KEPT H-shared", "2 recorded, 0 replaced, 0 reworded, 1 kept, 3 added, 0 missing, 0 bad"])
        added = "".join(f"{hypothesis(h)}\n" for h in ("H-R-3", "H-shared", "H-R-1"))
        self.assertEqual(self.list.read_text(encoding="utf-8"), f"{LIST}\n{added}")

    def test_appended_lines_follow_one_blank_line_and_the_file_s_line_ending(self):
        line = hypothesis("H-9")
        cases = {
            "ends with a line": ("a\n", f"a\n\n{line}\n"),
            "ends with a blank line": ("a\n\n", f"a\n\n{line}\n"),
            "ends with a line of spaces": ("a\n  \n", f"a\n  \n{line}\n"),
            "has no final line feed": ("a", f"a\n\n{line}\n"),
            "has CRLF endings": ("# H\r\na\r\n", f"# H\r\na\r\n\r\n{line}\r\n"),
            "is empty": ("", f"{line}\n"),
        }
        for name, (text, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(ar.Markdown(text).with_lines_appended([line]), expected)

    def test_a_malformed_hypothesis_line_is_bad_and_its_rule_writes_nothing(self):
        no_opening = "does not open `- **<id>** · `"
        lines_by_case = {
            "no bullet": ("H-R-1 · a claim · kind: claim", "R-1", no_opening),
            "no separator after the id": ("- **H-R-1** a claim · kind: claim", "H-R-1", no_opening),
            "a line break": ("- **H-R-1** · a claim\n · kind: claim", "H-R-1", "holds a line break"),
        }
        for name, (line, named, reason) in lines_by_case.items():
            with self.subTest(name):
                self.reset()
                path = self.result("a.json", rule("R-1", hypotheses=(hypothesis("H-R-1a"), line)))
                code, lines, err = self.apply(path)
                self.assertEqual((code, lines), (1, ["BAD R-1", f"BAD {named}",
                                                     "0 recorded, 0 replaced, 0 reworded, 0 kept, 0 added, 0 missing, 2 bad"]))
                self.assertUntouched()
                self.assertEqual(err, f"BAD R-1: a hypothesis line of the rule is BAD, so the record is not written ({path})\n"
                                      f"BAD {named}: hypothesis line 2 of R-1 {reason} ({path})\n")

    def test_a_malformed_hypothesis_line_keeps_out_the_other_lines_of_a_rule_already_recorded(self):
        path = self.result("a.json", rule("R-2", hypotheses=(hypothesis("H-R-2"), "H-R-2b · no bullet")))
        code, lines, _ = self.apply(path)
        self.assertEqual((code, lines), (1, ["KEPT R-2", "BAD R-2",
                                             "0 recorded, 0 replaced, 0 reworded, 1 kept, 0 added, 0 missing, 1 bad"]))
        self.assertUntouched()


class Replacing(Base):
    def replace(self, *results: str) -> tuple[int, list[str], str]:
        return self.apply(*results, options=("--replace",))

    def test_a_record_is_replaced_and_the_text_and_every_other_byte_stay(self):
        for name, newline in (("LF", "\n"), ("CRLF", "\r\n")):
            with self.subTest(name):
                self.reset(map_text=MAP.replace("\n", newline))
                code, lines, err = self.replace(self.result("a.json", rule("R-2")))
                self.assertEqual((code, lines, err), (0, ["REPLACED R-2", summary(replaced=1)], ""))
                self.assertEqual(self.map.read_bytes(), MAP.replace(NORM, record("R-2")).replace("\n", newline).encode("utf-8"))
                self.assertEqual(self.list.read_bytes(), LIST.encode("utf-8"))

    def test_a_text_is_replaced_and_the_record_and_every_other_line_stay(self):
        cases = {
            "an id followed by a separator": ("R-2", " · the second rule", " · the second rule, worded anew"),
            "an id followed by a clause": ("R-4", ", and R-5 by the same source · the fourth rule",
                                           ", and R-5 by one source · the fourth rule, worded anew"),
            "a line that carries no record": ("R-3", " · the third rule", " · the third rule, worded anew"),
        }
        for name, (rule_id, in_place, text) in cases.items():
            with self.subTest(name):
                self.reset(map_text=MAP + FOURTH)
                code, lines, _ = self.replace(self.result("a.json", worded(rule_id, text)))
                self.assertEqual((code, lines), (0, [f"KEPT {rule_id}", f"REWORDED {rule_id}", summary(reworded=1, kept=1)]))
                expected = (MAP + FOURTH).replace(f"- **{rule_id}**{in_place}", f"- **{rule_id}**{text}")
                self.assertEqual(self.files(), (expected, LIST))

    def test_the_record_and_the_text_of_one_rule_are_replaced_in_one_run(self):
        code, lines, _ = self.replace(self.result("a.json", rule("R-2", text=" · the second rule, worded anew")))
        self.assertEqual((code, lines), (0, ["REPLACED R-2", "REWORDED R-2", summary(replaced=1, reworded=1)]))
        self.assertEqual(self.files(), (MAP.replace(f" · the second rule · {NORM}",
                                                    f" · the second rule, worded anew · {record('R-2')}"), LIST))

    def test_the_same_results_applied_twice_are_kept_and_written_nothing_the_second_time(self):
        path = self.result("a.json",
                           rule("R-2", text=" · the second rule, worded anew", hypotheses=(REWORDED_H01, hypothesis("H-R-2"))),
                           rule("R-3", text=" · the third rule, worded anew"))
        code, lines, _ = self.replace(path)
        self.assertEqual((code, lines), (0, ["REPLACED R-2", "REWORDED R-2", "RECORDED R-3", "REWORDED R-3", "REPLACED H-01",
                                             "ADDED H-R-2", summary(recorded=1, replaced=2, reworded=2, added=1)]))
        first = self.files()
        inodes = (self.map.stat().st_ino, self.list.stat().st_ino)
        code, lines, _ = self.replace(path)
        self.assertEqual((code, lines), (0, ["KEPT R-2", "KEPT R-3", "KEPT H-01", "KEPT H-R-2", summary(kept=4)]))
        self.assertEqual(self.files(), first)
        self.assertEqual((self.map.stat().st_ino, self.list.stat().st_ino), inodes)

    def test_without_replace_a_text_is_not_read_and_its_rule_is_kept(self):
        path = self.result("a.json", rule("R-2", text=" · the second rule, worded anew"),
                           worded("R-3", " · the third rule\nbroken"), rule("R-1", hypotheses=(REWORDED_H01,)))
        code, lines, err = self.apply(path)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(lines, ["KEPT R-2", "KEPT R-3", "RECORDED R-1", "KEPT H-01", summary(recorded=1, kept=3)])
        self.assertEqual(self.files(), (recorded(MAP, "R-1"), LIST))

    def test_a_lowered_claim_takes_a_decision_record_and_its_hypothesis_once(self):
        claim = ("kind: claim · standing: supported · measure: Spearman's |rs| · against: ROUGE-1 · scope: cited claims"
                 " · refuter: no higher · test: external arXiv:2005.00661 §5.4 Table 4 first-hand")
        decision = f"{record('R-2')} · hypothesis: H-R-2"
        self.reset(map_text=MAP.replace(NORM, claim))
        path = self.result("a.json", rule("R-2", decision, hypotheses=(hypothesis("H-R-2"),)))
        self.assertEqual(self.replace(path)[:2], (0, ["REPLACED R-2", "ADDED H-R-2", summary(replaced=1, added=1)]))
        self.assertEqual(self.replace(path)[:2], (0, ["KEPT R-2", "KEPT H-R-2", summary(kept=2)]))
        self.assertEqual(self.files(), (MAP.replace(NORM, decision), f"{LIST}\n{hypothesis('H-R-2')}\n"))

    def test_a_listed_hypothesis_with_other_text_is_replaced_under_replace_and_kept_without(self):
        replaced = LIST.replace("- **H-01** · an old hypothesis", "- **H-01** · the same id, reworded")
        cases = {
            "under --replace": (("--replace",), LIST, "REPLACED H-01", replaced),
            "under --replace, CRLF endings": (("--replace",), LIST.replace("\n", "\r\n"), "REPLACED H-01",
                                              replaced.replace("\n", "\r\n")),
            "without --replace": ((), LIST, "KEPT H-01", LIST),
        }
        for name, (options, list_text, outcome, expected) in cases.items():
            with self.subTest(name):
                self.reset(list_text=list_text)
                code, lines, _ = self.apply(self.result("a.json", rule("R-2", hypotheses=(REWORDED_H01,))), options=options)
                self.assertEqual((code, lines[1]), (0, outcome))
                self.assertEqual(self.list.read_bytes(), expected.encode("utf-8"))

    def test_a_bad_text_or_record_is_bad_and_nothing_is_written_for_its_rule(self):
        not_written = "the text of the rule is BAD, so the record is not written"
        cases = {
            "a text with a record segment": (
                rule("R-2", text=" · the second rule · kind: norm"),
                ["BAD R-2", "BAD R-2", "RECORDED R-3", summary(recorded=1, bad=2)],
                [not_written, "the text holds a segment that opens `kind:`"]),
            "a text with a line break": (
                worded("R-2", " · the second\nrule"),
                ["KEPT R-2", "BAD R-2", "RECORDED R-3", summary(recorded=1, kept=1, bad=1)],
                ["the text holds a line break"]),
            "a text that ends in a separator's dot": (
                worded("R-2", " · the second rule ·"),
                ["KEPT R-2", "BAD R-2", "RECORDED R-3", summary(recorded=1, kept=1, bad=1)],
                ["the rewritten line would not read back with this text and record"]),
            "a malformed record": (
                rule("R-2", "decision · owner: x", text=" · reworded"),
                ["BAD R-2", "RECORDED R-3", summary(recorded=1, bad=1)],
                ["the record does not open with `kind: `"]),
        }
        for name, (bad, outcomes, reasons) in cases.items():
            with self.subTest(name):
                self.reset()
                path = self.result("a.json", {**bad, "hypotheses": [hypothesis("H-R-2")]}, rule("R-3"))
                code, lines, err = self.replace(path)
                self.assertEqual((code, lines), (1, outcomes))
                self.assertEqual(self.files(), (recorded(MAP, "R-3"), LIST))
                self.assertEqual(err, "".join(f"BAD R-2: {reason} ({path})\n" for reason in reasons))

    def test_a_hypothesis_whose_id_stands_on_two_lines_of_the_list_is_bad(self):
        listed = LIST + "- **H-01** · the same id again · kind: claim · standing: hypothesis\n"
        self.reset(list_text=listed)
        path = self.result("a.json", rule("R-2", hypotheses=(REWORDED_H01,)))
        code, lines, err = self.replace(path)
        self.assertEqual((code, lines), (1, ["BAD R-2", "BAD H-01", summary(bad=2)]))
        self.assertEqual(self.files(), (MAP, listed))
        self.assertIn(f"BAD H-01: hypothesis line 1 of R-2 has an id that stands on the rule lines 3, 4 of the list ({path})",
                      err)

    def test_a_hypothesis_line_that_differs_from_the_one_the_run_writes_for_its_id_is_bad(self):
        other = "- **H-shared** · another claim behind the rule · kind: claim · standing: hypothesis"
        path = self.result("a.json", rule("R-1", hypotheses=(hypothesis("H-shared"),)), rule("R-3", hypotheses=(other,)))
        code, lines, err = self.replace(path)
        self.assertEqual((code, lines), (1, ["RECORDED R-1", "BAD R-3", "ADDED H-shared", "BAD H-shared",
                                             summary(recorded=1, added=1, bad=2)]))
        self.assertEqual(self.files(), (recorded(MAP, "R-1"), f"{LIST}\n{hypothesis('H-shared')}\n"))
        self.assertIn("BAD H-shared: hypothesis line 1 of R-3 differs from the line this run already writes for "
                      f"H-shared ({path})", err)

    def test_a_dry_run_under_replace_prints_the_same_lines_and_writes_nothing(self):
        path = self.result("a.json", rule("R-2", text=" · reworded", hypotheses=(REWORDED_H01,)), worded("R-3", " · reworded"))
        inodes = (self.map.stat().st_ino, self.list.stat().st_ino)
        dry = self.apply(path, options=("--replace", "--dry-run"))
        self.assertUntouched()
        self.assertEqual((self.map.stat().st_ino, self.list.stat().st_ino), inodes)
        self.assertEqual(self.replace(path), dry)
        self.assertEqual(dry[:2], (0, ["REPLACED R-2", "REWORDED R-2", "KEPT R-3", "REWORDED R-3", "REPLACED H-01",
                                       summary(replaced=2, reworded=2, kept=1)]))


class Inputs(Base):
    def test_a_rule_with_neither_record_nor_text_exits_2_and_writes_nothing(self):
        carried = rule("R-1")
        del carried["record"]
        path = self.result("a.json", carried)
        code, lines, err = self.apply(path)
        self.assertEqual((code, lines), (2, []))
        self.assertEqual(err, f"{path}: rule 1: the rule carries neither record nor text\n")
        self.assertUntouched()

    def test_one_id_in_two_result_files_exits_2_naming_both_and_writes_nothing(self):
        first = self.result("a.json", rule("R-1"))
        second = self.result("b.json", rule("R-3"), rule("R-1"))
        code, lines, err = self.apply(first, second, options=("--corrections", str(self.dir / "report.md")))
        self.assertEqual((code, lines), (2, []))
        self.assertIn(f"rule id 'R-1' stands in {first} and in {second}", err)
        self.assertUntouched()
        self.assertFalse((self.dir / "report.md").exists())

    def test_a_malformed_result_file_exits_2_and_writes_nothing(self):
        good = rule("R-1")
        cases = {
            "not JSON": b'{"rules": [',
            "not UTF-8": b'{"rules": [], "unopened": ["\xff"]}',
            "top level an array": json.dumps([good]).encode(),
            "rules missing": json.dumps({"unopened": []}).encode(),
            "unopened not an array": json.dumps({"rules": [good], "unopened": "none"}).encode(),
            "unopened item a number": json.dumps({"rules": [good], "unopened": [3]}).encode(),
            "rule not an object": json.dumps({"rules": ["R-1"], "unopened": []}).encode(),
            "id empty": json.dumps({"rules": [{**good, "id": ""}], "unopened": []}).encode(),
            "id with a star": json.dumps({"rules": [{**good, "id": "R-1**"}], "unopened": []}).encode(),
            "id with an outer space": json.dumps({"rules": [{**good, "id": "R-1 "}], "unopened": []}).encode(),
            "record not a string": json.dumps({"rules": [{**good, "record": None}], "unopened": []}).encode(),
            "hypotheses item not a string": json.dumps({"rules": [{**good, "hypotheses": [1]}], "unopened": []}).encode(),
            "source without seen": json.dumps({"rules": [{**good, "sources": [{"source": "S"}]}], "unopened": []}).encode(),
            "correction not an object": json.dumps({"rules": [{**good, "corrections": ["x"]}], "unopened": []}).encode(),
            "notes missing": json.dumps({"rules": [{k: v for k, v in good.items() if k != "notes"}],
                                         "unopened": []}).encode(),
            "a repeated name": b'{"rules": [{"id": "R-1", "id": "R-3", "record": "kind: x", "hypotheses": [],'
                               b' "sources": [], "corrections": [], "notes": ""}], "unopened": []}',
            "an id twice in one file": json.dumps({"rules": [good, good], "unopened": []}).encode(),
        }
        for name, content in cases.items():
            with self.subTest(name):
                path = self.dir / "a.json"
                path.write_bytes(content)
                code, lines, err = self.apply(str(path))
                self.assertEqual((code, lines), (2, []))
                self.assertIn(str(path), err)
                self.assertUntouched()

    def test_an_unreadable_map_or_list_exits_2(self):
        path = self.result("a.json", rule("R-1"))
        self.map.unlink()
        code, lines, err = self.apply(path)
        self.assertEqual((code, lines), (2, []))
        self.assertIn(f"cannot read {self.map}", err)
        self.map.write_bytes(MAP.encode("utf-8"))
        self.list.write_bytes(b"- **H-01** \xff\n")
        code, lines, err = self.apply(path)
        self.assertEqual((code, lines), (2, []))
        self.assertIn(f"{self.list} is not UTF-8", err)
        self.assertEqual(self.map.read_text(encoding="utf-8"), MAP)

    def test_wrong_usage_exits_2(self):
        path = self.result("a.json", rule("R-1"))
        usages = {
            "no result file": ("--map", str(self.map), "--hypotheses", str(self.list)),
            "no map": ("--hypotheses", str(self.list), path),
            "map and list one file": ("--map", str(self.map), "--hypotheses", str(self.map), path),
            "report over the map": ("--map", str(self.map), "--hypotheses", str(self.list), "--corrections",
                                    str(self.map), path),
            "report over a result file": ("--map", str(self.map), "--hypotheses", str(self.list), "--corrections",
                                          path, path),
        }
        for name, args in usages.items():
            with self.subTest(name):
                self.assertEqual(self.run_main(*args)[:2], (2, []))
                self.assertUntouched()


class DryRun(Base):
    def test_a_dry_run_prints_the_same_lines_and_writes_nothing(self):
        path = self.result("a.json", rule("R-1", hypotheses=(hypothesis("H-R-1"),)), rule("R-9"), rule("R-2"),
                           rule("R-3", "no record"))
        report = self.dir / "report.md"
        inodes = (self.map.stat().st_ino, self.list.stat().st_ino)
        dry = self.apply(path, options=("--dry-run", "--corrections", str(report)))
        self.assertUntouched()
        self.assertEqual((self.map.stat().st_ino, self.list.stat().st_ino), inodes)
        self.assertFalse(report.exists())
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["a.json", "method-provenance.md", "pending-evidence.md"])
        self.assertEqual(self.apply(path, options=("--corrections", str(report))), dry)
        self.assertEqual(dry[:2], (1, ["RECORDED R-1", "MISSING R-9", "KEPT R-2", "BAD R-3", "ADDED H-R-1",
                                       "1 recorded, 0 replaced, 0 reworded, 1 kept, 1 added, 1 missing, 1 bad"]))


class Corrections(Base):
    def test_the_report_follows_the_map_with_the_unopened_sources_last(self):
        first = self.result(
            "a.json",
            rule("R-3", corrections=({"where": "the provenance line", "says": "61.8 pp",
                                      "source_says": "\"a relative drop of 61.8%\""},),
                 notes="check the figure again.",
                 sources=({"source": "Smith 2024", "seen": "full text", "says": "S"},
                          {"source": "Jones 2025", "seen": "not opened", "says": ""})),
            rule("R-2", sources=({"source": "IEEE 1003.1", "seen": "full text", "says": "S"},)),
            unopened=("Jones 2025: the publisher answered 403",))
        second = self.result(
            "b.json",
            rule("R-9", corrections=({"where": "the card", "says": "three runs", "source_says": "\"two runs\"\nand a pilot"},)),
            rule("R-1", notes="  the source is a preprint.\n", sources=({"source": "arXiv:2401.00001", "seen": "abstract alone"},)),
            unopened=("Brown 2023: no copy found", "Jones 2025: the publisher answered 403"))
        report = self.dir / "report.md"
        code, _, _ = self.apply(first, second, options=("--corrections", str(report)))
        self.assertEqual(code, 1)
        self.assertEqual(report.read_text(encoding="utf-8"), (
            "# Corrections and notes\n"
            "\n## R-1\n"
            "\nNote: the source is a preprint.\n"
            "\nSources:\n\n"
            "- arXiv:2401.00001 (abstract alone)\n"
            "\n## R-3\n\n"
            "- Where: the provenance line\n"
            "  - Our text says: 61.8 pp\n"
            "  - The source says: \"a relative drop of 61.8%\"\n"
            "\nNote: check the figure again.\n"
            "\nSources:\n\n"
            "- Smith 2024 (full text)\n"
            "- Jones 2025 (not opened)\n"
            "\n## R-9\n\n"
            "- Where: the card\n"
            "  - Our text says: three runs\n"
            "  - The source says: \"two runs\"\n"
            "    and a pilot\n"
            "\n## Unopened sources\n\n"
            "- Jones 2025: the publisher answered 403\n"
            "- Brown 2023: no copy found\n"))

    def test_a_report_with_no_unopened_source_says_none(self):
        report = self.dir / "report.md"
        self.apply(self.result("a.json", rule("R-1")), options=("--corrections", str(report)))
        self.assertEqual(report.read_text(encoding="utf-8"), "# Corrections and notes\n\n## Unopened sources\n\nNone.\n")


class Writing(Base):
    def test_a_rewritten_file_keeps_its_mode_and_leaves_no_temporary_file(self):
        os.chmod(self.map, 0o640)
        path = self.result("a.json", rule("R-1"))
        self.assertEqual(self.apply(path)[0], 0)
        self.assertEqual(stat.S_IMODE(self.map.stat().st_mode), 0o640)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["a.json", "method-provenance.md", "pending-evidence.md"])

    def test_a_report_that_cannot_be_written_exits_2_before_the_map_and_the_list_change(self):
        path = self.result("a.json", rule("R-1", hypotheses=(hypothesis("H-R-1"),)))
        code, lines, err = self.apply(path, options=("--corrections", str(self.dir / "absent" / "report.md")))
        self.assertEqual((code, lines), (2, []))
        self.assertIn("cannot write", err)
        self.assertUntouched()


class CommandLine(Base):
    def test_the_script_runs_under_python_isolated_as_a_subprocess(self):
        path = self.result("a.json", rule("R-1", hypotheses=(hypothesis("H-R-1"),)))
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--map", str(self.map), "--hypotheses", str(self.list),
                              path], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.splitlines(), ["RECORDED R-1", "ADDED H-R-1",
                                                   "1 recorded, 0 replaced, 0 reworded, 0 kept, 1 added, 0 missing, 0 bad"])
        self.assertEqual(self.files(), (recorded(MAP, "R-1"), f"{LIST}\n{hypothesis('H-R-1')}\n"))


if __name__ == "__main__":
    unittest.main()
