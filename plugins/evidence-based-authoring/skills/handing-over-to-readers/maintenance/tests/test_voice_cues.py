import contextlib
import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/voice_cues.py"
spec = importlib.util.spec_from_file_location("voice_cues", SCRIPT)
vc = importlib.util.module_from_spec(spec)
sys.modules["voice_cues"] = vc
spec.loader.exec_module(vc)


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


# A synthesiser that speaks one word a second into a silent WAV of 10 frames a second.
FAKE_VOICE = '''
import io, re, wave
from dataclasses import dataclass

@dataclass
class Speech:
    wav: bytes
    words: list

def speak(text, lang, words=False):
    found = [{"offset": m.start(), "length": len(m.group()), "start": float(i), "end": i + 0.8}
             for i, m in enumerate(re.finditer(r"\\\\w+", text))]
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(10)
        out.writeframes(b"\\\\0\\\\0" * 10 * len(found))
    return Speech(buffer.getvalue(), found)
'''.replace("\\\\", "\\")

# A TTS command: writes a silent WAV of one second per word, at 10 frames a second, to the path after
# --out. The word "fail" makes it exit 3, the word "nothing" makes it write no file, the word
# "stereo" makes it write two channels.
FAKE_COMMAND = '''
import sys, wave
text, out = sys.argv[sys.argv.index("--text") + 1], sys.argv[sys.argv.index("--out") + 1]
words = text.split()
if "fail" in text:
    print("synthesis failed", file=sys.stderr)
    sys.exit(3)
if "nothing" in text:
    sys.exit(0)
with wave.open(out, "wb") as audio:
    channels = 2 if "stereo" in text else 1
    audio.setnchannels(channels); audio.setsampwidth(2); audio.setframerate(10)
    audio.writeframes(b"\\0\\0" * channels * 10 * len(words))
'''


def run(argv, environ=None):
    """main() with its stderr captured: (exit code, stderr text)."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        code = vc.main(argv, environ if environ is not None else {})
    return code, err.getvalue()


class Splitting(unittest.TestCase):
    def test_paragraphs_join_their_lines(self):
        self.assertEqual(["One two.", "Three."], vc.paragraphs("One\ntwo.\n\n \nThree.\n"))

    def test_sentence_spans_cover_the_sentences(self):
        text = "Как это работает. Клиент ждёт? Да!"
        self.assertEqual(["Как это работает.", "Клиент ждёт?", "Да!"], [text[a:b] for a, b in vc.sentence_spans(text)])

    def test_a_colon_does_not_end_a_sentence(self):
        self.assertEqual(1, len(vc.sentence_spans("Первый: повторять только чтение.")))


class Timing(unittest.TestCase):
    def test_a_sentence_runs_from_its_first_word_to_its_last(self):
        text = "One two. Three."
        words = [{"offset": 0, "start": 0.1, "end": 0.4}, {"offset": 4, "start": 0.5, "end": 0.9}, {"offset": 9, "start": 1.3, "end": 1.8}]
        self.assertEqual([(0.1, 0.9), (1.3, 1.8)], vc.sentence_times(vc.sentence_spans(text), words))

    def test_a_sentence_without_words_takes_the_previous_end(self):
        self.assertEqual([(0.0, 0.5), (0.5, 0.5)], vc.sentence_times([(0, 4), (5, 8)], [{"offset": 0, "start": 0.0, "end": 0.5}]))


class Workspace(unittest.TestCase):
    """A temporary directory with the fake voice, the fake command and a story."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        (self.dir / "voice.py").write_text(FAKE_VOICE, encoding="utf-8")
        (self.dir / "tts.py").write_text(FAKE_COMMAND, encoding="utf-8")
        self.command = f"{shlex.quote(sys.executable)} {shlex.quote(str(self.dir / 'tts.py'))} --text {{text}} --out {{out}}"

    def tearDown(self):
        self._tmp.cleanup()

    def story(self, text):
        (self.dir / "story.txt").write_text(text, encoding="utf-8")
        return [str(self.dir / "story.txt"), str(self.dir / "out.wav"), str(self.dir / "cues.json")]

    def cues(self):
        return json.loads((self.dir / "cues.json").read_text(encoding="utf-8"))


class ModuleBackend(Workspace):
    def test_cues_are_offset_by_the_earlier_paragraphs_and_the_pause(self):
        code, _ = run(["--voice-module", str(self.dir / "voice.py"), "--pause", "0.5"] + self.story("One two. Three.\n\nFour five.\n"))
        self.assertEqual(0, code)
        cues = self.cues()
        self.assertEqual([(1, 1, "One two."), (1, 2, "Three."), (2, 1, "Four five.")], [(c["paragraph"], c["sentence"], c["text"]) for c in cues])
        self.assertEqual([(0.0, 1.8), (2.0, 2.8), (3.5, 5.3)], [(c["start"], c["end"]) for c in cues])  # paragraph 1 lasts 3 s, the pause 0.5 s
        with wave.open(str(self.dir / "out.wav")) as audio:
            self.assertEqual(60, audio.getnframes())  # 3 s + 0.5 s + 2 s + 0.5 s at 10 frames a second

    def test_a_missing_module_is_exit_2(self):
        code, err = run(["--voice-module", str(self.dir / "absent.py")] + self.story("One.\n"))
        self.assertEqual(2, code)
        self.assertIn("absent.py", err)


class CommandBackend(Workspace):
    def test_the_closing_line_is_utf8_under_another_stream_encoding(self):
        (self.dir / "story.txt").write_text("One two.\n", encoding="utf-8")
        out = self.dir / "рассказ.wav"
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONIOENCODING": "cp1252", "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]}
        done = subprocess.run([sys.executable, str(SCRIPT), "--tts-command", self.command, str(self.dir / "story.txt"), str(out), str(self.dir / "cues.json")],
                              capture_output=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        self.assertIn(out.name, done.stdout.decode("utf-8"))

    def test_cues_follow_the_audio_with_gap_and_pause(self):
        code, err = run(["--tts-command", self.command, "--gap", "0.2", "--pause", "0.5"] + self.story("One two. Three.\n\nFour five six.\n"))
        self.assertEqual(0, code, err)
        cues = self.cues()
        self.assertEqual([(1, 1, "One two."), (1, 2, "Three."), (2, 1, "Four five six.")], [(c["paragraph"], c["sentence"], c["text"]) for c in cues])
        # 2 s, gap 0.2; 1 s, gap 0.2, pause 0.5; 3 s, gap 0.2, pause 0.5
        self.assertEqual([(0.0, 2.0), (2.2, 3.2), (3.9, 6.9)], [(c["start"], c["end"]) for c in cues])
        with wave.open(str(self.dir / "out.wav")) as audio:
            self.assertEqual(76, audio.getnframes())

    def test_the_sentence_reaches_the_command_as_one_argument(self):
        code, err = run(["--tts-command", self.command] + self.story("It's a \"quoted\" line; $HOME stays.\n"))
        self.assertEqual(0, code, err)
        self.assertEqual("It's a \"quoted\" line; $HOME stays.", self.cues()[0]["text"])
        self.assertEqual(0.0, self.cues()[0]["start"])
        self.assertEqual(6.0, self.cues()[0]["end"])

    def test_a_non_zero_exit_is_exit_2_naming_the_sentence(self):
        code, err = run(["--tts-command", self.command] + self.story("One two.\n\nThree. Then fail here.\n"))
        self.assertEqual(2, code)
        self.assertIn("sentence 2.2", err)
        self.assertIn("exited with 3", err)
        self.assertFalse((self.dir / "out.wav").exists())
        self.assertFalse((self.dir / "cues.json").exists())

    def test_a_missing_output_is_exit_2_naming_the_sentence(self):
        code, err = run(["--tts-command", self.command] + self.story("One. Say nothing.\n"))
        self.assertEqual(2, code)
        self.assertIn("sentence 1.2", err)
        self.assertIn("no audio", err)

    def test_a_mismatched_wav_is_exit_2_naming_the_sentence(self):
        code, err = run(["--tts-command", self.command] + self.story("One. Two.\n\nNow stereo.\n"))
        self.assertEqual(2, code)
        self.assertIn("sentence 2.1", err)
        self.assertIn("2 channel(s)", err)
        self.assertFalse((self.dir / "out.wav").exists())

    def test_a_command_without_the_out_placeholder_is_exit_2(self):
        code, err = run(["--tts-command", "say {text}"] + self.story("One.\n"))
        self.assertEqual(2, code)
        self.assertIn("{out}", err)


class ChoosingTheBackend(Workspace):
    def test_both_options_are_exit_2_naming_both(self):
        code, err = run(["--voice-module", str(self.dir / "voice.py"), "--tts-command", self.command] + self.story("One.\n"))
        self.assertEqual(2, code)
        self.assertIn("--voice-module", err)
        self.assertIn("--tts-command", err)

    def test_no_backend_is_exit_2_naming_both_options(self):
        code, err = run(self.story("One.\n"))
        self.assertEqual(2, code)
        self.assertIn("--voice-module", err)
        self.assertIn("--tts-command", err)

    def test_both_variables_are_exit_2(self):
        environ = {"HANDOVER_VOICE_MODULE": str(self.dir / "voice.py"), "HANDOVER_TTS_COMMAND": self.command}
        code, err = run(self.story("One.\n"), environ)
        self.assertEqual(2, code)
        self.assertIn("--voice-module", err)

    def test_the_command_variable_is_the_default(self):
        code, err = run(self.story("One two.\n"), {"HANDOVER_TTS_COMMAND": self.command})
        self.assertEqual(0, code, err)
        self.assertEqual([(0.0, 2.0)], [(c["start"], c["end"]) for c in self.cues()])

    def test_the_module_variable_is_the_default(self):
        code, err = run(self.story("One two.\n"), {"HANDOVER_VOICE_MODULE": str(self.dir / "voice.py")})
        self.assertEqual(0, code, err)
        self.assertEqual([(0.0, 1.8)], [(c["start"], c["end"]) for c in self.cues()])

    def test_an_option_overrides_either_variable(self):
        environ = {"HANDOVER_VOICE_MODULE": str(self.dir / "absent.py"), "HANDOVER_TTS_COMMAND": "absent {text} {out}"}
        code, err = run(["--tts-command", self.command] + self.story("One two.\n"), environ)
        self.assertEqual(0, code, err)
        self.assertEqual([(0.0, 2.0)], [(c["start"], c["end"]) for c in self.cues()])


if __name__ == "__main__":
    unittest.main()
