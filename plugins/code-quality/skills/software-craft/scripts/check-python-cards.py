#!/usr/bin/env python3
"""Check drafted Python craft cards against the harvested catalogs and the network.
Authoring time only; never part of a build or a review.

Usage:  python3 check-python-cards.py --state <dir> --harvest <harvest_dir> [--keys k1,k2]
                                      [--universal <universal.json>] [--skill <skill dir>]
                                      [--no-network] [--json]

Reads <dir>/<key>.json for each key, or every *.json in <dir> when --keys is absent: a draft
object {key, status, filename, card_markdown, provenance_line, pending_entry, checks, notes} as
scripts/python-topic-workflow.js defines it. A file holding a top-level "spine" key is not a
draft and is passed over; a draft whose status is "pending" is skipped with a note. A key with
no <key>.json but a <key>.md is read from the markdown alone, its filename built from the rule_id
and the title, and its provenance line goes unchecked with a note.

Checks per card:
  validator   scripts/validate-craft-cards.py --language python, run once on a temporary
              directory holding every card under its filename; an error line goes to the card it
              names, a line naming no card to every card; a numbering-gap warning is no failure.
  example     the Example's one fenced block splits into the bad: and good: groups; the good
              group, labels stripped and dedented, with each `...` or `{ ... }` elision given the
              body `pass`, parses with ast.parse.
  triggers    every regex trigger compiles and at least one matches a line of the bad group; a
              card whose triggers are all signal: passes with a note.
  source      every `- ` bullet of ## Source is one locator: Ruff <CODE>, Pylint <symbol> [(<code>)],
              SonarSource python S<n>, Bandit B<nnn> and flake8-bugbear B<nnn> resolve against
              items.jsonl and the cache under <harvest>/src/; PEP <n> and arXiv:<id> resolve by an
              HTTP 200 from peps.python.org and arxiv.org/abs; any other bullet resolves by its
              https:// URL or its (<owner>/<repo> <path>) GitHub locator on raw.githubusercontent.com
              (branch main, then master). A Caveat: bullet is passed over; a bullet of no known
              shape fails.
  fragment    every quoted span of a Source bullet and of the provenance line's citations — between
              straight double quotes, or straight single quotes when longer than 25 characters —
              occurs in its locator's text after whitespace collapsing, with Markdown backticks and
              asterisks ignored (the first 80 characters of a longer fragment; each part of a
              fragment elided with ... or …). A bullet marked (relayed), and a provenance fragment
              followed by a relayed marker, is exempt with a note.
  title       with --universal: the title and the H1 equal no universal card title.
  provenance  the line begins with `- **<rule_id>** · ` and holds ` · topic: `.

Fetched pages are cached under <dir>/../check-cache/<sha256 of the URL>; a cached page is not
fetched again. --no-network skips every fetch with a note. A fetch waits 20 s, is retried once on
a 5xx answer or a transport error, and is never retried on a 4xx answer.

Output: one line per failure `<key>: <check>: <detail>`, one line per note
`<key>: note: <check>: <detail>`, then `check-python-cards: N card(s), F failure(s), S skipped`;
with --json the object {cards: {key: {failures, notes}}, summary: {cards, failures, skipped}}.
Exit status 1 when a check fails, 2 when an input is missing. Writes only the temporary directory
and the fetch cache; standard library only.
"""
import argparse
import ast
import dataclasses
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cardlib import parse_frontmatter, parse_inline_list, read_card, strip_quotes, is_signal  # noqa: E402

USER_AGENT = "Mozilla/5.0 (check-python-cards)"
TIMEOUT_SECONDS = 20
FRAGMENT_PREFIX = 80
LABEL_CHARS = 60  # how much of a bullet or a fragment a failure line quotes
ELISION = re.compile(r"^(\s*)(?:\.\.\.|\{\s*\.\.\.\s*\})\s*$")
ELISION_AFTER_COLON = re.compile(r"^(.*:)\s*(?:\.\.\.|\{\s*\.\.\.\s*\})\s*$")
DOUBLE_QUOTED = re.compile(r'"([^"\n]+)"')
# An apostrophe inside a word (Python's) neither opens nor closes a single-quoted span.
SINGLE_QUOTED = re.compile(r"(?<!\w)'([^\n]{26,}?)'(?!\w)")
GITHUB_LOCATOR = re.compile(r"\(([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\s+([^\s)]+)\)")
CATALOG_KINDS = ("ruff", "pylint", "sonar", "bandit", "bugbear")
URL = re.compile(r"https://[^\s)>\]'\"`]+")


class InputError(Exception):
    """A required input is missing; main reports it in one line."""


# ---- fetching -------------------------------------------------------------------------------------

def urllib_open(url, timeout):
    """Return (status, body bytes); an HTTP error answer is a status, a transport failure raises OSError."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""


class Fetcher:
    """Fetches a URL once per cache directory; `opener(url, timeout)` is replaceable for tests."""

    def __init__(self, cache_dir, network=True, opener=urllib_open):
        self.cache_dir = cache_dir
        self.network = network
        self.opener = opener

    def cache_path(self, url):
        return os.path.join(self.cache_dir, hashlib.sha256(url.encode("utf-8")).hexdigest())

    def get(self, url):
        """Return (status, text, error). status is None when no answer came."""
        path = self.cache_path(url)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                return 200, handle.read(), ""
        status, body, error = None, b"", ""
        for _attempt in range(2):
            try:
                status, body = self.opener(url, TIMEOUT_SECONDS)
                error = ""
            except OSError as exc:
                status, body, error = None, b"", f"{type(exc).__name__}: {exc}"
                continue
            if status < 500:
                break
        if status == 200:
            text = body.decode("utf-8", errors="replace")
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            return 200, text, ""
        return status, "", error or f"HTTP {status}"


# ---- the harvest ----------------------------------------------------------------------------------

class Harvest:
    """The harvested catalog: items.jsonl and the cached texts under src/."""

    def __init__(self, harvest_dir):
        self.dir = os.path.abspath(harvest_dir)
        path = os.path.join(self.dir, "items.jsonl")
        if not os.path.isfile(path):
            raise InputError(f"items.jsonl not found: {path}")
        self.items = []
        with open(path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    self.items.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise InputError(f"{path}:{number} does not parse: {exc}") from exc
        self._ruff = None

    def find(self, source, code=None, name=None):
        for item in self.items:
            if item.get("source") != source:
                continue
            if (code and item.get("code") == code) or (name and item.get("name") == name):
                return item
        return None

    def read(self, relative):
        path = relative if os.path.isabs(relative) else os.path.join(self.dir, relative)
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()

    def ruff_rule(self, code):
        if self._ruff is None:
            raw = self.read(os.path.join("src", "ruff", "rules.json"))
            try:
                self._ruff = {r.get("code"): r for r in json.loads(raw)} if raw else {}
            except json.JSONDecodeError as exc:
                raise InputError(f"{self.dir}/src/ruff/rules.json does not parse: {exc}") from exc
        return self._ruff.get(code)

    @staticmethod
    def item_text(item):
        return "\n".join(item.get(k, "") for k in ("title", "summary", "explanation")) if item else ""

    def text_for(self, kind, value, symbol=None):
        """The catalog text a quoted fragment of this locator must occur in."""
        if kind == "ruff":
            rule = self.ruff_rule(value) or {}
            return "\n".join([rule.get("summary", ""), rule.get("explanation", ""), self.item_text(self.find("ruff", value))])
        if kind == "pylint":
            item = self.find("pylint", code=value, name=symbol)
            symbol = symbol or (item or {}).get("name", "")
            files = [self.read(os.path.join("src", "pylint", symbol, f)) for f in ("details.rst", "bad.py", "good.py")]
            return "\n".join(files + [self.item_text(item)])
        if kind == "sonar":
            return "\n".join([self.read(os.path.join("src", "sonar", f"{value}.html")),
                              self.read(os.path.join("src", "sonar", f"{value}.json")),
                              self.item_text(self.find("sonar", value))])
        if kind == "bandit":
            item = self.find("bandit", value) or {}
            rst = [self.read(p) for p in glob.glob(os.path.join(self.dir, "src", "bandit", f"{value.lower()}_*.rst"))]
            return "\n".join(rst + [self.read(item.get("cache_path", "")) if item.get("cache_path") else "", self.item_text(item)])
        if kind == "bugbear":
            return "\n".join([self.read(os.path.join("src", "bugbear", "README.rst")), self.item_text(self.find("bugbear", value))])
        return ""

    def exists(self, kind, value, symbol=None):
        if kind == "pylint":
            return (self.find("pylint", code=value, name=symbol) is not None
                    or bool(symbol and os.path.isdir(os.path.join(self.dir, "src", "pylint", symbol))))
        if kind == "sonar":
            return os.path.isfile(os.path.join(self.dir, "src", "sonar", f"{value}.html"))
        return self.find(kind, value) is not None


# ---- card parts -----------------------------------------------------------------------------------

def body_sections(markdown):
    """{heading: text} of the H2 blocks after the frontmatter."""
    m = re.match(r"---\n.*?\n---\n", markdown, re.S)
    body = markdown[m.end():] if m else markdown
    sections, current, buf = {}, None, []
    for line in body.split("\n"):
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf)
            current, buf = line[3:].strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


def h1_of(markdown):
    m = re.search(r"^# (.+)$", markdown, re.M)
    return m.group(1).strip() if m else ""


def strip_label(lines, label):
    """Blank out the label so the code keeps the columns it has under the label, then dedent."""
    first = lines[0]
    at = first.index(label) + len(label)
    return textwrap.dedent("\n".join([" " * at + first[at:], *lines[1:]])).strip("\n")


def split_example(markdown):
    """Return (bad code, good code, error) from the Example's single fenced block."""
    example = body_sections(markdown).get("Example")
    if example is None:
        return None, None, "no ## Example block"
    fences = re.findall(r"^\s*```[^\n]*\n(.*?)^\s*```", example, re.S | re.M)
    if len(fences) != 1:
        return None, None, f"the Example holds {len(fences)} fenced block(s); one is the form"
    lines = fences[0].rstrip("\n").split("\n")
    bad_at = next((i for i, line in enumerate(lines) if line.lstrip().startswith("bad:")), None)
    good_at = next((i for i, line in enumerate(lines) if line.lstrip().startswith("good:")), None)
    if bad_at is None or good_at is None:
        return None, None, "the Example needs a line starting with bad: and one starting with good:"
    bad_end = good_at if good_at > bad_at else len(lines)
    good_end = bad_at if bad_at > good_at else len(lines)
    return strip_label(lines[bad_at:bad_end], "bad:"), strip_label(lines[good_at:good_end], "good:"), None


def replace_elisions(code):
    out = []
    for line in code.split("\n"):
        m = ELISION.match(line)
        if m:
            out.append(f"{m.group(1)}pass")
            continue
        m = ELISION_AFTER_COLON.match(line)
        out.append(f"{m.group(1)} pass" if m else line)
    return "\n".join(out)


def syntax_error(code):
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return exc
    return None


def parse_good(code):
    """Return None when the good half parses with its elisions given a body, else the error text.
    Code that parses as written passes too: `lambda: ...` is valid only unreplaced."""
    replaced = replace_elisions(code)
    error = syntax_error(replaced)
    if error is None or syntax_error(code) is None:
        return None
    lines = replaced.split("\n")
    shown = lines[error.lineno - 1].strip() if error.lineno and 0 < error.lineno <= len(lines) else ""
    return f"the good half does not parse: {error.msg} (line {error.lineno}: {shown!r})"


def card_frontmatter(path, markdown):
    """Return (rule_id, title, triggers, error)."""
    rec, err = read_card(path)
    if rec:
        return rec["rule_id"], rec["title"], rec["triggers"], None
    _keys, data, ferr = parse_frontmatter(markdown)
    if ferr:
        return "", "", None, ferr
    triggers, terr = parse_inline_list(data.get("triggers", ""))
    return data.get("rule_id", "").strip(), strip_quotes(data.get("title", "")), triggers, terr or err


def source_bullets(markdown):
    """The `- ` bullets of ## Source, each with its continuation lines joined."""
    bullets = []
    for line in body_sections(markdown).get("Source", "").split("\n"):
        if line.startswith("- "):
            bullets.append(line[2:].strip())
        elif line.strip() and bullets:
            bullets[-1] += " " + line.strip()
    return bullets


# ---- locators and fragments -------------------------------------------------------------------------

def classify(bullet):
    """Return (kind, value, symbol) for a Source bullet; kind None when the shape is unknown."""
    patterns = (
        ("ruff", r"Ruff\s+([A-Z]+[0-9]+)\b"),
        ("pylint", r"Pylint\s+([a-z][a-z0-9-]*)(?:\s+\(([A-Z]\d{4})\))?"),
        ("sonar", r"SonarSource\s+python\s+(S\d+|[A-Z][A-Za-z]+)\b"),
        ("bandit", r"Bandit\s+(B\d{3})\b"),
        ("bugbear", r"flake8-bugbear\s+(B\d{3})\b"),
        ("pep", r"PEP\s+(\d+)\b"),
        ("arxiv", r"arXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)"),
    )
    for kind, pattern in patterns:
        m = re.match(pattern, bullet)
        if m:
            if kind == "pylint":
                return kind, m.group(2), m.group(1)
            return kind, m.group(1), None
    m = re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)", bullet)
    if m:
        return "arxiv", m.group(1), None
    if URL.search(bullet) or GITHUB_LOCATOR.search(bullet):
        return "web", None, None
    return None, None, None


def web_targets(bullet):
    """The URL candidates of a web bullet: each https URL, else the GitHub locator on main then master."""
    urls = [u.rstrip(".,;:") for u in URL.findall(bullet)]
    if urls:
        return [[u] for u in urls]
    owner, repo, path = GITHUB_LOCATOR.search(bullet).groups()
    return [[f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}" for branch in ("main", "master")]]


def normalise(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return " ".join(text.replace("`", "").replace("*", "").split())


def quoted_fragments(text):
    """Return [(fragment, end offset)] of the double-quoted and long single-quoted spans."""
    found = [(m.group(1), m.end()) for m in DOUBLE_QUOTED.finditer(text)]
    found += [(m.group(1), m.end()) for m in SINGLE_QUOTED.finditer(text)]
    return found


def fragment_found(fragment, haystack):
    parts = [normalise(p) for p in re.split(r"\.\.\.|…", fragment)]
    parts = [p for p in parts if p]
    return all(p[:FRAGMENT_PREFIX] in haystack for p in parts)


def is_relayed_after(text, end):
    """Whether the status written after a quote, up to the next quote, marks it relayed."""
    tail = re.split(r"[\"']", text[end:], maxsplit=1)[0]
    return "relayed" in tail.lower()


# ---- one card --------------------------------------------------------------------------------------

class CardResult:
    def __init__(self):
        self.failures = []
        self.notes = []

    def fail(self, check, detail):
        self.failures.append(f"{check}: {detail}")

    def note(self, check, detail):
        self.notes.append(f"{check}: {detail}")


def fetch_bullet(bullet, kind, value, fetcher, result):
    """Return (text, checkable) of a PEP, arXiv or web bullet: every target must answer 200."""
    if kind == "pep":
        targets = [[f"https://peps.python.org/pep-{int(value):04d}/"]]
    elif kind == "arxiv":
        targets = [[f"https://arxiv.org/abs/{value}"]]
    else:
        targets = web_targets(bullet)
    text, checkable = "", True
    for alternatives in targets:
        fetched, error = None, ""
        for url in alternatives:
            status, page, error = fetcher.get(url)
            if status == 200:
                fetched = page
                break
        if fetched is None:
            result.fail("source", f"{alternatives[-1]} answered {error}: {bullet[:LABEL_CHARS]}")
            checkable = False
        else:
            text += "\n" + fetched
    return text, checkable


def resolve_bullet(bullet, harvest, fetcher, result):
    """Return (text, checkable) of one Source bullet, or None when its locator fails."""
    label = bullet[:LABEL_CHARS]
    kind, value, symbol = classify(bullet)
    if kind is None:
        result.fail("source", f"locator not recognised: {label}")
        return None
    if kind in CATALOG_KINDS:
        if not harvest.exists(kind, value, symbol):
            result.fail("source", f"no {kind} entry {symbol or value} in the harvest: {label}")
            return None
        return harvest.text_for(kind, value, symbol), True
    if "(relayed)" in bullet.lower():
        result.note("source", f"relayed, not fetched: {label}")
        return "", False
    if not fetcher.network:
        result.note("source", f"--no-network, not fetched: {label}")
        return "", False
    return fetch_bullet(bullet, kind, value, fetcher, result)


def check_sources(markdown, harvest, fetcher, result):
    """Run the source and fragment checks of the Source bullets; return the normalised texts resolved."""
    texts = []
    for bullet in source_bullets(markdown):
        if bullet.startswith("Caveat:"):
            continue
        label = bullet[:LABEL_CHARS]
        relayed = "(relayed)" in bullet.lower()
        resolved = resolve_bullet(bullet, harvest, fetcher, result)
        if resolved is None:
            continue
        text, checkable = resolved
        haystack = normalise(text)
        if text:
            texts.append(haystack)
        if relayed:
            if quoted_fragments(bullet):
                result.note("fragment", f"relayed, fragments not checked: {label}")
            continue
        for fragment, _end in quoted_fragments(bullet):
            if not checkable:
                result.note("fragment", f"not checked, no text: {fragment[:LABEL_CHARS]}")
            elif not fragment_found(fragment, haystack):
                result.fail("fragment", f"{label}: not found: {fragment[:LABEL_CHARS]}")
    return texts


def check_provenance(line, rule_id, texts, result):
    if not line:
        result.note("provenance", "no provenance line to check")
        return
    if not rule_id or not line.startswith(f"- **{rule_id}** · "):
        result.fail("provenance", f"does not begin with '- **{rule_id}** · '")
    if " · topic: " not in line:
        result.fail("provenance", "holds no ' · topic: '")
    citations = line.split(" · topic: ", 1)[0]
    haystack = "\n".join(texts)
    for fragment, end in quoted_fragments(citations):
        if is_relayed_after(citations, end):
            result.note("fragment", f"provenance fragment marked relayed, not checked: {fragment[:LABEL_CHARS]}")
        elif not haystack:
            result.note("fragment", f"provenance fragment not checked, no source text: {fragment[:LABEL_CHARS]}")
        elif not fragment_found(fragment, haystack):
            result.fail("fragment", f"provenance: not found in any Source text: {fragment[:LABEL_CHARS]}")


@dataclasses.dataclass(frozen=True)
class CheckContext:
    """What every card of one run is checked against."""
    harvest: Harvest
    fetcher: Fetcher
    universal_titles: dict | None
    skill_dir: str


def check_trigger_match(triggers, frontmatter_error, bad, result):
    if triggers is None:
        result.fail("triggers", f"the triggers do not parse: {frontmatter_error}")
    elif not triggers:
        result.note("triggers", "no triggers")
    elif all(is_signal(t) for t in triggers):
        result.note("triggers", "signal triggers only; nothing to match")
    elif bad is None:
        result.note("triggers", "not checked; the Example did not split into its bad and good halves")
    else:
        lines = [line for line in bad.split("\n") if line.strip()]
        candidates = lines + [line.strip() for line in lines]
        compiled = []
        for t in triggers:
            if is_signal(t):
                continue
            try:
                compiled.append(re.compile(t))
            except re.error as exc:
                result.fail("triggers", f"{t!r} does not compile: {exc}")
        if compiled and not any(p.search(line) for p in compiled for line in candidates):
            result.fail("triggers", "no trigger matches a line of the bad half")


def check_card(draft, path, context, result):
    markdown = draft["card_markdown"]
    rule_id, title, triggers, ferr = card_frontmatter(path, markdown)
    bad, good, eerr = split_example(markdown)
    if eerr:
        result.fail("example", eerr)
    else:
        perr = parse_good(good)
        if perr:
            result.fail("example", perr)
    check_trigger_match(triggers, ferr, bad, result)
    texts = check_sources(markdown, context.harvest, context.fetcher, result)
    universal_titles = context.universal_titles
    if universal_titles is not None:
        for label, value in (("title", title), ("H1", h1_of(markdown))):
            hit = universal_titles.get(" ".join(value.lower().split()))
            if value and hit:
                result.fail("title", f"the {label} equals the title of universal card {hit}")
    if draft.get("_from_markdown"):
        result.note("provenance", f"read {draft['key']}.md without {draft['key']}.json; provenance not checked")
    else:
        check_provenance(draft.get("provenance_line", ""), rule_id, texts, result)


# ---- the run -----------------------------------------------------------------------------------------

def slugify(text, limit=60):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].rstrip("-") or "card"


def draft_from_markdown(key, markdown):
    _keys, data, _err = parse_frontmatter(markdown)
    data = data or {}
    rule_id = data.get("rule_id", "").strip()
    m = re.fullmatch(r"([A-Z]+)-(\d{2,3})", rule_id)
    filename = f"{m.group(1).lower()}-{m.group(2)}--{slugify(strip_quotes(data.get('title', '')))}.md" if m else f"{key}.md"
    return {"key": key, "status": "card", "filename": filename, "card_markdown": markdown, "provenance_line": "",
            "_from_markdown": True}


def load_drafts(state_dir, keys):
    """Return [(key, draft or None, error)] in key order."""
    if keys is None:
        stems = {os.path.basename(p)[:-len(".json")] for p in glob.glob(os.path.join(state_dir, "*.json"))}
        stems |= {os.path.basename(p)[:-len(".md")] for p in glob.glob(os.path.join(state_dir, "*.md"))}
        keys = sorted(stems)
    out = []
    for key in keys:
        json_path = os.path.join(state_dir, f"{key}.json")
        md_path = os.path.join(state_dir, f"{key}.md")
        if os.path.isfile(json_path):
            try:
                with open(json_path, encoding="utf-8") as handle:
                    obj = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                out.append((key, None, f"{json_path} does not parse: {exc}"))
                continue
            if isinstance(obj, dict) and "spine" in obj:
                continue
            if not isinstance(obj, dict):
                out.append((key, None, f"{json_path} is not a draft object"))
                continue
            obj.setdefault("key", key)
            out.append((key, obj, None))
        elif os.path.isfile(md_path):
            with open(md_path, encoding="utf-8") as handle:
                out.append((key, draft_from_markdown(key, handle.read()), None))
        else:
            out.append((key, None, f"neither {key}.json nor {key}.md in {state_dir}"))
    return out


def run_validator(skill_dir, card_dir, by_filename, results):
    validator = os.path.join(skill_dir, "scripts", "validate-craft-cards.py")
    proc = subprocess.run([sys.executable, validator, "--language", "python", card_dir],
                          capture_output=True, text=True, check=False)
    errors = 0
    for line in proc.stdout.splitlines():
        m = re.match(r"^(.*?): (error|warning): (.*)$", line)
        if not m:
            continue
        where, level, message = m.groups()
        keys = by_filename.get(os.path.basename(where))
        if level == "warning":
            if keys and "numbering gap" not in message:
                for key in keys:
                    results[key].note("validator", message)
            continue
        errors += 1
        for key in keys or list(results):
            results[key].fail("validator", message)
    if proc.returncode != 0 and errors == 0:
        reason = (proc.stderr.strip().splitlines() or [f"exit status {proc.returncode}"])[-1]
        for result in results.values():
            result.fail("validator", f"the validator did not run: {reason}")


def check_all(state_dir, context, keys=None):
    """Return ({key: CardResult}, checked count, skipped count)."""
    results, skipped, checked = {}, 0, []
    for key, draft, error in load_drafts(state_dir, keys):
        result = results.setdefault(key, CardResult())
        if error:
            result.fail("input", error)
            continue
        if draft.get("status") == "pending":
            result.note("input", "status pending; skipped")
            skipped += 1
            continue
        if not draft.get("card_markdown"):
            result.fail("input", "card_markdown is empty")
            continue
        checked.append((key, draft))
    by_filename = {}
    with tempfile.TemporaryDirectory(prefix="check-python-cards-") as tmp:
        paths = {}
        for key, draft in checked:
            filename = os.path.basename(draft.get("filename") or "")
            if not filename.endswith(".md"):
                results[key].fail("input", f"filename {draft.get('filename')!r} is not a .md file name")
                filename = f"{key}.md"
            if filename in by_filename:
                results[key].fail("input", f"filename {filename} is also the filename of {by_filename[filename][0]}")
            by_filename.setdefault(filename, []).append(key)
            paths[key] = os.path.join(tmp, filename)
            with open(paths[key], "w", encoding="utf-8") as handle:
                handle.write(draft["card_markdown"])
        if checked:
            run_validator(context.skill_dir, tmp, by_filename, {k: results[k] for k, _ in checked})
        for key, draft in checked:
            check_card(draft, paths[key], context, results[key])
    return results, len(checked), skipped


def load_universal_titles(path):
    if path is None:
        return None
    if not os.path.isfile(path):
        raise InputError(f"universal index not found: {path}")
    try:
        with open(path, encoding="utf-8") as handle:
            cards = json.load(handle)
    except json.JSONDecodeError as exc:
        raise InputError(f"universal index does not parse: {path}: {exc}") from exc
    return {" ".join(c["title"].lower().split()): c["rule_id"] for c in cards}


def main(argv, opener=urllib_open):
    parser = argparse.ArgumentParser(prog="check-python-cards.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--state", required=True)
    parser.add_argument("--harvest", required=True)
    parser.add_argument("--keys")
    parser.add_argument("--universal")
    parser.add_argument("--skill", default=os.path.dirname(HERE))
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--json", action="store_true")
    opts = parser.parse_args(argv)
    state = os.path.abspath(opts.state)
    try:
        if not os.path.isdir(state):
            raise InputError(f"state directory not found: {state}")
        harvest = Harvest(opts.harvest)
        universal_titles = load_universal_titles(opts.universal)
        fetcher = Fetcher(os.path.join(os.path.dirname(state), "check-cache"), network=not opts.no_network, opener=opener)
        keys = [k for k in opts.keys.split(",") if k] if opts.keys else None
        context = CheckContext(harvest, fetcher, universal_titles, opts.skill)
        results, checked, skipped = check_all(state, context, keys)
    except InputError as exc:
        print(f"check-python-cards: {exc}", file=sys.stderr)
        return 2
    failures = sum(len(r.failures) for r in results.values())
    summary = {"cards": checked, "failures": failures, "skipped": skipped}
    if opts.json:
        print(json.dumps({"cards": {k: {"failures": r.failures, "notes": r.notes} for k, r in results.items()},
                          "summary": summary}, ensure_ascii=False, indent=2))
    else:
        for key, result in results.items():
            for failure in result.failures:
                print(f"{key}: {failure}")
        for key, result in results.items():
            for note in result.notes:
                print(f"{key}: note: {note}")
        print(f"check-python-cards: {checked} card(s), {failures} failure(s), {skipped} skipped")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
