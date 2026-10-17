#!/usr/bin/env python3
"""Check that every skill keeps what a run loads or executes apart from what a maintainer reads.

The run set of a skill is SKILL.md, references/, scripts/, agents/ and assets/, and the
plugin-level agents/*.md beside its plugin's skills; the maintainer set is maintenance/ and
evals/ (README.md §Skill layout). A skill is a directory plugins/<plugin>/skills/<name>/ that
holds a SKILL.md. Rules:
  a  no run-set file contains "maintenance/" or "evals/"; SKILL.md may name
     "maintenance/README.md" on one line
  b  no file under references/ or scripts/, outside a card corpus references/*-cards*/, has a
     name matching MAINTAINER_NAMES, and no tests/ directory sits under scripts/
  c  no run-set file contains a phrase of AUTHORING_PHRASES
  d  every card corpus references/<corpus>/ (<corpus> matching *-cards*) has its provenance map
     maintenance/<corpus>-provenance.md
  e  a skill with maintenance/ has maintenance/README.md and a README.md with a "## Layout" heading
  f  the two files of each SYNC_PAIRS entry are byte-identical; the first is the canonical one
  g  no run-set Markdown file carries a provenance note outside code spans and fences: a
     citation bracket (a bracketed source locator, eval expectation or evidence verdict), an
     eval expectation tag `eval <name> E<n>`, or a fetch marker such as (fetched) or
     **unfetched**; the source behind a rule stands on its line in
     maintenance/<name>-provenance.md, and a card corpus keeps the compact `## Source`
     locator its taxonomy documents

Usage:  python3 check-skill-layout.py [--root <repository>] [--table]
--table prints, per skill, the layout the check derives: each top-level entry and its set.
Reads only the repository; writes nothing; no network; standard library only.
Exit status 0 when no rule is violated, 1 with one line per violation.
"""
import fnmatch
import os
import re
import sys

RUN_DIRS = ("references", "scripts", "agents", "assets")
MAINTAINER_DIRS = ("maintenance", "evals")
FORBIDDEN = ("maintenance/", "evals/")
POINTER = "maintenance/README.md"
MAINTAINER_NAMES = ("*provenance*", "*taxonomy*", "pending-evidence*", "maintenance*", "validate-*",
                    "check-*-cards*", "*-topic-workflow*", "research-*", "harvest-*", "write-topic-*")
AUTHORING_PHRASES = ("authoring time only", "never part of a build or a review")
CORPUS = "*-cards*"
LAYOUT_HEADING = re.compile(r"^## Layout\s*$", re.M)

# Rule g. A bracket is a citation when it holds a source locator, an eval expectation, an evidence
# verdict or two author-year pairs; a Markdown link, a footnote and a reference-style link are not.
FENCE = re.compile(r"^\s*(?:`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`[^`\n]*`")
BRACKET = re.compile(r"\[(?!\^)([^\[\]\n]+)\](?![\(\[])")
SOURCE_ID = re.compile(r"arXiv:\d{4}\.\d{4,5}|\bdoi:\s*10\.|\b10\.\d{4,9}/\S|https?://|\bDOT/FAA/|\bRFC ?\d{3,5}\b|\bREADME \d+\b")
AUTHOR_YEAR = re.compile(r"\b[A-Z][A-Za-z'’-]+(?: et al\.)?(?: & [A-Z][A-Za-z'’-]+)? (?:19|20)\d\d\b")
EVIDENCE_VERDICT = re.compile(r"\b(?:untested|not opened|no source|no opened study|first-hand|relay(?:ed)?|consistent only|definition)\b")
EVAL_TAG = re.compile(r"\beval [a-z][a-z0-9-]* E\d+\b")
FETCH_MARKER = re.compile(r"\((?:un)?fetched\)|\(relayed\)|\*\*(?:un)?fetched\*\*|\*\*relayed\*\*")

# (canonical, copy): the copy is kept byte-identical to the canonical file.
SYNC_PAIRS = (
    ("plugins/evidence-based-authoring/skills/auditing-ai-context/references/kb-card-specification.md",
     "plugins/evidence-based-authoring/skills/reading-companion/references/kb-card-specification.md"),
)


def visible(name):
    return not name.startswith(".") and name != "__pycache__"


def walk_files(top):
    """Every file under top, hidden entries and __pycache__ pruned; [] when top is absent."""
    found = []
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames[:] = sorted(d for d in dirnames if visible(d))
        found += [os.path.join(dirpath, f) for f in sorted(filenames) if visible(f)]
    return found


def skills(root):
    base = os.path.join(root, "plugins")
    found = []
    for plugin in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        skills_dir = os.path.join(base, plugin, "skills")
        for name in sorted(os.listdir(skills_dir)) if os.path.isdir(skills_dir) else []:
            if visible(name) and os.path.isfile(os.path.join(skills_dir, name, "SKILL.md")):
                found.append(os.path.join(skills_dir, name))
    return found


def plugin_agents(root):
    base = os.path.join(root, "plugins")
    found = []
    for plugin in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        agents = os.path.join(base, plugin, "agents")
        if os.path.isdir(agents):
            found += [os.path.join(agents, f) for f in sorted(os.listdir(agents)) if f.endswith(".md") and visible(f)]
    return found


def run_set(skill):
    return [os.path.join(skill, "SKILL.md")] + [f for d in RUN_DIRS for f in walk_files(os.path.join(skill, d))]


def read_text(path):
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8", errors="replace")


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def is_citation(content):
    return bool(SOURCE_ID.search(content) or EVAL_TAG.search(content) or EVIDENCE_VERDICT.search(content)
                or len(AUTHOR_YEAR.findall(content)) >= 2)


def check_provenance(key, number, prose, out):
    """Rule g over one line of run-set prose with its code spans removed."""
    for match in BRACKET.finditer(prose):
        if is_citation(match.group(1)):
            out.append(f"{key}:{number}: g: a citation bracket in a run-set file: [{match.group(1)[:60]}]")
    if EVAL_TAG.search(BRACKET.sub("", prose)):
        out.append(f"{key}:{number}: g: an eval expectation tag in a run-set file")
    if FETCH_MARKER.search(prose):
        out.append(f"{key}:{number}: g: a fetch marker in a run-set file")


def check_names(root, path, out):
    """Rules a, c and g over one run-set file."""
    text = read_text(path)
    key = rel(root, path)
    is_skill_md = os.path.basename(path) == "SKILL.md"
    is_markdown = path.endswith(".md")
    pointer_lines = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if is_skill_md and POINTER in line:
            pointer_lines.append(number)
            line = line.replace(POINTER, "")
        for needle in FORBIDDEN:
            if needle in line:
                out.append(f"{key}:{number}: a: a run-set file names \"{needle}\"")
        lowered = line.lower()
        for phrase in AUTHORING_PHRASES:
            if phrase in lowered:
                out.append(f"{key}:{number}: c: a run-set file carries \"{phrase}\"")
        if is_markdown:
            if FENCE.match(line):
                in_fence = not in_fence
            elif not in_fence:
                check_provenance(key, number, INLINE_CODE.sub("", line), out)
    if len(pointer_lines) > 1:
        out.append(f"{key}:{pointer_lines[1]}: a: SKILL.md names \"{POINTER}\" on more than one line "
                   f"(lines {', '.join(map(str, pointer_lines))})")


def check_skill(root, skill, out):
    for path in run_set(skill):
        if os.path.isfile(path):
            check_names(root, path, out)
    for top in ("references", "scripts"):
        for path in walk_files(os.path.join(skill, top)):
            parts = os.path.relpath(path, skill).split(os.sep)
            if top == "references" and len(parts) > 2 and fnmatch.fnmatch(parts[1], CORPUS):
                continue
            name = parts[-1]
            if any(fnmatch.fnmatch(name, pattern) for pattern in MAINTAINER_NAMES):
                out.append(f"{rel(root, path)}: b: a maintainer file under {top}/")
    for dirpath, dirnames, _ in os.walk(os.path.join(skill, "scripts")):
        dirnames[:] = [d for d in dirnames if visible(d)]
        if "tests" in dirnames:
            out.append(f"{rel(root, os.path.join(dirpath, 'tests'))}/: b: a tests directory under scripts/")
    references = os.path.join(skill, "references")
    for corpus in sorted(os.listdir(references)) if os.path.isdir(references) else []:
        if os.path.isdir(os.path.join(references, corpus)) and fnmatch.fnmatch(corpus, CORPUS):
            map_path = os.path.join(skill, "maintenance", corpus + "-provenance.md")
            if not os.path.isfile(map_path):
                out.append(f"{rel(root, map_path)}: d: the provenance map of references/{corpus}/ is missing")
    if os.path.isdir(os.path.join(skill, "maintenance")):
        if not os.path.isfile(os.path.join(skill, "maintenance", "README.md")):
            out.append(f"{rel(root, skill)}/maintenance/README.md: e: missing")
        readme = os.path.join(skill, "README.md")
        if not os.path.isfile(readme):
            out.append(f"{rel(root, readme)}: e: missing")
        elif not LAYOUT_HEADING.search(read_text(readme)):
            out.append(f"{rel(root, readme)}: e: no \"## Layout\" heading")


def check_sync(root, pairs, out):
    for canonical, copy in pairs:
        paths = [os.path.join(root, canonical), os.path.join(root, copy)]
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            out += [f"{rel(root, p)}: f: missing (synced with {copy if p == paths[0] else canonical})" for p in missing]
            continue
        with open(paths[0], "rb") as a, open(paths[1], "rb") as b:
            if a.read() != b.read():
                out.append(f"{copy}: f: differs from {canonical}; copy the canonical file over it")


def scan(root, sync_pairs=None):
    """Return the violations under root, one line each."""
    sync_pairs = SYNC_PAIRS if sync_pairs is None else sync_pairs
    out = []
    for skill in skills(root):
        check_skill(root, skill, out)
    for path in plugin_agents(root):
        check_names(root, path, out)
    check_sync(root, sync_pairs, out)
    return out


def describe(path):
    if os.path.isdir(path):
        n = len(walk_files(path))
        return f"{os.path.basename(path)}/ {n} file{'s' if n != 1 else ''}"
    return os.path.basename(path)


def table(root):
    """The derived layout: per skill, its top-level entries by set."""
    lines = []
    for skill in skills(root):
        groups = {"run": [], "maintainer": [], "other": []}
        for name in sorted(os.listdir(skill)):
            if not visible(name):
                continue
            kind = ("run" if name == "SKILL.md" or name in RUN_DIRS
                    else "maintainer" if name in MAINTAINER_DIRS else "other")
            groups[kind].append(describe(os.path.join(skill, name)))
        lines.append(rel(root, skill))
        for kind in ("run", "maintainer", "other"):
            if groups[kind]:
                lines.append(f"  {kind:<11} {' · '.join(groups[kind])}")
    return lines


def main(argv):
    root = os.path.dirname(os.path.abspath(__file__))
    show_table = False
    i = 0
    while i < len(argv):
        if argv[i] == "--root" and i + 1 < len(argv):
            root = os.path.abspath(argv[i + 1])
            i += 2
        elif argv[i] == "--table":
            show_table = True
            i += 1
        else:
            sys.exit(f"check-skill-layout: unexpected argument {argv[i]!r}\n{__doc__}")
    if show_table:
        print("\n".join(table(root)))
    violations = scan(root)
    for line in violations:
        print(line)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
