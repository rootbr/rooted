#!/usr/bin/env python3
"""The developer agent's card index: list craft cards by facet as `rule_id · title · path`.

Usage:  python3 craft-cards.py [--step <step>] [--domain <domain>] [--applies-to <scope>]
                              [--cards-dir <dir>] [--format lines|json]
Filters combine with AND; a card matches --step when its step list holds the value,
--applies-to when its list holds the value or `universal`. With no filter every card is
listed. The developer reads the titles and opens the cards whose titles apply.
Reads only the cards; writes nothing; no network; stdlib only.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import read_card, STEPS, APPLIES_TO, PREFIX_DOMAIN  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CARDS = os.path.normpath(os.path.join(HERE, "..", "references", "craft-cards"))


def main(argv):
    opts = {"step": None, "domain": None, "applies_to": None, "cards_dir": DEFAULT_CARDS, "format": "lines"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            sys.exit(__doc__)
        if not a.startswith("--") or i + 1 >= len(argv):
            sys.exit(f"craft-cards: unexpected argument {a!r}")
        key = a[2:].replace("-", "_")
        if key not in opts:
            sys.exit(f"craft-cards: unknown option {a}")
        opts[key] = argv[i + 1]
        i += 2
    if opts["step"] and opts["step"] not in STEPS:
        sys.exit(f"craft-cards: --step must be one of {', '.join(STEPS)}")
    if opts["applies_to"] and opts["applies_to"] not in APPLIES_TO:
        sys.exit(f"craft-cards: --applies-to must be one of {', '.join(APPLIES_TO)}")
    if opts["domain"] and opts["domain"] not in PREFIX_DOMAIN.values():
        sys.exit(f"craft-cards: --domain must be one of {', '.join(sorted(PREFIX_DOMAIN.values()))}")
    if not os.path.isdir(opts["cards_dir"]):
        sys.exit(f"craft-cards: no cards directory at {opts['cards_dir']}")
    rows, skipped = [], []
    for name in sorted(os.listdir(opts["cards_dir"])):
        if not name.endswith(".md"):
            continue
        rec, err = read_card(os.path.join(opts["cards_dir"], name))
        if err:
            skipped.append(f"{name}: {err}")
            continue
        if opts["step"] and opts["step"] not in rec["step"]:
            continue
        if opts["domain"] and rec["domain"] != opts["domain"]:
            continue
        if opts["applies_to"] and opts["applies_to"] not in rec["applies_to"] and "universal" not in rec["applies_to"]:
            continue
        rows.append(rec)
    rows.sort(key=lambda r: (r["domain"], r["rule_id"]))
    if opts["format"] == "json":
        json.dump([{k: r[k] for k in ("rule_id", "title", "path", "domain", "step", "applies_to")} for r in rows], sys.stdout, indent=1)
        print()
    else:
        for r in rows:
            print(f"{r['rule_id']} · {r['title']} · {r['path']}")
        print(f"# {len(rows)} card(s)" + (f"; filters: " + ", ".join(f"{k}={v}" for k, v in opts.items() if v and k in ('step', 'domain', 'applies_to')) if any(opts[k] for k in ('step', 'domain', 'applies_to')) else ""))
    for s in skipped:
        print(f"# skipped {s}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
