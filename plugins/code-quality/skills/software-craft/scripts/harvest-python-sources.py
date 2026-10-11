#!/usr/bin/env python3
"""Collect the rule catalogs of the Python static-analysis tools into one JSON-lines file,
caching every fetched text on disk so later authoring phases grep the cache instead of the
network. Authoring time only; never part of a build or a review.

Usage:
  harvest-python-sources.py --out <state-dir> [--only ruff,pylint,sonar,bandit,bugbear]
                            [--ruff-json <file>] [--offline]
    --out        the directory that receives items.jsonl, summary.json and src/<source>/...
    --only       a comma-separated subset of the sources (default: all five)
    --ruff-json  a saved `ruff rule --all --output-format json` catalog, read instead of running
                 `uvx ruff rule --all --output-format json`
    --offline    no network: every text comes from src/ and a text missing there is a failure

Reads:
  ruff     the Ruff catalog: --ruff-json, else src/ruff/rules.json, else the uvx command
  pylint   the GitHub tree of pylint-dev/pylint; doc/data/messages/<l>/<symbol>/{details.rst,
           bad.py, bad/*.py, good.py, good/*.py}; doc/user_guide/checkers/features.rst and
           extensions.rst, whose `:<symbol> (<code>):` entries give the codes (an extension's
           message is off by default); doc/user_guide/messages/messages_overview.rst, whose
           `<category>/<symbol>` lines give the type letter of a message neither index lists
  sonar    the GitHub tree of SonarSource/sonar-python (branch master, else main); the
           <key>.html and <key>.json pairs and Sonar_way_profile.json under
           python-checks/src/main/resources/org/sonar/l10n/py/rules/python/; a rule whose json
           status is not "ready" is dropped
  bandit   the GitHub tree of PyCQA/bandit; doc/source/plugins/b<nnn>_<name>.rst and
           doc/source/blacklists/*.rst, which are autodoc stubs, and the bandit/*.py modules
           they name, whose docstrings carry the rule text; a page that carries its own text
           under a `.. deprecated::` directive documents a removed plugin and is dropped
  bugbear  the README.rst of PyCQA/flake8-bugbear, one rule per `**B<nnn>**:` paragraph

Writes, under --out:
  items.jsonl   one rule per line, sorted by source then code:
                {source, code, name, title, summary, explanation, url, default_on, category,
                 status, cache_path}
                source: ruff | pylint | sonar | bandit | bugbear; summary: the first prose
                paragraph, at most 300 characters; url: the raw URL of the source text;
                cache_path: that text's cache path, relative to --out
  summary.json  per source: the item count, the dropped count by reason, the texts it failed to
                obtain as fetch_failures (url, status, reason), notes, the wall-clock seconds and
                the fatal error, if any
  src/<source>/ every fetched text under its repository-relative name; src/<source>/tree.json
                holds the one GitHub listing of that source as {repo, branch, listing, response}

A cached file is never fetched again, so a cut run resumes where it stopped. One line per source
goes to standard output; the exit status is 1 when any source failed or lost a fetch, and each
such source's reason goes to standard error.
"""
import argparse
import ast
import concurrent.futures
import dataclasses
import json
import os
import re
import socket
import subprocess
import sys
import textwrap
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, namedtuple
from html.parser import HTMLParser
from types import MappingProxyType

SOURCES = ("ruff", "pylint", "sonar", "bandit", "bugbear")
USER_AGENT = "Mozilla/5.0 (harvest-python-sources)"
TIMEOUT_SECONDS = 20
# The largest text read is the Pylint tree listing, a few megabytes; the cap only stops a runaway body.
MAX_RESPONSE_BYTES = 64 * 1024 * 1024
FETCH_THREADS = 8
SUMMARY_LIMIT = 300
RAW = "https://raw.githubusercontent.com"
API = "https://api.github.com"

RUFF_CMD = ("uvx", "ruff", "rule", "--all", "--output-format", "json")
# The first uvx run downloads Ruff before it prints the catalog.
RUFF_TIMEOUT_SECONDS = 600
RUFF_RAW = RAW + "/astral-sh/ruff/main/"
RUFF_DROPPED_LINTERS = MappingProxyType({
    "pydocstyle": "D", "pydoclint": "DOC", "flake8-pyi": "PYI", "pep8-naming": "N",
    "flake8-import-conventions": "ICN", "Airflow": "AIR", "flake8-django": "DJ", "FastAPI": "FAST",
    "NumPy-specific rules": "NPY", "pandas-vet": "PD", "flake8-print": "T20", "flake8-debugger": "T10",
    "isort": "I", "flake8-commas": "COM", "flake8-quotes": "Q", "flake8-copyright": "CPY",
    "flake8-fixme": "FIX", "flake8-todos": "TD",
})
RUFF_DROPPED_CODES = ("E1", "E2", "E3", "E501", "W1", "W2", "W3", "W505")
RUFF_DEFAULT_SELECT = ("E4", "E7", "E9", "F")
RUFF_KEPT_STATUS = MappingProxyType({"Stable": "stable", "Preview": "preview"})

PYLINT_REPO = "pylint-dev/pylint"
PYLINT_MESSAGES = "doc/data/messages/"
PYLINT_CORE_INDEX = "doc/user_guide/checkers/features.rst"
PYLINT_EXTENSION_INDEX = "doc/user_guide/checkers/extensions.rst"
PYLINT_OVERVIEW = "doc/user_guide/messages/messages_overview.rst"

SONAR_REPO = "SonarSource/sonar-python"
SONAR_DIR = "python-checks/src/main/resources/org/sonar/l10n/py/rules/python"
SONAR_PROFILE = "Sonar_way_profile.json"

BANDIT_REPO = "PyCQA/bandit"
BANDIT_DOC_DIRS = ("doc/source/plugins/", "doc/source/blacklists/")

BUGBEAR_URL = RAW + "/PyCQA/flake8-bugbear/main/README.rst"


class FetchError(Exception):
    """A text could not be obtained; `status` is the HTTP status, or None without a response."""

    def __init__(self, url, status, reason):
        super().__init__(f"{url}: {status if status is not None else reason}")
        self.url, self.status, self.reason = url, status, reason


class SourceError(Exception):
    """A source cannot produce its catalog at all."""


# ---------------------------------------------------------------- network and cache

def _transient(err):
    if isinstance(err, urllib.error.HTTPError):
        return 500 <= err.code < 600
    if isinstance(err, (TimeoutError, socket.timeout)):
        return True
    return isinstance(err, urllib.error.URLError) and isinstance(err.reason, (TimeoutError, socket.timeout))


def http_get(url, headers=None):
    """Return the body of a GET as text. Raises FetchError; a 5xx or a timeout is retried once,
    any other failure is final because a later attempt of the same request cannot clear it."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise FetchError(url, None, f"response exceeds {MAX_RESPONSE_BYTES} bytes")
            return body.decode("utf-8")
        except (urllib.error.URLError, TimeoutError, socket.timeout) as err:
            status = None
            if isinstance(err, urllib.error.HTTPError):
                status = err.code
                err.close()
            if attempt == 1 and _transient(err):
                continue
            raise FetchError(url, status, str(getattr(err, "reason", err))) from err
    raise AssertionError("unreachable: the second attempt returns or raises")


class Cache:
    """Texts under <out>/src/, fetched once. Safe for concurrent use on distinct paths."""

    def __init__(self, out, offline, fetch=http_get):
        self.out, self.offline, self._fetch = out, offline, fetch

    def path(self, rel):
        return os.path.join(self.out, rel)

    def has(self, rel):
        return os.path.isfile(self.path(rel))

    def read(self, rel):
        with open(self.path(rel), encoding="utf-8") as fh:
            return fh.read()

    def write(self, rel, text):
        _write_atomic(self.path(rel), text)

    def fetch(self, url, headers=None):
        if self.offline:
            raise FetchError(url, None, "offline and not cached")
        return self._fetch(url, headers)

    def fetch_once(self, url, rel, headers=None):
        """The text cached at `rel`, fetched from `url` and written there first when absent."""
        if self.has(rel):
            return self.read(rel)
        body = self.fetch(url, headers)
        self.write(rel, body)
        return body


def _write_atomic(path, text):
    # A cut run must never leave a partial file behind: the next run takes any file as cached.
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def fetch_all(cache, jobs):
    """Fetch (url, rel) jobs through the cache on a thread pool. Returns ({rel: text}, failures)."""
    texts, failures = {}, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=FETCH_THREADS) as pool:
        futures = {pool.submit(cache.fetch_once, url, rel): (url, rel) for url, rel in jobs}
        for future in concurrent.futures.as_completed(futures):
            url, rel = futures[future]
            try:
                texts[rel] = future.result()
            except FetchError as err:
                failures.append(_failure(err))
    return texts, failures


def raw_url(repo, branch, path):
    # Tree paths can hold non-ASCII names (Pylint's non-ascii-name examples); an HTTP request line cannot.
    return f"{RAW}/{repo}/{branch}/{urllib.parse.quote(path)}"


def _failure(err):
    return {"url": err.url, "status": err.status, "reason": err.reason}


def _api_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_listing(cache, source, repo, branches, flat_dir=None):
    """The one cached GitHub listing of `repo`: the recursive tree of the first branch that
    exists. The unauthenticated API allows 60 requests an hour, so the listing is requested once
    and kept in src/<source>/tree.json. A truncated tree falls back to the contents listing of
    `flat_dir`, which holds every file the source needs; without one it is a SourceError."""
    rel = f"src/{source}/tree.json"
    if cache.has(rel):
        return json.loads(cache.read(rel))
    headers = _api_headers()
    for index, branch in enumerate(branches):
        try:
            response = json.loads(cache.fetch(f"{API}/repos/{repo}/git/trees/{branch}?recursive=1", headers))
        except FetchError as err:
            if err.status == 404 and index + 1 < len(branches):
                continue
            raise
        listing = {"repo": repo, "branch": branch, "listing": "tree", "response": response}
        if response.get("truncated"):
            if flat_dir is None:
                raise SourceError(f"the GitHub tree of {repo} is truncated")
            contents = cache.fetch(f"{API}/repos/{repo}/contents/{flat_dir}?ref={branch}", headers)
            listing.update(listing="contents", response=json.loads(contents))
        cache.write(rel, json.dumps(listing))
        return listing
    raise SourceError(f"none of the branches {branches} of {repo} exists")


def listing_paths(listing):
    if listing["listing"] == "tree":
        return [entry["path"] for entry in listing["response"]["tree"] if entry["type"] == "blob"]
    return [entry["path"] for entry in listing["response"] if entry["type"] == "file"]


# ---------------------------------------------------------------- text helpers

_HEADING_LINE = re.compile(r"^\s*(#{1,6}\s|[=\-~^*#+]{3,}\s*$)")


def first_paragraph(text, limit=SUMMARY_LIMIT):
    """The first prose paragraph of `text`, whitespace collapsed, clipped to `limit` characters
    (unclipped when `limit` is None). Heading lines (Markdown `#`, reStructuredText underlines)
    and their titles are skipped."""
    for block in re.split(r"\n\s*\n", text or ""):
        lines = block.strip().splitlines()
        if len(lines) >= 2 and re.fullmatch(r"[=\-~^*#+]{3,}\s*", lines[1]):
            lines = lines[2:]
        prose = " ".join(" ".join(line for line in lines if not _HEADING_LINE.match(line)).split())
        if prose:
            return prose if limit is None else clip(prose, limit)
    return ""


def first_sentence(text):
    collapsed = " ".join((text or "").split())
    match = re.match(r"(.+?[.!?])(\s|$)", collapsed)
    return clip(match.group(1) if match else collapsed, SUMMARY_LIMIT)


def clip(text, limit):
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def code_matches(code, prefix):
    """True when a rule code falls under a selector prefix: the letters match exactly and the
    digits start with the prefix's digits, so "D" selects D100 but not DTZ001 or DOC201."""
    code_match = re.fullmatch(r"([A-Z]+)(\d+)", code or "")
    prefix_match = re.fullmatch(r"([A-Z]+)(\d*)", prefix)
    return bool(code_match and prefix_match and code_match.group(1) == prefix_match.group(1)
                and code_match.group(2).startswith(prefix_match.group(2)))


@dataclasses.dataclass(frozen=True)
class Item:
    """One line of items.jsonl; the field order is the line's key order."""
    source: str
    code: str
    name: str
    title: str
    summary: str
    explanation: str
    url: str
    default_on: bool
    category: str
    status: str
    cache_path: str


class SourceResult:
    """What one source produced. The harvest functions fill it in place, so a source that fails
    part-way still reports the items, drops and fetch failures it reached."""

    def __init__(self, source):
        self.source = source
        self.items = []
        self.dropped = Counter()
        self.failures = []
        self.notes = []
        self.error = None
        self.seconds = 0.0

    def failed(self):
        return self.error is not None or bool(self.failures)

    def summary(self):
        return {"items": len(self.items), "dropped": {"total": sum(self.dropped.values()),
                                                       "reasons": dict(sorted(self.dropped.items()))},
                "fetch_failures": sorted(self.failures, key=lambda f: f["url"]), "notes": self.notes,
                "error": self.error, "seconds": round(self.seconds, 2)}


# ---------------------------------------------------------------- ruff

def ruff_items(rules, result):
    for rule in rules:
        code, linter = rule.get("code") or "", rule.get("linter") or ""
        status = next(iter(rule.get("status") or {"Unknown": None}))
        if status not in RUFF_KEPT_STATUS:
            result.dropped[f"status:{status}"] += 1
            continue
        reason = _ruff_drop_reason(code, linter)
        if reason:
            result.dropped[reason] += 1
            continue
        stable = RUFF_KEPT_STATUS[status] == "stable"
        source_file = (rule.get("source_location") or {}).get("file") or ""
        explanation = rule.get("explanation") or ""
        result.items.append(Item(
            "ruff", code, rule.get("name") or "", rule.get("summary") or "", first_paragraph(explanation),
            explanation, RUFF_RAW + source_file if source_file else "",
            stable and any(code_matches(code, p) for p in RUFF_DEFAULT_SELECT),
            f"{linter}/{rule.get('category') or ''}", RUFF_KEPT_STATUS[status], "src/ruff/rules.json"))


def _ruff_drop_reason(code, linter):
    if linter in RUFF_DROPPED_LINTERS:
        return f"linter:{linter}"
    for name, prefix in RUFF_DROPPED_LINTERS.items():
        if code_matches(code, prefix):
            return f"linter:{name}"
    for prefix in RUFF_DROPPED_CODES:
        if code_matches(code, prefix):
            return f"code:{prefix}"
    return None


def harvest_ruff(cache, result, ruff_json=None):
    rel = "src/ruff/rules.json"
    if ruff_json:
        with open(ruff_json, encoding="utf-8") as fh:
            text = fh.read()
        if not cache.has(rel) or cache.read(rel) != text:
            cache.write(rel, text)
    elif cache.has(rel):
        text = cache.read(rel)
    elif cache.offline:
        raise SourceError("offline and src/ruff/rules.json is not cached")
    else:
        try:
            run = subprocess.run(RUFF_CMD, capture_output=True, encoding="utf-8", check=True,
                                 timeout=RUFF_TIMEOUT_SECONDS)
        except (OSError, subprocess.SubprocessError) as err:
            stderr = getattr(err, "stderr", "") or ""
            raise SourceError(f"`{' '.join(RUFF_CMD)}` failed: {err} {stderr.strip()[:200]}") from err
        text = run.stdout
        cache.write(rel, text)
    try:
        rules = json.loads(text)
    except json.JSONDecodeError as err:
        raise SourceError(f"the Ruff catalog is not JSON: {err}") from err
    ruff_items(rules, result)


# ---------------------------------------------------------------- pylint

_PYLINT_ENTRY = re.compile(r"^:([a-z0-9-]+) \(([A-Z]\d{4})\):\s*(?:\*(.*)\*)?\s*$")


def parse_pylint_index(text):
    """{symbol: (code, message, description)} from the `:<symbol> (<code>): *<message>*` entries
    of a checkers index, the description being the indented lines under the entry."""
    entries, lines, i = {}, text.splitlines(), 0
    while i < len(lines):
        match = _PYLINT_ENTRY.match(lines[i])
        i += 1
        if not match:
            continue
        symbol, code, message = match.group(1), match.group(2), match.group(3) or ""
        body = []
        while i < len(lines) and lines[i].startswith(" ") and lines[i].strip():
            body.append(lines[i].strip())
            i += 1
        if not message and body and re.fullmatch(r"\*.*\*", body[0]):
            message = body.pop(0)[1:-1]
        entries[symbol] = (code, message.strip(), " ".join(body))
    return entries


def parse_pylint_overview(text):
    """{symbol: type letter} from the `<category>/<symbol>` toctree lines of the messages
    overview, which lists every message, including those the checkers indexes leave out."""
    return {m.group(2): m.group(1)[0].upper() for m in re.finditer(
        r"^\s+(fatal|error|warning|convention|refactor|information)/([a-z0-9-]+)\s*$", text, re.M)}


def pylint_message_files(paths):
    """{symbol: [repo path, ...]} for the details, bad and good files of each message directory."""
    messages = {}
    for path in paths:
        if not path.startswith(PYLINT_MESSAGES):
            continue
        parts = path[len(PYLINT_MESSAGES):].split("/")
        if len(parts) < 3:
            continue
        symbol, rest = parts[1], "/".join(parts[2:])
        if rest in ("details.rst", "bad.py", "good.py") or re.fullmatch(r"(bad|good)/[^/]+\.py", rest):
            messages.setdefault(symbol, []).append(path)
    return messages


PylintIndex = namedtuple("PylintIndex", "entries extensions categories")
PylintIndex.__doc__ = """What Pylint's own indexes say of each message symbol: `entries` maps it to
(code, message, description) from the checkers indexes, `extensions` holds the symbols of optional
extensions, `categories` maps it to its type letter from the messages overview."""


def pylint_index(core_text, extension_text, overview_text):
    extension_entries = parse_pylint_index(extension_text)
    return PylintIndex({**parse_pylint_index(core_text), **extension_entries}, frozenset(extension_entries),
                       parse_pylint_overview(overview_text))


def pylint_item(symbol, texts, index, branch="main"):
    """`texts` maps each file of the message, relative to its directory (details.rst, bad.py,
    bad/x.py, ...), to its text; `index` is the PylintIndex."""
    code, message, description = index.entries.get(symbol, ("", "", ""))
    details = (texts.get("details.rst") or "").strip()
    parts = [details or description]
    for kind in ("bad", "good"):
        for name in sorted(n for n in texts if n == f"{kind}.py" or n.startswith(f"{kind}/")):
            parts.append(f"--- {name} ---\n{texts[name].rstrip()}")
    explanation = "\n\n".join(p for p in parts if p)
    prose = details or description
    first = "details.rst" if "details.rst" in texts else sorted(texts)[0]
    letter = symbol[0]
    return Item("pylint", code, symbol, message or first_sentence(first_paragraph(prose, None)) or symbol,
                first_paragraph(prose), explanation,
                raw_url(PYLINT_REPO, branch, f"{PYLINT_MESSAGES}{letter}/{symbol}/{first}"),
                symbol not in index.extensions, code[:1] or index.categories.get(symbol, ""), "stable",
                f"src/pylint/{symbol}")


def harvest_pylint(cache, result):
    listing = github_listing(cache, "pylint", PYLINT_REPO, ["main"])
    branch = listing["branch"]
    indexes = {}
    for repo_path in (PYLINT_CORE_INDEX, PYLINT_EXTENSION_INDEX, PYLINT_OVERVIEW):
        rel = "src/pylint/" + repo_path.rsplit("/", 1)[1]
        try:
            indexes[repo_path] = cache.fetch_once(raw_url(PYLINT_REPO, branch, repo_path), rel)
        except FetchError as err:
            result.failures.append(_failure(err))
    index = pylint_index(*(indexes.get(p, "") for p in (PYLINT_CORE_INDEX, PYLINT_EXTENSION_INDEX, PYLINT_OVERVIEW)))
    messages = pylint_message_files(listing_paths(listing))
    if not messages:
        raise SourceError(f"no message directories under {PYLINT_MESSAGES} in the tree")
    jobs = [(raw_url(PYLINT_REPO, branch, p), _pylint_rel(p)) for paths in messages.values() for p in paths]
    texts, failures = fetch_all(cache, jobs)
    result.failures.extend(failures)
    for symbol, paths in sorted(messages.items()):
        files = {_pylint_rel(p).split("/", 3)[3]: texts[_pylint_rel(p)] for p in paths if _pylint_rel(p) in texts}
        if files:
            result.items.append(pylint_item(symbol, files, index, branch))
    missing = sorted(set(index.entries) - set(messages))
    if missing:
        result.notes.append(f"{len(missing)} indexed symbols have no message directory: {', '.join(missing[:10])}")


def _pylint_rel(repo_path):
    # doc/data/messages/<l>/<symbol>/<file...> -> src/pylint/<symbol>/<file...>
    return "src/pylint/" + "/".join(repo_path[len(PYLINT_MESSAGES):].split("/")[1:])


# ---------------------------------------------------------------- sonar

class _HtmlText(HTMLParser):
    BLOCKS = frozenset({"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "table", "tr",
                        "blockquote", "dl", "dt", "dd", "br"})

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.inline, self.prefix, self.pre, self.depth = [], [], "", None, 0

    def _flush(self):
        text = " ".join("".join(self.inline).split())
        if text:
            self.blocks.append(self.prefix + text)
        self.inline, self.prefix = [], ""

    def handle_starttag(self, tag, attrs):
        if self.pre is not None:
            return
        if tag == "pre":
            self._flush()
            self.pre = []
        elif tag in self.BLOCKS:
            self._flush()
            if tag in ("ul", "ol"):
                self.depth += 1
            elif tag == "li":
                self.prefix = "  " * max(self.depth - 1, 0) + "- "

    def handle_endtag(self, tag):
        if tag == "pre" and self.pre is not None:
            code = "".join(self.pre).strip("\n")
            if code.strip():
                self.blocks.append(textwrap.indent(code, "    "))
            self.pre = None
        elif self.pre is None and tag in self.BLOCKS:
            self._flush()
            if tag in ("ul", "ol"):
                self.depth = max(self.depth - 1, 0)

    def handle_data(self, data):
        (self.pre if self.pre is not None else self.inline).append(data)

    def text(self):
        self._flush()
        return "\n\n".join(self.blocks)


def html_to_text(html):
    """Paragraphs separated by blank lines, list items as `- `, `<pre>` blocks verbatim and
    indented by four spaces."""
    parser = _HtmlText()
    parser.feed(html)
    parser.close()
    return parser.text()


def sonar_item(key, meta, html, profile_keys, branch="master"):
    explanation = html_to_text(html) if html else ""
    title = meta.get("title") or ""
    return Item("sonar", key, slug(title), title, first_paragraph(explanation), explanation,
                raw_url(SONAR_REPO, branch, f"{SONAR_DIR}/{key}.html"), key in profile_keys,
                f"{meta.get('type') or ''}/{meta.get('defaultSeverity') or ''}", "stable", f"src/sonar/{key}.html")


def harvest_sonar(cache, result):
    listing = github_listing(cache, "sonar", SONAR_REPO, ["master", "main"], flat_dir=SONAR_DIR)
    branch = listing["branch"]
    names = {p.rsplit("/", 1)[1] for p in listing_paths(listing) if p.startswith(SONAR_DIR + "/")}
    keys = sorted(n[:-5] for n in names if n.endswith(".json") and not n.endswith("_profile.json"))
    if not keys:
        raise SourceError(f"no rule files under {SONAR_DIR} on {branch}")
    jobs = [(raw_url(SONAR_REPO, branch, f"{SONAR_DIR}/{SONAR_PROFILE}"), "src/sonar/" + SONAR_PROFILE)]
    jobs += [(raw_url(SONAR_REPO, branch, f"{SONAR_DIR}/{n}"), "src/sonar/" + n) for k in keys for n in (k + ".json", k + ".html") if n in names]
    texts, failures = fetch_all(cache, jobs)
    result.failures.extend(failures)
    profile_text = texts.get("src/sonar/" + SONAR_PROFILE)
    if profile_text is None:
        raise SourceError(f"{SONAR_PROFILE} could not be fetched, so default_on is unknown")
    profile_keys = set(json.loads(profile_text).get("ruleKeys", []))
    for key in keys:
        meta_text = texts.get(f"src/sonar/{key}.json")
        if meta_text is None:
            continue
        meta = json.loads(meta_text)
        if meta.get("status", "ready") != "ready":
            result.dropped[f"status:{meta['status']}"] += 1
            continue
        result.items.append(sonar_item(key, meta, texts.get(f"src/sonar/{key}.html", ""), profile_keys, branch))


# ---------------------------------------------------------------- bandit

_BANDIT_HEADING = re.compile(r"^(B\d{3})(?:\s*-\s*(B\d{3}))?: (.+)\n[-=~^]{3,}[ \t]*$", re.M)


def bandit_code_from_filename(filename):
    match = re.match(r"b(\d{3})_", os.path.basename(filename))
    return f"B{match.group(1)}" if match else ""


def bandit_stub_target(rst):
    """(module, function) an autodoc stub documents; function is None for an automodule."""
    function = re.search(r"^\.\. autofunction:: (\w+)", rst, re.M)
    current = re.search(r"^\.\. currentmodule:: ([\w.]+)", rst, re.M)
    if function and current:
        return current.group(1), function.group(1)
    module = re.search(r"^\.\. automodule:: ([\w.]+)", rst, re.M)
    return (module.group(1), None) if module else (None, None)


def python_docstring(source, function=None):
    """The docstring of `function` in the module source, or the module's own docstring; None
    when the module defines no such function. The source is parsed, never executed."""
    tree = ast.parse(source)
    if function is None:
        return ast.get_docstring(tree) or ""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function:
            return ast.get_docstring(node) or ""
    return None


_RST_ADORNMENT = re.compile(r"[=\-~^*+#]{3,}\s*")


def bandit_plugin_item(filename, rst, docstring, url, cache_path):
    """The rule a plugin page documents. Its docstring opens with the title either as a bold
    line, `**B602: Test for ...**`, or as an overlined heading, `B101: Test for ...`."""
    code = bandit_code_from_filename(filename)
    heading = re.search(r"^B\d{3}: (\w+)\s*$", rst, re.M)
    name = heading.group(1) if heading else os.path.splitext(filename)[0].split("_", 1)[-1]
    lines = docstring.strip().splitlines()
    while lines and _RST_ADORNMENT.fullmatch(lines[0]):
        lines.pop(0)
    title_line = lines.pop(0) if lines else ""
    while lines and _RST_ADORNMENT.fullmatch(lines[0]):
        lines.pop(0)
    title = re.sub(r"^\*\*|\*\*$", "", title_line.strip())
    title = re.sub(r"^B\d{3}:\s*", "", title).strip() or name
    return Item("bandit", code, name, title, first_paragraph("\n".join(lines)), docstring.strip(), url, True,
                "security", "stable", cache_path)


def bandit_blacklist_items(filename, docstring, url, cache_path):
    """One item per code under the `B<nnn>: <name>` headings of a blacklist docstring, a
    `B<nnn> - B<mmm>` heading giving every code of its range; one item with code "" when the
    docstring carries no such heading."""
    headings = list(_BANDIT_HEADING.finditer(docstring))
    stem = os.path.splitext(filename)[0]
    if not headings:
        return [Item("bandit", "", stem, first_sentence(first_paragraph(docstring, None)) or stem,
                     first_paragraph(docstring), docstring.strip(), url, True, "security", "stable", cache_path)]
    items = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(docstring)
        block = docstring[heading.end():end].strip()
        first, last = int(heading.group(1)[1:]), int((heading.group(2) or heading.group(1))[1:])
        for number in range(first, last + 1):
            code = f"B{number}"
            row = re.search(rf"^\|\s*{code}\s*\|\s*([^|]+?)\s*\|", block, re.M)
            name = row.group(1) if row else heading.group(3).strip()
            items.append(Item("bandit", code, name, first_sentence(first_paragraph(block, None)) or name,
                              first_paragraph(block), f"{heading.group(0)}\n\n{block}", url, True, "security",
                              "stable", cache_path))
    return items


def harvest_bandit(cache, result):
    listing = github_listing(cache, "bandit", BANDIT_REPO, ["main"])
    branch = listing["branch"]
    plugins_dir, blacklists_dir = BANDIT_DOC_DIRS
    stubs = [p for p in listing_paths(listing) if p.endswith(".rst") and os.path.basename(p) != "index.rst"
             and ((p.startswith(plugins_dir) and bandit_code_from_filename(p)) or p.startswith(blacklists_dir))]
    if not stubs:
        raise SourceError("no plugin or blacklist pages under doc/source/ in the tree")
    rst_rel = {p: "src/bandit/" + os.path.basename(p) for p in stubs}
    rsts, failures = fetch_all(cache, [(raw_url(BANDIT_REPO, branch, p), rst_rel[p]) for p in stubs])
    result.failures.extend(failures)
    targets = {p: bandit_stub_target(rsts[rst_rel[p]]) for p in stubs if rst_rel[p] in rsts}
    modules = sorted({module for module, _ in targets.values() if module})
    module_url = {m: raw_url(BANDIT_REPO, branch, m.replace(".", "/") + ".py") for m in modules}
    module_rel = {m: f"src/bandit/py/{m.replace('.', '/')}.py" for m in modules}
    sources, failures = fetch_all(cache, [(module_url[m], module_rel[m]) for m in modules])
    result.failures.extend(failures)
    for path, (module, function) in sorted(targets.items()):
        filename, rst = os.path.basename(path), rsts[rst_rel[path]]
        is_plugin = bool(bandit_code_from_filename(filename))
        if module is None:
            # A page without an autodoc target carries its own text; removed plugins keep such a page.
            if re.search(r"^\.\. deprecated::", rst, re.M):
                result.dropped["status:deprecated"] += 1
                continue
            text, url, cache_path = _rst_body(rst), raw_url(BANDIT_REPO, branch, path), rst_rel[path]
        elif module_rel[module] in sources:
            text = python_docstring(sources[module_rel[module]], function)
            url, cache_path = module_url[module], module_rel[module]
            if text is None:
                result.failures.append({"url": url, "status": None,
                                        "reason": f"{path} documents {function}, which {module} does not define"})
                continue
        else:
            continue
        if is_plugin:
            result.items.append(bandit_plugin_item(filename, rst, text, url, cache_path))
        else:
            result.items.extend(bandit_blacklist_items(filename, text, url, cache_path))


def _rst_body(rst):
    return re.sub(r"\A\s*[-=]{3,}\n.*\n[-=]{3,}\n", "", rst).strip()


# ---------------------------------------------------------------- bugbear

_BUGBEAR_START = re.compile(r"^\*\*(B\d{3})\*\*:\s*(.*)$")
_BUGBEAR_END = re.compile(r"^(\.\. _B\d+:|\*\*B\d{3}\*\*:)")


def bugbear_items(readme, url=BUGBEAR_URL, cache_path="src/bugbear/README.rst"):
    """One item per `**B<nnn>**: text` paragraph, which runs to the next rule's anchor or
    paragraph or the next section heading. B9xx rules are opinionated and off by default."""
    lines, items, i = readme.splitlines(), [], 0
    while i < len(lines):
        match = _BUGBEAR_START.match(lines[i])
        i += 1
        if not match:
            continue
        body = [match.group(2)]
        while i < len(lines) and not _BUGBEAR_END.match(lines[i]) and not _is_rst_heading(lines, i):
            body.append(lines[i])
            i += 1
        text = "\n".join(body).strip()
        code = match.group(1)
        items.append(Item("bugbear", code, "", first_sentence(text), first_paragraph(text), text, url,
                          not code.startswith("B9"), "bugbear", "stable", cache_path))
    return items


def _is_rst_heading(lines, i):
    return (bool(lines[i].strip()) and i + 1 < len(lines)
            and re.fullmatch(r"[=\-~^*+#]{3,}\s*", lines[i + 1]) is not None)


def harvest_bugbear(cache, result):
    readme = cache.fetch_once(BUGBEAR_URL, "src/bugbear/README.rst")
    result.items.extend(bugbear_items(readme))
    if not result.items:
        raise SourceError("no **B<nnn>**: paragraphs in the README")


# ---------------------------------------------------------------- main

def run_source(source, cache, ruff_json=None):
    """Harvest one source; its failure is recorded on the result and never stops the others."""
    result, started = SourceResult(source), time.monotonic()
    try:
        if source == "ruff":
            harvest_ruff(cache, result, ruff_json)
        else:
            {"pylint": harvest_pylint, "sonar": harvest_sonar, "bandit": harvest_bandit,
             "bugbear": harvest_bugbear}[source](cache, result)
    except (SourceError, FetchError) as err:
        result.error = str(err)
    except Exception as err:  # noqa: BLE001 - a source is the isolation point; the rest still run
        traceback.print_exc(file=sys.stderr)
        result.error = f"{type(err).__name__}: {err}"
    result.seconds = time.monotonic() - started
    return result


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", required=True)
    parser.add_argument("--only", default=",".join(SOURCES))
    parser.add_argument("--ruff-json")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    args.only = [s.strip() for s in args.only.split(",") if s.strip()]
    unknown = [s for s in args.only if s not in SOURCES]
    if unknown:
        parser.error(f"--only names unknown sources {unknown}; known: {', '.join(SOURCES)}")
    return args


def main(argv=None, fetch=http_get):
    args = parse_args(argv)
    cache = Cache(args.out, args.offline, fetch)
    results = [run_source(source, cache, args.ruff_json) for source in SOURCES if source in args.only]
    items = sorted((i for r in results for i in r.items), key=lambda i: (SOURCES.index(i.source), i.code, i.name))
    _write_atomic(os.path.join(args.out, "items.jsonl"),
                  "".join(json.dumps(dataclasses.asdict(i), ensure_ascii=False) + "\n" for i in items))
    _write_atomic(os.path.join(args.out, "summary.json"),
                  json.dumps({r.source: r.summary() for r in results}, indent=2, ensure_ascii=False) + "\n")
    for r in results:
        print(f"{r.source}: {len(r.items)} items, {sum(r.dropped.values())} dropped, "
              f"{len(r.failures)} fetch failures, {r.seconds:.1f}s" + (f", error: {r.error}" if r.error else ""))
    failed = [r for r in results if r.failed()]
    for r in failed:
        reason = r.error or f"{len(r.failures)} fetch failures, first {r.failures[0]['url']} ({r.failures[0]['status']})"
        print(f"harvest-python-sources: {r.source} failed: {reason}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
