#!/usr/bin/env python3
"""Per-stage cost profile of the batch-3 workflow agents, from their transcripts (this session's own runs).

Usage: measure-agents.py [wf_id ...] [-wf_id ...] — positional ids restrict the profile to those runs, a leading minus excludes a run; no ids = every run."""
import json
import sys, glob, os, sys, statistics as st
from datetime import datetime
W = "/root/.claude/projects/-home-user-rooted/e90d4d4d-b4c5-58b7-8385-bbb5069933a1/subagents/workflows"
rows = []
ONLY = set(a for a in sys.argv[1:] if not a.startswith("-"))          # wf ids to include; none = every run
EXCLUDE = set(a[1:] for a in sys.argv[1:] if a.startswith("-"))       # -wf_id excludes a run
def selected(wd):
    wid = os.path.basename(wd)
    if wid in EXCLUDE: return False
    return not ONLY or wid in ONLY
for wd in glob.glob(W + "/wf_*"):
    if not selected(wd): continue
    labels = {}
    try:
        for line in open(wd + "/journal.jsonl"):
            r = json.loads(line)
            if r.get("type") == "started": labels[r["agentId"]] = r["label"]
    except FileNotFoundError: continue
    for f in glob.glob(wd + "/agent-*.jsonl"):
        aid = os.path.basename(f)[6:-6]
        label = labels.get(aid, "?")
        calls = 0; read = write = fresh = out = think = 0; tools = {}; first = last = None; ctx = 0; done = False; seen = set()
        for line in open(f, errors="ignore"):
            try: r = json.loads(line)
            except ValueError: continue
            ts = r.get("timestamp")
            if ts: first = first or ts; last = ts
            if r.get("type") != "assistant": continue
            m = r.get("message") or {}
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tools[c["name"]] = tools.get(c["name"], 0) + 1
                    if c["name"] == "StructuredOutput": done = True
            mid = m.get("id")
            if mid in seen: continue
            seen.add(mid)
            u = m.get("usage") or {}
            if not u: continue
            calls += 1
            read += u.get("cache_read_input_tokens") or 0; write += u.get("cache_creation_input_tokens") or 0; fresh += u.get("input_tokens") or 0
            out += u.get("output_tokens") or 0; think += ((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0)
            ctx = (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("input_tokens") or 0)
        if calls == 0: continue
        dur = (datetime.fromisoformat(last.replace("Z","+00:00")) - datetime.fromisoformat(first.replace("Z","+00:00"))).total_seconds()/60 if first and last else 0
        eq = fresh + 1.25*write + 0.05*read + 5*out
        rows.append(dict(stage=label.split(":")[0], label=label, calls=calls, read=read, write=write, fresh=fresh, out=out, think=think, ctx=ctx, dur=dur, eq=eq, done=done, bash=tools.get("Bash",0), tools=tools))
def mean(xs): return st.mean(xs) if xs else 0
print(f"{len(rows)} agents with calls; {sum(r['done'] for r in rows)} returned structured output")
print(f"{'stage':8s} {'n':>3s} {'calls':>6s} {'bash':>5s} {'ctx_k':>6s} {'read_M':>7s} {'write_k':>8s} {'out_k':>6s} {'think_k':>8s} {'min':>5s} {'eqM':>6s}  read% write% out%")
tot = {"eq":0,"read":0,"write":0,"out":0,"fresh":0}
for stage in ["draft","verify","fix","verify2","close1","close2","?"]:
    rs = [r for r in rows if r["stage"] == stage and r["done"]]
    if not rs: continue
    eq = mean([r["eq"] for r in rs]); rd = mean([0.05*r["read"] for r in rs]); wr = mean([1.25*r["write"] for r in rs]); ou = mean([5*r["out"] for r in rs])
    print(f"{stage:8s} {len(rs):3d} {mean([r['calls'] for r in rs]):6.1f} {mean([r['bash'] for r in rs]):5.1f} {mean([r['ctx'] for r in rs])/1e3:6.0f} {mean([r['read'] for r in rs])/1e6:7.2f} {mean([r['write'] for r in rs])/1e3:8.0f} {mean([r['out'] for r in rs])/1e3:6.1f} {mean([r['think'] for r in rs])/1e3:8.1f} {mean([r['dur'] for r in rs]):5.1f} {eq/1e6:6.2f}  {100*rd/eq:4.0f}% {100*wr/eq:4.0f}% {100*ou/eq:4.0f}%")
    for k in tot: tot[k] += sum(r[k] for r in rs)
cut = [r for r in rows if not r["done"]]
print(f"\ncut agents (no structured output): {len(cut)}, mean calls {mean([r['calls'] for r in cut]):.1f}, their eq weight {sum(r['eq'] for r in cut)/1e6:.1f}M")
print(f"finished agents eq weight total {tot['eq']/1e6:.1f}M: cache read {0.05*tot['read']/1e6:.1f}M (raw {tot['read']/1e9:.2f}G tokens), cache write {1.25*tot['write']/1e6:.1f}M, output {5*tot['out']/1e6:.1f}M (raw {tot['out']/1e6:.2f}M)")
# first-call context (prefix) and tools used
fc = []
for wd in glob.glob(W + "/wf_*"):
    if not selected(wd): continue
    for f in glob.glob(wd + "/agent-*.jsonl")[:3]:
        for line in open(f, errors="ignore"):
            try: r = json.loads(line)
            except ValueError: continue
            if r.get("type") == "assistant" and (r.get("message") or {}).get("usage"):
                u = r["message"]["usage"]; fc.append((u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("input_tokens") or 0)); break
print(f"first-call context (prefix + prompt): median {st.median(fc)/1e3:.0f}k, min {min(fc)/1e3:.0f}k, max {max(fc)/1e3:.0f}k over {len(fc)} agents")
alltools = {}
for r in rows:
    for k,v in r["tools"].items(): alltools[k] = alltools.get(k,0)+v
print("tools:", alltools)
