#!/usr/bin/env python3
"""Keep what a reader holds, the answers he gave and the deliverables handed to him, and find the records that may answer a question.

    records.py reader find --topic TEXT [--floor F] [--json]
    records.py reader add --topic TEXT --basis TEXT [--holds X ...] [--lacks Y ...] [--words W ...] [--barred B ...] [--use U] [--depth D] [--turns N]
    records.py reader show
    records.py ledger find --question TEXT [--floor F] [--json]
    records.py ledger add --kind K --question TEXT --answer TEXT --basis TEXT [--scope TEXT] [--overturns TEXT]
    records.py ledger note ID [--answer TEXT] [--scope TEXT] [--overturns TEXT] [--basis TEXT]
    records.py ledger supersede ID --by ID
    records.py ledger show
    records.py ledger capture --hook < hook-input.json
    records.py exchange add --topic TEXT --form text|page --opening O [--reply R] [--asked TEXT ...] [--note TEXT]
    records.py exchange note ID [--reply R] [--asked TEXT ...] [--note TEXT]
    records.py exchange show
    records.py exchange count

Three stores, each a JSON Lines file of one record per line, rewritten whole on every change
through a temporary file in the same directory and a rename, so a failed write leaves the old
file as it was.

The reader record holds what one reader knows about a topic. It is personal and belongs to no
project: the file is $XDG_DATA_HOME/handing-over-to-readers/reader.jsonl ($HOME/.local/share
when the variable is unset or empty); --reader-file, else $HANDOVER_READER_FILE, names another.
Every reader command refuses, with exit 2, a reader file inside a git work tree unless that work
tree ignores it, so the record never becomes content of a repository. A record:
    {"id": "r-0001", "date": "YYYY-MM-DD", "topic": "...", "holds": ["..."], "lacks": ["..."],
     "words": ["..."], "barred": ["..."],
     "use": "decide|defend|build|know", "depth": "mechanism|change", "turns": 1, "basis": "..."}
holds, lacks, words, barred, use, depth and turns are optional; turns, from 1 to 3, is the
number of intake cards that were asked. An item of words is the reader's own word for a thing
with what it names ("cache key: the name a picture is stored under"); an item of barred is a word
he rejected or misread ("fingerprint"). A list option drops its blank items, and a list left
empty is not stored.

The record of exchanges holds the long deliverables handed to one reader: how the opening of each
was confirmed before the rest was built, and the reader's first reply to the whole. It is
personal like the reader record: the file is
$XDG_DATA_HOME/handing-over-to-readers/exchanges.jsonl; --exchange-file, else
$HANDOVER_EXCHANGE_FILE, names another; every exchange command refuses, with exit 2, a file inside
a git work tree unless that work tree ignores it. A record:
    {"id": "x-0001", "date": "YYYY-MM-DD", "topic": "...", "form": "text|page",
     "opening": "said-back|accepted|corrected|none", "reply": "acted|asked|corrected",
     "asked": ["..."], "note": "..."}
reply, asked and note are optional. opening: said-back, the reader said in his own words what he
took and it was what was meant; corrected, his words differed and the opening was rewritten
before the rest; accepted, he answered with a bare yes; none, the opening was not sent first.
reply, his first reply to the whole deliverable: acted, he decided, answered or went on with no
question about what the text says; asked, he asked what something in it means or for something
it left out; corrected, he had taken a meaning the author did not intend. asked holds his
questions.

The ledger holds the answers and decisions of one project: the file is
<root>/.claude/handing-over-to-readers/ledger.jsonl. --ledger-file names another file, else
--root the root, else $HANDOVER_LEDGER_FILE the file, else $CLAUDE_PROJECT_DIR the root, else
the nearest ancestor of the working directory that holds .git, else the working directory. A
record:
    {"id": "a-0001", "date": "YYYY-MM-DD", "kind": "answer|default|closure", "question": "...",
     "answer": "...", "basis": "...", "scope": "...", "overturns": "...",
     "status": "active|superseded", "superseded_by": "a-0007"}
scope, overturns and superseded_by are optional.

find scores the query against each record and keeps the records whose score reaches the floor. A
ledger record is matched by its question alone (its answer and scope are printed, not matched); a
reader record by its topic and by every item of holds and lacks, each a text of its own (its
words and barred are printed, not matched). Superseded ledger records are left out. The record of
exchanges has no find.

Units. A text is lower-cased and cut into maximal runs of letters and digits of any script; a
run of digits is one unit, a run of three or more characters that is not all digits gives its
character trigrams as units ("timeout": tim, ime, meo, eou, out), and a shorter run gives none.
Trigrams let a reworded question, an inflected word or a shortened one ("prod", "production")
still share most of its units with the record.

Sentences. A text is split at white space that follows . ! ? … or ;. A sentence of fewer than
six units is dropped; a text all of whose sentences are dropped is one sentence, the whole text.
The question of a text is its last sentence. A text of one sentence is its own question; a last
sentence of fewer than six units after other sentences ("Keep 250 ms?" after its fact) is no
question to match by.

Score. Two sentences match by the size of the multiset intersection of their units divided by
the geometric mean of their two unit counts: between 0 and 1, and 1 for two equal sentences. The
geometric mean weighs the length of both sentences, so a short sentence does not match a long one
on a few shared trigrams (five shared units of nine against forty score 0.26), while a short
question still matches the card sentence that holds it, which is not much longer. A record's
score is the best match over its pairs of sentences, and the two stores pair them differently.
A ledger record pairs the question of the query with every sentence of its question text, and
every sentence of the query with the question of that text; a side with no question to match by
gives no pair of its own. When neither side has one, the two whole texts are the one pair, so a
card repeated word for word scores 1; whole texts and not their sentences, because a form
sentence two unrelated cards share matches in full as a pair of sentences and only as a part of
each whole card. A question card, as the capture hook records it whole, carries the card form's
own sentences (the fact, what the answer changes, why it is asked) before its question: those
sentences repeat from card to card, so two cards on unrelated matters would meet through them,
while the question is a card's own.
Sentence against sentence still lets a short question match the card sentence that holds it,
where a whole-text share of a long card stays low however close the question is. A reader
record pairs every sentence of the query with every sentence of each of its texts, a topic and
single items, none of them a card. A unit is not weighted by its rarity among the records,
because a project's ledger holds few records: in a small store the rarity of a unit says little,
and the words a store lacks would get the highest weight and swamp the words it shares. A query
without a unit is unusable input.

Records at or above the floor (default 0.37) are printed best first, at most five, one line
each:
    <id> · <date> · <score> · <topic or question> -> <holds and lacks, or answer> · basis: <basis>
--json prints the same records as a JSON list, each with its "score".

add appends a record with today's date and the next id and prints its id; ledger note changes
the named fields of one ledger record; supersede marks a ledger record superseded by another; show
prints every record, one line each, newest first. A line of the record of exchanges:
    <id> · <date> · <form> · <topic> -> opening: O; reply: R; asked: a, b · note: <note>
with the absent parts left out.

exchange note completes a record after the reader's first reply: --reply sets the field, --asked
extends the list, --note sets the field; a call that changes none of them, or names an unknown
id, exits 2. exchange count prints, also for an empty store:
    deliverables: 12 (text 9, page 3)
    opening: said-back 4, accepted 3, corrected 1, none 4
    first reply: acted 7, asked 3, corrected 1, open 1
    opening confirmed: first reply acted 6 of 8
    opening not confirmed: first reply acted 1 of 3
open counts the records with no reply yet, which the two last lines leave out; an opening
said-back, accepted or corrected is confirmed, none is not.

capture --hook is the PostToolUse hook on AskUserQuestion. It reads the hook payload on stdin
and appends one ledger record of kind "answer" for every question of tool_input.questions that
tool_response.answers maps to a non-empty answer: a text stripped of white space, or a list of
non-empty texts joined with ", ". A question without an answer, as in a dialog closed without a
choice, gets no record, and one line on stderr names the numbers of those questions. When it
appended records it prints a PostToolUse hookSpecificOutput whose additionalContext names the new
ids and asks for each answer's scope and what would overturn it; when it appended none it leaves
the ledger file as it was, creating none, and prints nothing on stdout. It always exits 0: an
unreadable payload or an unreadable or unwritable ledger is one line on stderr and nothing on
stdout.

Exit: 0 done (find: a record printed); 1 find printed none; 2 unusable input or an unreadable
or unwritable store. The script reads and writes only the stores named above, runs git only to
ask whether a reader or exchange file is ignored, opens no network connection and uses the Python
standard library alone. With the usage journal of feedback.py turned on, every command but show
and exchange count that did its work adds to it one line of counts: what find found, the number
of items and the words of use, depth and turns of a reader record, the kind of a ledger record,
the number of answers capture recorded, the form, opening and reply of a new exchange (reply none
when add set none), the reply an exchange note set (none when it set none) and the number of
questions it added; a capture that recorded none adds no line.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

STORE_DIR = "handing-over-to-readers"
DEFAULT_FLOOR = 0.37
MAX_FOUND = 5
CAPTURE_BASIS = "the reader's answer on a card"
RUN = re.compile(r"[^\W_]+")
TRIGRAM_RUN = 3
SENTENCE_BREAK = re.compile(r"(?<=[.!?…;])\s+")
MIN_SENTENCE_UNITS = 6
LEDGER_KINDS = ("answer", "default", "closure")
READER_USES = ("decide", "defend", "build", "know")
READER_DEPTHS = ("mechanism", "change")
READER_TURNS = (1, 2, 3)
READER_LISTS = ("holds", "lacks", "words", "barred")
EXCHANGE_FORMS = ("text", "page")
EXCHANGE_OPENINGS = ("said-back", "accepted", "corrected", "none")
CONFIRMED_OPENINGS = ("said-back", "accepted", "corrected")
EXCHANGE_REPLIES = ("acted", "asked", "corrected")


class StoreError(Exception):
    """A store or an input the command cannot use; the message names the file or the value."""


def one_line(text: object) -> str:
    return " ".join(str(text).split())


@dataclass(frozen=True)
class Store:
    """How one store numbers, ranks and prints its records."""

    prefix: str
    texts: Callable[[dict], list[str]]
    score: Callable[[str, list[str]], float]
    head: Callable[[dict], str]
    body: Callable[[dict], str]
    tags: Callable[[dict], list[str]]
    extra: Callable[[dict], list[str]]

    def is_live(self, record: dict) -> bool:
        return record.get("status", "active") != "superseded"


def _reader_body(record: dict) -> str:
    parts = [f"{name}: {', '.join(one_line(x) for x in record[name])}" for name in READER_LISTS if record.get(name)]
    return "; ".join(parts) or "-"


def _exchange_body(record: dict) -> str:
    parts = [f"{name}: {one_line(record[name])}" for name in ("opening", "reply") if record.get(name)]
    if record.get("asked"):
        parts.append(f"asked: {', '.join(one_line(x) for x in record['asked'])}")
    return "; ".join(parts) or "-"


# The score lambdas look up the scoring functions of § Matching, below, when they run.
READER = Store(
    prefix="r",
    texts=lambda r: [str(r.get("topic", ""))] + [str(x) for x in r.get("holds") or []] + [str(x) for x in r.get("lacks") or []],
    score=lambda query, texts: sentence_score(query, texts),
    head=lambda r: one_line(r.get("topic", "")),
    body=_reader_body,
    tags=lambda r: [],
    extra=lambda r: [f"{name}: {r[name]}" for name in ("use", "depth", "turns") if r.get(name)],
)
LEDGER = Store(
    prefix="a",
    texts=lambda r: [str(r.get("question", ""))],
    score=lambda query, texts: question_score(query, texts),
    head=lambda r: one_line(r.get("question", "")),
    body=lambda r: one_line(r.get("answer", "")),
    tags=lambda r: [str(r.get("kind", "")), str(r.get("status", "active"))],
    extra=lambda r: [f"{name}: {one_line(r[name])}" for name in ("scope", "overturns") if r.get(name)]
    + ([f"superseded by {r['superseded_by']}"] if r.get("superseded_by") else []),
)
# The record of exchanges is shown and counted, never searched: no command calls find on it.
EXCHANGE = Store(
    prefix="x",
    texts=lambda r: [str(r.get("topic", ""))],
    score=lambda query, texts: sentence_score(query, texts),
    head=lambda r: one_line(r.get("topic", "")),
    body=_exchange_body,
    tags=lambda r: [str(r.get("form", ""))],
    extra=lambda r: [f"note: {one_line(r['note'])}"] if r.get("note") else [],
)


# Paths


def _nonempty(environ: Mapping[str, str], name: str) -> str | None:
    return environ.get(name) or None


def _home(environ: Mapping[str, str]) -> Path:
    return Path(environ["HOME"]) if environ.get("HOME") else Path.home()


@dataclass(frozen=True)
class PrivateFile:
    """A personal store: where it lies by default, how the user names another, and what its refusal calls it."""

    name: str
    option: str
    variable: str
    kind: str
    store_name: str


READER_FILE = PrivateFile("reader.jsonl", "--reader-file", "HANDOVER_READER_FILE", "reader", "the reader record")
EXCHANGE_FILE = PrivateFile("exchanges.jsonl", "--exchange-file", "HANDOVER_EXCHANGE_FILE", "exchange", "the record of exchanges")


def private_path(store: PrivateFile, option: str | None, environ: Mapping[str, str]) -> Path:
    """The option's file, else the environment variable's, else the store's file under $XDG_DATA_HOME or $HOME/.local/share."""
    named = option or _nonempty(environ, store.variable)
    if named:
        return Path(named).expanduser()
    data = _nonempty(environ, "XDG_DATA_HOME")
    base = Path(data) if data else _home(environ) / ".local" / "share"
    return base / STORE_DIR / store.name


def reader_path(option: str | None, environ: Mapping[str, str]) -> Path:
    return private_path(READER_FILE, option, environ)


def exchange_path(option: str | None, environ: Mapping[str, str]) -> Path:
    return private_path(EXCHANGE_FILE, option, environ)


def project_root(cwd: Path) -> Path:
    """The nearest ancestor of cwd, cwd included, that holds .git; cwd itself when none does."""
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".git").exists():
            return candidate
    return cwd


def ledger_path(ledger_file: str | None, root: str | None, environ: Mapping[str, str], cwd: Path | None = None) -> Path:
    """The ledger file: options first, then the environment, then the work tree around cwd."""
    if ledger_file:
        return Path(ledger_file).expanduser()
    if not root:
        named = _nonempty(environ, "HANDOVER_LEDGER_FILE")
        if named:
            return Path(named).expanduser()
        root = _nonempty(environ, "CLAUDE_PROJECT_DIR")
    base = Path(root).expanduser() if root else project_root((cwd or Path.cwd()).resolve())
    return base / ".claude" / STORE_DIR / "ledger.jsonl"


def tracking_work_tree(path: Path) -> Path | None:
    """The git work tree that would hold path as content, or None.

    The nearest ancestor holding .git is the work tree; a path that work tree ignores is not its
    content. When git cannot answer, the work tree is returned, so a doubt refuses the path.
    """
    path = path.resolve()
    for parent in path.parents:
        if (parent / ".git").exists():
            try:
                done = subprocess.run(
                    ["git", "-C", str(parent), "check-ignore", "-q", "--", str(path)],
                    capture_output=True, timeout=10,
                )
            except (OSError, subprocess.SubprocessError):
                return parent
            return None if done.returncode == 0 else parent
    return None


def checked_private_path(store: PrivateFile, path: Path) -> Path:
    """path itself; raises StoreError when a git work tree would hold it as content."""
    tree = tracking_work_tree(path)
    if tree is not None:
        raise StoreError(f"the {store.kind} file {path} lies inside the git work tree {tree}; {store.store_name} is personal and belongs to no repository: name a file outside every work tree with {store.option} or ${store.variable}")
    return path


# Storage


def read_records(path: Path) -> list[dict]:
    """Every record of a store in file order; a missing file holds none.

    Raises StoreError when the file cannot be read or a line is not a JSON object with a string id.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as e:
        raise StoreError(f"cannot read {path}: {e}") from e
    records = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except ValueError as e:
            raise StoreError(f"{path}:{number}: not a JSON record: {e}") from e
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise StoreError(f"{path}:{number}: a record is a JSON object with a string id")
        records.append(record)
    return records


def write_text_atomic(path: Path, text: str) -> None:
    """Replace path with text in one rename; on any failure the old file stays and no temporary file remains."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary)
        raise


def write_records(path: Path, records: list[dict]) -> None:
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    try:
        write_text_atomic(path, text)
    except OSError as e:
        raise StoreError(f"cannot write {path}: {e}") from e


def next_id(store: Store, records: list[dict]) -> str:
    """One past the highest number among the store's ids; ids never repeat while the file keeps its records."""
    pattern = re.compile(rf"{store.prefix}-(\d+)")
    numbers = [int(m.group(1)) for r in records if (m := pattern.fullmatch(r["id"]))]
    return f"{store.prefix}-{max(numbers, default=0) + 1:04d}"


def today() -> str:
    return datetime.date.today().isoformat()


# Matching


def units(text: str) -> list[str]:
    """The matching units of text: each run of digits whole, the trigrams of each other run of three or more characters."""
    found: list[str] = []
    for run in RUN.findall(text.lower()):
        if run.isdigit():
            found.append(run)
        elif len(run) >= TRIGRAM_RUN:
            found.extend(run[i:i + TRIGRAM_RUN] for i in range(len(run) - TRIGRAM_RUN + 1))
    return found


def sentences(text: str) -> list[Counter]:
    """The units of each sentence of text with at least MIN_SENTENCE_UNITS units; the whole text when none has."""
    kept = [c for c in (Counter(units(s)) for s in SENTENCE_BREAK.split(text)) if sum(c.values()) >= MIN_SENTENCE_UNITS]
    return kept or [Counter(units(text))]


def question(text: str) -> Counter | None:
    """The units of the last sentence of text; None when it has fewer than MIN_SENTENCE_UNITS units after other sentences.

    A text of one sentence is its own question, however few units it has.
    """
    parts = SENTENCE_BREAK.split(text.strip())
    last = Counter(units(parts[-1]))
    return last if len(parts) == 1 or sum(last.values()) >= MIN_SENTENCE_UNITS else None


def overlap(a: Counter, b: Counter) -> float:
    """The multiset intersection of a and b divided by the geometric mean of their unit counts; 0 when either is empty."""
    product = sum(a.values()) * sum(b.values())
    return sum((a & b).values()) / math.sqrt(product) if product else 0.0


def sentence_score(query: str, texts: list[str]) -> float:
    """The best overlap of a sentence of the query with a sentence of any of the texts."""
    query_sentences = sentences(query)
    return max((overlap(q, t) for text in texts for t in sentences(text) for q in query_sentences), default=0.0)


def question_score(query: str, texts: list[str]) -> float:
    """The best overlap of the query's question with a sentence of a text, or of a sentence of the query with a text's question.

    A side without a question to match by gives no pair of its own. When neither the query nor a
    text has one, the two whole texts are the one pair.
    """
    query_question = question(query)
    query_sentences = sentences(query)
    pairs: list[tuple[Counter, Counter]] = []
    for text in texts:
        text_question = question(text)
        if query_question is None and text_question is None:
            pairs.append((Counter(units(query)), Counter(units(text))))
        if query_question is not None:
            pairs.extend((query_question, t) for t in sentences(text))
        if text_question is not None:
            pairs.extend((q, text_question) for q in query_sentences)
    return max((overlap(a, b) for a, b in pairs), default=0.0)


def find(store: Store, query: str, records: list[dict], floor: float = DEFAULT_FLOOR) -> list[tuple[float, dict]]:
    """The live records whose score against the query reaches floor, best first, at most MAX_FOUND.

    Raises StoreError when the query holds no unit, since every score would then be zero.
    """
    if not units(query):
        raise StoreError(f"the query {query!r} holds no run of digits and no word of three or more letters")
    ranked = [(store.score(query, store.texts(r)), r) for r in records if store.is_live(r)]
    ranked = [(s, r) for s, r in ranked if s >= floor]
    ranked.sort(key=lambda pair: -pair[0])
    return ranked[:MAX_FOUND]


def found_line(store: Store, score: float, record: dict) -> str:
    return f"{record['id']} · {record.get('date', '')} · {score:.2f} · {store.head(record)} -> {store.body(record)} · basis: {one_line(record.get('basis', ''))}"


def show_line(store: Store, record: dict) -> str:
    fields = [record["id"], str(record.get("date", "")), *store.tags(record)]
    fields.append(f"{store.head(record)} -> {store.body(record)}")
    if "basis" in record:
        fields.append(f"basis: {one_line(record['basis'])}")
    return " · ".join(fields + store.extra(record))


# Commands


def nonblank(value: str, option: str) -> str:
    if not value or not value.strip():
        raise StoreError(f"{option} is empty")
    return value.strip()


def cmd_find(store: Store, path: Path, query: str, floor: float, as_json: bool) -> int:
    if not 0 <= floor <= 1:
        raise StoreError(f"--floor {floor} lies outside 0..1")
    hits = find(store, query, read_records(path), floor)
    if as_json:
        print(json.dumps([dict(r, score=round(s, 2)) for s, r in hits], ensure_ascii=False, indent=2))
    else:
        for s, r in hits:
            print(found_line(store, s, r))
    if store is READER:
        journal("reader_find", found=bool(hits))
    else:
        journal("ledger_find", found=len(hits))
    return 0 if hits else 1


def cmd_show(store: Store, path: Path) -> int:
    for record in reversed(read_records(path)):
        print(show_line(store, record))
    return 0


def append(store: Store, path: Path, fields: dict) -> str:
    records = read_records(path)
    record = {"id": next_id(store, records), "date": today(), **fields}
    write_records(path, records + [record])
    return record["id"]


def kept_items(values: list[str] | None) -> list[str]:
    """The items of a list option stripped, blank ones dropped."""
    return [v.strip() for v in values or [] if v.strip()]


def reader_add(path: Path, args: argparse.Namespace) -> int:
    fields = {"topic": nonblank(args.topic, "--topic")}
    for name in READER_LISTS:
        values = kept_items(getattr(args, name))
        if values:
            fields[name] = values
    for name in ("use", "depth", "turns"):
        if getattr(args, name):
            fields[name] = getattr(args, name)
    fields["basis"] = nonblank(args.basis, "--basis")
    print(append(READER, path, fields))
    counts = {"turns": args.turns} if args.turns else {}
    journal("reader_add", **{name: len(fields.get(name, [])) for name in READER_LISTS},
            use=args.use or "none", depth=args.depth or "none", **counts)
    return 0


def ledger_add(path: Path, args: argparse.Namespace) -> int:
    fields = {
        "kind": args.kind,
        "question": nonblank(args.question, "--question"),
        "answer": nonblank(args.answer, "--answer"),
        "basis": nonblank(args.basis, "--basis"),
    }
    for name in ("scope", "overturns"):
        if getattr(args, name):
            fields[name] = nonblank(getattr(args, name), f"--{name}")
    fields["status"] = "active"
    print(append(LEDGER, path, fields))
    journal("ledger_add", kind=args.kind)
    return 0


def index_of(records: list[dict], record_id: str, path: Path) -> int:
    for n, r in enumerate(records):
        if r["id"] == record_id:
            return n
    raise StoreError(f"{path}: no record {record_id}")


def ledger_note(path: Path, args: argparse.Namespace) -> int:
    changes = {name: nonblank(getattr(args, name), f"--{name}") for name in ("answer", "scope", "overturns", "basis") if getattr(args, name) is not None}
    if not changes:
        raise StoreError("note changes nothing: name at least one of --answer, --scope, --overturns, --basis")
    records = read_records(path)
    records[index_of(records, args.id, path)].update(changes)
    write_records(path, records)
    print(args.id)
    journal("ledger_note")
    return 0


def ledger_supersede(path: Path, args: argparse.Namespace) -> int:
    if args.id == args.by:
        raise StoreError(f"{args.id} cannot supersede itself")
    records = read_records(path)
    index_of(records, args.by, path)
    old = records[index_of(records, args.id, path)]
    old["status"] = "superseded"
    old["superseded_by"] = args.by
    write_records(path, records)
    print(f"{args.id} superseded by {args.by}")
    journal("ledger_supersede")
    return 0


def exchange_add(path: Path, args: argparse.Namespace) -> int:
    fields = {"topic": nonblank(args.topic, "--topic"), "form": args.form, "opening": args.opening}
    if args.reply:
        fields["reply"] = args.reply
    asked = kept_items(args.asked)
    if asked:
        fields["asked"] = asked
    if args.note is not None:
        fields["note"] = nonblank(args.note, "--note")
    print(append(EXCHANGE, path, fields))
    journal("exchange_add", form=args.form, opening=args.opening, reply=args.reply or "none")
    return 0


def exchange_note(path: Path, args: argparse.Namespace) -> int:
    asked = kept_items(args.asked)
    note = nonblank(args.note, "--note") if args.note is not None else None
    if args.reply is None and not asked and note is None:
        raise StoreError("note changes nothing: name at least one of --reply, --asked, --note")
    records = read_records(path)
    record = records[index_of(records, args.id, path)]
    if args.reply is not None:
        record["reply"] = args.reply
    if asked:
        record["asked"] = list(record.get("asked") or []) + asked
    if note is not None:
        record["note"] = note
    write_records(path, records)
    print(args.id)
    journal("exchange_note", reply=args.reply or "none", asked=len(asked))
    return 0


def every_count(counter: Counter, order: tuple[str, ...]) -> str:
    """'word count, ...' for every word of order, a zero count included."""
    return ", ".join(f"{word} {counter[word]}" for word in order)


def acted_share(replied: list[dict]) -> str:
    acted = sum(1 for r in replied if r.get("reply") == "acted")
    return f"first reply acted {acted} of {len(replied)}"


def exchange_count(path: Path) -> int:
    records = read_records(path)
    replied = [r for r in records if r.get("reply")]
    replies = Counter(r.get("reply") for r in replied)
    print(f"deliverables: {len(records)} ({every_count(Counter(r.get('form') for r in records), EXCHANGE_FORMS)})")
    print(f"opening: {every_count(Counter(r.get('opening') for r in records), EXCHANGE_OPENINGS)}")
    print(f"first reply: {every_count(replies, EXCHANGE_REPLIES)}, open {len(records) - len(replied)}")
    print(f"opening confirmed: {acted_share([r for r in replied if r.get('opening') in CONFIRMED_OPENINGS])}")
    print(f"opening not confirmed: {acted_share([r for r in replied if r.get('opening') == 'none'])}")
    return 0


# The PostToolUse hook


def captured_answer(question: str, response: object) -> str | None:
    """The reader's chosen text for question, or None when the response maps it to no non-empty answer.

    The answer is response["answers"][question]: a string stripped of white space, or a list of
    non-empty strings joined with ", ". An empty or white-space string, an empty list, a list with
    an empty item or a value of another type gives None, and so does a response that is no mapping
    or whose "answers" is no mapping.
    """
    answers = response.get("answers") if isinstance(response, Mapping) else None
    chosen = answers.get(question) if isinstance(answers, Mapping) else None
    if isinstance(chosen, str):
        return chosen.strip() or None
    if isinstance(chosen, list) and chosen:
        items = [x.strip() if isinstance(x, str) else "" for x in chosen]
        return ", ".join(items) if all(items) else None
    return None


def capture(stdin_text: str, path: Path) -> int:
    """Record every answered question of an AskUserQuestion call; a failure is one stderr line, never an exit code.

    A question without an answer gets no record and is named on stderr; a call that answers none
    leaves the ledger file as it was and prints nothing on stdout.
    """
    try:
        payload = json.loads(stdin_text)
        if not isinstance(payload, dict):
            raise ValueError("the payload is not a JSON object")
        tool_input = payload.get("tool_input") or {}
        questions = tool_input.get("questions") if isinstance(tool_input, dict) else None
        if not isinstance(questions, list):
            raise ValueError("the payload holds no tool_input.questions list")
    except ValueError as e:
        print(f"records.py capture: unreadable payload: {e}", file=sys.stderr)
        return 0
    response = payload.get("tool_response")
    texts = [q["question"].strip() for q in questions if isinstance(q, dict) and isinstance(q.get("question"), str) and q["question"].strip()]
    answered: list[tuple[str, str]] = []
    unanswered: list[str] = []
    for number, text in enumerate(texts, 1):
        answer = captured_answer(text, response)
        if answer is None:
            unanswered.append(str(number))
        else:
            answered.append((text, answer))
    if unanswered:
        noun = "question" if len(unanswered) == 1 else "questions"
        print(f"records.py capture: no answer in tool_response, so no record, for {noun} {', '.join(unanswered)} of {len(texts)}", file=sys.stderr)
    if not answered:
        return 0
    try:
        records = read_records(path)
        new = []
        for text, answer in answered:
            record = {"id": next_id(LEDGER, records), "date": today(), "kind": "answer", "question": text,
                      "answer": answer, "basis": CAPTURE_BASIS, "status": "active"}
            records.append(record)
            new.append(record["id"])
        write_records(path, records)
    except StoreError as e:
        print(f"records.py capture: {e}", file=sys.stderr)
        return 0
    script = Path(__file__).resolve()
    context = (
        f"The reader's answers on this card are recorded in the project ledger {path} as {', '.join(new)}. "
        "Each record lacks what its answer applies to and what would overturn it; add both for each id with: "
        f"python3 -I {script} ledger note <id> --ledger-file {path} --scope TEXT --overturns TEXT"
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}, ensure_ascii=False))
    journal("answer", count=len(new))
    return 0


# Command line


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    stores = top.add_subparsers(dest="store", required=True)

    reader_file = argparse.ArgumentParser(add_help=False)
    reader_file.add_argument("--reader-file", help="default: $HANDOVER_READER_FILE, else $XDG_DATA_HOME/handing-over-to-readers/reader.jsonl")
    ledger_file = argparse.ArgumentParser(add_help=False)
    ledger_file.add_argument("--ledger-file", help="default: <root>/.claude/handing-over-to-readers/ledger.jsonl")
    ledger_file.add_argument("--root", help="project root; default: $HANDOVER_LEDGER_FILE, $CLAUDE_PROJECT_DIR, the git work tree, the working directory")
    finding = argparse.ArgumentParser(add_help=False)
    finding.add_argument("--floor", type=float, default=DEFAULT_FLOOR, help=f"lowest score printed (default {DEFAULT_FLOOR})")
    finding.add_argument("--json", action="store_true", help="print the found records as a JSON list")

    reader = stores.add_parser("reader", help="what a reader holds about a topic").add_subparsers(dest="command", required=True)
    p = reader.add_parser("find", parents=[reader_file, finding])
    p.add_argument("--topic", required=True)
    p = reader.add_parser("add", parents=[reader_file])
    p.add_argument("--topic", required=True)
    p.add_argument("--basis", required=True)
    p.add_argument("--holds", nargs="+", action="extend")
    p.add_argument("--lacks", nargs="+", action="extend")
    p.add_argument("--words", nargs="+", action="extend", help="the reader's own word for a thing with what it names")
    p.add_argument("--barred", nargs="+", action="extend", help="a word the reader rejected or misread")
    p.add_argument("--use", choices=READER_USES)
    p.add_argument("--depth", choices=READER_DEPTHS)
    p.add_argument("--turns", type=int, choices=READER_TURNS, help="the number of intake cards that were asked")
    reader.add_parser("show", parents=[reader_file])

    ledger = stores.add_parser("ledger", help="the answers and decisions of one project").add_subparsers(dest="command", required=True)
    p = ledger.add_parser("find", parents=[ledger_file, finding])
    p.add_argument("--question", required=True)
    p = ledger.add_parser("add", parents=[ledger_file])
    p.add_argument("--kind", required=True, choices=LEDGER_KINDS)
    p.add_argument("--question", required=True)
    p.add_argument("--answer", required=True)
    p.add_argument("--basis", required=True)
    p.add_argument("--scope")
    p.add_argument("--overturns")
    p = ledger.add_parser("note", parents=[ledger_file])
    p.add_argument("id")
    for name in ("answer", "scope", "overturns", "basis"):
        p.add_argument(f"--{name}")
    p = ledger.add_parser("supersede", parents=[ledger_file])
    p.add_argument("id")
    p.add_argument("--by", required=True)
    ledger.add_parser("show", parents=[ledger_file])
    p = ledger.add_parser("capture", parents=[ledger_file], help="the PostToolUse hook on AskUserQuestion")
    p.add_argument("--hook", action="store_true", required=True, help="read the hook payload on stdin; always exit 0")

    exchange_file = argparse.ArgumentParser(add_help=False)
    exchange_file.add_argument("--exchange-file", help="default: $HANDOVER_EXCHANGE_FILE, else $XDG_DATA_HOME/handing-over-to-readers/exchanges.jsonl")
    exchange = stores.add_parser("exchange", help="the long deliverables handed to one reader").add_subparsers(dest="command", required=True)
    p = exchange.add_parser("add", parents=[exchange_file])
    p.add_argument("--topic", required=True)
    p.add_argument("--form", required=True, choices=EXCHANGE_FORMS)
    p.add_argument("--opening", required=True, choices=EXCHANGE_OPENINGS, help="how the opening was confirmed before the rest was built")
    p.add_argument("--reply", choices=EXCHANGE_REPLIES, help="the reader's first reply to the whole deliverable")
    p.add_argument("--asked", nargs="+", action="extend", help="a question the reader asked")
    p.add_argument("--note")
    p = exchange.add_parser("note", parents=[exchange_file])
    p.add_argument("id")
    p.add_argument("--reply", choices=EXCHANGE_REPLIES, help="the reader's first reply to the whole deliverable")
    p.add_argument("--asked", nargs="+", action="extend", help="a question the reader asked")
    p.add_argument("--note")
    exchange.add_parser("show", parents=[exchange_file])
    exchange.add_parser("count", parents=[exchange_file])
    return top


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    args = parser().parse_args(argv)
    environ = os.environ if environ is None else environ
    if args.store == "ledger" and args.command == "capture":
        try:
            path = ledger_path(args.ledger_file, args.root, environ)
            stdin_text = sys.stdin.read()
        except (OSError, ValueError) as e:
            print(f"records.py capture: {e}", file=sys.stderr)
            return 0
        return capture(stdin_text, path)
    try:
        if args.store == "reader":
            path = checked_private_path(READER_FILE, reader_path(args.reader_file, environ))
            if args.command == "find":
                return cmd_find(READER, path, args.topic, args.floor, args.json)
            if args.command == "add":
                return reader_add(path, args)
            return cmd_show(READER, path)
        if args.store == "exchange":
            path = checked_private_path(EXCHANGE_FILE, exchange_path(args.exchange_file, environ))
            if args.command == "add":
                return exchange_add(path, args)
            if args.command == "note":
                return exchange_note(path, args)
            if args.command == "count":
                return exchange_count(path)
            return cmd_show(EXCHANGE, path)
        path = ledger_path(args.ledger_file, args.root, environ)
        if args.command == "find":
            return cmd_find(LEDGER, path, args.question, args.floor, args.json)
        if args.command == "add":
            return ledger_add(path, args)
        if args.command == "note":
            return ledger_note(path, args)
        if args.command == "supersede":
            return ledger_supersede(path, args)
        return cmd_show(LEDGER, path)
    except StoreError as e:
        print(f"records.py: {e}", file=sys.stderr)
        return 2


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
