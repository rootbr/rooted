"""records.py: the reader record, the ledger of answers, the record of exchanges, their matching and the capture hook."""
from __future__ import annotations

import contextlib
import io
import json
import math
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


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


TIMEOUT_Q = "The acknowledgement timeout is 250 ms. Keep the acknowledgement timeout at 250 ms?"
REWORDED_Q = "Should we keep a 250 ms timeout for the acknowledgement?"
UNRELATED_Q = "What colour should the dashboard header have?"
RETRY_Q = "Should the retry limit stay at three attempts?"


def run_script(*args, env, stdin=None, cwd=None):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "records.py"), *args], input=stdin, capture_output=True, text=True,
                          env={**env, "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]}, cwd=cwd)


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

    def test_the_overlap_divides_by_the_geometric_mean_of_the_two_unit_counts(self):
        """Four units and nine sharing two: the smaller count gives 1/2, the larger 2/9, the geometric mean 6 gives 1/3."""
        four = records.Counter(records.units("250 400 300 500"))
        nine = records.Counter(records.units("250 400 600 700 800 900 100 110 120"))
        self.assertEqual((sum(four.values()), sum(nine.values()), sum((four & nine).values())), (4, 9, 2))
        self.assertAlmostEqual(records.overlap(four, nine), 2 / 6)
        self.assertAlmostEqual(records.overlap(nine, four), 2 / 6)
        self.assertAlmostEqual(records.overlap(four, four), 1.0)
        self.assertEqual(records.overlap(four, records.Counter()), 0.0)
        self.assertEqual(records.overlap(records.Counter(), records.Counter()), 0.0)

    def test_a_short_sentence_sharing_a_few_units_with_a_long_one_stays_below_the_floor(self):
        """Nine units sharing five with a record sentence of forty: 5/sqrt(9*40) is 0.26."""
        query, question = "Deploy tonight?", "Should the billing service wait tonight for the schema migrations to finish?"
        short, long_one = records.Counter(records.units(query)), records.Counter(records.units(question))
        self.assertEqual((sum(short.values()), sum(long_one.values()), sum((short & long_one).values())), (9, 40, 5))
        self.assertEqual(records.sentences(question), [long_one])
        self.assertEqual(records.find(records.LEDGER, query, [{"id": "a-0001", "question": question}]), [])
        [(score, _)] = records.find(records.LEDGER, query, [{"id": "a-0001", "question": question}], floor=0)
        self.assertAlmostEqual(score, 5 / math.sqrt(9 * 40))

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
        """The query's eight units all lie in the lacks item of thirteen units, which no other text of the record dilutes."""
        record = {"id": "r-0001", "topic": "TCP congestion control", "holds": ["slow start"], "lacks": ["pacing of bursts in the sender"]}
        [(score, _)] = records.find(records.READER, "pacing of bursts", [record])
        self.assertAlmostEqual(score, 8 / math.sqrt(8 * 13))


FORM_SENTENCE = "Only you know whether the operations team can take a change this week."
SHORT_ENDED_CARD = ("The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; "
                    "after rollout the decision is irreversible. Keep 250 ms?")


class QuestionMatching(unittest.TestCase):
    """The ledger store matches a card through its question, and two texts without one whole; the reader store keeps every pair of sentences."""

    def ledger_score(self, query, record_question):
        [(score, _)] = records.find(records.LEDGER, query, [{"id": "a-0001", "question": record_question}], floor=0)
        return score

    def test_the_question_of_a_text_is_its_last_sentence(self):
        long_last = "Keep the acknowledgement timeout at 250 ms?"
        self.assertEqual(records.question(RETRY_Q), records.Counter(records.units(RETRY_Q)))
        self.assertEqual(records.question(f"The acknowledgement timeout is 250 ms. {long_last}"), records.Counter(records.units(long_last)))

    def test_a_last_sentence_under_the_minimum_after_other_sentences_is_no_question(self):
        self.assertIsNone(records.question(SHORT_ENDED_CARD))

    def test_a_last_sentence_of_exactly_the_minimum_is_a_question(self):
        """The question "Retry stays?" gives six units (ret, etr, try, sta, tay, ays), and "Retry now 2?" gives five."""
        fact = "The retry limit is three attempts."
        six = records.Counter(records.units("Retry stays?"))
        self.assertEqual(sum(six.values()), records.MIN_SENTENCE_UNITS)
        self.assertEqual(records.question(f"{fact} Retry stays?"), six)
        self.assertIsNone(records.question(f"{fact} Retry now 2?"))

    def test_a_text_whose_only_sentence_is_under_the_minimum_is_its_own_question(self):
        self.assertEqual(records.question(" Keep 250 ms? "), records.Counter(records.units("Keep 250 ms?")))

    def test_two_cards_sharing_a_form_sentence_meet_only_under_the_reader_score(self):
        """The cards differ in fact and question and share one sentence of the form word for word."""
        timeout = f"The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. {FORM_SENTENCE} Should the acknowledgement timeout stay at 250 ms?"
        export = f"The exporter writes plain text and the new parser reads JSON lines. {FORM_SENTENCE} Which log format should the exporter write from now on?"
        self.assertEqual(records.find(records.LEDGER, timeout, [{"id": "a-0001", "question": export}]), [])
        self.assertEqual(records.find(records.LEDGER, export, [{"id": "a-0001", "question": timeout}]), [])
        [(score, _)] = records.find(records.READER, timeout, [{"id": "r-0001", "topic": export}])
        self.assertGreaterEqual(score, records.DEFAULT_FLOOR)

    def test_a_short_record_question_and_a_full_card_that_rewords_it_find_each_other(self):
        card = ("The client retries a failed payment call three times, and the payments team's test counts the attempts. "
                "Raising the limit changes that test; only you know whether the team accepts it. Do we keep the retry limit at three attempts?")
        self.assertGreaterEqual(self.ledger_score(card, RETRY_Q), records.DEFAULT_FLOOR)
        self.assertGreaterEqual(self.ledger_score(RETRY_Q, card), records.DEFAULT_FLOOR)

    def test_a_card_ending_in_a_short_question_is_found_by_its_fact_against_a_record_that_is_one_question(self):
        self.assertGreaterEqual(self.ledger_score(SHORT_ENDED_CARD, "Which acknowledgement timeout do we keep in production?"), records.DEFAULT_FLOOR)

    def test_a_card_ending_in_a_short_question_is_found_by_its_repeat_word_for_word(self):
        """Neither side has a question, so the two whole texts are the one pair."""
        [(score, record)] = records.find(records.LEDGER, SHORT_ENDED_CARD, [{"id": "a-0001", "question": SHORT_ENDED_CARD}])
        self.assertEqual((record["id"], score), ("a-0001", 1.0))

    def test_two_short_question_cards_sharing_a_form_sentence_reach_the_floor_when_scored_whole(self):
        """What the whole-text pair does: a fact sentence, the shared form sentence and a short question each, the form about half
        of each card's units (28, 32, 3 and 31, 32, 4), score 0.57, and the record on another matter is found."""
        timeout = f"The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. {FORM_SENTENCE} Keep 250 ms?"
        export = f"The exporter writes plain text and the new parser reads JSON lines. {FORM_SENTENCE} Keep JSON?"
        self.assertEqual([len(records.units(s)) for s in records.SENTENCE_BREAK.split(timeout)], [28, 32, 3])
        self.assertEqual([len(records.units(s)) for s in records.SENTENCE_BREAK.split(export)], [31, 32, 4])
        [(score, _)] = records.find(records.LEDGER, timeout, [{"id": "a-0001", "question": export}])
        self.assertAlmostEqual(score, 0.57, places=2)


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
    ("Should production use the new library version or wait?",
     "Which acknowledgement timeout should production have, 250 or 400 milliseconds?"),
    ("После переезда код перестаёт читать старую таблицу лимитов, но в ней осталась история. Удаление таблицы необратимо, и только ты знаешь, нужна ли история. Удалить старую таблицу или оставить?",
     "Тест коллеги ждёт подтверждения 400 мс, а код ждёт 250. Ответ меняет лимит повторов и его тест; после выкатки это необратимо. Сколько ждать подтверждения в проде — 250 мс или 400?"),
]
# Repeats the question rule does not find: the record has no question to match by, and the query's question shares little with the record's sentences.
MISSED_REPEATS = [
    ("A colleague's test expects the router to wait 400 ms for an acknowledgement and the code waits 250. The answer decides which of the two changes; a rollout is undone only by another rollout. Which wait goes to production, 400 or 250?",
     SHORT_ENDED_CARD),
]
MARGIN_HUNDREDTHS = 3


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

    def test_a_missed_repeat_stays_below_the_floor(self):
        """The record card ends in "Keep 250 ms?", under the minimum, so only the query's question pairs with the record's sentences, and those share little with it."""
        for query, record_question in MISSED_REPEATS:
            with self.subTest(query=query, record=record_question):
                self.assertIsNone(records.question(record_question))
                self.assertLess(self.score(query, record_question), records.DEFAULT_FLOOR)

    def test_the_floor_keeps_its_margin_to_the_lowest_repeat_and_the_highest_unrelated_pair(self):
        """At least three hundredths on each side, with every score taken in whole hundredths, the precision find prints."""
        floor = round(records.DEFAULT_FLOOR * 100)
        lowest_repeat = min(round(self.score(q, r) * 100) for q, r in REPEATS)
        highest_unrelated = max(round(self.score(q, r) * 100) for q, r in UNRELATED)
        self.assertGreaterEqual(lowest_repeat - floor, MARGIN_HUNDREDTHS, f"lowest repeat {lowest_repeat}/100, floor {floor}/100")
        self.assertGreaterEqual(floor - highest_unrelated, MARGIN_HUNDREDTHS, f"highest unrelated {highest_unrelated}/100, floor {floor}/100")


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


class ReaderWords(InProcess):
    """The reader's own words and the words he barred: stored, printed after holds and lacks, journalled as counts, never matched."""

    WORD = "cache key: the name a picture is stored under"

    def add(self, *argv):
        code, out, err = self.reader_cmd("add", "--topic", "image cache", "--basis", "he named the key himself", *argv)
        self.assertEqual(code, 0, err)
        return out.strip()

    def test_the_two_lists_are_stored_without_blank_items(self):
        self.add("--holds", "eviction", "--words", self.WORD, " ", "--words", "thumbnail: the small picture", "--barred", "fingerprint", "")
        [record] = self.stored(self.reader)
        self.assertEqual(record["words"], [self.WORD, "thumbnail: the small picture"])
        self.assertEqual(record["barred"], ["fingerprint"])

    def test_a_list_left_empty_is_not_stored(self):
        self.add("--words", " ", "--barred", "")
        [record] = self.stored(self.reader)
        self.assertNotIn("words", record)
        self.assertNotIn("barred", record)

    def test_find_and_show_print_holds_lacks_words_barred_in_that_order(self):
        self.add("--barred", "fingerprint", "--words", self.WORD, "--lacks", "eviction", "--holds", "a hash")
        body = f"image cache -> holds: a hash; lacks: eviction; words: {self.WORD}; barred: fingerprint"
        code, out, _ = self.reader_cmd("find", "--topic", "image cache")
        self.assertEqual(code, 0)
        self.assertIn(f" · {body} · basis: ", out)
        code, out, _ = self.reader_cmd("show")
        self.assertIn(f" · {body} · basis: ", out)

    def test_words_and_barred_are_not_matched(self):
        record = {"id": "r-0001", "topic": "image cache", "words": [self.WORD], "barred": ["fingerprint of a thumbnail"]}
        self.assertEqual(records.READER.texts(record), ["image cache"])
        self.assertEqual(records.find(records.READER, "fingerprint of a thumbnail", [record]), [])

    def test_the_journal_counts_the_items_of_each_list(self):
        with mock.patch.object(records, "journal", autospec=True) as journal:
            self.add("--holds", "a", "--words", self.WORD, "--barred", "fingerprint", "digest")
            self.add()
        self.assertEqual(journal.call_args_list, [
            mock.call("reader_add", holds=1, lacks=0, words=1, barred=2, use="none", depth="none"),
            mock.call("reader_add", holds=0, lacks=0, words=0, barred=0, use="none", depth="none"),
        ])


class Exchange(InProcess):
    """The record of exchanges, in a file named by the option."""

    def setUp(self):
        super().setUp()
        self.exchanges = self.dir / "exchanges.jsonl"

    def exchange_cmd(self, command, *argv):
        return self.main("exchange", command, "--exchange-file", str(self.exchanges), *argv)

    def add(self, *argv, topic="the cache explainer", form="page", opening="said-back"):
        code, out, err = self.exchange_cmd("add", "--topic", topic, "--form", form, "--opening", opening, *argv)
        self.assertEqual(code, 0, err)
        return out.strip()

    def test_add_prints_the_id_and_stores_the_record(self):
        self.assertEqual(self.add("--reply", "asked", "--asked", "what is a key?", " ", "--note", " he read it twice "), "x-0001")
        self.assertEqual(self.add(form="text", opening="none"), "x-0002")
        first, second = self.stored(self.exchanges)
        self.assertEqual(first, {"id": "x-0001", "date": records.today(), "topic": "the cache explainer", "form": "page", "opening": "said-back",
                                 "reply": "asked", "asked": ["what is a key?"], "note": "he read it twice"})
        self.assertEqual(second, {"id": "x-0002", "date": records.today(), "topic": "the cache explainer", "form": "text", "opening": "none"})

    def test_add_refuses_a_blank_topic_or_note_and_a_value_outside_its_set(self):
        code, _, err = self.exchange_cmd("add", "--topic", "  ", "--form", "page", "--opening", "none")
        self.assertEqual(code, 2)
        self.assertIn("--topic is empty", err)
        code, _, err = self.exchange_cmd("add", "--topic", "t", "--form", "page", "--opening", "none", "--note", " ")
        self.assertEqual(code, 2)
        self.assertIn("--note is empty", err)
        self.assertFalse(self.exchanges.exists())
        for argv in (["--form", "video", "--opening", "none"], ["--form", "page", "--opening", "maybe"],
                     ["--form", "page", "--opening", "none", "--reply", "ignored"], ["--form", "page"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                records.main(["exchange", "add", "--exchange-file", str(self.exchanges), "--topic", "t", *argv], {})
            self.assertEqual(raised.exception.code, 2)

    def test_note_sets_the_reply(self):
        self.add()
        code, out, err = self.exchange_cmd("note", "x-0001", "--reply", "acted")
        self.assertEqual((code, out, err), (0, "x-0001\n", ""))
        self.assertEqual(self.stored(self.exchanges)[0]["reply"], "acted")
        self.exchange_cmd("note", "x-0001", "--reply", "corrected")
        self.assertEqual(self.stored(self.exchanges)[0]["reply"], "corrected")

    def test_note_extends_the_questions(self):
        self.add("--asked", "what is a key?")
        self.assertEqual(self.exchange_cmd("note", "x-0001", "--asked", "why a version?", " ", "--asked", "which cache?")[0], 0)
        self.assertEqual(self.stored(self.exchanges)[0]["asked"], ["what is a key?", "why a version?", "which cache?"])
        self.add()
        self.exchange_cmd("note", "x-0002", "--asked", "what is a key?")
        self.assertEqual(self.stored(self.exchanges)[1]["asked"], ["what is a key?"])

    def test_note_sets_the_note_and_leaves_the_rest(self):
        self.add("--note", "first", "--reply", "asked")
        self.assertEqual(self.exchange_cmd("note", "x-0001", "--note", "he went on with the rollout")[0], 0)
        [record] = self.stored(self.exchanges)
        self.assertEqual((record["note"], record["reply"], record["opening"]), ("he went on with the rollout", "asked", "said-back"))

    def test_note_of_an_unknown_id_exits_2(self):
        self.add()
        before = self.exchanges.read_bytes()
        code, _, err = self.exchange_cmd("note", "x-0042", "--reply", "acted")
        self.assertEqual(code, 2)
        self.assertIn("no record x-0042", err)
        self.assertEqual(self.exchanges.read_bytes(), before)

    def test_note_that_changes_nothing_exits_2(self):
        self.add()
        before = self.exchanges.read_bytes()
        for argv in ([], ["--asked", " "]):
            with self.subTest(argv=argv):
                code, _, err = self.exchange_cmd("note", "x-0001", *argv)
                self.assertEqual(code, 2)
                self.assertIn("note changes nothing", err)
        self.assertEqual(self.exchange_cmd("note", "x-0001", "--note", " ")[0], 2)
        self.assertEqual(self.exchanges.read_bytes(), before)

    def test_show_prints_every_record_newest_first_with_the_absent_parts_left_out(self):
        self.add("--reply", "asked", "--asked", "what is a key?", "why a version?", "--note", "he read it twice")
        self.add(topic="the retry change", form="text", opening="none")
        code, out, _ = self.exchange_cmd("show")
        self.assertEqual(code, 0)
        today = records.today()
        self.assertEqual(out.splitlines(), [
            f"x-0002 · {today} · text · the retry change -> opening: none",
            f"x-0001 · {today} · page · the cache explainer -> opening: said-back; reply: asked; asked: what is a key?, why a version? · note: he read it twice",
        ])

    def test_count_of_an_empty_store(self):
        code, out, _ = self.exchange_cmd("count")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [
            "deliverables: 0 (text 0, page 0)",
            "opening: said-back 0, accepted 0, corrected 0, none 0",
            "first reply: acted 0, asked 0, corrected 0, open 0",
            "opening confirmed: first reply acted 0 of 0",
            "opening not confirmed: first reply acted 0 of 0",
        ])
        self.assertFalse(self.exchanges.exists())

    def test_count_of_a_store_that_fills_every_line(self):
        """Confirmed: said-back acted, accepted acted, corrected asked, said-back open; not confirmed: none acted, none corrected, none asked."""
        for opening, reply, form in (("said-back", "acted", "page"), ("accepted", "acted", "text"), ("corrected", "asked", "text"),
                                     ("said-back", None, "page"), ("none", "acted", "text"), ("none", "corrected", "text"), ("none", "asked", "text")):
            self.add(*(["--reply", reply] if reply else []), form=form, opening=opening)
        code, out, _ = self.exchange_cmd("count")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [
            "deliverables: 7 (text 5, page 2)",
            "opening: said-back 2, accepted 1, corrected 1, none 3",
            "first reply: acted 3, asked 2, corrected 1, open 1",
            "opening confirmed: first reply acted 2 of 3",
            "opening not confirmed: first reply acted 1 of 3",
        ])

    def test_the_journal_records_add_and_note_but_not_show_or_count(self):
        with mock.patch.object(records, "journal", autospec=True) as journal:
            self.add(form="text", opening="accepted")
            self.add("--reply", "corrected", form="page", opening="none")
            self.exchange_cmd("note", "x-0001", "--asked", "what is a key?", "why a version?")
            self.exchange_cmd("note", "x-0001", "--reply", "asked")
            self.exchange_cmd("show")
            self.exchange_cmd("count")
        self.assertEqual(journal.call_args_list, [
            mock.call("exchange_add", form="text", opening="accepted", reply="none"),
            mock.call("exchange_add", form="page", opening="none", reply="corrected"),
            mock.call("exchange_note", reply="none", asked=2),
            mock.call("exchange_note", reply="asked", asked=0),
        ])

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_an_exchange_file_inside_a_git_work_tree_is_refused_unless_ignored(self):
        tree = self.dir / "repo"
        tree.mkdir()
        subprocess.run(["git", "init", "-q", str(tree)], check=True)
        inside = tree / "notes" / "exchanges.jsonl"
        for command in (["add", "--topic", "t", "--form", "page", "--opening", "none"], ["note", "x-0001", "--reply", "acted"], ["show"], ["count"]):
            with self.subTest(command=command[0]):
                code, _, err = self.main("exchange", command[0], "--exchange-file", str(inside), *command[1:])
                self.assertEqual(code, 2)
                self.assertIn(f"the exchange file {inside} lies inside the git work tree", err)
                self.assertIn("--exchange-file or $HANDOVER_EXCHANGE_FILE", err)
        self.assertFalse(inside.exists())
        (tree / ".gitignore").write_text("notes/\n", encoding="utf-8")
        code, _, err = self.main("exchange", "add", "--exchange-file", str(inside), "--topic", "t", "--form", "page", "--opening", "none")
        self.assertEqual(code, 0, err)


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

    def exchange_add(self, *argv, env):
        done = run_script("exchange", "add", "--topic", "t", "--form", "text", "--opening", "none", *argv, env=env, cwd=self.work)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_exchange_file_by_default_under_home_and_under_xdg_data_home(self):
        self.exchange_add(env=self.env())
        self.exchange_add(env=self.env(XDG_DATA_HOME=""))
        default = self.home / ".local" / "share" / "handing-over-to-readers" / "exchanges.jsonl"
        self.assertEqual(len(default.read_text(encoding="utf-8").splitlines()), 2)
        data = self.dir / "data"
        self.exchange_add(env=self.env(XDG_DATA_HOME=str(data)))
        self.assertTrue((data / "handing-over-to-readers" / "exchanges.jsonl").is_file())

    def test_exchange_file_from_the_environment_and_from_the_option(self):
        named = self.dir / "named" / "exchanges.jsonl"
        option = self.dir / "option" / "exchanges.jsonl"
        self.exchange_add(env=self.env(HANDOVER_EXCHANGE_FILE=str(named), HANDOVER_READER_FILE=str(self.dir / "reader.jsonl")))
        self.exchange_add("--exchange-file", str(option), env=self.env(HANDOVER_EXCHANGE_FILE=str(named)))
        self.assertEqual(len(named.read_text(encoding="utf-8").splitlines()), 1)
        self.assertEqual(len(option.read_text(encoding="utf-8").splitlines()), 1)
        self.assertFalse((self.home / ".local").exists())
        self.assertFalse((self.dir / "reader.jsonl").exists())

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

    def assert_records_nothing(self, response):
        """The call exits 0, prints nothing on stdout, names both questions on one stderr line and creates no ledger file."""
        done = self.capture(self.payload(response))
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1, done.stderr)
        self.assertIn("questions 1, 2 of 2", done.stderr)
        self.assertFalse(self.ledger.exists())

    def test_an_empty_answers_records_nothing(self):
        """A dialog closed without a choice."""
        self.assert_records_nothing({"questions": self.QUESTIONS, "answers": {}})

    def test_answers_without_the_question_record_nothing(self):
        self.assert_records_nothing({"answers": {"Which colour should the dashboard header be?": "Blue"}})

    def test_an_empty_or_white_space_answer_records_nothing(self):
        for chosen in ("", "  \n", [], ["Three", " "], None, 3):
            with self.subTest(chosen=chosen):
                self.assert_records_nothing({"answers": {TIMEOUT_Q: chosen, RETRY_Q: chosen}})

    def test_a_response_that_is_no_mapping_records_nothing(self):
        for response in ("Keep 250 ms", ["Keep 250 ms"], None, {"result": "Keep 250 ms"}, {"answers": ["Keep 250 ms"]}):
            with self.subTest(response=response):
                self.assert_records_nothing(response)

    def test_of_two_questions_only_the_answered_one_is_recorded(self):
        done = self.capture(self.payload({"answers": {TIMEOUT_Q: " Keep 250 ms "}}))
        self.assertEqual(done.returncode, 0)
        self.assertEqual(len(done.stderr.splitlines()), 1, done.stderr)
        self.assertIn("question 2 of 2", done.stderr)
        [record] = self.stored()
        self.assertEqual((record["id"], record["question"], record["answer"]), ("a-0001", TIMEOUT_Q, "Keep 250 ms"))
        context = json.loads(done.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn(" as a-0001. ", context)
        self.assertNotIn("a-0002", context)

    def test_the_chosen_text_is_stripped_and_a_list_is_joined(self):
        self.assertEqual(records.captured_answer(RETRY_Q, {"answers": {RETRY_Q: ["Three", " Five "]}}), "Three, Five")
        self.assertEqual(records.captured_answer(RETRY_Q, {"answers": {RETRY_Q: "\tThree "}}), "Three")
        self.assertIsNone(records.captured_answer(RETRY_Q, {"answers": {TIMEOUT_Q: "Keep 250 ms"}}))

    def test_a_call_that_records_nothing_adds_no_journal_line(self):
        """In process, with the journal replaced: a call that records one answer journals it, one that records none does not."""
        answered = json.dumps(self.payload({"answers": {TIMEOUT_Q: "Keep 250 ms"}}))
        unanswered = json.dumps(self.payload({"answers": {}}))
        with mock.patch.object(records, "journal", autospec=True) as journal, \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(records.capture(unanswered, self.ledger), 0)
            self.assertEqual((journal.call_count, out.getvalue()), (0, ""))
            self.assertFalse(self.ledger.exists())
            self.assertEqual(records.capture(answered, self.ledger), 0)
        journal.assert_called_once_with("answer", count=1)
        before = (self.ledger.read_bytes(), self.ledger.stat().st_ino)
        with mock.patch.object(records, "journal", autospec=True) as journal, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(records.capture(unanswered, self.ledger), 0)
        self.assertEqual((journal.call_count, (self.ledger.read_bytes(), self.ledger.stat().st_ino)), (0, before))

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
            done = self.capture(self.payload({"answers": {TIMEOUT_Q: "Keep 250 ms", RETRY_Q: "Three"}}))
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
        done = self.capture(self.payload({"answers": {TIMEOUT_Q: "Keep 250 ms", RETRY_Q: "Three"}}), env=env)
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1)
        self.assertIn("cannot read", done.stderr)


class StreamEncoding(unittest.TestCase):
    def test_utf8_under_another_stream_encoding(self):
        """Text outside the cp1252 code page passes through the streams although the process's encoding is cp1252."""
        question = "Лимит подтверждения 250 ms, für Rückfragen zu knapp. Оставить?"
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "PYTHONIOENCODING": "cp1252", "HANDOVER_LEDGER_FILE": str(ledger), "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]}
            payload = json.dumps({"tool_input": {"questions": [{"question": question}]}, "tool_response": {"answers": {question: "Оставить"}}}, ensure_ascii=False).encode("utf-8")
            capture = subprocess.run([sys.executable, str(SCRIPTS / "records.py"), "ledger", "capture", "--hook"], input=payload, capture_output=True, env=env)
            self.assertEqual(capture.returncode, 0)
            self.assertEqual(capture.stderr, b"")
            found = subprocess.run([sys.executable, str(SCRIPTS / "records.py"), "ledger", "find", "--question", question], capture_output=True, env=env)
        self.assertEqual(found.returncode, 0, found.stderr.decode("utf-8", "replace"))
        self.assertIn(f"{question} -> Оставить", found.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
