"""records.py: the reader record, the ledger of answers, their matching and the capture hook."""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import records  # noqa: E402

TIMEOUT_Q = "The acknowledgement timeout is 250 ms. Keep the acknowledgement timeout at 250 ms?"
REWORDED_Q = "Should we keep a 250 ms timeout for the acknowledgement?"
UNRELATED_Q = "What colour should the dashboard header have?"
RETRY_Q = "Should the retry limit stay at three attempts?"


def run_script(*args, env, stdin=None, cwd=None):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "records.py"), *args], input=stdin, capture_output=True, text=True, env=env, cwd=cwd)


class InProcess(unittest.TestCase):
    """Runs main() with an empty environment and explicit store files in a temporary directory."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.ledger = self.dir / "ledger.jsonl"
        self.reader = self.dir / "reader.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def main(self, *argv, environ=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = records.main(list(argv), environ or {"HOME": str(self.dir)})
        return code, out.getvalue(), err.getvalue()

    def ledger_cmd(self, command, *argv):
        return self.main("ledger", command, "--ledger-file", str(self.ledger), *argv)

    def reader_cmd(self, command, *argv):
        return self.main("reader", command, "--reader-file", str(self.reader), *argv)

    def add_answer(self, question, answer, kind="answer", *extra):
        code, out, err = self.ledger_cmd("add", "--kind", kind, "--question", question, "--answer", answer, "--basis", "a card", *extra)
        self.assertEqual(code, 0, err)
        return out.strip()

    def stored(self, path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class Ledger(InProcess):
    def test_add_writes_the_record_with_today_and_the_next_id(self):
        first = self.add_answer(TIMEOUT_Q, "Keep 250 ms", "answer", "--scope", "the order gateway", "--overturns", "a p99 above 250 ms")
        self.assertEqual(first, "a-0001")
        [record] = self.stored(self.ledger)
        self.assertEqual(record["kind"], "answer")
        self.assertEqual(record["status"], "active")
        self.assertEqual(record["scope"], "the order gateway")
        self.assertEqual(record["overturns"], "a p99 above 250 ms")
        self.assertEqual(record["date"], records.today())

    def test_ids_count_on_past_the_highest_and_past_superseded_records(self):
        self.ledger.write_text(json.dumps({"id": "a-0007", "date": "2026-01-01", "kind": "default", "question": "q?", "answer": "a", "basis": "b", "status": "superseded", "superseded_by": "a-0002"}) + "\n", encoding="utf-8")
        self.assertEqual(self.add_answer(RETRY_Q, "Keep three"), "a-0008")
        self.assertEqual(self.add_answer(UNRELATED_Q, "Blue"), "a-0009")

    def test_add_refuses_an_unknown_kind_or_an_empty_answer(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            records.main(["ledger", "add", "--ledger-file", str(self.ledger), "--kind", "guess", "--question", "q?", "--answer", "a", "--basis", "b"], {})
        self.assertEqual(raised.exception.code, 2)
        code, _, err = self.ledger_cmd("add", "--kind", "answer", "--question", "q?", "--answer", "  ", "--basis", "b")
        self.assertEqual(code, 2)
        self.assertIn("--answer is empty", err)
        self.assertFalse(self.ledger.exists())

    def test_note_changes_only_the_named_fields(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        self.add_answer(RETRY_Q, "Keep three")
        code, out, err = self.ledger_cmd("note", "a-0001", "--scope", "the order gateway", "--overturns", "a p99 above 250 ms")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "a-0001")
        first, second = self.stored(self.ledger)
        self.assertEqual((first["scope"], first["overturns"], first["answer"]), ("the order gateway", "a p99 above 250 ms", "Keep 250 ms"))
        self.assertNotIn("scope", second)

    def test_note_without_a_field_or_with_an_unknown_id_exits_2(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        self.assertEqual(self.ledger_cmd("note", "a-0001")[0], 2)
        code, _, err = self.ledger_cmd("note", "a-0042", "--scope", "x")
        self.assertEqual(code, 2)
        self.assertIn("no record a-0042", err)

    def test_supersede_sets_the_status_and_the_pointer(self):
        self.add_answer(RETRY_Q, "Raise it to five")
        self.add_answer(RETRY_Q, "Keep three")
        code, _, err = self.ledger_cmd("supersede", "a-0001", "--by", "a-0002")
        self.assertEqual(code, 0, err)
        old, new = self.stored(self.ledger)
        self.assertEqual((old["status"], old["superseded_by"]), ("superseded", "a-0002"))
        self.assertEqual(new["status"], "active")
        self.assertEqual(self.ledger_cmd("supersede", "a-0001", "--by", "a-0099")[0], 2)
        self.assertEqual(self.ledger_cmd("supersede", "a-0002", "--by", "a-0002")[0], 2)

    def test_show_prints_every_record_newest_first(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        self.add_answer(RETRY_Q, "Raise it to five")
        self.add_answer(RETRY_Q, "Keep three")
        self.ledger_cmd("supersede", "a-0002", "--by", "a-0003")
        code, out, _ = self.ledger_cmd("show")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertEqual([line.split(" · ")[0] for line in lines], ["a-0003", "a-0002", "a-0001"])
        self.assertIn("superseded", lines[1])
        self.assertIn("superseded by a-0003", lines[1])

    def test_find_ranks_repeats_above_the_floor_and_leaves_out_the_rest(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        self.add_answer("Which log format does the export write?", "JSON lines", "default")
        self.add_answer(RETRY_Q, "Raise it to five")
        self.add_answer(RETRY_Q, "Keep three")
        self.ledger_cmd("supersede", "a-0003", "--by", "a-0004")

        code, out, _ = self.ledger_cmd("find", "--question", TIMEOUT_Q)
        self.assertEqual(code, 0)
        self.assertEqual([line.split(" · ")[0] for line in out.splitlines()], ["a-0001"])
        self.assertRegex(out, r"^a-0001 · \d{4}-\d\d-\d\d · 1\.00 · The acknowledgement timeout .* -> Keep 250 ms · basis: a card$")

        code, out, _ = self.ledger_cmd("find", "--question", REWORDED_Q)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("a-0001 · "), out)

        code, out, _ = self.ledger_cmd("find", "--question", UNRELATED_Q)
        self.assertEqual((code, out), (1, ""))

        code, out, _ = self.ledger_cmd("find", "--question", RETRY_Q)
        self.assertEqual([line.split(" · ")[0] for line in out.splitlines()], ["a-0004"])

    def test_find_json_prints_the_records_with_their_scores(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        code, out, _ = self.ledger_cmd("find", "--question", TIMEOUT_Q, "--json")
        self.assertEqual(code, 0)
        [hit] = json.loads(out)
        self.assertEqual((hit["id"], hit["answer"], hit["score"]), ("a-0001", "Keep 250 ms", 1.0))
        code, out, _ = self.ledger_cmd("find", "--question", UNRELATED_Q, "--json")
        self.assertEqual((code, json.loads(out)), (1, []))

    def test_find_on_unusable_input_exits_2(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        self.assertEqual(self.ledger_cmd("find", "--question", "? a !")[0], 2)
        self.assertEqual(self.ledger_cmd("find", "--question", TIMEOUT_Q, "--floor", "1.5")[0], 2)
        self.ledger.write_text("not json\n", encoding="utf-8")
        code, _, err = self.ledger_cmd("find", "--question", TIMEOUT_Q)
        self.assertEqual(code, 2)
        self.assertIn("ledger.jsonl:1", err)


class Matching(unittest.TestCase):
    def test_a_record_identical_to_the_query_scores_1(self):
        entries = [{"id": "a-0001", "question": RETRY_Q}, {"id": "a-0002", "question": TIMEOUT_Q, "answer": "Keep 250 ms"}]
        [(score, record), *_] = records.find(records.LEDGER, RETRY_Q, entries, floor=0)
        self.assertEqual((record["id"], score), ("a-0001", 1.0))
        reader = [{"id": "r-0001", "topic": "TCP congestion control"}]
        self.assertEqual(records.find(records.READER, "TCP congestion control", reader)[0][0], 1.0)

    def test_units_are_whole_digit_runs_and_trigrams_of_longer_runs_in_any_script(self):
        self.assertEqual(records.units("Timeout 250 ms p99 Тайм-аут x_yz"),
                         ["tim", "ime", "meo", "eou", "out", "250", "p99", "тай", "айм", "аут"])
        self.assertEqual(records.units("ms ab x"), [])

    def test_a_query_without_a_unit_is_unusable(self):
        with self.assertRaises(records.StoreError):
            records.find(records.LEDGER, "ms or ok?", [{"id": "a-0001", "question": "ms or ok?"}])

    def test_the_overlap_divides_by_the_smaller_sentence(self):
        three = records.Counter(records.units("250 400 timeout"))
        self.assertEqual(records.overlap(three, records.Counter(records.units("250"))), 1.0)
        self.assertEqual(records.overlap(three, records.Counter(records.units("250 300"))), 0.5)
        self.assertEqual(records.overlap(three, records.Counter()), 0.0)

    def test_sentences_shorter_than_six_units_are_dropped_unless_all_are(self):
        long_one = "The acknowledgement timeout is 250 ms."
        kept = records.sentences(f"{long_one} Keep it? Yes; no.")
        self.assertEqual(kept, [records.Counter(records.units(long_one))])
        self.assertEqual(records.sentences("Keep it? Yes."), [records.Counter(records.units("Keep it? Yes."))])
        self.assertEqual(len(records.sentences("First sentence holds enough units here… Second sentence holds enough units too! Third one?")), 2)

    def test_a_ledger_record_is_matched_by_its_question_alone(self):
        record = {"id": "a-0001", "question": RETRY_Q, "answer": "Keep the acknowledgement timeout", "scope": "the dispatch router"}
        self.assertEqual(records.find(records.LEDGER, "Keep the acknowledgement timeout for the dispatch router", [record]), [])

    def test_a_reader_record_is_matched_by_each_item_on_its_own(self):
        record = {"id": "r-0001", "topic": "TCP congestion control", "holds": ["slow start"], "lacks": ["pacing of bursts in the sender"]}
        [(score, _)] = records.find(records.READER, "pacing of bursts", [record])
        self.assertEqual(score, 1.0)


# The pairs a hand run of the gate scored: each query against a ledger record whose question is the second text.
REPEATS = [
    ("What wait for an acknowledgement do we ship: 250 ms or 400 ms?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("How long should the router wait for an ack in production?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("Do we switch the logs to UTC or keep the local timestamps?",
     "Should the log timestamps stay in local time or move to UTC?"),
    ("Сколько ждать подтверждения в проде — 250 мс или 400?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("Какое время ожидания подтверждения оставить в продакшене?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("Запись о читателе держим в репозитории или отдельно, в личном файле?",
     "Где хранить запись о читателе: в проекте или в личном файле?"),
    ("The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("A colleague's test expects the router to wait 400 ms for an acknowledgement and the code waits 250. The answer decides which of the two changes; a rollout is undone only by another rollout. Which wait goes to production, 400 or 250?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("Тест коллеги ждёт подтверждения 400 мс, а код ждёт 250. Ответ меняет лимит повторов и его тест; после выкатки это необратимо. Сколько ждать подтверждения в проде — 250 мс или 400?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("A colleague's test expects the router to wait 400 ms for an acknowledgement and the code waits 250. The answer decides which of the two changes; a rollout is undone only by another rollout. Which wait goes to production, 400 or 250?",
     "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?"),
    ("Which acknowledgement timeout do we keep in production?",
     "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?"),
    ("Какой таймаут подтверждения оставляем?",
     "Тест коллеги ждёт подтверждения 400 мс, а код ждёт 250. Ответ меняет лимит повторов и его тест; после выкатки это необратимо. Сколько ждать подтверждения в проде — 250 мс или 400?"),
    ("The new logging library writes timestamps in UTC and the operations alert matches the old local form. The answer decides whether we set one option or wait for the operations team; a silent alert is costly. Keep the old time form or ask operations to change the pattern?",
     "Should the log timestamps stay in local time or move to UTC?"),
]
UNRELATED = [
    ("Which colour should the dashboard header be?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("Should the release wait for the operations team?",
     "Should the log timestamps stay in local time or move to UTC?"),
    ("Какого цвета делать шапку панели?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("Ставим ли новую версию библиотеки в прод сейчас?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("Когда опрашивать читателя: одной карточкой или диалогом?",
     "Где хранить запись о читателе: в проекте или в личном файле?"),
    ("After the move the code stops reading the old limits table in the database, but the table still holds the limit history. Dropping the table cannot be undone, and only you know whether the history is needed. Drop the old table or keep it?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("The new logging library writes timestamps in UTC and the operations alert matches the old local form. The answer decides whether we set one option or wait for the operations team; a silent alert is costly. Keep the old time form or ask operations to change the pattern?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("The retry repeats a payment after a timeout, and the payments team's test forbids it. The answer decides whether the client repeats only reads; a double charge cannot be taken back. Repeat only reads, or ask the payments team to change its test?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("После переезда код перестаёт читать старую таблицу лимитов, но в ней осталась история. Удаление таблицы необратимо, и только ты знаешь, нужна ли история. Удалить старую таблицу или оставить?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("Новая библиотека пишет время в UTC, а оповещение эксплуатации ждёт старый вид. Ответ решает, ставим ли мы настройку или ждём эксплуатацию; молчащее оповещение стоит дорого. Оставить старый вид времени или просить эксплуатацию поменять шаблон?",
     "Какой таймаут подтверждения ставим в прод: 250 или 400 миллисекунд?"),
    ("After the move the code stops reading the old limits table in the database, but the table still holds the limit history. Dropping the table cannot be undone, and only you know whether the history is needed. Drop the old table or keep it?",
     "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?"),
    ("The new logging library writes timestamps in UTC and the operations alert matches the old local form. The answer decides whether we set one option or wait for the operations team; a silent alert is costly. Keep the old time form or ask operations to change the pattern?",
     "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?"),
    ("The retry repeats a payment after a timeout, and the payments team's test forbids it. The answer decides whether the client repeats only reads; a double charge cannot be taken back. Repeat only reads, or ask the payments team to change its test?",
     "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?"),
    ("Новая библиотека пишет время в UTC, а оповещение эксплуатации ждёт старый вид. Ответ решает, ставим ли мы настройку или ждём эксплуатацию; молчащее оповещение стоит дорого. Оставить старый вид времени или просить эксплуатацию поменять шаблон?",
     "Тест коллеги ждёт подтверждения 400 мс, а код ждёт 250. Ответ меняет лимит повторов и его тест; после выкатки это необратимо. Сколько ждать подтверждения в проде — 250 мс или 400?"),
]
KNOWN_FALSE_MATCHES = [
    ("Should production use the new library version or wait?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("После переезда код перестаёт читать старую таблицу лимитов, но в ней осталась история. Удаление таблицы необратимо, и только ты знаешь, нужна ли история. Удалить старую таблицу или оставить?",
     "Тест коллеги ждёт подтверждения 400 мс, а код ждёт 250. Ответ меняет лимит повторов и его тест; после выкатки это необратимо. Сколько ждать подтверждения в проде — 250 мс или 400?"),
]


class RepeatsAndUnrelated(unittest.TestCase):
    """Each query against a ledger record holding the paired question, at the default floor."""

    def score(self, query, record_question):
        found = records.find(records.LEDGER, query, [{"id": "a-0001", "question": record_question}], floor=0)
        return found[0][0]

    def test_every_repeat_reaches_the_floor(self):
        for query, record_question in REPEATS:
            with self.subTest(query=query, record=record_question):
                self.assertGreaterEqual(self.score(query, record_question), records.DEFAULT_FLOOR)

    def test_every_unrelated_question_stays_below_the_floor(self):
        for query, record_question in UNRELATED:
            with self.subTest(query=query, record=record_question):
                self.assertLess(self.score(query, record_question), records.DEFAULT_FLOOR)

    def test_the_known_false_matches_score_between_the_floor_and_one_half(self):
        """Shared trigrams carry these unrelated questions over the floor; they stay below one half."""
        for query, record_question in KNOWN_FALSE_MATCHES:
            with self.subTest(query=query, record=record_question):
                self.assertGreaterEqual(self.score(query, record_question), records.DEFAULT_FLOOR)
                self.assertLess(self.score(query, record_question), 0.50)


class AtomicWrite(InProcess):
    def test_a_failed_write_leaves_the_old_file_and_no_temporary_file(self):
        self.add_answer(TIMEOUT_Q, "Keep 250 ms")
        before = self.ledger.read_bytes()
        with mock.patch.object(records.os, "replace", side_effect=OSError("disk full")):
            code, _, err = self.ledger_cmd("add", "--kind", "answer", "--question", RETRY_Q, "--answer", "Keep three", "--basis", "a card")
        self.assertEqual(code, 2)
        self.assertIn("disk full", err)
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["ledger.jsonl"])


class Reader(InProcess):
    def test_add_find_and_show(self):
        code, out, err = self.reader_cmd("add", "--topic", "TCP congestion control", "--basis", "he named BBR and CUBIC unprompted",
                                         "--holds", "slow start", "cwnd", "--lacks", "pacing", "--use", "build", "--depth", "mechanism")
        self.assertEqual((code, out.strip()), (0, "r-0001"), err)
        self.reader_cmd("add", "--topic", "German tax letters", "--basis", "asked for help", "--lacks", "the Bescheid structure")
        [first, second] = self.stored(self.reader)
        self.assertEqual(first["holds"], ["slow start", "cwnd"])
        self.assertEqual((first["use"], first["depth"]), ("build", "mechanism"))
        self.assertNotIn("holds", second)

        code, out, _ = self.reader_cmd("find", "--topic", "congestion control in TCP")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"^r-0001 · \S+ · \d\.\d\d · TCP congestion control -> holds: slow start, cwnd; lacks: pacing · basis: he named BBR and CUBIC unprompted\n$")
        self.assertEqual(self.reader_cmd("find", "--topic", "Kubernetes ingress")[0], 1)

        code, out, _ = self.reader_cmd("show")
        self.assertEqual([line.split(" · ")[0] for line in out.splitlines()], ["r-0002", "r-0001"])
        self.assertIn("use: build", out.splitlines()[1])

    def test_a_missing_reader_file_shows_nothing_and_finds_nothing(self):
        self.assertEqual(self.reader_cmd("show")[:2], (0, ""))
        self.assertEqual(self.reader_cmd("find", "--topic", "anything")[0], 1)

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_a_reader_file_inside_a_git_work_tree_is_refused_unless_ignored(self):
        tree = self.dir / "repo"
        tree.mkdir()
        subprocess.run(["git", "init", "-q", str(tree)], check=True)
        inside = tree / "notes" / "reader.jsonl"
        code, _, err = self.main("reader", "add", "--reader-file", str(inside), "--topic", "t", "--basis", "b")
        self.assertEqual(code, 2)
        self.assertIn("git work tree", err)
        self.assertFalse(inside.exists())
        self.assertEqual(self.main("reader", "show", "--reader-file", str(inside))[0], 2)

        (tree / ".gitignore").write_text("notes/\n", encoding="utf-8")
        code, _, err = self.main("reader", "add", "--reader-file", str(inside), "--topic", "t", "--basis", "b")
        self.assertEqual(code, 0, err)

    def test_a_directory_that_only_looks_like_a_work_tree_is_refused(self):
        """When git cannot answer for the .git it finds, the doubt refuses the file."""
        (self.dir / "fake" / ".git").mkdir(parents=True)
        code, _, err = self.main("reader", "show", "--reader-file", str(self.dir / "fake" / "reader.jsonl"))
        self.assertEqual(code, 2)
        self.assertIn("git work tree", err)


class StorePaths(unittest.TestCase):
    """The store files from the options, from the environment and by default, under a temporary HOME."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.home = self.dir / "home"
        self.work = self.dir / "work"
        self.home.mkdir()
        self.work.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def env(self, **extra):
        return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.home), **extra}

    def reader_add(self, *argv, env):
        done = run_script("reader", "add", "--topic", "t", "--basis", "b", *argv, env=env, cwd=self.work)
        self.assertEqual(done.returncode, 0, done.stderr)

    def ledger_add(self, *argv, env, cwd=None):
        done = run_script("ledger", "add", "--kind", "answer", "--question", "q?", "--answer", "a", "--basis", "b", *argv, env=env, cwd=cwd or self.work)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_reader_file_by_default_under_home_and_under_xdg_data_home(self):
        self.reader_add(env=self.env())
        self.reader_add(env=self.env(XDG_DATA_HOME=""))
        default = self.home / ".local" / "share" / "handing-over-to-readers" / "reader.jsonl"
        self.assertEqual(len(default.read_text(encoding="utf-8").splitlines()), 2)
        data = self.dir / "data"
        self.reader_add(env=self.env(XDG_DATA_HOME=str(data)))
        self.assertTrue((data / "handing-over-to-readers" / "reader.jsonl").is_file())

    def test_reader_file_from_the_environment_and_from_the_option(self):
        named = self.dir / "named" / "reader.jsonl"
        option = self.dir / "option" / "reader.jsonl"
        self.reader_add(env=self.env(HANDOVER_READER_FILE=str(named)))
        self.reader_add("--reader-file", str(option), env=self.env(HANDOVER_READER_FILE=str(named)))
        self.assertEqual(len(named.read_text(encoding="utf-8").splitlines()), 1)
        self.assertEqual(len(option.read_text(encoding="utf-8").splitlines()), 1)
        self.assertFalse((self.home / ".local").exists())

    def test_ledger_file_by_default_in_the_working_directory_or_its_work_tree(self):
        self.ledger_add(env=self.env())
        self.assertTrue((self.work / ".claude" / "handing-over-to-readers" / "ledger.jsonl").is_file())
        project = self.dir / "project"
        (project / ".git").mkdir(parents=True)
        (project / "src" / "deep").mkdir(parents=True)
        self.ledger_add(env=self.env(), cwd=project / "src" / "deep")
        self.assertTrue((project / ".claude" / "handing-over-to-readers" / "ledger.jsonl").is_file())

    def test_ledger_file_from_the_environment_and_from_the_options(self):
        claude_project = self.dir / "claude-project"
        named = self.dir / "named.jsonl"
        root = self.dir / "root"
        option = self.dir / "option.jsonl"
        self.ledger_add(env=self.env(CLAUDE_PROJECT_DIR=str(claude_project)))
        self.ledger_add(env=self.env(CLAUDE_PROJECT_DIR=str(claude_project), HANDOVER_LEDGER_FILE=str(named)))
        self.ledger_add("--root", str(root), env=self.env(HANDOVER_LEDGER_FILE=str(named)))
        self.ledger_add("--ledger-file", str(option), "--root", str(root), env=self.env(HANDOVER_LEDGER_FILE=str(named)))
        for path in (claude_project / ".claude" / "handing-over-to-readers" / "ledger.jsonl", named,
                     root / ".claude" / "handing-over-to-readers" / "ledger.jsonl", option):
            self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 1, path)
        self.assertFalse((self.work / ".claude").exists())


class Capture(unittest.TestCase):
    """ledger capture --hook: the PostToolUse hook on AskUserQuestion always exits 0."""

    QUESTIONS = [
        {"question": TIMEOUT_Q, "header": "Timeout", "options": [{"label": "Keep 250 ms", "description": "d"}, {"label": "400 ms", "description": "d"}], "multiSelect": False},
        {"question": RETRY_Q, "header": "Retry", "options": [{"label": "Three", "description": "d"}, {"label": "Five", "description": "d"}], "multiSelect": True},
    ]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.ledger = self.dir / "project" / ".claude" / "handing-over-to-readers" / "ledger.jsonl"
        self.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.dir), "CLAUDE_PROJECT_DIR": str(self.dir / "project")}

    def tearDown(self):
        self.tmp.cleanup()

    def capture(self, payload, env=None):
        stdin = payload if isinstance(payload, str) else json.dumps(payload)
        return run_script("ledger", "capture", "--hook", stdin=stdin, env=env or self.env, cwd=self.dir)

    def payload(self, response):
        return {"session_id": "s1", "hook_event_name": "PostToolUse", "tool_name": "AskUserQuestion",
                "tool_input": {"questions": self.QUESTIONS}, "tool_response": response}

    def stored(self):
        return [json.loads(line) for line in self.ledger.read_text(encoding="utf-8").splitlines()]

    def test_a_response_with_answers_records_the_chosen_labels(self):
        response = {"questions": self.QUESTIONS, "answers": {TIMEOUT_Q: "Keep 250 ms", RETRY_Q: "Three,Five"}}
        done = self.capture(self.payload(response))
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        first, second = self.stored()
        self.assertEqual((first["id"], first["kind"], first["question"], first["answer"]), ("a-0001", "answer", TIMEOUT_Q, "Keep 250 ms"))
        self.assertEqual((second["id"], second["answer"], second["basis"]), ("a-0002", "Three,Five", "the reader's answer on a card"))
        output = json.loads(done.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PostToolUse")
        self.assertIn("a-0001, a-0002", output["additionalContext"])
        self.assertIn("ledger note <id>", output["additionalContext"])
        self.assertIn("--overturns", output["additionalContext"])

    def test_a_response_of_another_shape_is_recorded_whole_and_cut_at_2000_characters(self):
        done = self.capture(self.payload({"result": "Keep 250 ms"}))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.stored()[0]["answer"], '{"result":"Keep 250 ms"}')
        long = "x" * 5000
        self.capture(self.payload(long))
        self.assertEqual(self.stored()[-1]["answer"], json.dumps(long)[:2000])
        self.assertEqual(len(self.stored()[-1]["answer"]), 2000)

    def test_an_unreadable_payload_is_one_stderr_line_and_exit_0(self):
        done = self.capture("not json")
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1)
        self.assertIn("unreadable payload", done.stderr)
        self.assertFalse(self.ledger.exists())

    @unittest.skipIf(os.name != "posix" or os.geteuid() == 0, "needs a directory the process cannot write")
    def test_an_unwritable_ledger_is_one_stderr_line_and_exit_0(self):
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_text("", encoding="utf-8")
        self.ledger.parent.chmod(0o500)
        try:
            done = self.capture(self.payload({"answers": {}}))
        finally:
            self.ledger.parent.chmod(0o700)
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1)
        self.assertIn("cannot write", done.stderr)
        self.assertEqual(self.ledger.read_text(encoding="utf-8"), "")

    def test_an_unreadable_ledger_is_one_stderr_line_and_exit_0(self):
        blocker = self.dir / "blocker"
        blocker.write_text("a file where a directory must be", encoding="utf-8")
        env = dict(self.env, HANDOVER_LEDGER_FILE=str(blocker / "ledger.jsonl"))
        done = self.capture(self.payload({"answers": {}}), env=env)
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1)
        self.assertIn("cannot read", done.stderr)


class StreamEncoding(unittest.TestCase):
    def test_utf8_under_another_stream_encoding(self):
        """Text outside the cp1252 code page passes through the streams although the process's encoding is cp1252."""
        question = "Лимит подтверждения 250 ms, für Rückfragen zu knapp. Оставить?"
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "PYTHONIOENCODING": "cp1252", "HANDOVER_LEDGER_FILE": str(ledger)}
            payload = json.dumps({"tool_input": {"questions": [{"question": question}]}, "tool_response": {"answers": {question: "Оставить"}}}, ensure_ascii=False).encode("utf-8")
            capture = subprocess.run([sys.executable, str(SCRIPTS / "records.py"), "ledger", "capture", "--hook"], input=payload, capture_output=True, env=env)
            self.assertEqual(capture.returncode, 0)
            self.assertEqual(capture.stderr, b"")
            found = subprocess.run([sys.executable, str(SCRIPTS / "records.py"), "ledger", "find", "--question", question], capture_output=True, env=env)
        self.assertEqual(found.returncode, 0, found.stderr.decode("utf-8", "replace"))
        self.assertIn(f"{question} -> Оставить", found.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
