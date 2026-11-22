"""grade.py: how the grader of the evals reads the items of a client's question list."""
import re
import sys
import unittest
from pathlib import Path

EVALS = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS))
import grade  # noqa: E402

CHANNEL = r"\bchannel\b|second (network )?(line|link|connection)"


def channel_items(text):
    return [x for x in grade.client_items(text) if re.search(CHANNEL, x.text, re.IGNORECASE)]


class ClientItems(unittest.TestCase):
    def test_an_option_bullet_belongs_to_the_question_above_it(self):
        text = "\n".join([
            "1. A second network connection on your side",
            "",
            "- A. Keep one connection plus our backup storage.",
            "- B. Add a second connection on your side.",
            "",
            "2. How a missed prediction is counted",
            "",
            "- A. By message.",
            "- B. By time.",
        ])
        items = grade.client_items(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(channel_items(text)), 1)
        self.assertIn("B. Add a second connection", items[0].text)

    def test_two_questions_on_one_topic_stay_two_items(self):
        text = "\n".join([
            "1. Is a second network link acceptable on your side?",
            "2. Who pays for the second link?",
        ])
        self.assertEqual(len(channel_items(text)), 2)

    def test_a_bullet_that_is_no_option_is_an_item_of_its_own(self):
        text = "\n".join([
            "- Is a pause of two seconds acceptable?",
            "- Should a doubtful time be shown?",
        ])
        self.assertEqual(len(grade.client_items(text)), 2)

    def test_the_internal_block_is_left_out(self):
        text = "\n".join([
            "1. Is a pause acceptable?",
            "",
            "## Internal",
            "",
            "- B. a note of ours, not an option",
        ])
        self.assertEqual(len(grade.client_items(text)), 1)


if __name__ == "__main__":
    unittest.main()
