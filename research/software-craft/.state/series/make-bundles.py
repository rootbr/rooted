#!/usr/bin/env python3
"""Validate the series topic objects against the design note's taxonomy table and write one
research-workflow bundle per topic (EMBEDDED_ARGS after `meta`), so a Workflow call names only a
script path. Usage: make-bundles.py [--only slug,slug] [--existing-titles-from <cards-dir>] topics-*.json"""
import json, os, re, sys, importlib.util
ROOT = "/home/user/rooted"
SKILL = f"{ROOT}/plugins/code-quality/skills/software-craft"
spec = importlib.util.spec_from_file_location("rc", f"{SKILL}/scripts/research-continue.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
NOTE = open(f"{ROOT}/research/2026-09-26_software-craft-cards.md", encoding="utf-8").read()
tax, cur = {}, None
for full, dom, pre, slug, con in re.findall(r"^\| ((?:[A-J]), `(\w+)`, `(\w+)`)? *\| `([a-z0-9-]+)`( \(contested\))? \|", NOTE, re.M):
    if dom: cur = (dom, pre, full[0])
    tax[slug] = {"domain": cur[0], "prefix": cur[1], "letter": cur[2], "contested": bool(con)}
CHANNEL_NOTE = ("the WebSearch tool answers every call with 'this session has used its web search budget (200 of 200 WebSearch calls)'; "
    "do not call it, and treat a paper as reachable only where a GitHub-hosted copy or a GitHub-hosted page quoting it exists. Openable paper channels: "
    "the topic's candidate_evidence items marked 'relayed by the orchestrator's search' carry a search snippet and its URL that you may quote as relayed; "
    "raw.githubusercontent.com/neverworkintheory/neverworkintheory.github.io/main/ (the source of neverworkintheory.org, one Markdown post per reviewed paper with its abstract and DOI; list the tree through the repository's README or guess the post path from the URL of the review); "
    "raw.githubusercontent.com/ligurio/swebok-v3/master/3_software_construction.md (the SWEBOK V3 Software Construction chapter, HTTP 200); "
    "raw.githubusercontent.com/abseil/abseil.github.io/master/resources/swe-book/html/chNN.html (Software Engineering at Google, CC BY-NC-ND, all chapters); "
    "raw.githubusercontent.com/papers-we-love/papers-we-love/master/<area>/README.md (paper lists with links, some PDFs in-tree); "
    "an author's GitHub Pages site as raw.githubusercontent.com/<user>/<user>.github.io/<branch>/<path> when a candidate names one; "
    "raw.githubusercontent.com/tpn/pdfs/master/<title>.pdf (a mirror of some classic papers, e.g. the Nagappan TDD study). "
    "A paper reached only through one of these is 'fetched' when you opened the text that states the claim and 'relayed' when only the orchestrator's snippet states it; a paper reached through neither is 'unfetched' and never a card's only anchor.")
KEYS = ["slug", "title", "group", "domain", "prefix", "locators", "candidate_evidence", "contested", "notes"]

def titles_in(cards_dir, prefix):
    out = []
    if not os.path.isdir(cards_dir): return out
    for fn in sorted(os.listdir(cards_dir)):
        txt = open(os.path.join(cards_dir, fn), encoding="utf-8").read()
        m = re.search(r"^rule_id: (\w+)-\d+", txt, re.M); t = re.search(r"^title: (.+)$", txt, re.M)
        if m and t and m.group(1) == prefix: out.append(t.group(1).strip())
    return out

def main(argv):
    only, cards_dir, files = None, f"{SKILL}/references/craft-cards", []
    i = 0
    while i < len(argv):
        if argv[i] == "--only": only = set(argv[i + 1].split(",")); i += 2
        elif argv[i] == "--existing-titles-from": cards_dir = argv[i + 1]; i += 2
        else: files.append(argv[i]); i += 1
    topics = []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        topics += d if isinstance(d, list) else [d]
    problems, out_dir = [], f"{os.path.dirname(os.path.abspath(__file__))}/bundles"
    os.makedirs(out_dir, exist_ok=True)
    script = open(f"{SKILL}/scripts/research-topic-workflow.js", encoding="utf-8").read()
    seen = set()
    for n, t in enumerate(topics):
        s = t.get("slug")
        if list(t.keys()) != KEYS: problems.append(f"{s}: keys {list(t.keys())}")
        if s not in tax: problems.append(f"{s}: not in the taxonomy table"); continue
        if s in seen: problems.append(f"{s}: duplicate")
        seen.add(s)
        row = tax[s]
        for k in ("domain", "prefix"):
            if t.get(k) != row[k]: problems.append(f"{s}: {k} {t.get(k)!r} != {row[k]!r}")
        if bool(t.get("contested")) != row["contested"]: problems.append(f"{s}: contested {t.get('contested')} != {row['contested']}")
        if not t.get("group", "").startswith(row["letter"] + "."): problems.append(f"{s}: group {t.get('group')!r} not letter {row['letter']}")
        ce = t.get("candidate_evidence", [])
        if not (5 <= len(ce) <= 12): problems.append(f"{s}: {len(ce)} candidate_evidence items")
        if "legacy" in (s + t.get("title", "")).lower(): problems.append(f"{s}: 'legacy' in slug/title")
        for k in ("locators", "notes", "title"):
            if not isinstance(t.get(k), str) or len(t[k]) < 20 and k != "title": problems.append(f"{s}: {k} short or missing")
    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems)); return 1 if any("not in the taxonomy" in p or "keys" in p for p in problems) else 0
    for n, t in enumerate(topics):
        if only and t["slug"] not in only: continue
        args = {"root": ROOT, "topic": t, "next_id": 1, "existing_titles": titles_in(cards_dir, t["prefix"]),
                "max_rules": 12, "rotation_start": n % 5, "channel_note": CHANNEL_NOTE}
        path = os.path.join(out_dir, f"{t['slug']}.js")
        open(path, "w", encoding="utf-8").write(rc.bundle(script, args))
        print(f"{path}: {os.path.getsize(path)} bytes, {len(args['existing_titles'])} existing title(s), rotation {n % 5}")
    missing = sorted(set(tax) - seen - {"naming-identifiers", "error-and-exception-handling", "test-doubles"})
    print(f"{len(seen)} topic(s) validated; not covered: {missing or 'none'}")
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
