#!/usr/bin/env python3
"""Voice a story and write when each of its sentences sounds.

    voice_cues.py (--voice-module PATH | --tts-command CMD) [--lang ru] [--pause 0.6] [--gap 0.25]
                  [--cache DIR] STORY.txt OUT.wav OUT.json

STORY.txt is the spoken text: paragraphs separated by an empty line. A sentence ends at `.`, `!`,
`?` or `…` followed by white space. One backend voices it, chosen by exactly one of two options;
without either option, $HANDOVER_VOICE_MODULE or $HANDOVER_TTS_COMMAND supplies it, and an option
given on the command line overrides both variables.

--voice-module PATH  a Python module providing `speak(text, lang, words=True)`, whose result has
    `.wav` (the bytes of a WAV file) and `.words` (a list of {"offset", "length", "start", "end"}:
    code-point offsets into the text, seconds from the start of that WAV). One call per paragraph;
    a sentence runs from its first word's start to its last word's end, and a sentence that holds
    no word of the timings fails the run. --pause seconds of silence follow every paragraph.
--tts-command CMD  a command line holding the placeholders {text} and {out}. It is split like a
    shell line and run without a shell, once per sentence, {text} replaced by the sentence and
    {out} by a temporary WAV path the command writes. A sentence's cue is the span its audio
    occupies in OUT.wav. --gap seconds of silence follow every sentence, and --pause seconds more
    follow the last sentence of a paragraph. --lang is not passed to the command.
--cache DIR  keeps the backend's audio between runs in DIR, created when missing, so a run voices
    only what no earlier run voiced. An entry is a file named by the SHA-256 of its key parts
    joined by a zero byte: for --tts-command the command line as given and the sentence, the entry
    holding the sentence's WAV; for --voice-module the module's resolved path, --lang and the
    paragraph, the entry holding the paragraph's WAV and word timings. A run takes an entry instead
    of calling the backend, voices again an entry that cannot be read or is damaged and replaces it,
    and keeps nothing of a paragraph that fails. The closing line then counts the sentences or
    paragraphs synthesised and those taken from the cache.

Every WAV of a run has the same channels, sample width and rate. OUT.wav joins them in order.
OUT.json lists the sentences: [{"paragraph", "sentence", "text", "start", "end"}], numbered from
1, in seconds of OUT.wav. The script writes OUT.wav and OUT.json and nothing else beside the
command's temporary files, the entries of --cache DIR and, with the usage journal of feedback.py
turned on, one line of counts to that journal: the backend, written or failed, the numbers of
sentences and paragraphs and the whole seconds of audio; a failed run leaves no OUT.wav behind
and journals only a failure of the backend it chose.

Exit: 0 written; 2 no usable backend, unreadable input, a cache directory that cannot be created
or written, or a backend failure (the message names the sentence or paragraph).
"""
from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
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
from typing import Any, Callable, Mapping, NamedTuple

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


class AudioCache:
    """Synthesised audio kept between runs, one file per entry, named by the SHA-256 of the key parts joined by a zero byte.

    Without a directory every lookup misses and nothing is kept. The directory is created when
    missing and must take a file, which the constructor tries before any backend runs; VoiceError
    otherwise. An entry is written to a temporary file and renamed into place, so a reader finds a
    whole entry or none."""

    def __init__(self, directory: Path | None):
        self._directory = directory
        if directory is not None:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryFile(dir=directory):
                    pass  # creating the file is the test; it is deleted on close
            except OSError as e:
                raise VoiceError(f"cannot create or write the cache directory {directory}: {e}") from e

    def get(self, key_parts: tuple[str, ...]) -> bytes | None:
        """The bytes kept under the key; None when the entry is absent or cannot be read."""
        if self._directory is None:
            return None
        try:
            return self._entry(key_parts).read_bytes()
        except OSError:  # an unreadable entry is a miss: the backend voices it again and put() replaces it
            return None

    def put(self, key_parts: tuple[str, ...], data: bytes) -> None:
        """Keep the bytes under the key, replacing an earlier entry; VoiceError when the directory cannot be written."""
        if self._directory is None:
            return
        part: Path | None = None
        try:
            handle, name = tempfile.mkstemp(dir=self._directory, suffix=".part")
            part = Path(name)
            with os.fdopen(handle, "wb") as out:
                out.write(data)
            part.replace(self._entry(key_parts))
        except OSError as e:
            if part is not None:
                with contextlib.suppress(OSError):  # the write failed already; a stray .part file is never read as an entry
                    part.unlink()
            raise VoiceError(f"cannot write to the cache directory {self._directory}: {e}") from e

    def _entry(self, key_parts: tuple[str, ...]) -> Path:
        # a command line or a path may carry bytes the file system could not decode, held as surrogates
        joined = b"\0".join(part.encode("utf-8", "surrogatepass") for part in key_parts)
        return self._directory / hashlib.sha256(joined).hexdigest()


def is_complete_wav(data: bytes) -> bool:
    """Whether the bytes are a readable WAV file holding every frame its header announces."""
    try:
        with wave.open(io.BytesIO(data)) as audio:
            announced = audio.getnframes() * audio.getsampwidth() * audio.getnchannels()
            return len(audio.readframes(audio.getnframes())) == announced
    except (wave.Error, EOFError):
        return False


class Speech(NamedTuple):
    """A paragraph's audio and its word timings, as speak() returned them or as the cache kept them."""

    wav: bytes
    words: list[dict]


class ModuleVoice(NamedTuple):
    """The speak() of a synthesiser module with what tells its audio apart in the cache: the module's resolved path and the language."""

    speak: Callable[..., Any]
    path: str
    lang: str


class Pacing(NamedTuple):
    """Seconds of silence: `gap` after every sentence of the command backend, `pause` after every paragraph."""

    gap: float
    pause: float


def word_timing(word: Mapping[str, float]) -> dict[str, float]:
    """The parts of a word timing the cues read, as plain JSON numbers."""
    return {"offset": int(word["offset"]), "start": float(word["start"]), "end": float(word["end"])}


def speech_entry(speech: Speech) -> bytes:
    """A module entry of the cache: one JSON object holding the WAV in base64 and the word timings."""
    stored = {"wav": base64.b64encode(speech.wav).decode("ascii"), "words": [word_timing(word) for word in speech.words]}
    return json.dumps(stored).encode("utf-8")


def cached_speech(entry: bytes | None) -> Speech | None:
    """The speech a module entry holds; None when there is no entry or it is not of the shape speech_entry() writes."""
    if entry is None:
        return None
    try:
        stored = json.loads(entry)
        speech = Speech(base64.b64decode(stored["wav"], validate=True), [word_timing(word) for word in stored["words"]])
    except (ValueError, KeyError, TypeError, OverflowError):
        return None
    return speech if is_complete_wav(speech.wav) else None


def untimed_sentence(spans: list[tuple[int, int]], words: list[dict]) -> int | None:
    """The number, from 1, of the first sentence whose span holds no word of the timings; None when each has one."""
    for index, (start, end) in enumerate(spans, 1):
        if not any(start <= word["offset"] < end for word in words):
            return index
    return None


def require_timings(number: int, spans: list[tuple[int, int]], words: list[dict]) -> None:
    """Raise VoiceError naming the first sentence of paragraph `number` whose span holds no word of the timings."""
    index = untimed_sentence(spans, words)
    if index is not None:
        raise VoiceError(
            f"sentence {number}.{index}: the synthesiser module returned no word timing for this sentence, "
            "and its cue needs one; --tts-command needs none"
        )


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


def voice_with_module(story: list[str], voice: ModuleVoice, pause: float, joiner: WavJoiner, cache: AudioCache) -> tuple[list[dict], int]:
    """Voice each paragraph in one call, or take it from the cache, and time its sentences by the word timings.

    Returns the cues and the number of paragraphs the module voiced. A paragraph reaches the cache
    only after each of its sentences has a word timing."""
    cues: list[dict] = []
    synthesised = 0
    for number, paragraph in enumerate(story, 1):
        key = (voice.path, voice.lang, paragraph)
        spans = sentence_spans(paragraph)
        speech = cached_speech(cache.get(key))
        if speech is not None and untimed_sentence(spans, speech.words) is not None:
            speech = None  # an entry whose timings miss a sentence of today's split is voiced again, like a damaged one
        fresh = speech is None
        if speech is None:
            spoken = voice.speak(paragraph, voice.lang, words=True)
            speech = Speech(spoken.wav, list(spoken.words or []))
        require_timings(number, spans, speech.words)
        offset = joiner.seconds
        joiner.append(speech.wav, f"paragraph {number}")
        joiner.silence(pause)
        if fresh:
            cache.put(key, speech_entry(speech))
            synthesised += 1
        for index, ((a, b), (begin, finish)) in enumerate(zip(spans, sentence_times(spans, speech.words)), 1):
            cues.append(cue(number, index, paragraph[a:b], offset + begin, offset + finish))
    return cues, synthesised


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


def voice_with_command(story: list[str], command: str, pacing: Pacing, joiner: WavJoiner, cache: AudioCache) -> tuple[list[dict], int]:
    """Voice each sentence in one run of the command, or take its WAV from the cache; a sentence's cue is the span its audio occupies.

    Returns the cues and the number of sentences the command voiced."""
    template = command_template(command)
    cues: list[dict] = []
    synthesised = 0
    with tempfile.TemporaryDirectory(prefix="voice_cues-") as scratch:
        for number, paragraph in enumerate(story, 1):
            for index, (a, b) in enumerate(sentence_spans(paragraph), 1):
                text, label = paragraph[a:b], f"sentence {number}.{index}"
                key = (command, text)
                audio = cache.get(key)
                fresh = audio is None or not is_complete_wav(audio)
                if fresh:
                    audio = run_command(template, text, Path(scratch) / f"{number}.{index}.wav", label)
                start = joiner.seconds
                length = joiner.append(audio, label)
                if fresh:
                    cache.put(key, audio)
                    synthesised += 1
                cues.append(cue(number, index, text, start, start + length))
                joiner.silence(pacing.gap)
            joiner.silence(pacing.pause)
    return cues, synthesised


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
    parser.add_argument("--cache", type=Path, help="directory that keeps the backend's audio between runs")
    args = parser.parse_args(argv)
    joiner = WavJoiner(args.wav)
    voicing = False  # true while the chosen backend runs: only its failure is journaled
    try:
        kind, backend = choose_backend(args.voice_module, args.tts_command, os.environ if environ is None else environ)
        try:
            story = paragraphs(args.story.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as e:
            raise VoiceError(f"cannot read the story {args.story}: {e}") from e
        if not story:
            raise VoiceError(f"the story {args.story} has no paragraph")
        cache = AudioCache(args.cache)
        voicing = True
        if kind == "module":
            voice = ModuleVoice(load_speak(backend), str(Path(backend).resolve()), args.lang)
            cues, synthesised = voice_with_module(story, voice, args.pause, joiner, cache)
        else:
            cues, synthesised = voice_with_command(story, backend, Pacing(gap=args.gap, pause=args.pause), joiner, cache)
        voicing = False
        joiner.close()
        args.cues.write_text(json.dumps(cues, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    except (VoiceError, OSError) as e:
        joiner.abandon()
        print(f"voice_cues: {e}", file=sys.stderr)
        if voicing:
            journal("voice", backend=kind, outcome="failed", paragraphs=len(story))
        return 2
    reuse = cache_count(kind, synthesised, len(story) if kind == "module" else len(cues)) if args.cache is not None else ""
    print(f"{len(cues)} sentences in {cues[-1]['paragraph']} paragraphs, {joiner.seconds:.1f} s -> {args.wav}, {args.cues}{reuse}")
    journal("voice", backend=kind, outcome="written", sentences=len(cues), paragraphs=len(story), seconds=round(joiner.seconds))
    return 0


def cache_count(kind: str, synthesised: int, voiced: int) -> str:
    """The closing line's tail under --cache: how many of the voiced sentences or paragraphs were synthesised, how many cached."""
    unit = "paragraphs" if kind == "module" else "sentences"
    return f"; {synthesised} {unit} synthesised, {voiced - synthesised} from the cache"


def journal(event: str, **fields: object) -> None:
    """Add one line of counts to the usage journal of feedback.py beside this script, when the user turned it on."""
    try:
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import feedback

        feedback.record(event, **fields)
    except Exception:  # noqa: BLE001 - an isolation point: a missing or broken feedback.py changes nothing in this run
        pass


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
