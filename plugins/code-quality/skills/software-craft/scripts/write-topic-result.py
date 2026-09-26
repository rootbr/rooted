#!/usr/bin/env python3
"""Write one research-topic run into the tree: the research note, the cards, the
provenance lines and the pending entries.

The research workflow (scripts/research-topic-workflow.js) writes no files; it returns
its material, and this script turns a run's return value into files. Input is the
Workflow tool's task output (a JSON object whose "result" key holds the return value
and whose "workflowProgress" key holds the per-agent token counts), or the bare return
value.

Usage:  python3 write-topic-result.py --run <run.json> --root <repo root> [--status verified]
                                     [--cards-dir <dir>] [--provenance <map.md>] [--pending <pending.md>]
                                     [--notes-dir research/software-craft] [--dry-run]
Ids are renumbered contiguously per domain from the cards already in the cards
directory, so a rule that went to pending leaves no gap; every occurrence of a card's
provisional id in its markdown, its filename and its provenance line is replaced.
Writes exactly the note, the cards and the two appended maps; stdlib only.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, ".."))
DOMAIN_ORDER = ["code", "design", "interface", "errors", "tests", "change", "performance", "tooling", "docs", "input"]
DOMAIN_TITLES = {"code": "CODE — code inside a function", "design": "DSN — module design", "interface": "API — interfaces",
                 "errors": "ERR — errors and resilience", "tests": "TST — tests", "change": "CHG — changing code",
                 "performance": "PRF — diagnostics and performance", "tooling": "TOOL — tools and hygiene",
                 "docs": "DOC — reading and documenting", "input": "INP — input and security hygiene"}
PROVENANCE_HEADER = """# Craft-cards provenance map

Out-of-runtime maintainer record. Neither consumer receives this file: a card carries the rule, its numbers and a compact `## Source` locator; this map carries the full citation with its fetch status, the topic and research note the card came from, the formulation source where a practitioner text supplied the wording, the reception, and the maintenance notes. Round-trip rule: a card plus its line here plus its topic's research note reconstruct everything known about the rule.

One line per card: `rule_id · evidence citation(s) with fetch status and the quoted statement · topic (research note) · formulation source · reception · notes` (evidence strength, ownership, caveats).

Fetch status per citation, as the design note's source policy defines it: `fetched` — opened from the authoring environment and quoted; **relayed** — the search index's statement of the claim, quoted, the paper itself unopened; **unfetched** — cited from memory, never a card's only anchor. A relayed or unfetched citation is openable by any reader and stands to be re-verified.

---
"""
PENDING_HEADER = """# Pending evidence — rules held back

A rule listed here has no card and no id. It ships when an admissible source — academic research with an arXiv id or DOI, a technical standard or official documentation by section, or verified hands-on experience in an openable form — is found to state the claim as the rule words it, or, for a contested rule, when a sourced condition separates the cases. Each entry keeps the rule's original wording, its topic, its formulation source, what was searched and what would unblock it, so the next search starts where the last one stopped.

Entry shape: `domain · topic slug · original wording · formulation · searched · what would unblock`; a contested rule without a separating condition begins with `no separating condition ·` and lists both positions.

---
"""


def load_run(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict) and "cards" in data["result"]:
        return data["result"], data.get("workflowProgress") or []
    return data, []


def cost_line(progress, result):
    agents = [p for p in progress if p.get("type") == "workflow_agent"]
    tokens = sum(int(p.get("tokens") or 0) for p in agents)
    starts = [p.get("queuedAt") or p.get("startedAt") for p in agents if p.get("queuedAt") or p.get("startedAt")]
    ends = [p.get("lastProgressAt") for p in agents if p.get("lastProgressAt")]
    wall = (max(ends) - min(starts)) // 1000 if starts and ends else None
    n = len(agents) or (result.get("cost") or {}).get("agents_run", 0)
    parts = [f"agents run: {n}"]
    if tokens:
        parts.append(f"sub-agent tokens: {tokens:,}")
    if wall is not None:
        parts.append(f"wall-clock: {wall} s")
    return "; ".join(parts)


def existing_max(cards_dir, prefix):
    mx = 0
    if os.path.isdir(cards_dir):
        for name in os.listdir(cards_dir):
            m = re.match(rf"^{prefix.lower()}-(\d{{2}})--", name)
            if m:
                mx = max(mx, int(m.group(1)))
    return mx


def renumber(card, old_id, new_id):
    """Replace the provisional id everywhere in the card, its filename and its provenance line."""
    md = card["markdown"].replace(old_id, new_id)
    fn = re.sub(rf"^{old_id.split('-')[0].lower()}-\d{{2}}--", f"{new_id.split('-')[0].lower()}-{new_id.split('-')[1]}--", card["filename"])
    return md, fn


def note_markdown(result, status, cost, written, pendings):
    t = result["topic"]
    spine = result.get("spine") or {}
    out = [f"---\ntopic: {t['slug']}\ntitle: {t['title']}\ngroup: {t['group']}\ndomain: {t['domain']}\nprefix: {t['prefix']}\nstatus: {status}\n---\n",
           f"# Research note — {t['title']}\n",
           f"Topic `{t['slug']}` of group {t['group']}, domain `{t['domain']}`, id prefix `{t['prefix']}`. Formulation locators: {t.get('locators') or 'none in the canon; researched from the evidence layer'}.{' Marked contested in the design note.' if t.get('contested') else ''}\n",
           spine.get("summary", ""), ""]
    for layer in result.get("sources") or []:
        out += [f"## {layer['layer'].capitalize()} layer", "", layer.get("summary", ""), "",
                "| Claim | Source · locator | Status · class | Quote | Notes |", "|--|--|--|--|--|"]
        for it in layer.get("items", []):
            out.append("| " + " | ".join(esc(x) for x in (it["claim"], f"{it['source']} · {it['locator']}" + (f" · {it['url']}" if it.get("url") else ""),
                                                            f"{it['fetch_status']} · {it['admissible_class']}" + (" · contested" if it.get("contested") else ""),
                                                            it["quote"], it["notes"])) + " |")
        out.append("")
    out += ["## Spine — candidate rules in source order", ""]
    for i, r in enumerate(spine.get("rules", []), 1):
        ev = "; ".join(f"{e['source']} — {e['locator']} ({e['fetch_status']}, {e['admissible_class']})" for e in r.get("evidence", [])) or "none found"
        rec = ("contested — " + " / ".join(f"{p['side']} ({p['holder']}): {p['statement']}; evidence: {p['evidence']}" for p in r.get("positions", []))
               + (f"; separating condition: {r['separating_condition']}" if r.get("separating_condition") else "")) if r.get("contested") else "not contested"
        out += [f"{i}. **{r['title']}** — {r['statement']}",
                f"   - formulation: {'; '.join(r.get('formulation') or []) or 'none named'}",
                f"   - reception: {rec}",
                f"   - evidence: {ev}",
                f"   - disposition: {r['disposition']}" + (f" — {r['hold_reason']}" if r.get("hold_reason") else "") + (f"; searched: {r['searched']}" if r.get("searched") else ""),
                f"   - facets: step {r.get('step')}, applies_to {r.get('applies_to')}, triggers {r.get('triggers')}, scope {r.get('scope')}, {r.get('check_kind')}, {r.get('severity_default')}"]
    if spine.get("dropped"):
        out += ["", "Source items that yielded no rule:", ""] + [f"- {d}" for d in spine["dropped"]]
    out += ["", "## Cards derived", ""]
    if written:
        out += ["| Rule id | Title | Card | Verification |", "|--|--|--|--|"]
        for w in written:
            out.append(f"| {w['rule_id']} | {esc(w['title'])} | `references/craft-cards/{w['filename']}` | {esc(w['verification'])} |")
    else:
        out.append("No card shipped from this topic.")
    out += ["", "## Rules held back", ""]
    if pendings:
        out += [f"- {esc(p['key'])} — {p['reason']}: {p['entry'][2:] if p['entry'].startswith('- ') else p['entry']}" for p in pendings]
    else:
        out.append("None.")
    held = [h for h in result.get("held", []) if h["disposition"] in ("held-not-checkable", "folded", "held-cap")]
    if held:
        out += ["", "Held without a pending entry (no checkable form on a diff, or folded into a sibling rule):", ""]
        out += [f"- {h['title']} — {h['disposition']}: {h['hold_reason']}" for h in held]
    out += ["", "## Cost", "", f"- {cost}", ""]
    return "\n".join(out)


def esc(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def append_under(path, header, section_title, lines, dry):
    text = open(path, encoding="utf-8").read() if os.path.isfile(path) else header
    heading = f"## {section_title}"
    if heading not in text:
        # keep the domain sections in the corpus order
        sections = re.split(r"(?m)^(?=## )", text)
        head, rest = sections[0], sections[1:]
        rest.append(f"{heading}\n\n")
        order = {f"## {DOMAIN_TITLES[d]}": i for i, d in enumerate(DOMAIN_ORDER)}
        rest.sort(key=lambda s: order.get(s.split("\n", 1)[0].strip(), 99))
        text = head + "".join(s if s.endswith("\n\n") else s.rstrip("\n") + "\n\n" for s in rest)
    idx = text.index(heading)
    nxt = text.find("\n## ", idx + len(heading))
    end = len(text) if nxt < 0 else nxt + 1
    block = text[idx:end].rstrip("\n") + "\n" + "\n".join(lines) + "\n\n"
    text = text[:idx] + block + text[end:]
    if not dry:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)


def main(argv):
    opts = {"run": None, "root": None, "status": "verified", "cards_dir": os.path.join(SKILL, "references", "craft-cards"),
            "provenance": os.path.join(SKILL, "references", "craft-cards-provenance.md"),
            "pending": os.path.join(SKILL, "references", "pending-evidence.md"),
            "notes_dir": None, "dry_run": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--dry-run":
            opts["dry_run"] = True
            i += 1
            continue
        key = a[2:].replace("-", "_")
        if not a.startswith("--") or key not in opts or i + 1 >= len(argv):
            sys.exit(f"write-topic-result: unexpected argument {a!r}\n{__doc__}")
        opts[key] = argv[i + 1]
        i += 2
    if not opts["run"] or not opts["root"]:
        sys.exit("write-topic-result: --run and --root are required")
    root = os.path.abspath(opts["root"])
    notes_dir = opts["notes_dir"] or os.path.join(root, "research", "software-craft")
    result, progress = load_run(opts["run"])
    t = result["topic"]
    dry = opts["dry_run"]
    # renumber contiguously from the cards already in the tree
    next_id = existing_max(opts["cards_dir"], t["prefix"]) + 1
    written, prov_lines = [], []
    outcomes = {o["key"]: o for o in result.get("outcomes", [])}
    for card, prov in zip(result.get("cards", []), result.get("provenance_lines", [])):
        new_id = f"{t['prefix']}-{next_id:02d}"
        md, fn = renumber(card, card["rule_id"], new_id)
        prov_line = prov.replace(card["rule_id"], new_id)
        if not prov_line.startswith(f"- **{new_id}**"):
            prov_line = f"- **{new_id}** · " + prov_line.lstrip("- ").lstrip()
        path = os.path.join(opts["cards_dir"], fn)
        if os.path.exists(path):
            sys.exit(f"write-topic-result: {path} exists; refusing to overwrite")
        if not dry:
            os.makedirs(opts["cards_dir"], exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(md.rstrip("\n") + "\n")
        o = outcomes.get(card["key"], {})
        verification = "accepted on the first verdict" if not o.get("verdict2") else f"accepted after one fix ({o.get('verdict1', '')[:160]})"
        written.append({"rule_id": new_id, "title": card["title"], "filename": fn, "verification": verification})
        prov_lines.append(prov_line)
        next_id += 1
    pendings = result.get("pending_entries", [])
    if prov_lines:
        append_under(opts["provenance"], PROVENANCE_HEADER, DOMAIN_TITLES[t["domain"]], prov_lines, dry)
    if pendings:
        append_under(opts["pending"], PENDING_HEADER, t["domain"], [p["entry"] for p in pendings], dry)
    cost = cost_line(progress, result)
    note = note_markdown(result, opts["status"], cost, written, pendings)
    note_path = os.path.join(notes_dir, f"{t['slug']}.md")
    if not dry:
        os.makedirs(notes_dir, exist_ok=True)
        with open(note_path, "w", encoding="utf-8") as fh:
            fh.write(note)
    print(f"{t['slug']}: {len(written)} card(s) written, {len(pendings)} pending entr{'y' if len(pendings) == 1 else 'ies'}, "
          f"{len(result.get('held', []))} held; note {os.path.relpath(note_path, root)}; {cost}{' (dry run)' if dry else ''}")
    for w in written:
        print(f"  {w['rule_id']}  {w['filename']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
