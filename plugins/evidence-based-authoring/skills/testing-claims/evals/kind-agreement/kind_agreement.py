#!/usr/bin/env python3
"""Draw the sample, build the readers' brief and score the two readers of the kind-agreement test.

    kind_agreement.py sample --root DIR --seed SEED --out FILE
    kind_agreement.py brief  --root DIR --sample FILE --method FILE --protocol FILE --out FILE [--wrap N]
    kind_agreement.py score  --sample FILE --a FILE --b FILE [--threshold N]

protocol.md beside this script states the test; this script serves its sections Sample, What a
reader gets and Measure.

sample  Over the four corpora of CORPORA, in that order: the candidates of a corpus are the ids of
        the rule lines of its provenance map (`- **<id>**`) that have exactly one card file
        `<lower-cased id>--*.md` in its cards directory. They are ordered by the hexadecimal
        SHA-256 of the UTF-8 string `<seed>:<id>` and the first N are taken; fewer than N is an
        error. FILE gets {"seed": SEED, "rules": [{"id", "corpus", "card", "provenance",
        "line"}]}, paths relative to the root, line the 1-based line of the rule line in the map.
        Prints `<n> rules drawn`.
brief   FILE gets a Markdown brief: the method's section "## Kinds of statement" and the
        protocol's "## Reading rule", each copied from its heading up to the next `## ` line; a
        section "## Answer" with the fenced block of the protocol's "## Readers"; and under
        "## Rules", per rule of the sample, its id, its card's frontmatter title, its card's
        Thesis and its provenance line inside a `~~~~` fence, cut before its record (the segment
        `kind: …` and everything after it), so no reader is handed a kind. With --wrap N every line longer
        than N characters is broken at its last space at or before N, so that a file reader
        shows the brief whole; the text is otherwise unchanged. Prints `<n> rules, <bytes> bytes
        written`.
score   Reads two reader files {"answers": [{"id", "kind", "why"}]}; each must answer every id of
        the sample once with one of KINDS, and nothing else. Prints one `<id>: a=<kind> b=<kind>`
        line per disagreement in sample order, the 4x4 table of counts (rows reader a, columns
        reader b), `agreed: <k> of <n>`, `kappa: <Cohen's kappa, two decimals>`, `threshold: <N>`
        and `holds` when k >= N, else `refuted`.

Exit: sample and brief 0 on success; score 0 on holds, 1 on refuted; every subcommand 2 on wrong
usage or invalid input (an unreadable or malformed file, a missing section, card or line, too few
candidates, an answer set that does not match the sample), with the message on stderr.

Privileges: reads files under the given paths as UTF-8; writes only the --out file and the
standard streams; opens no network connection; uses the standard library alone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# (corpus, cards directory, provenance map, number to draw), paths relative to the root.
CORPORA = (
    ("audit", "plugins/evidence-based-authoring/skills/auditing-ai-context/references/rule-cards",
     "plugins/evidence-based-authoring/skills/auditing-ai-context/maintenance/rule-cards-provenance.md", 10),
    ("craft", "plugins/code-quality/skills/software-craft/references/craft-cards",
     "plugins/code-quality/skills/software-craft/maintenance/craft-cards-provenance.md", 10),
    ("craft-python", "plugins/code-quality/skills/software-craft/references/craft-cards-python",
     "plugins/code-quality/skills/software-craft/maintenance/craft-cards-python-provenance.md", 5),
    ("craft-java", "plugins/code-quality/skills/software-craft/references/craft-cards-java",
     "plugins/code-quality/skills/software-craft/maintenance/craft-cards-java-provenance.md", 5),
)
RULE_LINE = re.compile(r"^- \*\*(?P<id>[^*]+)\*\*")
KINDS = ("decision", "definition", "norm", "claim")
DEFAULT_THRESHOLD = 24
ANSWER_SENTENCE = "Answer for every rule below, in the order given, with one of the four kinds."
FENCE = re.compile(r"^(`{3,}|~{3,})")


class InputError(Exception):
    """Invalid input: the subcommand stops with exit 2 and the message on stderr."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise InputError(f"cannot read {path}: {e}") from e


def read_json(path: Path):
    text = read_text(path)
    try:
        return json.loads(text)
    except ValueError as e:
        raise InputError(f"{path} is not JSON: {e}") from e


def write_text(path: Path, text: str) -> int:
    data = text.encode("utf-8")
    try:
        path.write_bytes(data)
    except OSError as e:
        raise InputError(f"cannot write {path}: {e}") from e
    return len(data)


# --- sample -----------------------------------------------------------------------------------

def rule_lines(map_path: Path) -> list[tuple[str, int]]:
    """(id, 1-based line number) of every rule line of a provenance map, in map order."""
    found: list[tuple[str, int]] = []
    seen: set[str] = set()
    for number, line in enumerate(read_text(map_path).splitlines(), 1):
        match = RULE_LINE.match(line)
        if not match:
            continue
        rule_id = match.group("id")
        if rule_id in seen:
            raise InputError(f"{map_path}:{number}: id {rule_id} has a second rule line")
        seen.add(rule_id)
        found.append((rule_id, number))
    return found


def card_files(cards_dir: Path, rule_id: str) -> list[Path]:
    prefix = f"{rule_id.lower()}--"
    return sorted(p for p in cards_dir.glob("*.md") if p.name.startswith(prefix))


def draw_key(seed: str, rule_id: str) -> str:
    return hashlib.sha256(f"{seed}:{rule_id}".encode("utf-8")).hexdigest()


def draw(root: Path, seed: str, corpora=CORPORA) -> list[dict]:
    """The sample's rules: per corpus in order, the first N candidates by draw_key."""
    rules: list[dict] = []
    for corpus, cards_rel, map_rel, count in corpora:
        cards_dir = root / cards_rel
        if not cards_dir.is_dir():
            raise InputError(f"no cards directory {cards_dir}")
        candidates = []
        for rule_id, line in rule_lines(root / map_rel):
            cards = card_files(cards_dir, rule_id)
            if len(cards) == 1:
                candidates.append((draw_key(seed, rule_id), rule_id, cards[0], line))
        if len(candidates) < count:
            raise InputError(f"corpus {corpus}: {len(candidates)} candidates, {count} to draw")
        for _, rule_id, card, line in sorted(candidates)[:count]:
            rules.append({"id": rule_id, "corpus": corpus, "card": card.relative_to(root).as_posix(),
                          "provenance": Path(map_rel).as_posix(), "line": line})
    return rules


def cmd_sample(args) -> int:
    rules = draw(Path(args.root), args.seed)
    write_text(Path(args.out), json.dumps({"seed": args.seed, "rules": rules}, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(rules)} rules drawn")
    return 0


# --- brief ------------------------------------------------------------------------------------

def section_lines(lines: list[str], heading: str, source) -> list[str]:
    """The lines from the heading line up to, not including, the next line that starts with `## `."""
    for start, line in enumerate(lines):
        if line.rstrip() == heading:
            break
    else:
        raise InputError(f"{source}: no section {heading!r}")
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return lines[start:end]


def strip_blank(lines: list[str]) -> list[str]:
    start, end = 0, len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def fenced_block(lines: list[str], source) -> list[str]:
    """The first fenced block of the lines, its fence lines included."""
    for start, line in enumerate(lines):
        opening = FENCE.match(line)
        if opening:
            fence = opening.group(1)
            for end in range(start + 1, len(lines)):
                closing = lines[end].rstrip()
                if closing.startswith(fence) and set(closing) == {fence[0]}:
                    return lines[start:end + 1]
            raise InputError(f"{source}: the fenced block is not closed")
    raise InputError(f"{source}: no fenced block")


def frontmatter_title(lines: list[str], source) -> str:
    if not lines or lines[0].rstrip() != "---":
        raise InputError(f"{source}: no frontmatter")
    for line in lines[1:]:
        if line.rstrip() == "---":
            break
        if line.startswith("title:"):
            title = line[len("title:"):].strip()
            if title:
                return title
            break
    raise InputError(f"{source}: no frontmatter title")


def card_parts(path: Path) -> tuple[str, str]:
    """(title, Thesis text) of one card; the Thesis without the heading and surrounding blank lines."""
    lines = read_text(path).splitlines()
    title = frontmatter_title(lines, path)
    thesis = strip_blank(section_lines(lines, "## Thesis", path)[1:])
    if not thesis:
        raise InputError(f"{path}: the Thesis is empty")
    return title, "\n".join(thesis)


def provenance_line(path: Path, number, rule_id: str) -> str:
    lines = read_text(path).splitlines()
    if not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= len(lines):
        raise InputError(f"{path}: no line {number!r} for {rule_id}")
    line = lines[number - 1]
    match = RULE_LINE.match(line)
    if not match or match.group("id") != rule_id:
        raise InputError(f"{path}:{number}: not the rule line of {rule_id}")
    return line


def sample_rules(sample_path: Path) -> list[dict]:
    payload = read_json(sample_path)
    rules = payload.get("rules") if isinstance(payload, dict) else None
    if not isinstance(rules, list) or not rules:
        raise InputError(f"{sample_path}: no rules list")
    ids = []
    for n, rule in enumerate(rules, 1):
        if not isinstance(rule, dict) or not isinstance(rule.get("id"), str):
            raise InputError(f"{sample_path}: rule {n} has no id")
        ids.append(rule["id"])
    if len(set(ids)) != len(ids):
        raise InputError(f"{sample_path}: an id is drawn twice")
    return rules


def build_brief(root: Path, rules: list[dict], method_text: str, protocol_text: str,
                method_name="method", protocol_name="protocol") -> str:
    method = method_text.splitlines()
    protocol = protocol_text.splitlines()
    parts = [
        ["# Kind agreement — brief"],
        strip_blank(section_lines(method, "## Kinds of statement", method_name)),
        strip_blank(section_lines(protocol, "## Reading rule", protocol_name)),
        ["## Answer", "", *fenced_block(section_lines(protocol, "## Readers", protocol_name), protocol_name),
         "", ANSWER_SENTENCE],
        ["## Rules"],
    ]
    for rule in rules:
        rule_id = rule["id"]
        for key in ("card", "provenance"):
            if not isinstance(rule.get(key), str):
                raise InputError(f"rule {rule_id}: no {key} path")
        title, thesis = card_parts(root / rule["card"])
        line = without_record(provenance_line(root / rule["provenance"], rule.get("line"), rule_id))
        parts.append([f"### {rule_id}", "", f"Title: {title}", "", thesis, "", "~~~~", line, "~~~~"])
    return "\n\n".join("\n".join(part) for part in parts) + "\n"


def without_record(line: str) -> str:
    """The rule line cut before the segment that opens its record, `kind: …`."""
    segments = line.split(" · ")
    start = next((i for i, segment in enumerate(segments) if segment.startswith("kind:")), None)
    return line if start is None else " · ".join(segments[:start])


def wrap_lines(text: str, width: int) -> str:
    """The text with every line longer than width broken at its last space at or before width."""
    out = []
    for line in text.split("\n"):
        while len(line) > width:
            cut = line.rfind(" ", 0, width + 1)
            if cut <= 0:
                break
            out.append(line[:cut])
            line = line[cut + 1:]
        out.append(line)
    return "\n".join(out)


def cmd_brief(args) -> int:
    rules = sample_rules(Path(args.sample))
    text = build_brief(Path(args.root), rules, read_text(Path(args.method)), read_text(Path(args.protocol)),
                       args.method, args.protocol)
    if args.wrap is not None:
        if args.wrap < 1:
            raise InputError("--wrap takes a positive number of characters")
        text = wrap_lines(text, args.wrap)
    size = write_text(Path(args.out), text)
    print(f"{len(rules)} rules, {size} bytes written")
    return 0


# --- score ------------------------------------------------------------------------------------

def reader_kinds(path: Path, ids: list[str]) -> dict[str, str]:
    """id -> kind of one reader file; every error of the file raised together."""
    payload = read_json(path)
    answers = payload.get("answers") if isinstance(payload, dict) else None
    if not isinstance(answers, list):
        raise InputError(f"{path}: no answers list")
    errors: list[str] = []
    kinds: dict[str, str] = {}
    known = set(ids)
    for n, answer in enumerate(answers, 1):
        if not isinstance(answer, dict):
            errors.append(f"answer {n} is not an object")
            continue
        rule_id, kind = answer.get("id"), answer.get("kind")
        if not isinstance(rule_id, str) or rule_id not in known:
            errors.append(f"answer {n}: id {rule_id!r} is outside the sample")
            continue
        if rule_id in kinds:
            errors.append(f"id {rule_id} is answered twice")
            continue
        if kind not in KINDS:
            errors.append(f"id {rule_id}: kind {kind!r} is outside {', '.join(KINDS)}")
        kinds[rule_id] = kind
    errors += [f"id {rule_id} has no answer" for rule_id in ids if rule_id not in kinds]
    if errors:
        raise InputError("\n".join(f"{path}: {e}" for e in errors))
    return kinds


def kappa(table: list[list[int]]) -> float:
    """Cohen's kappa of a square table of counts, rows one reader and columns the other; 1.0 when pe is 1."""
    n = sum(map(sum, table))
    po = sum(table[i][i] for i in range(len(table))) / n
    pe = sum(sum(table[i]) / n * sum(row[i] for row in table) / n for i in range(len(table)))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def score_lines(ids: list[str], a: dict[str, str], b: dict[str, str], threshold: int) -> tuple[list[str], bool]:
    out = [f"{rule_id}: a={a[rule_id]} b={b[rule_id]}" for rule_id in ids if a[rule_id] != b[rule_id]]
    table = [[sum(1 for i in ids if a[i] == ra and b[i] == cb) for cb in KINDS] for ra in KINDS]
    width = max(map(len, KINDS)) + 2
    out.append("a \\ b".ljust(width) + "".join(k.rjust(width) for k in KINDS))
    out += [ra.ljust(width) + "".join(str(c).rjust(width) for c in row) for ra, row in zip(KINDS, table)]
    agreed = sum(table[i][i] for i in range(len(KINDS)))
    holds = agreed >= threshold
    out += [f"agreed: {agreed} of {len(ids)}", f"kappa: {kappa(table):.2f}", f"threshold: {threshold}",
            "holds" if holds else "refuted"]
    return out, holds


def cmd_score(args) -> int:
    ids = [rule["id"] for rule in sample_rules(Path(args.sample))]
    errors, kinds = [], []
    for name in (args.a, args.b):
        try:
            kinds.append(reader_kinds(Path(name), ids))
        except InputError as e:
            errors.append(str(e))
    if errors:
        raise InputError("\n".join(errors))
    lines, holds = score_lines(ids, kinds[0], kinds[1], args.threshold)
    print("\n".join(lines))
    return 0 if holds else 1


# --- command line -----------------------------------------------------------------------------

def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = top.add_subparsers(dest="command", required=True)
    sample = sub.add_parser("sample", help="draw the sample")
    sample.add_argument("--root", required=True)
    sample.add_argument("--seed", required=True)
    sample.add_argument("--out", required=True)
    sample.set_defaults(run=cmd_sample)
    brief = sub.add_parser("brief", help="build the readers' brief")
    for name in ("--root", "--sample", "--method", "--protocol", "--out"):
        brief.add_argument(name, required=True)
    brief.add_argument("--wrap", type=int, default=None)
    brief.set_defaults(run=cmd_brief)
    score = sub.add_parser("score", help="score the two readers")
    for name in ("--sample", "--a", "--b"):
        score.add_argument(name, required=True)
    score.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    score.set_defaults(run=cmd_score)
    return top


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except InputError as e:
        print(e, file=sys.stderr)
        return 2


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
