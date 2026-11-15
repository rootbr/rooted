#!/usr/bin/env python3
"""Probe behind the absent-rule pilot: what a script can find, by wording alone, in the prose a
commit adds.

    absent_rule_probe.py candidates BASE HEAD            sentences with a denial or contrast marker
    absent_rule_probe.py history N REV                   the same per commit, N commits back from REV
    absent_rule_probe.py trace BASE HEAD --term REGEX    marker sentences plus sentences naming REGEX
    absent_rule_probe.py echo BASE HEAD                  marker sentences that deny a deleted term

It reads the repository of the current directory through `git diff`, `git log` and `git ls-tree`,
prints to standard output, writes nothing and uses the Python standard library alone. `protocol.md`
beside it holds the numbers each mode gave.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter

# marker name -> pattern. A hit nominates a sentence; it rules on nothing.
MARKERS = [
    ("neither-nor", re.compile(r"\bneither\b[^.!?\n]{1,90}?\bnor\b", re.I)),
    ("not-but", re.compile(r"\bnot\b[^.!?\n]{1,60}?\bbut\b", re.I)),
    ("is-not-a", re.compile(r"\b(?:is|are|was|were|means?)\s+not\s+(?:a|an|the)\b", re.I)),
    ("comma-not", re.compile(r",\s+not\b", re.I)),
    ("verb-no", re.compile(r"\b(?:needs?|requires?|takes?|has|have|having|carr(?:y|ies)|"
                           r"gives?|offers?|forms?|supports?)\s+no(?:thing)?\b", re.I)),
    ("never-np", re.compile(r"\bnever\s+(?:the|a|an|as|from|on|inside|means?)\b", re.I)),
    ("instead", re.compile(r"\binstead\b", re.I)),
    ("in-place-of", re.compile(r"\bin place of\b", re.I)),
    ("rather-than", re.compile(r"\brather than\b", re.I)),
    ("unlike", re.compile(r"\bunlike\b|\bas opposed to\b", re.I)),
    ("no-single", re.compile(r"\bno single\b|\bnone of (?:them|these|those)\b", re.I)),
    ("not-yet", re.compile(r"\bnot yet\b|\bas yet\b|\bfor now\b|\bso far\b", re.I)),
]
# The markers that fire least often on ordinary commits of this repository.
STRICT = {"neither-nor", "verb-no", "never-np", "no-single", "in-place-of", "is-not-a", "not-yet"}

# Prose that states the present design; maintainer records, eval data and card corpora are data.
SKIP = re.compile(r"(^|/)(maintenance|evals|research|tmp|node_modules)/|/rule-cards/"
                  r"|/craft-cards[^/]*/|/cards/|CHANGELOG")

STOP = set("""a an the and or of to in on for with by at from as is are was were be been it its this
that these those which who whom what when where how why not no nor neither but than then so if each
every any all one two three own our your their his her we you they he she them us there here also
only more most less least very can could may might must shall should will would do does did done
have has had into over under out up down off about above below between through during before after
again once such same other another both few many much some rule rules skill skills file files line
lines itself either single longer yet""".split())


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def design_prose(path):
    return path.endswith(".md") and not SKIP.search(path)


def words(text):
    return re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text)


def stem(word):
    w = word.lower()
    for suffix in ("ations", "ation", "ings", "ing", "ies", "ed", "es", "s", "e"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[:-len(suffix)]
    return w


def sentences(line):
    for part in re.split(r"(?<=[.!?;:])\s+|\s+\|\s+|^\|\s*|\s*\|$", line):
        part = part.strip()
        if part:
            yield part


def changed(base, head):
    """(deleted lines, [(path, added line)]) of the design prose between two revisions."""
    diff = git("diff", "--unified=0", "--no-color", base, head, "--", "*.md")
    deleted, added, old, new = [], [], None, None
    for line in diff.splitlines():
        if line.startswith("--- "):
            old = line[6:] if line.startswith("--- a/") else None
        elif line.startswith("+++ "):
            new = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith(("@@", "diff ")):
            continue
        elif line.startswith("-") and old and design_prose(old):
            deleted.append(line[1:])
        elif line.startswith("+") and new and design_prose(new):
            added.append((new, line[1:]))
    return deleted, added


def added_sentences(added):
    """(path, sentence) of the added prose, fenced blocks and headings left out."""
    fenced = {}
    for path, line in added:
        if re.match(r"^\s*```", line):
            fenced[path] = not fenced.get(path, False)
            continue
        if fenced.get(path) or re.match(r"^\s*#", line):
            continue
        for sentence in sentences(line):
            yield path, sentence


def marker_names(sentence, only=None):
    return [name for name, rx in MARKERS if (only is None or name in only) and rx.search(sentence)]


def cmd_candidates(args):
    deleted, added = changed(args.base, args.head)
    rows = [(p, marker_names(s), s) for p, s in added_sentences(added) if marker_names(s)]
    print(f"{args.base}..{args.head}: {len(added)} added design-prose lines, {len(deleted)} deleted; "
          f"{len(rows)} candidate sentence(s), "
          f"{sum(1 for _, names, _ in rows if set(names) & STRICT)} by the strict markers")
    for path, names, sentence in rows:
        print(f"  {path.rsplit('/', 1)[-1][:22]:22} {'+'.join(names):22} {sentence[:130]}")


def cmd_history(args):
    counts, per_marker, lines = [], Counter(), 0
    for sha in git("log", f"-{args.n}", "--format=%h", args.rev, "--", "*.md").split():
        try:
            _, added = changed(f"{sha}^", sha)
        except subprocess.CalledProcessError:
            continue
        if not added or len(added) > args.max_lines:
            continue
        rows = [marker_names(s) for _, s in added_sentences(added)]
        rows = [names for names in rows if names]
        for names in rows:
            per_marker.update(names)
        lines += len(added)
        counts.append((sum(1 for names in rows if set(names) & STRICT), len(rows)))
    strict = sorted(c[0] for c in counts)
    every = sorted(c[1] for c in counts)
    print(f"{len(counts)} commits that add design prose, {lines} added lines")
    print(f"strict markers: {sum(1 for n in strict if n)} commits with a candidate, "
          f"median {strict[len(strict) // 2]} per commit")
    print(f"all markers: {sum(1 for n in every if n)} commits with a candidate, "
          f"median {every[len(every) // 2]} per commit")
    for name, n in per_marker.most_common():
        print(f"  {name:12} {n:5}  {100 * n / max(lines, 1):5.2f} per 100 added lines")


def cmd_trace(args):
    term = re.compile(args.term, re.I)
    deleted, added = changed(args.base, args.head)
    per_file = Counter()
    rows = []
    for path, sentence in added_sentences(added):
        names_term = bool(term.search(sentence))
        denies = bool(marker_names(sentence, STRICT))
        if names_term or denies:
            per_file[path] += 1
            rows.append((path, names_term, denies, sentence))
    print(f"{args.base}..{args.head}: trace list of {len(rows)} sentence(s) in {len(per_file)} file(s)")
    for path, names_term, denies, sentence in rows:
        tag = ("term" if names_term else "") + ("+" if names_term and denies else "") + ("denial" if denies else "")
        print(f"  {path.rsplit('/', 1)[-1][:22]:22} {tag:12} {sentence[:130]}")


def cmd_echo(args):
    deleted, added = changed(args.base, args.head)
    removed = Counter(stem(w) for line in deleted for w in words(line) if w.lower() not in STOP)
    base_count, base_lines = Counter(), 0
    for path in git("ls-tree", "-r", "--name-only", args.base).splitlines():
        if design_prose(path):
            for line in git("show", f"{args.base}:{path}").splitlines():
                base_lines += 1
                base_count.update({stem(w) for w in words(line) if w.lower() not in STOP})
    # A term counts as the deleted rule's own when the rest of the repository rarely uses it.
    rare = {s for s in removed if base_count.get(s, 0) <= max(40, base_lines // 200)}
    rows = []
    for path, sentence in added_sentences(added):
        for name, rx in MARKERS:
            for match in rx.finditer(sentence):
                tail = sentence[match.start():match.end()] if name in ("neither-nor", "not-but") \
                    else sentence[match.end():]
                head_words = [w for w in words(tail) if w.lower() not in STOP][:3 if name in ("neither-nor", "not-but") else 2]
                hit = [w for w in head_words if stem(w) in rare]
                if hit:
                    rows.append((path, name, hit, sentence))
    print(f"{args.base}..{args.head}: {len(rare)} terms taken as the deleted rule's own; "
          f"{len(rows)} added sentence(s) deny one")
    for path, name, hit, sentence in rows:
        print(f"  {path.rsplit('/', 1)[-1][:22]:22} {name:12} {','.join(hit):20} {sentence[:110]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    for name, fn in (("candidates", cmd_candidates), ("trace", cmd_trace), ("echo", cmd_echo)):
        p = sub.add_parser(name)
        p.add_argument("base")
        p.add_argument("head")
        if name == "trace":
            p.add_argument("--term", required=True, help="regular expression naming the deleted rule's terms")
        p.set_defaults(fn=fn)
    p = sub.add_parser("history")
    p.add_argument("n", type=int)
    p.add_argument("rev")
    p.add_argument("--max-lines", type=int, default=700,
                   help="leave out a commit that adds more design-prose lines than this")
    p.set_defaults(fn=cmd_history)
    args = parser.parse_args()
    try:
        args.fn(args)
    except subprocess.CalledProcessError as error:
        sys.exit(f"absent_rule_probe: git failed: {error.stderr.strip()}")


if __name__ == "__main__":
    main()
