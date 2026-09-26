#!/usr/bin/env python3
"""Mechanical validator for the craft-card corpus of the software-craft skill.

Checks every card under a directory against the corpus schema that
references/craft-cards-taxonomy.md states: frontmatter keys and their order, the
rule_id / domain / filename agreement, the controlled vocabulary of every facet
(step, applies_to, scope, check_kind, severity_default), that every trigger
compiles as a Python regular expression or names a known structural signal, the
H1 / title agreement, the seven body blocks in order, the bad:/good: example in one
of the five example languages within its line budget, the single bold validator
question, the Finding-output block naming the card's own rule_id, the Source block,
and self-containment (no sibling rule id, no deixis, no practitioner attribution,
no language named in the Thesis). Corpus-level: unique ids and titles, contiguous
numbering per domain (a gap is a warning), the example-language distribution, and —
with --provenance and --pending — one provenance line per card and no shipped id
among the pending entries.

Usage:  python3 validate-craft-cards.py [--provenance <map.md>] [--pending <pending.md>] <cards-dir> [<card.md> ...]
Reads only the files named; writes nothing; no network; stdlib only.
Exit status 0 when no error was found (warnings do not fail the run).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import (KEYS, PREFIX_DOMAIN, STEPS, APPLIES_TO, SCOPES, CHECK_KINDS, SEVERITIES,  # noqa: E402
                     EXAMPLE_LANGS, parse_inline_list, parse_frontmatter, strip_quotes, check_triggers)

BLOCKS = ["Thesis", "Rationale", "Example", "Limits", "Validator", "Finding output", "Source"]
PREFIXES = "|".join(PREFIX_DOMAIN)
FILENAME = re.compile(rf"^({PREFIXES.lower()})-(\d{{2}})--([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
RULE_ID = re.compile(rf"^({PREFIXES})-(\d{{2}})$")
ANY_RULE_ID = re.compile(rf"\b(?:{PREFIXES})-\d{{2}}\b")
BOLD_QUESTION = re.compile(r"\*\*[^*\n]+\?\*\*")
DEIXIS = re.compile(r"\b(?:the skill|this skill|see above|see below|the checklist|this checklist|as noted|as mentioned|"
                    r"sibling card|another card|the other card|earlier in this|the previous card|the next card)\b", re.I)
# Practitioner texts, their authors and the forums: a formulation source at most, never
# evidence, never named in a card. Paper authors a Source may cite are not listed.
ATTRIBUTION = re.compile(r"\b(?:McConnell|Code Complete|Pragmatic Programmer|Clean Code|Clean Architecture|Clean Coder|"
                         r"Uncle Bob|Robert C\. Martin|Ousterhout|Philosophy of Software Design|Feathers|"
                         r"Working Effectively with Legacy Code|Kernighan|Rob Pike|Practice of Programming|"
                         r"Software Engineering at Google|Winters|Manshreck|Tidy First|Kent Beck|Fowler|"
                         r"Refactoring: Improving|Seemann|Code That Fits|97 Things|Effective Java|Bloch|"
                         r"Domain-Driven Design|Eric Evans|Vernon|Nygard|Release It|Kleppmann|Baeldung|"
                         r"Medium\.com|StackOverflow|Stack Overflow|Hacker News|Lobsters|InfoQ|DZone)\b")
# A language named in the Thesis: the rule would then hold in one language, which the corpus does not card.
LANGUAGE_IN_THESIS = re.compile(r"\b(?:Java|Python|TypeScript|JavaScript|Golang|Rust|Kotlin|C#|C\+\+|Ruby|Swift)\b")
MAX_EXAMPLE_LINES = 10


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
    """Validate one card; return (rule_id, domain, title, example_language) or None."""
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
    if ":" in title:
        rep.error(path, "title carries a colon")
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
    for field, vocab in (("step", STEPS), ("applies_to", APPLIES_TO)):
        items, ierr = parse_inline_list(data.get(field, ""), bare_ok=True)
        if ierr:
            rep.error(path, f"{field}: {ierr}")
        elif not items:
            rep.error(path, f"{field} is empty")
        else:
            bad = [x for x in items if x not in vocab]
            if bad:
                rep.error(path, f"{field} {bad} not in {vocab}")
            if field == "applies_to" and "universal" in items and len(items) > 1:
                rep.error(path, "applies_to: universal stands alone")
    triggers, terr = parse_inline_list(data.get("triggers", ""))
    if terr:
        rep.error(path, f"triggers: {terr}")
    else:
        terr = check_triggers(triggers)
        if terr:
            rep.error(path, terr)
        for t in triggers:
            if "\\." in t:
                rep.error(path, f"trigger {t!r} writes a literal dot as backslash-dot; write it as [.] so the pattern never reads as a backslash path")
        if not triggers:
            rep.warn(path, "triggers is [] — this card runs on every diff")
        if len(triggers) > 8:
            rep.warn(path, f"{len(triggers)} triggers; two to six is the form")
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

    lang = ""
    ex = bt.get("Example", "")
    fences = fenced(ex)
    if len(fences) != 1:
        rep.error(path, f"Example must hold exactly one fenced block, found {len(fences)}")
    else:
        info, lines = fences[0]
        lang = info
        if info not in EXAMPLE_LANGS:
            rep.error(path, f"Example fence must be tagged one of {EXAMPLE_LANGS}, found ```{info}")
        joined = "\n".join(lines)
        if not re.search(r"^\s*bad:", joined, re.M) or not re.search(r"^\s*good:", joined, re.M):
            rep.error(path, "Example needs a 'bad:' line and a 'good:' line")
        if len(lines) > MAX_EXAMPLE_LINES:
            rep.error(path, f"Example has {len(lines)} lines; the cap is {MAX_EXAMPLE_LINES}")
        if re.search(r"^[+-](?![+-])", joined, re.M):
            rep.error(path, "Example carries diff markers")
    if re.sub(r"```.*?```", "", ex, flags=re.S).strip():
        rep.warn(path, "Example carries prose outside the fence")

    thesis = bt.get("Thesis", "")
    lm = LANGUAGE_IN_THESIS.search(thesis)
    if lm:
        rep.error(path, f"Thesis names a language ({lm.group(0)!r}); a rule that holds in one language belongs to a language-specific corpus")

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
    return rule_id, domain, title, lang


def check_corpus(cards, rep, provenance=None, pending=None):
    seen_ids, seen_titles, per_domain, langs = {}, {}, {}, {}
    for path, (rid, domain, title, lang) in cards.items():
        if rid in seen_ids:
            rep.error(path, f"duplicate rule_id {rid} (also {seen_ids[rid]})")
        seen_ids[rid] = path
        if title in seen_titles:
            rep.error(path, f"duplicate title (also {seen_titles[title]})")
        seen_titles[title] = path
        m = RULE_ID.match(rid)
        if m:
            per_domain.setdefault(m.group(1), []).append(int(m.group(2)))
        langs[lang] = langs.get(lang, 0) + 1
    for prefix, nums in per_domain.items():
        nums = sorted(nums)
        missing = sorted(set(range(1, nums[-1] + 1)) - set(nums))
        if missing:
            rep.warn(f"{prefix}", f"numbering gap(s) {missing} — ids count shipped cards only, contiguous per domain")
    total = sum(langs.values())
    if total >= 10:
        for lang in EXAMPLE_LANGS:
            share = langs.get(lang, 0) / total
            if share > 1 / 3:
                rep.warn("corpus", f"example language {lang} carries {langs.get(lang, 0)} of {total} cards ({share:.0%}); the cap is a third")
            if share < 0.1:
                rep.warn("corpus", f"example language {lang} carries {langs.get(lang, 0)} of {total} cards ({share:.0%}); the floor is a tenth")
    if provenance:
        ptext = open(provenance, encoding="utf-8").read()
        for rid, path in seen_ids.items():
            if not re.search(rf"^- \*\*{re.escape(rid)}\*\*", ptext, re.M):
                rep.error(path, f"no provenance line '- **{rid}**' in {os.path.basename(provenance)}")
    if pending:
        ptext = open(pending, encoding="utf-8").read()
        for rid, path in seen_ids.items():
            if re.search(rf"^- \*\*{re.escape(rid)}\*\*|rule_id:\s*{re.escape(rid)}\b", ptext, re.M):
                rep.error(path, f"{rid} is both a shipped card and a pending-evidence entry")
    return langs


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
    langs = check_corpus(cards, rep, provenance, pending)
    for w in rep.warnings:
        print(w)
    for e in rep.errors:
        print(e)
    dist = ", ".join(f"{k or '?'} {v}" for k, v in sorted(langs.items(), key=lambda kv: -kv[1]))
    print(f"validate-craft-cards: {len(files)} card(s), {len(rep.errors)} error(s), {len(rep.warnings)} warning(s); example languages: {dist or 'none'}")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
