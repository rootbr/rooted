"""Shared parsing for the review-card corpus: frontmatter and the trigger list.

Imported by static-review.py (the pre-pass) and validate-review-cards.py (the
validator) so the two read a card the same way. Standard library only.
"""
import re

KEYS = ["title", "rule_id", "domain", "triggers", "scope", "check_kind", "severity_default"]
PREFIX_DOMAIN = {"CC": "concurrency", "SEC": "security", "PF": "performance",
                 "REL": "reliability", "MNT": "maintainability", "META": "meta"}
SCOPES = ("hunk", "file", "base-compare", "callers")
CHECK_KINDS = ("mechanical", "semantic")
SEVERITIES = ("critical", "major", "minor", "suggestion")
FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.S)


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
