#!/usr/bin/env python3
"""queue.py mark <slug> <part> <status> [task wf] | next [n] : maintain the launch queue (scratchpad queue.json)."""
import json, sys, subprocess
S="/tmp/claude-0/-home-user-rooted/e90d4d4d-b4c5-58b7-8385-bbb5069933a1/scratchpad"
q=json.load(open(f"{S}/queue.json"))
cmd=sys.argv[1]
if cmd=="mark":
    slug,part,status=sys.argv[2:5]
    for e in q["queue"]:
        if e["slug"]==slug and e["part"]==part:
            e["status"]=status
            if len(sys.argv)>5: e["task"],e["wf"]=sys.argv[5],sys.argv[6]
    json.dump(q,open(f"{S}/queue.json","w"),indent=1)
elif cmd=="next":
    n=int(sys.argv[2]) if len(sys.argv)>2 else 1
    running=[e for e in q["queue"] if e["status"]=="running"]
    todo=[e for e in q["queue"] if e["status"] in ("pending","rebuild")][:n]
    print(f"running {len(running)}, cap {q['cap']}")
    for e in todo:
        out=subprocess.run([f"{S}/rebuild.sh", e["slug"], e["kind"]] + (["2"] if "of2" in e["part"] else []), capture_output=True, text=True)
        lines=[l for l in out.stdout.splitlines() if "rule(s)," in l]
        print(e["slug"], e["part"], e["rules"], "rules ->", e["bundle"]); print("   ", "\n    ".join(l[:110] for l in lines))
elif cmd=="show":
    for e in q["queue"]: print(f"{e['status']:8s} {e['slug']:45s} {e['part']:14s} {e['rules']}")
