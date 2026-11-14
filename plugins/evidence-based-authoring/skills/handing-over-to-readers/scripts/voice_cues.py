#!/usr/bin/env python3
"""Voice a story and write when each of its sentences sounds.

    voice_cues.py (--voice-module PATH | --tts-command CMD) [--lang ru] [--pause 0.6] [--gap 0.25]
                  STORY.txt OUT.wav OUT.json

STORY.txt is the spoken text: paragraphs separated by an empty line. A sentence ends at `.`, `!`,
`?` or `…` followed by white space. One backend voices it, chosen by exactly one of two options;
without either option, $HANDOVER_VOICE_MODULE or $HANDOVER_TTS_COMMAND supplies it, and an option
given on the command line overrides both variables.

--voice-module PATH  a Python module providing `speak(text, lang, words=True)`, whose result has
    `.wav` (the bytes of a WAV file) and `.words` (a list of {"offset", "length", "start", "end"}:
    code-point offsets into the text, seconds from the start of that WAV). One call per paragraph;
    a sentence runs from its first word's start to its last word's end. --pause seconds of
    silence follow every paragraph.
--tts-command CMD  a command line holding the placeholders {text} and {out}. It is split like a
    shell line and run without a shell, once per sentence, {text} replaced by the sentence and
    {out} by a temporary WAV path the command writes. A sentence's cue is the span its audio
    occupies in OUT.wav. --gap seconds of silence follow every sentence, and --pause seconds more
    follow the last sentence of a paragraph. --lang is not passed to the command.

Every WAV of a run has the same channels, sample width and rate. OUT.wav joins them in order.
OUT.json lists the sentences: [{"paragraph", "sentence", "text", "start", "end"}], numbered from
1, in seconds of OUT.wav. The script writes OUT.wav and OUT.json and nothing else beside the
command's temporary files; a failed run leaves no OUT.wav behind.

Exit: 0 written; 2 no usable backend, unreadable input, or a backend failure (the message names
the sentence or paragraph).
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Callable, Mapping

SENTENCE_BREAK = re.compile(r"(?<=[.!?…])\s+")
PLACEHOLDER = re.compile(r"\{(text|out)\}")
MODULE_VARIABLE = "HANDOVER_VOICE_MODULE"
COMMAND_VARIABLE = "HANDOVER_TTS_COMMAND"


class VoiceError(Exception):
    """A backend or an input that the run cannot use; main() turns it into exit 2."""


def paragraphs(text: str) -> list[str]:
    """Paragraphs of the story, each on one line: the inner line breaks become spaces."""
    return [" ".join(part.split()) for part in re.split(r"\n\s*\n", text) if part.strip()]


def sentence_spans(paragraph: str) -> list[tuple[int, int]]:
    """Code-point spans [start, end) of the paragraph's sentences."""
    spans, start = [], 0
    for match in SENTENCE_BREAK.finditer(paragraph):
        spans.append((start, match.start()))
        start = match.end()
    if start < len(paragraph):
        spans.append((start, len(paragraph)))
    return spans


def sentence_times(spans: list[tuple[int, int]], words: list[dict]) -> list[tuple[float, float]]:
    """Start and end, in seconds, of each span: from its first word's start to its last word's end.
    A span without a word of its own takes the moment the previous span ended."""
    times, last_end = [], 0.0
    for start, end in spans:
        inside = [word for word in words if start <= word["offset"] < end]
        if inside:
            begin, finish = min(word["start"] for word in inside), max(word["end"] for word in inside)
        else:
            begin = finish = last_end
        times.append((begin, finish))
        last_end = finish
    return times


class WavJoiner:
    """Appends WAV parts and silence to one output file and keeps the running length in frames.

    The first part fixes channels, sample width and rate; a later part that differs raises
    VoiceError naming the part's label. close() must be called; abandon() closes and deletes."""

    def __init__(self, path: Path):
        self.path = path
        self._out: wave.Wave_write | None = None
        self._format: tuple[int, int, int] | None = None
        self.frames = 0

    @property
    def seconds(self) -> float:
        return self.frames / self._format[2] if self._format else 0.0

    def append(self, wav_bytes: bytes, label: str) -> float:
        """Append the frames of one WAV file; return its length in seconds."""
        try:
            with wave.open(io.BytesIO(wav_bytes)) as part:
                found = (part.getnchannels(), part.getsampwidth(), part.getframerate())
                frames = part.readframes(part.getnframes())
                count = part.getnframes()
        except (wave.Error, EOFError) as e:
            raise VoiceError(f"{label}: the audio is not a readable WAV file ({e})") from e
        if self._format is None:
            self._format = found
            self._out = wave.open(str(self.path), "wb")
            self._out.setnchannels(found[0])
            self._out.setsampwidth(found[1])
            self._out.setframerate(found[2])
        elif found != self._format:
            raise VoiceError(f"{label}: WAV with {describe(found)}, the run's earlier audio has {describe(self._format)}")
        self._out.writeframes(frames)
        self.frames += count
        return count / found[2]

    def silence(self, seconds: float) -> None:
        if self._format is None or seconds <= 0:
            return
        channels, width, rate = self._format
        count = int(round(rate * seconds))
        self._out.writeframes(b"\0" * count * width * channels)
        self.frames += count

    def close(self) -> None:
        if self._out is not None:
            self._out.close()
            self._out = None

    def abandon(self) -> None:
        self.close()
        if self._format is not None:
            self.path.unlink(missing_ok=True)


def describe(wav_format: tuple[int, int, int]) -> str:
    channels, width, rate = wav_format
    return f"{channels} channel(s), {width}-byte samples at {rate} Hz"


def cue(paragraph: int, sentence: int, text: str, start: float, end: float) -> dict:
    return {"paragraph": paragraph, "sentence": sentence, "text": text, "start": round(start, 3), "end": round(end, 3)}


def load_speak(path: str) -> Callable:
    """The `speak` function of the synthesiser module at `path`."""
    spec = importlib.util.spec_from_file_location("handover_voice", path)
    if spec is None or spec.loader is None:
        raise VoiceError(f"cannot load the synthesiser module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses of the module resolve their own module by name
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError, SyntaxError) as e:
        raise VoiceError(f"cannot load the synthesiser module {path}: {e}") from e
    if not hasattr(module, "speak"):
        raise VoiceError(f"the synthesiser module {path} has no speak()")
    return module.speak


def voice_with_module(story: list[str], speak: Callable, lang: str, pause: float, joiner: WavJoiner) -> list[dict]:
    """Voice each paragraph in one call and time its sentences by the word timings."""
    cues: list[dict] = []
    for number, paragraph in enumerate(story, 1):
        offset = joiner.seconds
        speech = speak(paragraph, lang, words=True)
        joiner.append(speech.wav, f"paragraph {number}")
        joiner.silence(pause)
        spans = sentence_spans(paragraph)
        for index, ((a, b), (begin, finish)) in enumerate(zip(spans, sentence_times(spans, speech.words)), 1):
            cues.append(cue(number, index, paragraph[a:b], offset + begin, offset + finish))
    return cues


def command_template(line: str) -> list[str]:
    """The command line split into arguments; it must hold both {text} and {out}."""
    try:
        template = shlex.split(line)
    except ValueError as e:
        raise VoiceError(f"cannot split the TTS command {line!r}: {e}") from e
    missing = [name for name in ("{text}", "{out}") if not any(name in part for part in template)]
    if not template or missing:
        raise VoiceError(f"the TTS command {line!r} lacks the placeholder(s) {' '.join(missing) or '{text} {out}'}")
    return template


def run_command(template: list[str], text: str, out: Path, label: str) -> bytes:
    """Run the command for one sentence and return the WAV it wrote."""
    values = {"text": text, "out": str(out)}
    argv = [PLACEHOLDER.sub(lambda match: values[match.group(1)], part) for part in template]
    try:
        done = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
    except OSError as e:
        raise VoiceError(f"{label}: cannot run the TTS command {argv[0]!r}: {e}") from e
    if done.returncode != 0:
        tail = done.stderr.decode("utf-8", "replace").strip().splitlines()[-1:] or [""]
        raise VoiceError(f"{label}: the TTS command exited with {done.returncode} {tail[0]}".rstrip())
    try:
        return out.read_bytes()
    except OSError as e:
        raise VoiceError(f"{label}: the TTS command wrote no audio to {{out}} ({e})") from e


def voice_with_command(story: list[str], template: list[str], pause: float, gap: float, joiner: WavJoiner) -> list[dict]:
    """Voice each sentence in one run of the command; a sentence's cue is the span its audio occupies."""
    cues: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="voice_cues-") as scratch:
        for number, paragraph in enumerate(story, 1):
            spans = sentence_spans(paragraph)
            for index, (a, b) in enumerate(spans, 1):
                label = f"sentence {number}.{index}"
                out = Path(scratch) / f"{number}.{index}.wav"
                audio = run_command(template, paragraph[a:b], out, label)
                start = joiner.seconds
                length = joiner.append(audio, label)
                cues.append(cue(number, index, paragraph[a:b], start, start + length))
                joiner.silence(gap)
            joiner.silence(pause)
    return cues


def choose_backend(module: str | None, command: str | None, environ: Mapping[str, str]) -> tuple[str, str]:
    """('module', PATH) or ('command', CMD): the options first, the environment when neither is given."""
    if module is None and command is None:
        module, command = environ.get(MODULE_VARIABLE) or None, environ.get(COMMAND_VARIABLE) or None
        source = f"${MODULE_VARIABLE} and ${COMMAND_VARIABLE}"
    else:
        source = "--voice-module and --tts-command"
    if module and command:
        raise VoiceError(f"both backends given by {source}: pass one of --voice-module or --tts-command")
    if module:
        return "module", module
    if command:
        return "command", command
    raise VoiceError(f"no backend: pass --voice-module PATH or --tts-command CMD, or set ${MODULE_VARIABLE} or ${COMMAND_VARIABLE}")


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("story", type=Path)
    parser.add_argument("wav", type=Path)
    parser.add_argument("cues", type=Path)
    parser.add_argument("--voice-module", help=f"synthesiser module; default ${MODULE_VARIABLE}")
    parser.add_argument("--tts-command", help=f"command with {{text}} and {{out}}; default ${COMMAND_VARIABLE}")
    parser.add_argument("--lang", default="ru", help="language passed to the synthesiser module")
    parser.add_argument("--pause", type=float, default=0.6, help="seconds of silence after each paragraph")
    parser.add_argument("--gap", type=float, default=0.25, help="seconds of silence after each sentence of --tts-command")
    args = parser.parse_args(argv)
    joiner = WavJoiner(args.wav)
    try:
        kind, backend = choose_backend(args.voice_module, args.tts_command, os.environ if environ is None else environ)
        try:
            story = paragraphs(args.story.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as e:
            raise VoiceError(f"cannot read the story {args.story}: {e}") from e
        if not story:
            raise VoiceError(f"the story {args.story} has no paragraph")
        if kind == "module":
            cues = voice_with_module(story, load_speak(backend), args.lang, args.pause, joiner)
        else:
            cues = voice_with_command(story, command_template(backend), args.pause, args.gap, joiner)
        joiner.close()
        args.cues.write_text(json.dumps(cues, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    except (VoiceError, OSError) as e:
        joiner.abandon()
        print(f"voice_cues: {e}", file=sys.stderr)
        return 2
    print(f"{len(cues)} sentences in {cues[-1]['paragraph']} paragraphs, {joiner.seconds:.1f} s -> {args.wav}, {args.cues}")
    return 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
