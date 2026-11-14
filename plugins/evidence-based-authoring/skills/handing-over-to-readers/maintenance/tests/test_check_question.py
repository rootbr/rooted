"""check_question.py: the card form of a question to the operator."""
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
import check_question as cq  # noqa: E402


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


GOOD = {
    "question": "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?",
    "header": "Timeout",
    "options": [
        {"label": "250 ms", "description": "Fewer retries; at a p99 spike some jobs go to retry, cost of error: a duplicate job."},
        {"label": "400 ms", "description": "Almost no retries; the acknowledgement arrives 150 ms later, cost of error: a missed update."},
    ],
}


def codes(questions):
    return [p.split(" ", 3)[2].rstrip(":") for p in cq.problems(questions)]


def run_script(*args, stdin, env=None):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_question.py"), *args], input=stdin, capture_output=True, text=True,
                          env=None if env is None else {**env, "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]})


class CardForm(unittest.TestCase):
    def test_good_card_passes(self):
        self.assertEqual(cq.problems([GOOD]), [])

    def test_bare_question_fails_on_fact_and_why(self):
        q = {"question": "Which timeout?", "options": [{"label": "250", "description": "keep the current timeout value"}]}
        self.assertEqual(set(codes([q])), {"FACT", "WHY-ASKED"})

    def test_two_questions_or_question_not_last(self):
        two = dict(GOOD, question="Timeout 250 ms. Keep it? Or raise it, the decision is irreversible?")
        self.assertIn("ONE", codes([two]))
        not_last = dict(GOOD, question="Timeout 250 ms. Keep 250 ms? The decision is irreversible.")
        self.assertIn("ONE", codes([not_last]))
        none = dict(GOOD, question="Timeout 250 ms, the decision is irreversible.")
        self.assertIn("ONE", codes([none]))

    def test_option_without_consequence(self):
        q = dict(GOOD, options=[{"label": "250 ms", "description": "keep"}])
        self.assertIn("OPTIONS", codes([q]))

    def test_identifier_in_card(self):
        q = dict(GOOD, question=GOOD["question"].replace("The acknowledgement timeout", "Agent a9facb10357345e1e: the acknowledgement timeout"))
        self.assertIn("IDENT", codes([q]))

    def test_title_field_is_read(self):
        q = dict(GOOD)
        q["title"] = q.pop("question")
        self.assertEqual(cq.problems([q]), [])

    def test_hook_payload_and_exit_codes(self):
        ok = run_script(stdin=json.dumps({"tool_input": {"questions": [GOOD]}}))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        bad = run_script(stdin=json.dumps({"tool_input": {"questions": [{"question": "Which?", "options": []}]}}))
        self.assertEqual(bad.returncode, 1)
        self.assertIn("FACT", bad.stdout)
        unreadable = run_script(stdin="not json")
        self.assertEqual(unreadable.returncode, 2)


class HookMode(unittest.TestCase):
    """--hook: the PreToolUse protocol blocks on exit 2 and shows stderr to the model."""

    def hook(self, stdin, env=None):
        return run_script("--hook", stdin=stdin, env=env)

    def test_passing_card_exits_0_silently(self):
        run = self.hook(json.dumps({"tool_name": "AskUserQuestion", "tool_input": {"questions": [GOOD]}}))
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stderr, "")

    def test_failing_card_exits_2_with_problems_and_guidance_on_stderr(self):
        bare = {"question": "Which one?", "header": "Pick", "options": [{"label": "A", "description": "a"}, {"label": "B", "description": "b"}], "multiSelect": False}
        run = self.hook(json.dumps({"tool_name": "AskUserQuestion", "tool_input": {"questions": [bare]}}))
        self.assertEqual(run.returncode, 2)
        self.assertIn("FACT", run.stderr)
        self.assertIn("OPTIONS", run.stderr)
        self.assertIn(cq.GUIDANCE, run.stderr)

    def test_unreadable_input_never_blocks(self):
        run = self.hook("not json")
        self.assertEqual(run.returncode, 0)
        self.assertIn("unreadable input", run.stderr)


class LedgerGate(unittest.TestCase):
    """--hook: a card that passed the form check is returned once per session when an earlier answer may cover it."""

    REWORDED = dict(GOOD, question="The worker p99 is 180 ms and the acknowledgement timeout stands at 250 ms. Changing it moves the retry limit; after rollout this is irreversible. Should the acknowledgement timeout stay at 250 ms?")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.ledger = self.dir / "ledger.jsonl"
        self.state = self.dir / "state"
        self.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.dir / "home"), "XDG_CONFIG_HOME": str(self.dir / "config"),
                    "XDG_STATE_HOME": str(self.state), "HANDOVER_LEDGER_FILE": str(self.ledger)}
        self.write_ledger(("a-0001", GOOD["question"], "Keep 250 ms"), ("a-0002", "Which log format does the exporter write?", "JSON lines"))

    def tearDown(self):
        self.tmp.cleanup()

    def write_ledger(self, *entries):
        with self.ledger.open("a", encoding="utf-8") as handle:
            for record_id, question, answer in entries:
                handle.write(json.dumps({"id": record_id, "date": "2026-11-01", "kind": "answer", "question": question, "answer": answer, "basis": "the reader's answer on a card", "status": "active"}) + "\n")

    def hook(self, card, session="session-1", env=None):
        payload = {"tool_name": "AskUserQuestion", "tool_input": {"questions": [card]}}
        if session:
            payload["session_id"] = session
        return run_script("--hook", stdin=json.dumps(payload), env=env or self.env)

    def test_a_repeated_question_blocks_once_with_guidance_and_candidates_on_stderr(self):
        first = self.hook(GOOD)
        self.assertEqual(first.returncode, 2, first.stderr)
        self.assertEqual(first.stdout, "")
        self.assertIn(cq.GATE_GUIDANCE, first.stderr)
        self.assertRegex(first.stderr, r"\na-0001 · 2026-11-01 · 1\.00 · The acknowledgement timeout .* -> Keep 250 ms · basis: the reader's answer on a card\n")
        self.assertNotIn("a-0002", first.stderr)
        again = self.hook(GOOD)
        self.assertEqual((again.returncode, again.stderr), (0, ""))

    def test_a_reworded_card_with_the_same_candidate_passes(self):
        self.assertEqual(self.hook(GOOD).returncode, 2)
        reworded = self.hook(self.REWORDED)
        self.assertEqual((reworded.returncode, reworded.stderr), (0, ""))

    def test_a_reworded_card_blocks_in_a_fresh_session(self):
        self.assertEqual(self.hook(self.REWORDED, session="session-2").returncode, 2)

    def test_a_full_card_is_returned_once_by_a_record_with_a_short_question(self):
        """The card form's sentences around the question do not dilute the match of the question's own sentence."""
        self.ledger.unlink()
        self.write_ledger(("a-0001", "Which acknowledgement timeout do we keep in production?", "Keep 250 ms"))
        first = self.hook(GOOD)
        self.assertEqual(first.returncode, 2, first.stderr)
        self.assertIn(cq.GATE_GUIDANCE, first.stderr)
        self.assertIn("a-0001 · ", first.stderr)
        again = self.hook(GOOD)
        self.assertEqual((again.returncode, again.stderr), (0, ""))

    def test_a_new_candidate_blocks_again(self):
        self.assertEqual(self.hook(GOOD).returncode, 2)
        self.write_ledger(("a-0003", GOOD["question"], "Raise to 400 ms"))
        again = self.hook(GOOD)
        self.assertEqual(again.returncode, 2)
        self.assertIn("a-0003", again.stderr)
        self.assertIn("a-0001", again.stderr)

    def test_without_a_session_id_the_card_passes(self):
        run = self.hook(GOOD, session=None)
        self.assertEqual((run.returncode, run.stderr), (0, ""))
        self.assertFalse(self.state.exists())

    def test_without_a_ledger_file_the_card_passes(self):
        self.ledger.unlink()
        run = self.hook(GOOD)
        self.assertEqual((run.returncode, run.stderr), (0, ""))

    def test_an_unreadable_ledger_lets_the_card_pass(self):
        self.ledger.write_text("not json\n", encoding="utf-8")
        run = self.hook(GOOD)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(len(run.stderr.splitlines()), 1)
        self.assertIn("ledger gate", run.stderr)

    def test_an_unwritable_state_directory_lets_the_card_pass(self):
        self.state.write_text("a file where the state directory must be", encoding="utf-8")
        run = self.hook(GOOD)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(len(run.stderr.splitlines()), 1)
        self.assertIn("ledger gate", run.stderr)

    def test_a_card_outside_the_form_is_rejected_before_the_gate(self):
        run = self.hook({"question": GOOD["question"].replace(" Keep 250 ms?", ""), "options": GOOD["options"]})
        self.assertEqual(run.returncode, 2)
        self.assertIn(cq.GUIDANCE, run.stderr)
        self.assertNotIn(cq.GATE_GUIDANCE, run.stderr)
        self.assertFalse(self.state.exists())

    def test_file_mode_is_untouched_by_the_gate(self):
        card = self.dir / "card.json"
        card.write_text(json.dumps({"session_id": "session-1", "tool_input": {"questions": [GOOD]}}), encoding="utf-8")
        run = run_script("--questions", str(card), stdin="", env=self.env)
        self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "", ""))
        self.assertFalse(self.state.exists())


class Lexicon(unittest.TestCase):
    """A lexicon adds a language's WHY-ASKED words; the hook reads the default file under XDG_CONFIG_HOME."""

    CARD = dict(GOOD, question="The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. After rollout there is no way back. Keep 250 ms?",
                options=[{"label": "250 ms", "description": "Fewer retries; a p99 spike sends some orders to retry."},
                         {"label": "400 ms", "description": "Almost no retries; the acknowledgement arrives 150 ms later."}])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = Path(self.tmp.name)
        (self.config / "handing-over-to-readers").mkdir()
        self.lexicon = self.config / "handing-over-to-readers" / "lexicon.json"
        self.lexicon.write_text(json.dumps({"check_question": {"WHY_ASKED": ["no way back"]}, "check_report": {"RISK": ["Danger"]}}), encoding="utf-8")
        self.env = {"XDG_CONFIG_HOME": str(self.config), "PATH": "/usr/bin:/bin"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_word_from_the_lexicon_passes_why_asked(self):
        payload = json.dumps({"questions": [self.CARD]})
        without = run_script(stdin=payload, env={"XDG_CONFIG_HOME": str(self.config / "none"), "PATH": "/usr/bin:/bin"})
        self.assertEqual(without.returncode, 1)
        self.assertIn("WHY-ASKED", without.stdout)
        named = run_script("--lexicon", str(self.lexicon), stdin=payload)
        self.assertEqual(named.returncode, 0, named.stdout)
        hook = run_script("--hook", stdin=json.dumps({"tool_name": "AskUserQuestion", "tool_input": {"questions": [self.CARD]}}), env=self.env)
        self.assertEqual(hook.returncode, 0, hook.stderr)

    def test_hook_reads_utf8_under_another_stream_encoding(self):
        """A lexicon word outside ASCII matches the payload although the process's streams are cp1252."""
        card = dict(GOOD, question="Das Limit steht bei 250 ms und p99 bei 180 ms. Die Antwort ändert das Limit und seinen Test; nach dem Rollout ist das nicht rückgängig zu machen. 250 ms behalten?")
        with tempfile.TemporaryDirectory() as tmp:
            lexicon = Path(tmp) / "lexicon.json"
            lexicon.write_text(json.dumps({"check_question": {"WHY_ASKED": ["nicht rückgängig"]}}, ensure_ascii=False), encoding="utf-8")
            payload = json.dumps({"tool_input": {"questions": [card]}}, ensure_ascii=False).encode("utf-8")
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONIOENCODING": "cp1252", "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]}
            done = subprocess.run([sys.executable, str(SCRIPTS / "check_question.py"), "--hook", "--lexicon", str(lexicon)], input=payload, capture_output=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))

    def test_unreadable_lexicon_is_reported_and_never_blocks_the_hook(self):
        self.lexicon.write_text("not json", encoding="utf-8")
        plain = run_script("--lexicon", str(self.lexicon), stdin=json.dumps({"questions": [GOOD]}))
        self.assertEqual(plain.returncode, 2)
        self.assertIn("lexicon", plain.stderr)
        hook = run_script("--hook", stdin=json.dumps({"tool_name": "AskUserQuestion", "tool_input": {"questions": [GOOD]}}), env=self.env)
        self.assertEqual(hook.returncode, 0, hook.stderr)
        self.assertIn("lexicon", hook.stderr)


if __name__ == "__main__":
    unittest.main()
