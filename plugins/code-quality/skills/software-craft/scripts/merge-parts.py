#!/usr/bin/env python3
"""Join the outputs of a review workflow run in parts (scripts/craft-review-workflow.js with
`part: {index, of}`).

Usage:
  merge-parts.py --stage find   --out craft/raw.json      <find-part output.json> ...
  merge-parts.py --stage verify --out craft/verdicts.json <verify-part output.json> ...

A part output is the Workflow tool's task output (its `result`) or the result object itself.
Stage find concatenates the parts' raw findings into one array for `bundle-run.py --stage
aggregate --raw`; stage verify concatenates the parts' verified findings, re-sorts them by
their ids and recomputes the tally the whole-run workflow reports. Standard library only."""
import json
import os
import sys


def load(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return d.get("result", d) if isinstance(d, dict) else d


def disposition_counts(findings):
    tally = {"confirmed": 0, "rejected": 0, "downgraded": 0, "upgraded": 0, "modified": 0, "restored": 0, "uncertain": 0, "unverified": 0}
    for f in findings:
        v = f.get("verdict")
        if not v:
            tally["unverified"] += 1
            continue
        key = (v.get("verdict") or "").lower()
        tally[key] = tally.get(key, 0) + 1
        r = f.get("ruling") or {}
        if r.get("ruling") == "refuted":
            tally["restored"] += 1
        if r.get("ruling") == "uncertain":
            tally["uncertain"] += 1
    return tally


def id_key(f):
    rid, _, n = (f.get("id") or "").rpartition(".")
    return (rid, int(n) if n.isdigit() else 0)


def main(argv):
    opts = {"stage": None, "out": None}
    paths = []
    i = 0
    while i < len(argv):
        if argv[i] in ("--stage", "--out") and i + 1 < len(argv):
            opts[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            paths.append(argv[i])
            i += 1
    if opts["stage"] not in ("find", "verify") or not opts["out"] or not paths:
        sys.exit(__doc__)
    parts = [load(p) for p in paths]
    seen = set()
    for p, part in zip(paths, parts):
        key = (part.get("part") or {}).get("index")
        if key in seen:
            sys.exit(f"merge-parts: part {key} appears twice ({p})")
        seen.add(key)
    if opts["stage"] == "find":
        raw = []
        for part in parts:
            raw.extend(part.get("raw") or [])
        out = raw
        summary = f"{len(raw)} finder result(s), {sum(len(r.get('findings') or []) for r in raw)} raw finding(s)"
    else:
        findings = []
        for part in parts:
            findings.extend(part.get("findings") or [])
        findings.sort(key=id_key)
        tally = disposition_counts(findings)
        out = {"stage": "verify", "findings": findings, "conflicts": parts[0].get("conflicts") or [], "tally": tally,
               "agents_run": sum(int(part.get("agents_run") or 0) for part in parts), "inventory": parts[0].get("inventory"),
               "parts": len(parts)}
        summary = f"{len(findings)} finding(s), tally {tally}"
    os.makedirs(os.path.dirname(os.path.abspath(opts["out"])), exist_ok=True)
    with open(opts["out"], "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"{opts['out']}: {len(parts)} part(s), {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
