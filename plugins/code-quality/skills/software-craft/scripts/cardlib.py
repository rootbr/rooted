"""Shared parsing for the craft-card corpus: frontmatter, the facet lists and the trigger list.

Imported by static-craft.py (the pre-pass), craft-cards.py (the developer's card index)
and validate-craft-cards.py (the validator) so the three read a card the same way.
Standard library only.
"""
import re

KEYS = ["title", "rule_id", "domain", "step", "applies_to", "triggers", "scope", "check_kind", "severity_default"]
PREFIX_DOMAIN = {"CODE": "code", "DSN": "design", "API": "interface", "ERR": "errors", "TST": "tests",
                 "CHG": "change", "PRF": "performance", "TOOL": "tooling", "DOC": "docs", "INP": "input"}
STEPS = ("design", "implement", "handle-errors", "test", "refactor", "document", "review")
APPLIES_TO = ("universal", "object-oriented", "functional", "public-api", "service-boundary", "library",
              "exceptions", "result-types", "garbage-collected", "manual-memory", "static-types", "dynamic-types",
              "tests", "build-config", "prose")
SCOPES = ("hunk", "file", "base-compare", "callers")
CHECK_KINDS = ("mechanical", "semantic")
SEVERITIES = ("major", "minor", "suggestion")
# The structural signals the pre-pass computes; a trigger `signal:<name>` names one of them.
SIGNALS = ("long_routine", "deep_nesting", "many_parameters", "boolean_argument", "empty_handler", "magic_number",
           "commented_out_code", "todo_marker", "duplicate_block", "test_file", "added_file")
EXAMPLE_LANGS = ("java", "python", "typescript", "go", "rust")
FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.S)
SIGNAL_PREFIX = "signal:"


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


def read_card(path):
    """Read one card file into its index record. Returns (record, error).

    The record is what plan.json and the developer's index carry per card: rule_id,
    path, title, domain, step, applies_to, triggers, scope, check_kind, severity_default.
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
    }
    prefix = rec["rule_id"].split("-")[0]
    if PREFIX_DOMAIN.get(prefix) != rec["domain"] and prefix != "PROJ":
        return None, f"rule_id {rec['rule_id']} does not match domain {rec['domain']!r}"
    if rec["scope"] not in SCOPES or rec["check_kind"] not in CHECK_KINDS or rec["severity_default"] not in SEVERITIES:
        return None, f"facet outside the controlled vocabulary in {path}"
    if any(s not in STEPS for s in rec["step"]) or not rec["step"]:
        return None, f"step {rec['step']} outside {STEPS} in {path}"
    if any(a not in APPLIES_TO for a in rec["applies_to"]) or not rec["applies_to"]:
        return None, f"applies_to {rec['applies_to']} outside {APPLIES_TO} in {path}"
    return rec, None
