"""trace_list.py: the prose units and cues of a text, and the list of a change in pair, staged and range mode."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL / "scripts"))
import trace_list as tl  # noqa: E402


def setUpModule():
    """Git in this module reads no configuration of the user or the system, and HOME is a temporary directory."""
    home = tempfile.TemporaryDirectory(prefix="trace-list-home-")
    unittest.addModuleCleanup(home.cleanup)
    environment = mock.patch.dict(os.environ, {
        "HOME": home.name, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
    })
    environment.start()
    unittest.addModuleCleanup(environment.stop)


def texts(markdown: str) -> list[str]:
    return [unit["text"] for unit in tl.units(markdown)]


class Units(unittest.TestCase):
    def test_a_paragraph_over_several_lines_is_cut_into_sentences_with_their_lines(self):
        self.assertEqual(tl.units("First line of a\nparagraph   that ends here. Second\nsentence.\n"), [
            {"line": 1, "end_line": 2, "text": "First line of a paragraph that ends here."},
            {"line": 2, "end_line": 3, "text": "Second sentence."},
        ])

    def test_a_blank_line_ends_a_paragraph(self):
        self.assertEqual(tl.units("One paragraph\n\nanother one\n"), [
            {"line": 1, "end_line": 1, "text": "One paragraph"},
            {"line": 3, "end_line": 3, "text": "another one"},
        ])

    def test_each_list_item_starts_a_paragraph_without_its_marker(self):
        markdown = "Intro line\n- dash item\n  continued\n* star item\n+ plus item\n  1. numbered item\n2) parenthesised item\n"
        self.assertEqual(tl.units(markdown), [
            {"line": 1, "end_line": 1, "text": "Intro line"},
            {"line": 2, "end_line": 3, "text": "dash item continued"},
            {"line": 4, "end_line": 4, "text": "star item"},
            {"line": 5, "end_line": 5, "text": "plus item"},
            {"line": 6, "end_line": 6, "text": "numbered item"},
            {"line": 7, "end_line": 7, "text": "parenthesised item"},
        ])

    def test_a_table_row_gives_one_paragraph_per_non_empty_cell_and_the_separator_none(self):
        markdown = "| Rule | Source |\n|:---|---:|\n| Cite it. Then check. | |\n"
        self.assertEqual(tl.units(markdown), [
            {"line": 1, "end_line": 1, "text": "Rule"},
            {"line": 1, "end_line": 1, "text": "Source"},
            {"line": 3, "end_line": 3, "text": "Cite it."},
            {"line": 3, "end_line": 3, "text": "Then check."},
        ])

    def test_a_fenced_block_holds_no_unit_up_to_its_matching_fence(self):
        markdown = "Before.\n```text\nNot prose.\n~~~\nStill code.\n```\n  ~~~\nTilde code.\n  ~~~\nAfter.\n"
        self.assertEqual(tl.units(markdown), [
            {"line": 1, "end_line": 1, "text": "Before."},
            {"line": 10, "end_line": 10, "text": "After."},
        ])

    def test_a_heading_holds_no_unit_and_a_block_quote_loses_its_mark(self):
        self.assertEqual(tl.units("# Title\nBody line\n###### Deep\n> Quoted line\n> goes on\n#hashtag\n"), [
            {"line": 2, "end_line": 2, "text": "Body line"},
            {"line": 4, "end_line": 6, "text": "Quoted line goes on #hashtag"},
        ])

    def test_a_thematic_break_and_a_comment_line_hold_no_unit(self):
        text = "One.\n\n---\n\n<!-- generated -->\n\n* * *\n\nTwo."
        self.assertEqual(texts(text), ["One.", "Two."])

    def test_front_matter_holds_only_its_folded_description(self):
        markdown = ("---\nname: tracer\ndescription: >-\n  Folded first line\n  continues here.\n"
                    "tools: Read, Grep\n---\nBody text.\n")
        self.assertEqual(tl.units(markdown), [
            {"line": 4, "end_line": 5, "text": "Folded first line continues here."},
            {"line": 8, "end_line": 8, "text": "Body text."},
        ])

    def test_front_matter_description_on_its_own_line_takes_its_continuation(self):
        markdown = "---\ndescription: Starts here\n  and ends here.\nname: x\n---\n"
        self.assertEqual(tl.units(markdown), [{"line": 2, "end_line": 3, "text": "Starts here and ends here."}])

    def test_every_block_scalar_mark_is_dropped(self):
        for mark in (">-", ">", "|-", "|"):
            with self.subTest(mark=mark):
                self.assertEqual(texts(f"---\ndescription: {mark}\n  The value.\n---\n"), ["The value."])

    def test_the_abbreviations_and_a_single_capital_end_no_sentence(self):
        for text in ("Read a file, e.g. README, first.", "Read the map, i.e. One file.",
                     "Keep notes, logs etc. Each in place.", "Weigh rules vs. Norms here.",
                     "See the card, cf. The method.", "Ask J. Smith about it.",
                     "Pick a tool (e.g. `grep`) now.", "E.g. Grep finds it.", "The U.S. Army spoke."):
            with self.subTest(text=text):
                self.assertEqual(texts(text), [text])

    def test_a_sentence_ends_before_a_capital_digit_or_opening_mark(self):
        self.assertEqual(texts('Stop here. Then go. 2 more. "Quoted" one. (Aside) two. [Link] three. `code` four. '
                               '*Bold* five. Über six. Eine sieben.'),
                         ["Stop here.", "Then go.", "2 more.", '"Quoted" one.', "(Aside) two.", "[Link] three.",
                          "`code` four.", "*Bold* five.", "Über six.", "Eine sieben."])

    def test_a_sentence_takes_its_closing_marks(self):
        self.assertEqual(texts('He said "stop." Then left. (A note.) Next one! Really? `x.` Yes.'),
                         ['He said "stop."', "Then left.", "(A note.)", "Next one!", "Really?", "`x.`", "Yes."])

    def test_no_sentence_ends_before_a_lower_case_letter_or_inside_a_word(self):
        for text in ("Use version 2.1 of it.", "Stop here. then go on.", "A file.txt name.",
                     "A word after a stop.] Then more."):
            with self.subTest(text=text):
                self.assertEqual(texts(text), [text])

    def test_a_lower_case_single_letter_ends_a_sentence(self):
        self.assertEqual(texts("Take option b. Then stop."), ["Take option b.", "Then stop."])


class Normalise(unittest.TestCase):
    def test_whitespace_collapses_and_typographic_quotes_become_plain(self):
        self.assertEqual(tl.normalise("  It’s ‘one’\n\t“two”  "), "It's 'one' \"two\"")

    def test_sha256_text_hashes_the_utf8_bytes(self):
        self.assertEqual(tl.sha256_text("Über"), hashlib.sha256("Über".encode("utf-8")).hexdigest())


class Cues(unittest.TestCase):
    def assert_cue(self, phrase: str):
        with self.subTest(phrase=phrase):
            self.assertIn(phrase, tl.cues(f"Some text {phrase} here."))
            self.assertIn(phrase, tl.cues(f"Some text {phrase.upper()} here."))

    def test_every_denial_word_is_a_cue(self):
        for word in ("not", "no", "never", "neither", "nor", "none", "nothing", "nobody", "nowhere", "without",
                     "cannot"):
            self.assert_cue(word)

    def test_every_contrast_phrase_is_a_cue(self):
        for phrase in ("instead", "rather than", "unlike", "as opposed to", "in place of", "in contrast", "whereas"):
            self.assert_cue(phrase)

    def test_every_history_phrase_is_a_cue(self):
        for phrase in ("no longer", "any longer", "anymore", "any more", "previously", "formerly", "originally",
                       "used to", "not yet", "so far", "for now", "currently", "legacy", "deprecated", "the old",
                       "the earlier", "the former", "the previous", "we now"):
            self.assert_cue(phrase)

    def test_now_is_a_cue_only_before_one_of_its_verbs(self):
        for verb in ("uses", "use", "reads", "runs", "returns", "takes", "lives", "is", "are", "has", "have", "does",
                     "do"):
            with self.subTest(verb=verb):
                self.assertEqual(tl.cues(f"The parser now {verb} it."), ["now"])
        self.assertEqual(tl.cues("Do it now. Now we wait, now then."), [])

    def test_the_contraction_with_either_apostrophe(self):
        self.assertEqual(tl.cues("It doesn't fit."), ["n't"])
        self.assertEqual(tl.cues("It won’t fit."), ["n't"])

    def test_a_cue_is_found_at_word_boundaries_only(self):
        self.assertEqual(tl.cues("Notice the known nominal notes of Nora, a nonce snowball."), [])

    def test_each_cue_once_in_order_of_first_occurrence(self):
        self.assertEqual(tl.cues("Never this, not that, never again, NOT ever."), ["never", "not"])

    def test_a_cue_inside_a_code_span_is_ignored(self):
        self.assertEqual(tl.cues("Pass `--no-cache` or `never` to it."), [])
        self.assertEqual(tl.cues("Pass `x` but not `y`."), ["not"])


class SameWord(unittest.TestCase):
    def test_a_word_is_the_same_up_to_a_plain_ending_either_way(self):
        for left, right in (("cite", "cites"), ("cite", "cited"), ("cite", "citing"), ("rule", "rules"),
                            ("box", "boxes"), ("use", "used"), ("rules", "rule"), ("Cite", "CITED"), ("run", "run")):
            with self.subTest(left=left, right=right):
                self.assertTrue(tl.same_word(left, right))

    def test_another_word_is_not_the_same(self):
        for left, right in (("cite", "citation"), ("cite", "excites"), ("cites", "cited"), ("rule", "ruler")):
            with self.subTest(left=left, right=right):
                self.assertFalse(tl.same_word(left, right))


class Run(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="trace-list-")
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_main(self, *args: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = tl.main(list(args))
            except SystemExit as usage:
                code = usage.code
        return code, out.getvalue(), err.getvalue()

    def listing(self, *args: str) -> dict:
        code, out, err = self.run_main(*args)
        self.assertEqual(code, 0, err)
        return json.loads(out)


COMMIT_DATES = {"GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00"}

SHARED = ["# Rules", ""] + [line for k in range(4) for line in (f"Shared paragraph {k} holds one sentence.", "")] + [""]
OLD_EXAMPLE = "\n".join(SHARED + ["Every rule cites a source.", ""])
NEW_SENTENCE = "The method is neither a sequence of steps nor a demand for a citation."
NEW_EXAMPLE = "\n".join(SHARED + ["", "", NEW_SENTENCE, ""])


class PairMode(Run):
    def test_the_example_of_the_description_end_to_end(self):
        old, new = self.write("old.md", OLD_EXAMPLE), self.write("new.md", NEW_EXAMPLE)
        self.assertEqual(self.listing("--old", str(old), "--new", str(new)), {
            "version": 1,
            "mode": "pair",
            "files": [{"file": str(new), "sha256": hashlib.sha256(NEW_EXAMPLE.encode("utf-8")).hexdigest()}],
            "deleted": [{"file": str(old), "line": 12, "text": "Every rule cites a source."}],
            "candidates": [{"id": "c001", "file": str(new), "line": 14, "end_line": 14, "sentence": NEW_SENTENCE,
                            "cues": ["neither", "nor"]}],
        })

    def test_file_names_stay_as_given(self):
        self.write("old.md", OLD_EXAMPLE)
        self.write("sub/new.md", NEW_EXAMPLE)
        cwd = os.getcwd()
        os.chdir(self.dir)
        try:
            listing = self.listing("--old", "old.md", "--new", "./sub/new.md")
        finally:
            os.chdir(cwd)
        self.assertEqual(listing["files"][0]["file"], "./sub/new.md")
        self.assertEqual(listing["deleted"][0]["file"], "old.md")
        self.assertEqual(listing["candidates"][0]["file"], "./sub/new.md")

    def test_an_added_sentence_without_a_cue_stays_off_the_list(self):
        listing = self.listing("--old", os.devnull, "--new", str(self.write("new.md", "Every rule cites a source.\n")))
        self.assertEqual(listing["candidates"], [])

    def test_a_sentence_spanning_an_added_and_an_unchanged_line_is_a_candidate(self):
        old = self.write("old.md", "Intro.\n\nThe parser reads\nevery file.\n")
        new = self.write("new.md", "Intro.\n\nThe parser reads\nno file.\n")
        candidates = self.listing("--old", str(old), "--new", str(new))["candidates"]
        self.assertEqual([(c["line"], c["end_line"], c["sentence"], c["cues"]) for c in candidates],
                         [(3, 4, "The parser reads no file.", ["no"])])

    def test_unchanged_sentences_with_cues_stay_off_the_list(self):
        old = self.write("old.md", "It does not fit.\n\nNever again.\n")
        new = self.write("new.md", "It does not fit.\n\nNever again.\n\nPlain words.\n\nInstead, this.\n")
        listing = self.listing("--old", str(old), "--new", str(new))
        self.assertEqual([(c["id"], c["sentence"]) for c in listing["candidates"]], [("c001", "Instead, this.")])
        self.assertEqual(listing["deleted"], [])

    def test_dev_null_gives_an_empty_old_text(self):
        new = self.write("new.md", "It is not here.\n")
        listing = self.listing("--old", os.devnull, "--new", str(new))
        self.assertEqual((listing["deleted"], [c["sentence"] for c in listing["candidates"]]),
                         ([], ["It is not here."]))

    def test_out_writes_the_list_and_prints_one_summary_line(self):
        old, new = self.write("old.md", OLD_EXAMPLE), self.write("new.md", NEW_EXAMPLE)
        out = self.dir / "list.json"
        code, stdout, err = self.run_main("--old", str(old), "--new", str(new), "--out", str(out))
        self.assertEqual(code, 0, err)
        self.assertEqual(stdout, "1 file(s), 1 deleted statement(s), 1 candidate(s)\n")
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["candidates"][0]["sentence"], NEW_SENTENCE)


class Errors(Run):
    def assert_exit_2(self, *args: str, message: str = ""):
        code, out, err = self.run_main(*args)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn(message, err)

    def test_wrong_usage(self):
        new = str(self.write("new.md", "Text.\n"))
        for args in ((), ("--new", new), ("--old", new), ("--old", new, "--new", new, "--staged"),
                     ("--staged", "--base", "HEAD"), ("--staged", "--head", "HEAD"), ("--bogus",),
                     ("--old", new, "--new", new, "--terms", new)):
            with self.subTest(args=args):
                self.assert_exit_2(*args)

    def test_a_missing_old_file(self):
        self.assert_exit_2("--old", str(self.dir / "missing.md"), "--new", str(self.write("new.md", "x\n")),
                           message="cannot read")

    def test_a_file_that_is_not_utf8(self):
        bad = self.dir / "bad.md"
        bad.write_bytes(b"caf\xe9\n")
        self.assert_exit_2("--old", os.devnull, "--new", str(bad), message="cannot read")

    def test_a_failed_git_command(self):
        self.assert_exit_2("--staged", "--root", str(self.dir), message="git")


class GitRepository(Run):
    """The temporary directory is a git repository with a committer of its own."""

    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")

    def git(self, *args: str, env: dict | None = None) -> str:
        run = subprocess.run(["git", "-C", str(self.dir), *args], capture_output=True, text=True,
                             env=None if env is None else {**os.environ, **env})
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("-c", "commit.gpgsign=false", "commit", "-q", "-m", message, env=COMMIT_DATES)

    def summary(self, listing: dict) -> tuple:
        return ([f["file"] for f in listing["files"]],
                [(d["file"], d["line"], d["text"]) for d in listing["deleted"]],
                [(c["id"], c["file"], c["line"], c["sentence"]) for c in listing["candidates"]])


class GitModes(GitRepository):
    def setUp(self):
        super().setUp()
        self.write("a.md", "Shared line.\n\nOld rule holds.\n")
        self.write("gone.md", "A removed statement.\n")
        self.write("notes.txt", "Text.\n")
        self.commit("base")

    def change(self) -> None:
        """A modified and an added Markdown file, a deleted one and a modified non-Markdown file."""
        self.write("a.md", "Shared line.\n\nThe rule no longer holds.\n")
        self.write("b.md", "A new file, not an old one.\n")
        self.write("notes.txt", "It is not Markdown.\n")
        (self.dir / "gone.md").unlink()

    EXPECTED = (["a.md", "b.md"],
                [("a.md", 3, "Old rule holds."), ("gone.md", 1, "A removed statement.")],
                [("c001", "a.md", 3, "The rule no longer holds."), ("c002", "b.md", 1, "A new file, not an old one.")])

    def test_staged_mode_reads_the_index_against_head_and_only_markdown(self):
        self.change()
        self.git("add", "-A")
        self.write("a.md", "Shared line.\n\nThe rule no longer holds.\n\nUnstaged, never listed.\n")
        listing = self.listing("--staged", "--root", str(self.dir))
        self.assertEqual(listing["mode"], "staged")
        self.assertEqual(self.summary(listing), self.EXPECTED)
        self.assertEqual(listing["files"][0]["sha256"], tl.sha256_text("Shared line.\n\nThe rule no longer holds.\n"))

    def test_exclude_drops_the_matching_paths(self):
        self.change()
        self.git("add", "-A")
        listing = self.listing("--staged", "--root", str(self.dir), "--exclude", "b*.md", "--exclude", "gone.*")
        self.assertEqual(self.summary(listing), (["a.md"], [("a.md", 3, "Old rule holds.")],
                                                 [("c001", "a.md", 3, "The rule no longer holds.")]))

    def test_range_mode_against_the_working_tree(self):
        self.change()
        self.git("add", "b.md")
        listing = self.listing("--base", "HEAD", "--root", str(self.dir))
        self.assertEqual(listing["mode"], "range")
        self.assertEqual(self.summary(listing), self.EXPECTED)

    def test_range_mode_between_two_revisions(self):
        self.change()
        self.commit("change")
        self.write("a.md", "Working tree, never listed.\n")
        listing = self.listing("--base", "HEAD~1", "--head", "HEAD", "--root", str(self.dir))
        self.assertEqual(self.summary(listing), self.EXPECTED)

    def test_an_unknown_revision_is_a_failed_git_command(self):
        code, out, err = self.run_main("--base", "no-such-rev", "--root", str(self.dir))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("git diff", err)


README = ("# Skill A\n\nThe skill reads one file and never writes one.\n\nEach run takes a list of paths.\n\n"
          "It opens no network connection.\n")
README_EDITED = README.replace("a list of paths.", "a list of paths, not a directory.")
SKILL = ("---\nname: skill-a\ndescription: Reads one file. Never writes one.\n---\n# Skill A\n\n"
         "Run it on a list of paths.\n\nIt does not follow a link.\n")
NOTES = "# Notes\n\nA note holds no rule.\n"
REWRITE_SENTENCE = "A path outside the root is never read."


def rewritten(text: str) -> str:
    """The text with eight paragraphs and REWRITE_SENTENCE appended, enough that git no longer pairs the two."""
    steps = "".join(f"\nStep {k} reads the next path and records its size in the log.\n" for k in range(1, 9))
    return f"{text}{steps}\n{REWRITE_SENTENCE}\n"


class GitRenames(GitRepository):
    """skill-a holds README.md and SKILL.md at the base; a test moves the directory to skill-b with git mv."""

    def setUp(self):
        super().setUp()
        self.write("skill-a/README.md", README)
        self.write("skill-a/SKILL.md", SKILL)
        self.commit("skill-a")

    def staged_status(self) -> str:
        """The index against HEAD as git pairs it, after staging the working tree."""
        self.git("add", "-A")
        return self.git("diff", "--cached", "-M", "--name-status", "HEAD")

    def staged_listing(self, *args: str) -> dict:
        return self.listing("--staged", "--root", str(self.dir), *args)

    def move_editing_readme_and_rewriting_skill(self) -> None:
        self.git("mv", "skill-a", "skill-b")
        self.write("skill-b/README.md", README_EDITED)
        self.write("skill-b/SKILL.md", rewritten(SKILL))

    EDIT_DELETED = ("skill-a/README.md", 5, "Each run takes a list of paths.")
    EDIT_ADDED = ("skill-b/README.md", 5, "Each run takes a list of paths, not a directory.")
    REWRITE_ADDED = ("skill-b/SKILL.md", 27, REWRITE_SENTENCE)
    MOVED_EDITED_REWRITTEN = (["skill-b/README.md", "skill-b/SKILL.md"], [EDIT_DELETED],
                              [("c001", *EDIT_ADDED), ("c002", *REWRITE_ADDED)])

    def test_a_moved_directory_lists_only_the_sentences_its_edit_adds(self):
        self.git("mv", "skill-a", "skill-b")
        self.write("skill-b/README.md", README_EDITED)
        self.assertIn("\tskill-a/README.md\tskill-b/README.md", self.staged_status())
        self.assertEqual(self.summary(self.staged_listing()),
                         (["skill-b/README.md", "skill-b/SKILL.md"], [self.EDIT_DELETED], [("c001", *self.EDIT_ADDED)]))

    def test_a_file_rewritten_past_git_pairing_is_compared_with_its_earlier_text_through_its_directory(self):
        self.move_editing_readme_and_rewriting_skill()
        status = self.staged_status()
        self.assertIn("A\tskill-b/SKILL.md", status)
        self.assertIn("\tskill-a/README.md\tskill-b/README.md", status)
        self.assertEqual(self.summary(self.staged_listing()), self.MOVED_EDITED_REWRITTEN)

    def test_a_rewritten_file_in_a_subdirectory_is_paired_through_the_directory_that_moved(self):
        self.write("skill-a/maintenance/notes.md", NOTES)
        self.commit("notes")
        self.git("mv", "skill-a", "skill-b")
        self.write("skill-b/maintenance/notes.md", rewritten(NOTES))
        self.assertIn("A\tskill-b/maintenance/notes.md", self.staged_status())
        self.assertEqual(self.summary(self.staged_listing()),
                         (["skill-b/README.md", "skill-b/SKILL.md", "skill-b/maintenance/notes.md"], [],
                          [("c001", "skill-b/maintenance/notes.md", 21, REWRITE_SENTENCE)]))

    def test_a_new_file_in_a_directory_nothing_moved_into_lists_every_candidate(self):
        self.git("mv", "skill-a", "skill-b")
        (self.dir / "skill-b" / "SKILL.md").unlink()
        self.write("skill-c/SKILL.md", "# Skill C\n\nIt writes no file.\n\nA run never stops early.\n\nPlain words.\n")
        self.assertIn("D\tskill-a/SKILL.md", self.staged_status())
        self.assertEqual(self.summary(self.staged_listing()), (
            ["skill-b/README.md", "skill-c/SKILL.md"],
            [("skill-a/SKILL.md", 3, "Reads one file."), ("skill-a/SKILL.md", 3, "Never writes one."),
             ("skill-a/SKILL.md", 7, "Run it on a list of paths."),
             ("skill-a/SKILL.md", 9, "It does not follow a link.")],
            [("c001", "skill-c/SKILL.md", 3, "It writes no file."),
             ("c002", "skill-c/SKILL.md", 5, "A run never stops early.")]))

    def test_range_mode_over_a_commit_with_a_rename_lists_what_staged_mode_listed_before_it(self):
        self.move_editing_readme_and_rewriting_skill()
        self.git("add", "-A")
        staged = self.staged_listing()
        self.assertEqual(self.summary(staged), self.MOVED_EDITED_REWRITTEN)
        self.commit("move")
        for head in (("--head", "HEAD"), ()):
            with self.subTest(head=head):
                self.assertEqual(self.listing("--base", "HEAD~1", *head, "--root", str(self.dir)),
                                 {**staged, "mode": "range"})

    def test_an_excluded_paired_file_leaves_its_earlier_path_off_the_list(self):
        self.move_editing_readme_and_rewriting_skill()
        self.git("add", "-A")
        cases = (("skill-b/SKILL.md", (["skill-b/README.md"], [self.EDIT_DELETED], [("c001", *self.EDIT_ADDED)])),
                 ("skill-b/README.md", (["skill-b/SKILL.md"], [], [("c001", *self.REWRITE_ADDED)])))
        for glob, expected in cases:
            with self.subTest(glob=glob):
                self.assertEqual(self.summary(self.staged_listing("--exclude", glob)), expected)

    def test_a_markdown_file_renamed_to_another_kind_of_file_counts_as_deleted(self):
        self.git("mv", "skill-a/README.md", "skill-a/README.txt")
        self.assertIn("\tskill-a/README.md\tskill-a/README.txt", self.staged_status())
        self.assertEqual(self.summary(self.staged_listing()), ([], [
            ("skill-a/README.md", 3, "The skill reads one file and never writes one."),
            ("skill-a/README.md", 5, "Each run takes a list of paths."),
            ("skill-a/README.md", 7, "It opens no network connection.")], []))


if __name__ == "__main__":
    unittest.main()
