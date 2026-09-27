#!/usr/bin/env python3
"""merge-seeds.py <seeds.json> <topics.json>: append the seeds' candidate_evidence items to the named topics."""
import json,sys
seeds=json.load(open(sys.argv[1])); path=sys.argv[2]; topics=json.load(open(path))
by={t["slug"]:t for t in topics}
for slug,items in seeds.items():
    t=by[slug]
    for it in items:
        if it not in t["candidate_evidence"]: t["candidate_evidence"].append(it)
    # drop placeholder lines that name no source once real seeds exist
    t["candidate_evidence"]=[c for c in t["candidate_evidence"] if not (("none confirmed" in c.lower() or "no confirmed" in c.lower()) and len(items))]
    print(slug, "->", len(t["candidate_evidence"]), "items")
json.dump(topics, open(path,"w"), ensure_ascii=False, indent=1)
