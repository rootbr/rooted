#!/usr/bin/env python3
"""round2-from-tree.py — the second fix round for a topic whose cards were written after one round:
a pass over the cards as they stand in the tree (HANDOVER §1 Rounds, §5.11).

A topic written after one round cannot take its second round from the journal: a journal-based fix
would re-fix the journal's draft and overwrite the card the spot-reads and the domain reviewers have
since edited. This script takes each tree card as the round's fixed draft instead and lets the
workflow verify it with one `max` verdict and, on a "revise", a closing edit that applies the verdict's
required edits verbatim; an "accept" leaves the card as it is and a "reject" is reported for the
orchestrator, never applied by hand.

Subcommands (run from the repository root):
  map   <slug> [<slug> ...]                 print the rule key -> tree card mapping of each topic and stop
  build <slug> --out-dir <dir> [--bundle <regenerated bundle>] [--only <id,id,...>]
        [--skeptic-model <id>] [--skeptic-effort <level>]
        write <dir>/<slug>--r2tree.js, a bundle of scripts/research-topic-workflow.js whose resume_state carries
        the topic's spine (from journals/<slug>.journal.jsonl.gz, else the output snapshot) and every tree card
        of the topic as a `fix2:` draft, with only_keys those cards, round 3 (labels verify3: / close3:),
        fix_after_verify false, closing_edit true and `written` the cards' ids and example languages; the
        bundle's channel_note comes from --bundle when given; the skeptic runs on --skeptic-model at --skeptic-effort
        (default claude-fable-5-1 at high, the operator's decision of 2026-10-09; the closing edits stay on the
        workflow's default drafter model)
  apply <slug> <pass output> [--dry-run]
        write the pass's result into the tree: a card the verdict accepted is left as it is; a card the closing
        edit changed replaces the tree card (and its filename when the title changed) and its provenance line;
        each note row's Verification column records the pass and the note's Cost gains a line; a card the
        verdict rejected, or a closing edit sent to pending, is printed with its reason and recorded in
        round2.json, and the tree is not changed for it
Launch: Workflow({ scriptPath: "<dir>/<slug>--r2tree.js" }); record the run in series/round2.json as a `runs`
entry {part: "r2tree", task, wf, launched, status}; snapshot with series-status.py --snapshot (which reads
round2.json after the batches); then `apply`, the validator, the spot-read of the changed cards, the commit.
Standard library only."""
import glob
import gzip
import importlib.util
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(STATE, "..", "..", ".."))
K = os.path.join(ROOT, "plugins", "code-quality", "skills", "software-craft")
CARDS = os.path.join(K, "references", "craft-cards")
PROVENANCE = os.path.join(K, "references", "craft-cards-provenance.md")
NOTES = os.path.join(ROOT, "research", "software-craft")
SCRIPT = os.path.join(K, "scripts", "research-topic-workflow.js")

_spec = importlib.util.spec_from_file_location("research_continue", os.path.join(K, "scripts", "research-continue.py"))
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)


def open_text(path):
    return gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") else open(path, encoding="utf-8")


def journal_results(path):
    """label -> result over one journal (gzip or plain), the first result per label."""
    key2label, results = {}, {}
    with open_text(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get("type") == "started":
                key2label[e["key"]] = e.get("label", "")
            elif e.get("type") == "result" and e.get("result") is not None:
                label = key2label.get(e["key"])
                if label and label not in results:
                    results[label] = e["result"]
    return results


def load_output(path):
    with open_text(path) as fh:
        d = json.load(fh)
    return d, (d["result"] if "result" in d else d)


def tree_files():
    out = {}
    for name in os.listdir(CARDS):
        m = re.match(r"^([a-z]+)-(\d\d)--(.+)\.md$", name)
        if m:
            out[name] = (m.group(1).upper() + "-" + m.group(2), m.group(1), m.group(3))
    return out


def tree_file_by_id(rule_id):
    pre, nn = rule_id.split("-")
    hits = glob.glob(os.path.join(CARDS, f"{pre.lower()}-{nn}--*.md"))
    if len(hits) != 1:
        sys.exit(f"round2-from-tree: {len(hits)} tree file(s) for {rule_id}: {hits}")
    return hits[0]


def card_title(md):
    fm = md.split("---")[1] if md.startswith("---") else ""
    m = re.search(r"^title:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else ""


def card_lang(md):
    m = re.search(r"^```(\w+)", md, re.M)
    return m.group(1) if m else ""


def note_rows(slug):
    path = os.path.join(NOTES, f"{slug}.md")
    txt = open(path, encoding="utf-8").read()
    rows = re.findall(r"^\| ([A-Z]+-\d\d) \| (.+?) \| `references/craft-cards/([^`]+)` \| (.*) \|$", txt, re.M)
    return txt, [(rid, title.replace("\\|", "|"), fn, ver) for rid, title, fn, ver in rows]


def topic_material(slug):
    """The topic object, next_id, spine and every (key -> title, filename) the runs produced."""
    outputs = sorted(glob.glob(os.path.join(STATE, "outputs", f"{slug}*.output.json.gz")))
    journals = sorted(glob.glob(os.path.join(STATE, "journals", f"{slug}*.journal.jsonl.gz")))
    if not outputs and not journals:
        sys.exit(f"round2-from-tree: no output or journal snapshot of {slug} under {STATE}")
    topic = next_id = spine = None
    produced = {}   # key -> (title, filename)
    for o in outputs:
        _, r = load_output(o)
        topic = topic or r.get("topic")
        next_id = next_id or r.get("next_id")
        if not spine and r.get("spine", {}).get("rules"):
            spine = r["spine"]
        for c in r.get("cards", []):
            produced[c["key"]] = (c["title"], c["filename"])
    original = os.path.join(STATE, "journals", f"{slug}.journal.jsonl.gz")
    if os.path.exists(original):
        res = journal_results(original)
        if res.get("spine", {}).get("rules"):
            spine = res["spine"]
    for j in journals:
        for label, d in journal_results(j).items():
            stage, _, key = label.partition(":")
            if key and (stage.startswith("close") or stage.startswith("fix")) and isinstance(d, dict) and d.get("status") == "card" and d.get("card_markdown"):
                produced.setdefault(key, (card_title(d["card_markdown"]), d.get("filename", "")))
    if not topic or not spine:
        sys.exit(f"round2-from-tree: {slug}: no topic object or no spine in the snapshots")
    return topic, next_id or 1, spine, produced


def overrides(slug):
    """round2-overrides.json: {slug: {rule_id: {"key": <rule key>, "from_key": <parent key, optional>}}} for a
    card no run output names — one renamed since (key only) or one split out of another card at the audit
    (from_key: the spine rule whose evidence and formulation the split card shares; the pass synthesizes a
    spine entry for it from that rule and the card's own title, Thesis and facets)."""
    path = os.path.join(HERE, "round2-overrides.json")
    if not os.path.exists(path):
        return {}
    return json.load(open(path, encoding="utf-8")).get(slug, {})


def card_facets(md):
    fm = md.split("---")[1] if md.startswith("---") else ""
    out = {}
    for k in ("step", "applies_to", "triggers", "scope", "check_kind", "severity_default"):
        m = re.search(rf"^{k}:\s*(.+)$", fm, re.M)
        out[k] = m.group(1).strip() if m else ""
    th = re.search(r"^## Thesis\n+(.+?)\n\n", md, re.S | re.M)
    out["thesis"] = th.group(1).strip() if th else ""
    return out


def synthesize_rule(spine, from_key, key, md):
    parent = next((r for r in spine.get("rules", []) if r.get("key") == from_key), None)
    if not parent:
        sys.exit(f"round2-from-tree: from_key {from_key!r} is not in the spine")
    r = json.loads(json.dumps(parent))
    f = card_facets(md)
    r.update({"key": key, "title": card_title(md), "statement": f["thesis"] or card_title(md), "disposition": "card", "hold_reason": "",
              "step": f["step"], "applies_to": f["applies_to"], "triggers": f["triggers"], "scope": f["scope"],
              "check_kind": f["check_kind"], "severity_default": f["severity_default"]})
    return r


def mapping(slug):
    """rule key -> (rule_id, tree filename) for every tree card of the topic; the keys with no tree card
    (folded or removed since) and the note rows no key reaches are returned for the report. A card the
    overrides name is mapped by its rule id, and one with a parent gets a synthesized spine entry."""
    topic, next_id, spine, produced = topic_material(slug)
    tree = tree_files()
    by_slug = {(pre, sl): name for name, (_, pre, sl) in tree.items()}
    _, rows = note_rows(slug)
    by_title = {title: rid for rid, title, _, _ in rows}
    mapped, unmapped = {}, []
    for key, (title, filename) in produced.items():
        m = re.match(r"^([a-z]+)-\d\d--(.+)\.md$", filename or "")
        name = by_slug.get((m.group(1), m.group(2))) if m else None
        rid = tree[name][0] if name else by_title.get(title)
        if rid and rid in {r for r, *_ in rows}:
            mapped[key] = (rid, os.path.basename(tree_file_by_id(rid)))
        else:
            unmapped.append(key)
    for rid, ov in overrides(slug).items():
        fn = os.path.basename(tree_file_by_id(rid))
        mapped[ov["key"]] = (rid, fn)
        unmapped = [k for k in unmapped if k != ov["key"]]
        if ov.get("from_key"):
            spine["rules"].append(synthesize_rule(spine, ov["from_key"], ov["key"], open(os.path.join(CARDS, fn), encoding="utf-8").read()))
    reached = {rid for rid, _ in mapped.values()}
    missing_rows = [rid for rid, *_ in rows if rid not in reached]
    return topic, next_id, spine, mapped, unmapped, missing_rows


def cmd_map(slugs):
    total = 0
    for slug in slugs:
        topic, _, spine, mapped, unmapped, missing_rows = mapping(slug)
        total += len(mapped)
        keys = {r["key"] for r in spine.get("rules", [])}
        print(f"{slug}: {len(mapped)} tree card(s) mapped" + (f"; keys with no tree card: {', '.join(unmapped)}" if unmapped else "")
              + (f"; NOTE ROWS NO KEY REACHES: {', '.join(missing_rows)}" if missing_rows else ""))
        ov = overrides(slug)
        for key, (rid, fn) in sorted(mapped.items(), key=lambda kv: kv[1][0]):
            tag = "" if key in keys else "  (KEY NOT IN THE SPINE)"
            if rid in ov:
                tag = f"  (override{': synthesized from ' + ov[rid]['from_key'] if ov[rid].get('from_key') else ''})"
            print(f"   {rid}  {key}{tag}  {fn}")
    print(f"total: {total} card(s) over {len(slugs)} topic(s)")


SKEPTIC_MODEL, SKEPTIC_EFFORT = "claude-fable-5-1", "high"


def cmd_build(slug, out_dir, bundle_path=None, only=None, skeptic_model=SKEPTIC_MODEL, skeptic_effort=SKEPTIC_EFFORT):
    topic, next_id, spine, mapped, unmapped, missing_rows = mapping(slug)
    if missing_rows:
        sys.exit(f"round2-from-tree: {slug}: note rows no key reaches: {missing_rows}; fix the mapping before a build")
    spine_keys = {r["key"] for r in spine.get("rules", [])}
    bad = [k for k in mapped if k not in spine_keys]
    if bad:
        sys.exit(f"round2-from-tree: {slug}: mapped keys the spine lacks: {bad}")
    if only:
        mapped = {k: v for k, v in mapped.items() if v[0] in only}
        if not mapped:
            sys.exit("round2-from-tree: --only names no mapped card")
    prov = open(PROVENANCE, encoding="utf-8").read().splitlines()
    drafts, written = {}, {}
    for key, (rid, fn) in mapped.items():
        md = open(os.path.join(CARDS, fn), encoding="utf-8").read()
        line = next((l for l in prov if l.startswith(f"- **{rid}**")), None)
        if not line:
            sys.exit(f"round2-from-tree: no provenance line for {rid}")
        drafts[key] = {"status": "card", "filename": fn, "card_markdown": md, "provenance_line": line, "pending_entry": "",
                       "notes": "the card as it stands in the tree after its spot-read and its domain reviewer; this pass verifies it as the round's draft"}
        written[key] = {"rule_id": rid, "example_language": card_lang(md)}
    # every card-disposition rule of the spine stays numbered so only_keys resolves; ids come from `written`
    card_rules = [r for r in spine.get("rules", []) if r.get("disposition") == "card"]
    launched = rc.read_bundle_args(bundle_path) if bundle_path else {}
    args_obj = {
        "root": ROOT, "topic": launched.get("topic") or topic, "next_id": next_id, "existing_titles": [],
        "max_rules": max(12, len(card_rules)), "rotation_start": int(launched.get("rotation_start", 0)),
        "resume_state": {"sources": [], "spine": spine, "drafts": drafts, "verdicts": {}},
        "only_keys": sorted(mapped, key=lambda k: mapped[k][0]), "include_held": False, "round": 3,
        "fix_after_verify": False, "closing_edit": True, "written": written,
        "skeptic_model": skeptic_model, "skeptic_effort": skeptic_effort,
    }
    if launched.get("channel_note"):
        args_obj["channel_note"] = launched["channel_note"]
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{slug}--r2tree.js")
    with open(SCRIPT, encoding="utf-8") as fh:
        script = fh.read()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(rc.bundle(script, args_obj))
    size = os.path.getsize(path)
    if size > 524288:
        sys.exit(f"round2-from-tree: {path} is {size} bytes, above the runtime's 524288-byte script limit; use --only to split the topic")
    print(f"{path}: {len(mapped)} card(s), {size} bytes, skeptic {skeptic_model} at {skeptic_effort} — {', '.join(rid for rid, _ in sorted(mapped.values()))}"
          + (f"; keys with no tree card left out: {', '.join(unmapped)}" if unmapped else ""))
    return 0


def esc(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def cost_of(data, r):
    progress = data.get("workflowProgress") or []
    agents = [p for p in progress if p.get("type") == "workflow_agent"]
    tokens = sum(int(p.get("tokens") or 0) for p in agents)
    starts = [p.get("queuedAt") or p.get("startedAt") for p in agents if p.get("queuedAt") or p.get("startedAt")]
    ends = [p.get("lastProgressAt") for p in agents if p.get("lastProgressAt")]
    wall = (max(ends) - min(starts)) // 1000 if starts and ends else 0
    n = len(agents) or (r.get("cost") or {}).get("agents_run", 0)
    return n, tokens, wall


def cmd_apply(slug, output_path, dry=False):
    data, r = load_output(output_path)
    if r.get("topic", {}).get("slug") != slug:
        sys.exit(f"round2-from-tree: the output names topic {r.get('topic', {}).get('slug')!r}, not {slug!r}")
    outcomes = {o["key"]: o for o in r.get("outcomes", [])}
    note_path = os.path.join(NOTES, f"{slug}.md")
    note, rows = note_rows(slug)
    prov_lines = open(PROVENANCE, encoding="utf-8").read().split("\n")
    accepted, edited, renamed, rejected = [], [], [], []
    for card, line in zip(r.get("cards", []), r.get("provenance_lines", [])):
        rid = card["rule_id"]
        o = outcomes.get(card["key"], {})
        old_path = tree_file_by_id(rid)
        old_name = os.path.basename(old_path)
        new_name = card["filename"] if re.match(rf"^{rid.split('-')[0].lower()}-{rid.split('-')[1]}--.+\.md$", card["filename"] or "") else old_name
        md = card["markdown"].rstrip("\n") + "\n"
        if o.get("closing_edit"):
            verification = (f"round 2 over the tree: shipped on a closing edit, the `max` verdict's required edits applied verbatim, "
                            f"no further verdict ({(o.get('last_verdict') or '')[:200]})")
            edited.append(rid)
            if not dry:
                with open(os.path.join(CARDS, new_name), "w", encoding="utf-8") as fh:
                    fh.write(md)
                if new_name != old_name:
                    os.remove(old_path)
            if new_name != old_name:
                renamed.append((old_name, new_name))
            if line and not line.startswith(f"- **{rid}**"):
                line = f"- **{rid}** · " + line.lstrip("- ").lstrip()
            idx = next((i for i, l in enumerate(prov_lines) if l.startswith(f"- **{rid}**")), None)
            if idx is None:
                sys.exit(f"round2-from-tree: no provenance line for {rid}")
            if line:
                prov_lines[idx] = line
        else:
            tree_md = open(old_path, encoding="utf-8").read()
            if tree_md.rstrip("\n") != md.rstrip("\n"):
                print(f"WARNING: {rid} was accepted but the output's markdown differs from the tree card; the tree card is kept")
            verification = f"round 2 over the tree: accepted by a `max` verdict ({(o.get('verdict1') or '')[:160]})"
            accepted.append(rid)
        # the note row
        pat = re.compile(rf"^\| {re.escape(rid)} \| (.+?) \| `references/craft-cards/([^`]+)` \| (.*) \|$", re.M)
        m = pat.search(note)
        if not m:
            sys.exit(f"round2-from-tree: the note has no Cards derived row for {rid}")
        row = f"| {rid} | {esc(card_title(md) or m.group(1))} | `references/craft-cards/{new_name}` | {m.group(3)}; {esc(verification)} |"
        note = note[:m.start()] + row + note[m.end():]
    for p in r.get("pending_entries", []):
        o = outcomes.get(p["key"], {})
        rejected.append({"key": p["key"], "rule_id": o.get("rule_id"), "reason": o.get("reason") or p.get("reason") or "", "entry": p.get("entry", "")})
        print(f"NOT ACCEPTED (tree unchanged, decide by hand): {o.get('rule_id')} {p['key']} — {(o.get('reason') or p.get('reason') or '')[:300]}")
    n, tokens, wall = cost_of(data, r)
    cost = f"- round 2 over the tree: agents run: {n}" + (f"; sub-agent tokens: {tokens:,}" if tokens else "") + (f"; wall-clock: {wall} s" if wall else "") \
        + f"; {len(accepted)} accepted, {len(edited)} closing-edited, {len(rejected)} not accepted"
    if "\n## Cost\n" not in note:
        sys.exit("round2-from-tree: the note has no Cost section")
    head, _, tail = note.rpartition("\n## Cost\n")
    note = head + "\n## Cost\n" + tail.rstrip("\n") + "\n" + cost + "\n"
    if not dry:
        with open(note_path, "w", encoding="utf-8") as fh:
            fh.write(note)
        with open(PROVENANCE, "w", encoding="utf-8") as fh:
            fh.write("\n".join(prov_lines))
        rec_path = os.path.join(HERE, "round2.json")
        rec = json.load(open(rec_path, encoding="utf-8")) if os.path.exists(rec_path) else {"topics": {}}
        t = rec.setdefault("topics", {}).setdefault(slug, {})
        t["result"] = {"applied": time.strftime("%Y-%m-%dT%H:%M UTC", time.gmtime()), "accepted": accepted, "closing_edited": edited,
                       "renamed": renamed, "not_accepted": rejected, "agents": n, "tokens": tokens, "wall_s": wall}
        json.dump(rec, open(rec_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{slug}: {len(accepted)} accepted ({', '.join(accepted)}), {len(edited)} closing-edited ({', '.join(edited)}), "
          f"{len(renamed)} renamed, {len(rejected)} not accepted{' (dry run)' if dry else ''}; {cost[2:]}")
    if not dry:
        print(f"next: python3 {K}/scripts/validate-craft-cards.py --provenance {PROVENANCE} --pending {K}/references/pending-evidence.md {CARDS}; spot-read the closing-edited cards; git add by name")


def main(argv):
    if not argv or argv[0] not in ("map", "build", "apply"):
        sys.exit(__doc__)
    cmd, rest = argv[0], argv[1:]
    if cmd == "map":
        return cmd_map(rest) if rest else sys.exit("round2-from-tree: map needs at least one slug")
    if cmd == "build":
        slug = rest[0] if rest else sys.exit("round2-from-tree: build needs a slug")
        out_dir = bundle = None; only = None; sm, se = SKEPTIC_MODEL, SKEPTIC_EFFORT
        i = 1
        while i < len(rest):
            if rest[i] == "--out-dir": out_dir = rest[i + 1]; i += 2
            elif rest[i] == "--bundle": bundle = rest[i + 1]; i += 2
            elif rest[i] == "--only": only = set(rest[i + 1].split(",")); i += 2
            elif rest[i] == "--skeptic-model": sm = rest[i + 1]; i += 2
            elif rest[i] == "--skeptic-effort": se = rest[i + 1]; i += 2
            else: sys.exit(f"round2-from-tree: unexpected argument {rest[i]!r}")
        if not out_dir:
            sys.exit("round2-from-tree: build needs --out-dir")
        return cmd_build(slug, out_dir, bundle, only, sm, se)
    if cmd == "apply":
        if len(rest) < 2:
            sys.exit("round2-from-tree: apply needs a slug and the pass output")
        return cmd_apply(rest[0], rest[1], dry="--dry-run" in rest[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
