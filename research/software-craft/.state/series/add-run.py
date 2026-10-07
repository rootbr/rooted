#!/usr/bin/env python3
"""add-run.py <batchN.json> <slug> <part> <task id> <wf id>: append one launched bundle to a continuation batch's `runs`."""
import json, sys
path, slug, part, task, wf = sys.argv[1:6]
b = json.load(open(path, encoding="utf-8"))
b["topics"].setdefault(slug, {"runs": []})["runs"].append({"part": part, "task": task, "wf": wf})
json.dump(b, open(path, "w", encoding="utf-8"), indent=1)
print(f"{slug}: {len(b['topics'][slug]['runs'])} run(s) recorded")
