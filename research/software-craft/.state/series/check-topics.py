#!/usr/bin/env python3
"""Where the series stands, from the tree: one row per topic of the design note's taxonomy (note status, cards the
note's `## Cards derived` table ships, held rules, pending entries, journal and output snapshots, batch records, audit
samples; a gap topic's note outside the taxonomy gets a row with letter "+"), then the note<->tree cross-check: every card in the tree is named as shipped by exactly one note and no note
names a card the tree lacks (a rule folded into an existing card appears in its own note's table as "folded into <id>",
which the check reports separately). Run from anywhere; read-only. Usage: check-topics.py"""
import re, os, glob, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = f"{ROOT}/plugins/code-quality/skills/software-craft"
ST = f"{ROOT}/research/software-craft/.state"
NOTE = open(f"{ROOT}/research/2026-09-26_software-craft-cards.md", encoding="utf-8").read()
tax, cur = [], None
for full, dom, pre, slug, con in re.findall(r"^\| ((?:[A-J]), `(\w+)`, `(\w+)`)? *\| `([a-z0-9-]+)`( \(contested\))? \|", NOTE, re.M):
    if dom: cur = (dom, pre, full[0])
    tax.append((slug, cur[0], cur[1], cur[2]))
# a note outside the taxonomy (a gap topic of series/make-gap-bundles.py) is a row of its own, letter "+"
for f in sorted(glob.glob(f"{ROOT}/research/software-craft/*.md")):
    _t = open(f, encoding="utf-8").read()
    _m = re.search(r"^topic: (\S+)", _t, re.M)
    if _m and _m.group(1) not in {s for s, *_ in tax}:
        _d, _p = re.search(r"^domain: (\S+)", _t, re.M), re.search(r"^prefix: (\S+)", _t, re.M)
        tax.append((_m.group(1), _d.group(1) if _d else "?", _p.group(1) if _p else "?", "+"))
tree = {}
for f in glob.glob(f"{K}/references/craft-cards/*.md"):
    tree[re.search(r"^rule_id: (\S+)", open(f, encoding="utf-8").read(), re.M).group(1)] = os.path.basename(f)
per_prefix = collections.Counter(i.split("-")[0] for i in tree)
batches = {}
for bf in sorted(glob.glob(f"{ST}/series/batch*.json")):
    b = json.load(open(bf, encoding="utf-8"))
    for slug, v in b["topics"].items():
        batches.setdefault(slug, []).append(f"b{b['batch']}:" + (v.get("status") or (f"runs:{len(v['runs'])}" if "runs" in v else "launched")))
samples = json.load(open(f"{ST}/series/audit-samples.json", encoding="utf-8"))["sampled"]
pend = collections.Counter()
for line in open(f"{K}/references/pending-evidence.md", encoding="utf-8"):
    if line.startswith("- "):
        m = re.search(r" · ([a-z0-9-]+) · ", line); pend[m.group(1) if m else "?"] += 1
shipped, folded = collections.defaultdict(list), collections.defaultdict(list)
rows = []
for slug, dom, pre, letter in tax:
    note = f"{ROOT}/research/software-craft/{slug}.md"
    st, n_ship, n_fold, n_held = "(no note)", 0, 0, 0
    if os.path.exists(note):
        t = open(note, encoding="utf-8").read()
        st = re.search(r"^status: (\S+)", t, re.M).group(1)
        m = re.search(r"^## Cards derived\n(.*?)(?=^## )", t, re.M | re.S)
        for line in (m.group(1) if m else "").splitlines():
            if not line.startswith("|"): continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4 or cells[0] in ("—", "-", "Card", "id") or set(cells[0]) <= set("-: "):
                fm = re.search(r"folded into (\w+-\d+)", line)
                if fm: folded[fm.group(1)].append(slug); n_fold += 1
                continue
            rid = re.match(r"(\w+-\d+)", cells[0])
            if rid: shipped[rid.group(1)].append(slug); n_ship += 1
        h = re.search(r"^## Rules held back\n(.*?)(?=^## )", t, re.M | re.S)
        n_held = len(re.findall(r"^- ", h.group(1), re.M)) if h else 0
    j = glob.glob(f"{ST}/journals/{slug}*.journal.jsonl.gz") + glob.glob(f"{ST}/{slug}--*journal.jsonl.gz")
    o = glob.glob(f"{ST}/outputs/{slug}*.output.json.gz") + glob.glob(f"{ST}/{slug}--*output.json.gz")
    rows.append((letter, pre, slug, st, n_ship, n_fold, n_held, pend.get(slug, 0), len(j), len(o), len(samples.get(slug, [])), ",".join(batches.get(slug, []))))
print(f"{'g':1s} {'pre':4s} {'topic':45s} {'note':9s} {'cards':5s} {'fold':4s} {'held':4s} {'pend':4s} {'jrn':3s} {'out':3s} {'aud':3s} batches")
for r in rows:
    print(f"{r[0]:1s} {r[1]:4s} {r[2]:45s} {r[3]:9s} {r[4]:<5d} {r[5]:<4d} {r[6]:<4d} {r[7]:<4d} {r[8]:<3d} {r[9]:<3d} {r[10]:<3d} {r[11]}")
st = collections.Counter(r[3] for r in rows)
print(f"\ntopics: {len(rows)} ({sum(1 for r in rows if r[0] == '+')} outside the taxonomy, letter +); by note status: {dict(st)}")
print(f"cards in tree: {len(tree)} ({dict(per_prefix)}); shipped by notes: {sum(r[4] for r in rows)}; pending entries: {sum(pend.values())}" + (f" ({pend['?']} without a topic slug)" if pend.get('?') else ""))
problems = []
for i in sorted(tree):
    if i not in shipped: problems.append(f"{i}: in the tree, shipped by no note")
    elif len(shipped[i]) > 1: problems.append(f"{i}: shipped by {shipped[i]}")
for i in sorted(shipped):
    if i not in tree: problems.append(f"{i}: shipped by {shipped[i]} but not in the tree")
for i in sorted(folded):
    if i not in tree: problems.append(f"{i}: a fold target that is not in the tree ({folded[i]})")
print("folds recorded:", {i: s for i, s in sorted(folded.items())})
print("cross-check:", "clean" if not problems else "\n  " + "\n  ".join(problems))
