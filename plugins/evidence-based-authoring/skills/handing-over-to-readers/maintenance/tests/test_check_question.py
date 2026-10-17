"""check_question.py: the card form of a question to the operator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_question as cq  # noqa: E402

GOOD = {
    "question": "The acknowledgement timeout is 250 ms and the exchange p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?",
    "header": "Timeout",
    "options": [
        {"label": "250 ms", "description": "Fewer retries; at a p99 spike some orders go to retry, cost of error: a duplicate order."},
        {"label": "400 ms", "description": "Almost no retries; the acknowledgement arrives 150 ms later, cost of error: a missed quote."},
    ],
}


def codes(questions):
    return [p.split(" ", 3)[2].rstrip(":") for p in cq.problems(questions)]


def run_script(*args, stdin, env=None):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_question.py"), *args], input=stdin, capture_output=True, text=True, env=env)


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


class Lexicon(unittest.TestCase):
    """A lexicon adds a language's WHY-ASKED words; the hook reads the default file under XDG_CONFIG_HOME."""

    CARD = dict(GOOD, question="The acknowledgement timeout is 250 ms and the exchange p99 is 180 ms. After rollout there is no way back. Keep 250 ms?",
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
