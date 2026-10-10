"""Shared parsing for the review-card corpus: frontmatter, the trigger list, the body blocks
and the provenance map.

Imported by static-review.py (the pre-pass) and validate-review-cards.py (the
validator) so the two read a card the same way; the report renderer reads the
provenance map through it. Standard library only.
"""
import os
import re

KEYS = ["title", "rule_id", "domain", "triggers", "scope", "check_kind", "severity_default"]
PREFIX_DOMAIN = {"CC": "concurrency", "SEC": "security", "PF": "performance",
                 "REL": "reliability", "MNT": "maintainability", "META": "meta"}
SCOPES = ("hunk", "file", "base-compare", "callers")
CHECK_KINDS = ("mechanical", "semantic")
SEVERITIES = ("critical", "major", "minor", "suggestion")
FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.S)

# The body of a card: these H2 blocks in this order and no other H2. A card carries no citation; its
# sources live on its provenance line, found by rule_id in the provenance map beside its cards directory.
BLOCKS = ["Thesis", "Rationale", "Example", "Limits", "Validator", "Finding output"]
SOURCE_BLOCK_ERROR = ("a `## Source` block is present; a card carries no citation — its sources live on its "
                      "provenance line, keyed by rule_id")
PROVENANCE_SUFFIX = "-provenance.md"
PROVENANCE_LINE = re.compile(r"^- \*\*([A-Z]+-\d+)\*\* · ")
# A quoted span: straight or curly double quotes, or straight single quotes around 26 characters or more
# that open and close outside a word, so an apostrophe never delimits one.
QUOTED_SPANS = (re.compile(r'"([^"\n]+)"'), re.compile(r"“([^”\n]+)”"), re.compile(r"(?<!\w)'([^\n]{26,}?)'(?!\w)"))
# A quoted statement opens right after a dash or a colon (`fetched — "…"`, `(fetched): "…"`); a quoted
# span anywhere else is part of the locator, a document or section title.
STATEMENT_OPENER = re.compile(r"[—–:]\s*$")
FIELD_SEPARATOR = re.compile(r" · ")
# Citations are separated by `; ` outside parentheses, except after an author's initial (`Soto, J.; McCall, J.`).
CITATION_SEPARATOR = re.compile(r"(?<![A-Z]\.);\s+")
FETCH_STATUS_WORD = re.compile(r"\b(?:fetched|relayed|unfetched)\b", re.I)
LOCATOR_WORD = re.compile(r"[A-Za-z0-9]{2,}")
STATUS_AFTER_DASH = re.compile(r"\s[—–]\s*\**(?:fetched|relayed|unfetched)\b", re.I)
POINTER_TAIL = re.compile(r"(?:[\s,;:—–(]|\**\b(?:fetched|relayed|unfetched)\b\**\)?(?:\s+from\b)?)+$", re.I)
POINTER_CHARS = 160


def block_problems(heads):
    """Return the errors of a card's H2 headings against BLOCKS: a `## Source` block, any other H2
    outside BLOCKS, and the blocks missing or out of order."""
    problems = []
    if "Source" in heads:
        problems.append(SOURCE_BLOCK_ERROR)
    extra = [h for h in heads if h not in BLOCKS and h != "Source"]
    if extra:
        problems.append(f"H2 {extra} outside the body blocks {BLOCKS}")
    known = [h for h in heads if h in BLOCKS]
    if known != BLOCKS:
        problems.append(f"body blocks {known} must be exactly {BLOCKS} in that order")
    return problems


def quoted_spans(text, patterns=QUOTED_SPANS):
    """Return [(fragment, start, end)] of the quoted spans in text order; a span that starts inside an
    earlier one is dropped."""
    found = sorted(((m.group(1), m.start(), m.end()) for p in patterns for m in p.finditer(text)), key=lambda s: s[1])
    spans, reach = [], 0
    for span in found:
        if span[1] >= reach:
            spans.append(span)
            reach = span[2]
    return spans


def split_outside(text, separator, spans):
    """Split text at each match of the compiled `separator` that lies outside every span."""
    parts, start = [], 0
    for m in separator.finditer(text):
        if m.start() >= start and not any(s <= m.start() < e for _f, s, e in spans):
            parts.append(text[start:m.start()])
            start = m.end()
    return parts + [text[start:]]


def provenance_map_path(cards_dir):
    """The provenance map beside a cards directory: references/review-cards → references/review-cards-provenance.md."""
    return os.path.normpath(cards_dir) + PROVENANCE_SUFFIX


def read_provenance(map_path):
    """Return {rule_id: provenance line} of a provenance map; {} when the file is absent."""
    if not os.path.isfile(map_path):
        return {}
    lines = {}
    with open(map_path, encoding="utf-8") as handle:
        for line in handle:
            m = PROVENANCE_LINE.match(line)
            if m:
                lines.setdefault(m.group(1), line.rstrip("\n"))
    return lines


def blank_quotes(text, patterns=QUOTED_SPANS):
    """The text with its quoted spans blanked, so a quoted word never reads as a locator."""
    chars = list(text)
    for _fragment, start, end in quoted_spans(text, patterns):
        chars[start:end] = " " * (end - start)
    return "".join(chars)


def split_citations(field, patterns=QUOTED_SPANS):
    """Split a citation field at each CITATION_SEPARATOR outside quoted spans and parentheses; a piece
    that holds only quotes and fetch statuses continues the citation before it."""
    ends = {start: end for _fragment, start, end in quoted_spans(field, patterns)}
    pieces, start, depth, i = [], 0, 0, 0
    while i < len(field):
        if i in ends:
            i = ends[i]
            continue
        sep = CITATION_SEPARATOR.match(field, i) if depth == 0 else None
        if sep:
            pieces.append(field[start:i])
            start = i = sep.end()
            continue
        depth = max(depth + {"(": 1, ")": -1}.get(field[i], 0), 0)
        i += 1
    pieces.append(field[start:])
    citations = []
    for piece in (p.strip() for p in pieces):
        if piece and citations and not LOCATOR_WORD.search(FETCH_STATUS_WORD.sub("", blank_quotes(piece, patterns))):
            citations[-1] += "; " + piece
        elif piece:
            citations.append(piece)
    return citations


def provenance_citations(line, patterns=QUOTED_SPANS):
    """The citations of a provenance line: its first field after `- **<rule_id>** · `, split by
    split_citations."""
    m = PROVENANCE_LINE.match(line)
    rest = line[m.end():] if m else line
    return split_citations(split_outside(rest, FIELD_SEPARATOR, quoted_spans(rest, patterns))[0], patterns)


def citation_locator(citation, limit=POINTER_CHARS):
    """A citation cut before its first quoted statement and before a fetch status set off by a dash, its
    trailing fetch status and separators stripped, and cut at `limit` characters with an ellipsis,
    closing a code span the cut opened."""
    for _fragment, start, _end in quoted_spans(citation):
        if STATEMENT_OPENER.search(citation[:start].replace("**", "")):
            citation = citation[:start]
            break
    status = STATUS_AFTER_DASH.search(blank_quotes(citation))
    citation = POINTER_TAIL.sub("", citation[:status.start()] if status else citation).strip()
    if len(citation) <= limit:
        return citation
    cut = citation[:limit - 1].rstrip() + "…"
    return cut + "`" if cut.count("`") % 2 else cut


def source_pointer(line, limit=POINTER_CHARS):
    """The one-line source pointer of a provenance line: its first citation's locator."""
    citations = provenance_citations(line)
    return citation_locator(citations[0], limit) if citations else ""



def parse_inline_list(raw):
    """Parse a YAML inline list of quoted strings. Returns (items, error)."""
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return None, "triggers must be an inline list [...]"
    body = raw[1:-1].strip()
    if body == "":
        return [], None
    items, i, n = [], 0, len(body)
    while i < n:
        while i < n and body[i] in " \t":
            i += 1
        if i >= n:
            break
        q = body[i]
        if q not in ("'", '"'):
            return None, f"trigger at offset {i} is not quoted"
        i += 1
        buf = []
        while i < n:
            c = body[i]
            if q == "'" and c == "'" and i + 1 < n and body[i + 1] == "'":
                buf.append("'")
                i += 2
                continue
            if q == '"' and c == "\\" and i + 1 < n and body[i + 1] in ('"', "\\"):
                buf.append(body[i + 1])
                i += 2
                continue
            if c == q:
                break
            buf.append(c)
            i += 1
        else:
            return None, "unterminated quoted trigger"
        items.append("".join(buf))
        i += 1
        while i < n and body[i] in " \t":
            i += 1
        if i < n:
            if body[i] != ",":
                return None, f"expected ',' after a trigger at offset {i}"
            i += 1
    return items, None


def strip_quotes(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def parse_frontmatter(text):
    """Return (ordered keys, dict of raw values, error) for the leading YAML block."""
    m = FRONTMATTER.match(text)
    if not m:
        return None, None, "missing frontmatter"
    keys, data = [], {}
    for line in m.group(1).split("\n"):
        km = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not km:
            return None, None, f"unparseable frontmatter line: {line!r}"
        keys.append(km.group(1))
        data[km.group(1)] = km.group(2)
    return keys, data, None


def read_card(path):
    """Read one card file into its index record. Returns (record, error).

    The record is what plan.json carries per card: rule_id, path, domain,
    triggers (list of patterns), scope, check_kind, severity_default, title.
    """
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    keys, data, err = parse_frontmatter(text)
    if err:
        return None, err
    missing = [k for k in KEYS if k not in data]
    if missing:
        return None, f"frontmatter lacks {missing}"
    triggers, terr = parse_inline_list(data["triggers"])
    if terr:
        return None, terr
    for t in triggers:
        try:
            re.compile(t)
        except re.error as e:
            return None, f"trigger {t!r} does not compile: {e}"
    rec = {
        "rule_id": data["rule_id"].strip(),
        "path": path,
        "title": strip_quotes(data["title"]),
        "domain": data["domain"].strip(),
        "triggers": triggers,
        "scope": data["scope"].strip(),
        "check_kind": data["check_kind"].strip(),
        "severity_default": data["severity_default"].strip(),
    }
    prefix = rec["rule_id"].split("-")[0]
    if PREFIX_DOMAIN.get(prefix) != rec["domain"] and prefix != "PROJ":
        return None, f"rule_id {rec['rule_id']} does not match domain {rec['domain']!r}"
    if rec["scope"] not in SCOPES or rec["check_kind"] not in CHECK_KINDS or rec["severity_default"] not in SEVERITIES:
        return None, f"facet outside the controlled vocabulary in {path}"
    return rec, None
