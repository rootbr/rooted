#!/usr/bin/env python3
"""Grade a review run of the fixture against evals/expected.json — mechanically, on
(rule_id, file, symbol) triples; no judge model.

Usage: python3 evals/grade.py --expected evals/expected.json --verdicts review/verdicts.json [--findings review/findings.json]

A finding counts when its disposition after verification is report, flagged or
downgraded — a rejected finding does not. A seed passes when a counting finding
carries its rule_id and file and its symbol's method part; a control passes when no
counting finding with a silent rule id sits on its file and symbol. --findings (the
pre-verification set) adds a raw-hit column so a control caught only by the skeptic is
visible. Exit status 1 when any seed or control fails.
"""
import json
import sys


def disposition(f):
    r = f.get("ruling") or {}
    v = f.get("verdict") or {}
    if r:
        return {"refuted": "report", "uncertain": "flagged"}.get((r.get("ruling") or "").lower(), "rejected")
    return {"rejected": "rejected", "downgraded": "downgraded"}.get((v.get("verdict") or "confirmed").lower(), "report")


def method_part(symbol):
    s = str(symbol or "")
    for sep in ("#", ".", "::"):
        if sep in s:
            s = s.rsplit(sep, 1)[1]
    return s.replace("()", "").strip().lower()


def matches(f, file, symbol):
    """`symbol` is one anchor or a list of the anchors a card admits (the method that performs
    the access, or the field it reads); the finding matches when its method part equals any."""
    symbols = symbol if isinstance(symbol, list) else [symbol]
    return f.get("file") == file and any(method_part(f.get("symbol")) == method_part(x) for x in symbols)


def carries(f, rule_id):
    """A finding carries a rule id as its own or as one folded into it (`also`) by aggregation."""
    return f.get("rule_id") == rule_id or rule_id in (f.get("also") or [])


def main(argv):
    opts = {"expected": "evals/expected.json", "verdicts": None, "findings": None}
    i = 0
    while i < len(argv):
        opts[argv[i][2:]] = argv[i + 1]
        i += 2
    if not opts["verdicts"]:
        sys.exit(__doc__)
    exp = json.load(open(opts["expected"], encoding="utf-8"))
    data = json.load(open(opts["verdicts"], encoding="utf-8"))
    verified = data["findings"] if isinstance(data, dict) else data
    raw = []
    if opts["findings"]:
        d = json.load(open(opts["findings"], encoding="utf-8"))
        raw = d["findings"] if isinstance(d, dict) else d
    counting = [f for f in verified if disposition(f) != "rejected"]
    failures = 0
    print("SEEDS")
    for s in exp["seeds"]:
        hit = [f for f in counting if carries(f, s["rule_id"]) and matches(f, s["file"], s["symbol"])]
        rawhit = [f for f in raw if carries(f, s["rule_id"]) and matches(f, s["file"], s["symbol"])]
        ok = bool(hit)
        failures += 0 if ok else 1
        extra = "" if not opts["findings"] else f"  raw={'hit' if rawhit else 'miss'}"
        print(f"  {'PASS' if ok else 'FAIL'}  {s['id']}  ({s['rule_id']} {s['symbol'] if isinstance(s['symbol'], str) else ' | '.join(s['symbol'])}){extra}"
              + (f"  verified as {hit[0].get('id')} [{disposition(hit[0])}]" if hit else ""))
    print("CONTROLS")
    for c in exp["controls"]:
        hit = [f for f in counting if any(carries(f, r) for r in c["silent"]) and matches(f, c["file"], c["symbol"])]
        rawhit = [f for f in raw if any(carries(f, r) for r in c["silent"]) and matches(f, c["file"], c["symbol"])]
        ok = not hit
        failures += 0 if ok else 1
        extra = "" if not opts["findings"] else f"  raw={'flagged then ' + ('rejected' if not hit else 'kept') if rawhit else 'silent'}"
        print(f"  {'PASS' if ok else 'FAIL'}  {c['id']}  (silent: {', '.join(c['silent'])} on {c['symbol']}){extra}"
              + (f"  kept as {hit[0].get('id')} [{disposition(hit[0])}]" if hit else ""))
    others = [f for f in counting if not any(carries(f, s["rule_id"]) and matches(f, s["file"], s["symbol"]) for s in exp["seeds"])]
    print(f"OTHER VERIFIED FINDINGS (not graded): {len(others)}")
    for f in others:
        print(f"  {f.get('id')} {f.get('severity')} {f.get('file')} {f.get('symbol')} [{disposition(f)}]")
    print(f"RESULT: {len(exp['seeds']) + len(exp['controls']) - failures}/{len(exp['seeds']) + len(exp['controls'])} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
