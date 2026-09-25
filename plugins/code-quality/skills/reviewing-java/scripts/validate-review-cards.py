#!/usr/bin/env python3
"""Mechanical validator for the review-card corpus of the reviewing-java skill.

Checks every card under a directory against the corpus schema that
references/review-cards-taxonomy.md states: frontmatter keys and their order,
the rule_id ↔ domain ↔ filename agreement, the controlled vocabulary of every
facet, that every trigger compiles as a Python regular expression, the H1 ↔
title agreement, the seven body blocks in order, the Java bad:/good: example
within its line budget, the single bold validator question, the Finding-output
block naming the card's own rule_id, the Source block, and self-containment
(no sibling rule id, no deixis, no practitioner attribution). Corpus-level:
unique ids and titles, contiguous numbering per domain (a gap is a warning),
and — with --provenance — one provenance line per card.

Usage:  python3 validate-review-cards.py [--provenance <map.md>] [--pending <pending.md>] <cards-dir> [<card.md> ...]
Reads only the files named; writes nothing; no network; stdlib only.
Exit status 0 when no error was found (warnings do not fail the run).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import (KEYS, PREFIX_DOMAIN, SCOPES, CHECK_KINDS, SEVERITIES,  # noqa: E402
                     parse_inline_list, parse_frontmatter, strip_quotes)

BLOCKS = ["Thesis", "Rationale", "Example", "Limits", "Validator", "Finding output", "Source"]
FILENAME = re.compile(r"^(cc|sec|pf|rel|mnt|meta)-(\d{2})--([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
RULE_ID = re.compile(r"^(CC|SEC|PF|REL|MNT|META)-(\d{2})$")
ANY_RULE_ID = re.compile(r"\b(?:CC|SEC|PF|REL|MNT|META)-\d{2}\b")
BOLD_QUESTION = re.compile(r"\*\*[^*\n]+\?\*\*")
DEIXIS = re.compile(r"\b(?:the skill|this skill|see above|see below|the checklist|this checklist|as noted|as mentioned|"
                    r"sibling card|another card|the other card|earlier in this|the previous card|the next card)\b", re.I)
# Practitioner texts and blogs: a formulation source at most, never evidence, never named in a card.
ATTRIBUTION = re.compile(r"\b(?:Goetz|JCIP|Java Concurrency in Practice|Bloch|Effective Java|Oaks|Visser|"
                         r"Uncle Bob|Robert C\. Martin|Clean Code|Clean Architecture|Fowler|Nygard|Release It|"
                         r"Kleppmann|DDIA|Herlihy|Shavit|Shipilev|Baeldung|Mihalcea|Vernon|Evans|Hombergs|"
                         r"Beck|Tidy First|Glass|Hickey|Lea, Doug|Doug Lea|Cohen|Kahneman|Armstrong|Pressler|"
                         r"Bateman|Tene|Thompson|Cashfree|Netflix|InfoQ|DZone|Medium\.com|StackOverflow|Stack Overflow)\b")
MAX_EXAMPLE_LINES = 10  # "up to about eight" with room for a wrapped good: half


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, msg):
        self.errors.append(f"{path}: error: {msg}")

    def warn(self, path, msg):
        self.warnings.append(f"{path}: warning: {msg}")


def split_blocks(body):
    """Return list of (heading, text, line_no) for H2 blocks; text before the first H2 in heading ''."""
    blocks, cur, buf, start = [], "", [], 1
    for i, line in enumerate(body.split("\n"), 1):
        if line.startswith("## "):
            blocks.append((cur, "\n".join(buf), start))
            cur, buf, start = line[3:].strip(), [], i
            continue
        buf.append(line)
    blocks.append((cur, "\n".join(buf), start))
    return blocks


def fenced(text):
    """Return the list of fenced code blocks as (info, lines)."""
    out, in_fence, info, lines = [], False, "", []
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            if in_fence:
                out.append((info, lines))
                in_fence, info, lines = False, "", []
            else:
                in_fence, info = True, line.strip()[3:].strip()
            continue
        if in_fence:
            lines.append(line)
    return out


def check_card(path, rep):
    """Validate one card; return its (rule_id, domain, title) or None."""
    name = os.path.basename(path)
    fm = FILENAME.match(name)
    if not fm:
        rep.error(path, "filename is not <prefix>-NN--<slug>.md")
    text = open(path, encoding="utf-8").read()
    keys, data, err = parse_frontmatter(text)
    if err:
        rep.error(path, err)
        return None
    if keys != KEYS:
        rep.error(path, f"frontmatter keys {keys} must be exactly {KEYS} in that order")
    title = strip_quotes(data.get("title", ""))
    rule_id = data.get("rule_id", "").strip()
    domain = data.get("domain", "").strip()
    if not title:
        rep.error(path, "empty title")
    if title.endswith("."):
        rep.error(path, "title ends with a period")
    if "?" in title:
        rep.error(path, "title is a question, not a claim")
    rm = RULE_ID.match(rule_id)
    if not rm:
        rep.error(path, f"rule_id {rule_id!r} is not <PREFIX>-NN")
    else:
        if PREFIX_DOMAIN[rm.group(1)] != domain:
            rep.error(path, f"rule_id prefix {rm.group(1)} does not match domain {domain!r}")
        if fm and (fm.group(1).upper() != rm.group(1) or fm.group(2) != rm.group(2)):
            rep.error(path, f"filename {name} does not match rule_id {rule_id}")
    if domain not in PREFIX_DOMAIN.values():
        rep.error(path, f"domain {domain!r} not in {sorted(PREFIX_DOMAIN.values())}")
    triggers, terr = parse_inline_list(data.get("triggers", ""))
    if terr:
        rep.error(path, terr)
    else:
        for t in triggers:
            try:
                re.compile(t)
            except re.error as e:
                rep.error(path, f"trigger {t!r} does not compile: {e}")
            if "\\." in t:
                rep.error(path, f"trigger {t!r} writes a literal dot as backslash-dot; write it as [.] so the pattern never reads as a backslash path")
        if not triggers:
            rep.warn(path, "triggers is [] — this card runs on every diff")
    for field, vocab in (("scope", SCOPES), ("check_kind", CHECK_KINDS), ("severity_default", SEVERITIES)):
        if data.get(field, "").strip() not in vocab:
            rep.error(path, f"{field} {data.get(field)!r} not in {vocab}")

    body = text[len(re.match(r"---\n.*?\n---\n", text, re.S).group(0)):]
    h1 = re.search(r"^# (.+)$", body, re.M)
    if not h1:
        rep.error(path, "missing H1")
    elif h1.group(1).strip() != title:
        rep.error(path, "H1 differs from the frontmatter title")
    if re.search(r"^#{3,} ", body, re.M):
        rep.error(path, "a heading deeper than H2 is present")
    blocks = split_blocks(body)
    pre = blocks[0][1]
    if re.sub(r"^# .+$", "", pre, flags=re.M).strip():
        rep.error(path, "text between the H1 and '## Thesis'")
    heads = [h for h, _, _ in blocks[1:]]
    if heads != BLOCKS:
        rep.error(path, f"body blocks {heads} must be exactly {BLOCKS} in that order")
    bt = {h: t for h, t, _ in blocks[1:]}
    for h in BLOCKS:
        if h in bt and not bt[h].strip():
            rep.error(path, f"block '{h}' is empty")

    ex = bt.get("Example", "")
    fences = fenced(ex)
    if len(fences) != 1:
        rep.error(path, f"Example must hold exactly one fenced block, found {len(fences)}")
    else:
        info, lines = fences[0]
        if info != "java":
            rep.error(path, f"Example fence must be ```java, found ```{info}")
        joined = "\n".join(lines)
        if not re.search(r"^\s*bad:", joined, re.M) or not re.search(r"^\s*good:", joined, re.M):
            rep.error(path, "Example needs a 'bad:' line and a 'good:' line")
        if len(lines) > MAX_EXAMPLE_LINES:
            rep.error(path, f"Example has {len(lines)} lines; the budget is about eight (hard cap {MAX_EXAMPLE_LINES})")
    if ex.replace("```", "").strip() and re.sub(r"```.*?```", "", ex, flags=re.S).strip():
        rep.warn(path, "Example carries prose outside the fence")

    val = bt.get("Validator", "")
    qs = BOLD_QUESTION.findall(val)
    if len(qs) == 0:
        rep.error(path, "Validator has no bold question ending in '?'")
    elif len(qs) > 1:
        rep.warn(path, f"Validator has {len(qs)} bold questions; one binary question is the form")

    fo = bt.get("Finding output", "")
    if rule_id and f"rule_id: {rule_id}" not in fo:
        rep.error(path, f"Finding output does not name `rule_id: {rule_id}`")
    if fo.count("## ") > 0:
        rep.error(path, "Finding output holds a nested heading")

    src = bt.get("Source", "")
    if ATTRIBUTION.search(src):
        rep.error(path, f"Source names a practitioner text ({ATTRIBUTION.search(src).group(0)!r}); cite the openable evidence and put the formulation in the provenance map")

    prose = "\n".join(bt.get(h, "") for h in BLOCKS if h != "Source")
    others = {m for m in ANY_RULE_ID.findall(prose + src) if m != rule_id}
    if others:
        rep.error(path, f"names sibling rule id(s) {sorted(others)} — a card is self-contained")
    dm = DEIXIS.search(prose)
    if dm:
        rep.error(path, f"deixis {dm.group(0)!r} in the body")
    am = ATTRIBUTION.search(prose)
    if am:
        rep.error(path, f"attribution {am.group(0)!r} in the body; the prose stays attribution-free")
    caps = re.findall(r"\b(MUST NOT|MUST|NEVER|ALWAYS|ONLY|SHALL)\b", prose)
    if len(caps) > 3:
        rep.error(path, f"{len(caps)} ALL-CAPS markers; at most three")
    return rule_id, domain, title


def check_corpus(cards, rep, provenance=None, pending=None):
    seen_ids, seen_titles, per_domain = {}, {}, {}
    for path, (rid, domain, title) in cards.items():
        if rid in seen_ids:
            rep.error(path, f"duplicate rule_id {rid} (also {seen_ids[rid]})")
        seen_ids[rid] = path
        if title in seen_titles:
            rep.error(path, f"duplicate title (also {seen_titles[title]})")
        seen_titles[title] = path
        m = RULE_ID.match(rid)
        if m:
            per_domain.setdefault(m.group(1), []).append(int(m.group(2)))
    for prefix, nums in per_domain.items():
        nums = sorted(nums)
        missing = sorted(set(range(1, nums[-1] + 1)) - set(nums))
        if missing:
            rep.warn(f"{prefix}", f"numbering gap(s) {missing} — ids count shipped cards only, contiguous per domain")
    if provenance:
        ptext = open(provenance, encoding="utf-8").read()
        for rid, path in seen_ids.items():
            if not re.search(rf"^- \*\*{re.escape(rid)}\*\*", ptext, re.M):
                rep.error(path, f"no provenance line '- **{rid}**' in {os.path.basename(provenance)}")
    if pending:
        ptext = open(pending, encoding="utf-8").read()
        for rid, path in seen_ids.items():
            if re.search(rf"\b{re.escape(rid)}\b", ptext):
                rep.error(path, f"{rid} is both a shipped card and a pending-evidence entry")


def main(argv):
    provenance = pending = None
    paths = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--provenance":
            provenance = argv[i + 1]
            i += 2
            continue
        if a == "--pending":
            pending = argv[i + 1]
            i += 2
            continue
        paths.append(a)
        i += 1
    if not paths:
        sys.exit(__doc__)
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith(".md"))
        else:
            files.append(p)
    rep = Report()
    cards = {}
    for f in files:
        r = check_card(f, rep)
        if r:
            cards[f] = r
    check_corpus(cards, rep, provenance, pending)
    for w in rep.warnings:
        print(w)
    for e in rep.errors:
        print(e)
    print(f"validate-review-cards: {len(files)} card(s), {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
