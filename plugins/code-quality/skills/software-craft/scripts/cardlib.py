"""Shared parsing for the craft-card corpus: frontmatter, the facet lists, the trigger list, the
body blocks and the provenance map.

Every script that reads a card or a provenance map imports it, so each reads a card the same
way and finds a map at the one address provenance_map_path computes. A card
belongs to the universal corpus, whose id prefix names its domain, or to a language corpus,
whose id prefix names its language and whose cards take any domain of CORPUS_DOMAINS.
Standard library only.
"""
import os
import re

KEYS = ["title", "rule_id", "domain", "step", "applies_to", "triggers", "scope", "check_kind", "severity_default"]
PREFIX_DOMAIN = {"CODE": "code", "DSN": "design", "API": "interface", "ERR": "errors", "TST": "tests",
                 "CHG": "change", "PRF": "performance", "TOOL": "tooling", "DOC": "docs", "INP": "input",
                 "ARCH": "architecture", "META": "meta"}
# Every domain a card may take: the universal prefixes' domains, and two that only a language card takes.
CORPUS_DOMAINS = (*PREFIX_DOMAIN.values(), "concurrency", "security")
# A language corpus prefix maps to the language its cards apply to; its cards take any domain of CORPUS_DOMAINS.
LANGUAGE_PREFIXES = {"PY": "python", "JAVA": "java"}
STEPS = ("design", "implement", "handle-errors", "test", "refactor", "document", "review")
APPLIES_TO = ("universal", "object-oriented", "functional", "public-api", "service-boundary", "library",
              "exceptions", "result-types", "garbage-collected", "manual-memory", "static-types", "dynamic-types",
              "tests", "build-config", "prose", "python", "java")
SCOPES = ("hunk", "file", "base-compare", "callers")
CHECK_KINDS = ("mechanical", "semantic")
SEVERITIES = ("critical", "major", "minor", "suggestion")
# The structural signals the pre-pass computes; a trigger `signal:<name>` names one of them.
SIGNALS = ("long_routine", "deep_nesting", "many_parameters", "boolean_argument", "empty_handler", "magic_number",
           "commented_out_code", "todo_marker", "duplicate_block", "test_file", "added_file")
EXAMPLE_LANGS = ("java", "python", "typescript", "go", "rust")
FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.S)
SIGNAL_PREFIX = "signal:"

# The body of a card: these H2 blocks in this order and no other H2. A card carries no citation; its
# sources live on its provenance line, found by rule_id in its corpus's provenance map (provenance_map_path).
BLOCKS = ["Thesis", "Rationale", "Example", "Limits", "Validator", "Finding output"]
SOURCE_BLOCK_ERROR = ("a `## Source` block is present; a card carries no citation — its sources live on its "
                      "provenance line, keyed by rule_id")
PROVENANCE_SUFFIX = "-provenance.md"
MAINTAINER_DIR = "maintenance"
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
    """The provenance map of a cards directory `<skill>/references/<name>`: `<name>-provenance.md` in the
    skill's MAINTAINER_DIR, the skill being two directories above the cards directory. The one place
    that knows the address."""
    cards_dir = os.path.normpath(cards_dir)
    skill = os.path.dirname(os.path.dirname(cards_dir))
    return os.path.join(skill, MAINTAINER_DIR, os.path.basename(cards_dir) + PROVENANCE_SUFFIX)


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


def parse_inline_list(raw, bare_ok=False):
    """Parse a YAML inline list. Items are quoted strings; with bare_ok, unquoted
    tokens of [A-Za-z0-9_-] are accepted too (the step and applies_to facets).
    Returns (items, error)."""
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return None, "value must be an inline list [...]"
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
        if q in ("'", '"'):
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
                return None, "unterminated quoted item"
            items.append("".join(buf))
            i += 1
        elif bare_ok:
            m = re.match(r"[A-Za-z0-9_-]+", body[i:])
            if not m:
                return None, f"item at offset {i} is neither quoted nor a bare token"
            items.append(m.group(0))
            i += len(m.group(0))
        else:
            return None, f"item at offset {i} is not quoted"
        while i < n and body[i] in " \t":
            i += 1
        if i < n:
            if body[i] != ",":
                return None, f"expected ',' after an item at offset {i}"
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


def is_signal(trigger):
    return trigger.startswith(SIGNAL_PREFIX)


def signal_name(trigger):
    return trigger[len(SIGNAL_PREFIX):]


def check_triggers(triggers):
    """Return an error string for the first bad trigger, else None."""
    for t in triggers:
        if is_signal(t):
            if signal_name(t) not in SIGNALS:
                return f"trigger {t!r} names no known signal (known: {', '.join(SIGNALS)})"
            continue
        try:
            re.compile(t)
        except re.error as e:
            return f"trigger {t!r} does not compile: {e}"
    return None


def prefix_domain_ok(rule_id, domain):
    """Whether the rule_id's prefix admits the domain: a universal prefix admits its own
    domain, a language prefix admits every domain of CORPUS_DOMAINS, PROJ admits any."""
    prefix = rule_id.split("-")[0]
    if prefix == "PROJ":
        return True
    if prefix in LANGUAGE_PREFIXES:
        return domain in CORPUS_DOMAINS
    return PREFIX_DOMAIN.get(prefix) == domain


def language_of_card(rec):
    """The language value the card's applies_to carries, or None for a card of no language corpus."""
    languages = set(LANGUAGE_PREFIXES.values())
    return next((a for a in rec["applies_to"] if a in languages), None)


def read_card(path):
    """Read one card file into its index record. Returns (record, error).

    The record is what plan.json and the developer's index carry per card: rule_id,
    path, title, domain, step, applies_to, triggers, scope, check_kind, severity_default,
    and corpus, the name of the directory the card sits in.
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
        return None, f"triggers: {terr}"
    terr = check_triggers(triggers)
    if terr:
        return None, terr
    step, serr = parse_inline_list(data["step"], bare_ok=True)
    if serr:
        return None, f"step: {serr}"
    applies, aerr = parse_inline_list(data["applies_to"], bare_ok=True)
    if aerr:
        return None, f"applies_to: {aerr}"
    rec = {
        "rule_id": data["rule_id"].strip(),
        "path": path,
        "title": strip_quotes(data["title"]),
        "domain": data["domain"].strip(),
        "step": step,
        "applies_to": applies,
        "triggers": triggers,
        "scope": data["scope"].strip(),
        "check_kind": data["check_kind"].strip(),
        "severity_default": data["severity_default"].strip(),
        "corpus": os.path.basename(os.path.dirname(os.path.abspath(path))),
    }
    if not prefix_domain_ok(rec["rule_id"], rec["domain"]):
        return None, f"rule_id {rec['rule_id']} does not match domain {rec['domain']!r}"
    if rec["scope"] not in SCOPES or rec["check_kind"] not in CHECK_KINDS or rec["severity_default"] not in SEVERITIES:
        return None, f"facet outside the controlled vocabulary in {path}"
    if any(s not in STEPS for s in rec["step"]) or not rec["step"]:
        return None, f"step {rec['step']} outside {STEPS} in {path}"
    if any(a not in APPLIES_TO for a in rec["applies_to"]) or not rec["applies_to"]:
        return None, f"applies_to {rec['applies_to']} outside {APPLIES_TO} in {path}"
    return rec, None
