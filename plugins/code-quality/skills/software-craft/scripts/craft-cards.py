#!/usr/bin/env python3
"""The developer agent's card index: list craft cards by facet as `rule_id · title · path`; and the
reader's lookup of a card's sources: print its provenance line.

Usage:  python3 craft-cards.py [--step <step>] [--domain <domain>] [--applies-to <scope>]
                              [--cards-dir <dir> ...] [--format lines|json]
        python3 craft-cards.py --provenance <RULE_ID> [--provenance <RULE_ID> ...] [--cards-dir <dir> ...]
Each --cards-dir adds a directory to the listing, so one call lists the universal and a
language corpus together; without one the universal corpus is listed. Filters combine with
AND; a card matches --step when its step list holds the value, --applies-to when its list
holds the value or `universal`. With no filter every card is listed. The developer scans the titles and opens the cards whose titles apply.
--provenance prints each named id's line from the provenance map of each --cards-dir
(cardlib.provenance_map_path): a card carries no citation, and
the line holds its sources — citations, quoted statements, fetch status, formulation, reception,
notes. It takes no filter; an id no map holds is named on stderr and the exit status is 1.
Reads only the cards and the provenance maps; writes nothing; no network; stdlib only.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import read_card, read_provenance, provenance_map_path, STEPS, APPLIES_TO, PREFIX_DOMAIN  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CARDS = os.path.normpath(os.path.join(HERE, "..", "references", "craft-cards"))


def print_provenance(rule_ids, cards_dirs):
    """Print each id's provenance line from the provenance maps of the cards directories; return the exit status."""
    lines = {}
    for cards_dir in cards_dirs:
        for rule_id, line in read_provenance(provenance_map_path(cards_dir)).items():
            lines.setdefault(rule_id, line)
    missing = [r for r in rule_ids if r not in lines]
    for rule_id in rule_ids:
        if rule_id in lines:
            print(lines[rule_id])
    if missing:
        maps = ", ".join(os.path.basename(provenance_map_path(d)) for d in cards_dirs)
        print(f"craft-cards: no provenance line for {', '.join(missing)} in {maps}", file=sys.stderr)
    return 1 if missing else 0


def main(argv):
    opts = {"step": None, "domain": None, "applies_to": None, "cards_dir": [], "provenance": [], "format": "lines"}
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
        if key in ("cards_dir", "provenance"):
            opts[key].append(argv[i + 1])
        else:
            opts[key] = argv[i + 1]
        i += 2
    cards_dirs = opts["cards_dir"] or [DEFAULT_CARDS]
    if opts["provenance"]:
        if any(opts[k] for k in ("step", "domain", "applies_to")):
            sys.exit("craft-cards: --provenance takes no filter")
        return print_provenance(opts["provenance"], cards_dirs)
    if opts["step"] and opts["step"] not in STEPS:
        sys.exit(f"craft-cards: --step must be one of {', '.join(STEPS)}")
    if opts["applies_to"] and opts["applies_to"] not in APPLIES_TO:
        sys.exit(f"craft-cards: --applies-to must be one of {', '.join(APPLIES_TO)}")
    if opts["domain"] and opts["domain"] not in PREFIX_DOMAIN.values():
        sys.exit(f"craft-cards: --domain must be one of {', '.join(sorted(PREFIX_DOMAIN.values()))}")
    missing = [d for d in cards_dirs if not os.path.isdir(d)]
    if missing:
        sys.exit(f"craft-cards: no cards directory at {', '.join(missing)}")
    names = [os.path.join(d, n) for d in cards_dirs for n in sorted(os.listdir(d)) if n.endswith(".md")]
    rows, skipped = [], []
    for card_path in names:
        name = os.path.basename(card_path)
        rec, err = read_card(card_path)
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
