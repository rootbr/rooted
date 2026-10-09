#!/usr/bin/env python3
"""Build one research-workflow bundle per domain from the queued gap runs of gap-runs.json: the concepts the
domain reviewers found with no card, no pending entry and an openable source, grouped by domain into a topic
object `gaps-<domain>` whose spine proposes one candidate rule per concept and no other. Each bundle runs the
full workflow (sources, spine, one drafter and one skeptic per rule, fix, second verdict, closing edit); its
round 2 comes from the journal as for any topic (HANDOVER §5.3 with --round 2), and the writer puts its
cards, note (research/software-craft/gaps-<domain>.md), provenance lines and pending entries in the tree.
Usage: make-gap-bundles.py [--out-dir <dir>] [--only domain,domain] [--print]
  --print  show the topic objects and write nothing
Grouping by domain is the orchestrator's choice (one sources phase per domain instead of one per concept);
a domain with one concept still gets its own run. Standard library only."""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SKILL = f"{ROOT}/plugins/code-quality/skills/software-craft"
_spec = importlib.util.spec_from_file_location("make_bundles", os.path.join(HERE, "make-bundles.py"))
mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mb)
GROUPS = {"code": "A. Code inside a function", "design": "B. Module design", "interface": "C. Interfaces", "errors": "D. Errors and resilience",
          "tests": "E. Tests", "change": "F. Changing code", "performance": "G. Diagnostics and performance", "tooling": "H. Tools and hygiene",
          "docs": "I. Reading and documenting", "input": "J. Input and security hygiene"}
PREFIX = {"code": "CODE", "design": "DSN", "interface": "API", "errors": "ERR", "tests": "TST", "change": "CHG", "performance": "PRF",
          "tooling": "TOOL", "docs": "DOC", "input": "INP"}


def topic_objects():
    runs = json.load(open(os.path.join(HERE, "gap-runs.json"), encoding="utf-8"))["runs"]
    by = {}
    for r in runs:
        if r.get("status") != "queued" or not r.get("source_path"):
            continue
        by.setdefault(r["domain"], []).append(r)
    topics = []
    for domain, rs in by.items():
        rows, locs = [], {}
        for r in rs:
            m = re.search(r"`([a-z0-9-]+)`(?: \(contested\))? *\| *([^|]*?) *\|\s*$", r.get("taxonomy_row") or "")
            rows.append(m.group(1) if m else None)
            if m:
                locs[m.group(1)] = m.group(2).strip()
        ce = [f"{r['concept'].strip()} — source: {r['source_path'].strip()} — claim: {(r['claim'] or '').strip()}"
              + (f" — taxonomy topic: {t}" if t else "") for r, t in zip(rs, rows)]
        locators = ("the taxonomy topics of the concepts and their canon locators: " + "; ".join(f"{s} ({l})" for s, l in sorted(locs.items()))) if locs \
            else "no canon chapter of its own; the concepts come from the domain reviewer's reading of the corpus"
        concepts = "; ".join(f"({i + 1}) {r['concept'].strip().split('.')[0].split(':')[0]}" for i, r in enumerate(rs))
        topics.append({
            "slug": f"gaps-{domain}",
            "title": f"Concepts the {domain} reviewer found uncovered",
            "group": GROUPS[domain], "domain": domain, "prefix": PREFIX[domain],
            "locators": locators,
            "candidate_evidence": ce,
            "contested": False,
            "notes": (f"This topic holds the {len(rs)} concept(s) the {domain}-domain reviewer found in the corpus with no card and no pending "
                      f"entry, each with an openable source the reviewer named: {concepts}. The spine proposes exactly one candidate rule per "
                      "concept in candidate_evidence, resting on the named source and on what the three layers find for that concept, and "
                      "proposes no rule beyond them; a concept whose claim no openable source states as a checkable rule is held with its "
                      "search recorded. Every rule is checked against the titles in existing_titles so that no existing card is written "
                      "twice, and a rule that only narrows an existing card is held as folded into it. Each concept names the taxonomy "
                      "topic it belongs to; the card's provenance line names this topic."),
        })
    return topics


def main(argv):
    out_dir, only, show = os.path.join(HERE, "bundles"), None, False
    i = 0
    while i < len(argv):
        if argv[i] == "--out-dir": out_dir = os.path.abspath(argv[i + 1]); i += 2
        elif argv[i] == "--only": only = set(argv[i + 1].split(",")); i += 2
        elif argv[i] == "--print": show = True; i += 1
        else: sys.exit(f"make-gap-bundles: unexpected argument {argv[i]!r}")
    topics = [t for t in topic_objects() if not only or t["domain"] in only]
    if show:
        print(json.dumps(topics, indent=1, ensure_ascii=False)); return 0
    os.makedirs(out_dir, exist_ok=True)
    script = open(f"{SKILL}/scripts/research-topic-workflow.js", encoding="utf-8").read()
    cards_dir = f"{SKILL}/references/craft-cards"
    for n, t in enumerate(topics):
        args = {"root": ROOT, "topic": t, "next_id": 1, "existing_titles": mb.titles_in(cards_dir, t["prefix"]),
                "max_rules": max(12, len(t["candidate_evidence"])), "rotation_start": n % 5, "channel_note": mb.CHANNEL_NOTE, "closing_edit": True}
        path = os.path.join(out_dir, f"{t['slug']}.js")
        open(path, "w", encoding="utf-8").write(mb.rc.bundle(script, args))
        print(f"{path}: {len(t['candidate_evidence'])} concept(s), {os.path.getsize(path)} bytes, {len(args['existing_titles'])} existing title(s), rotation {n % 5}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
