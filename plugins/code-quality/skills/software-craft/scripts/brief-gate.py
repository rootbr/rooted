#!/usr/bin/env python3
"""Check the shape of a design brief (craft/design.md) before the operator confirms it.

The brief's contract is SKILL.md §Phase 3: seven `##` sections in a fixed order, every one
present and non-empty (an empty one says "none"); `## Design` anchors at least one module or
type by `path:Symbol` and ends with `### Decisions`, whose numbered items each carry
`chosen:` and `alternative:`; `## Steps` holds numbered steps that each name a step kind
and a file; `## Failure paths` holds one line per path; `## Tests` entries name a test
location; `## Task` names the write zone as a path; `## Stack` reads its facts from named
files.

Usage:  python3 brief-gate.py <path to design.md> [--json]
Reads the brief; writes nothing; no network; standard library only.
Exit status 0 when the brief has the shape, 1 with one line per defect, 2 when the file
cannot be read.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import STEPS  # noqa: E402

SECTIONS = ("Task", "Stack", "Design", "Failure paths", "Tests", "Steps", "Out of scope")
STEP_KINDS = ("implement", "handle-errors", "test", "refactor", "document")
assert set(STEP_KINDS) < set(STEPS)
DECISIONS = "Decisions"
EMPTY = "none"

H2 = re.compile(r"^##\s+(.+?)\s*$")
H3 = re.compile(r"^###\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(?:`{3,}|~{3,})")
ITEM = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*)$")
NUMBERED = re.compile(r"^\s*\d+[.)]\s+")
EXTENSIONS = ("py", "java", "kt", "ts", "tsx", "js", "jsx", "mjs", "go", "rs", "rb", "php", "cs", "c", "h",
              "cpp", "hpp", "swift", "scala", "sql", "sh", "md", "toml", "yaml", "yml", "json", "xml",
              "gradle", "kts", "cfg", "ini", "txt", "lock", "properties", "proto", "html", "css")
PATH = re.compile(r"(?<![\w.])(?:[\w.-]+/)+[\w.-]*|(?<![\w.])[\w-]+\.(?:%s)\b" % "|".join(EXTENSIONS))
ANCHOR = re.compile(r"`(?:[\w.-]+/)*[\w.-]+\.\w+:[A-Za-z_][\w#.$]*`")
KIND = re.compile(r"(?<![\w-])(?:%s)(?![\w-])" % "|".join(re.escape(k) for k in STEP_KINDS))
CHOSEN = re.compile(r"\bchosen:", re.I)
ALTERNATIVE = re.compile(r"\balternative:", re.I)


def split_sections(text):
    """The `##` sections in document order: a list of (title, lines), lines outside any fence kept
    as they are and fenced lines kept with the section they sit in."""
    sections = []
    current = None
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
        heading = None if fenced else H2.match(line)
        if heading and not line.startswith("###"):
            current = (heading.group(1), [])
            sections.append(current)
        elif current is not None:
            current[1].append(line)
    return sections


def items_of(lines):
    """List items with their continuation lines: a list of (first line text, continuation count)."""
    items = []
    for line in lines:
        if not line.strip():
            continue
        item = ITEM.match(line)
        if item:
            items.append([item.group(1).strip(), 0])
        elif items:
            items[-1][0] += " " + line.strip()
            items[-1][1] += 1
    return items


def body_text(lines):
    return " ".join(line.strip() for line in lines if line.strip())


def is_empty(lines):
    return body_text(lines).strip().lower() in ("", EMPTY, EMPTY + ".")


def check_order(sections):
    titles = [title for title, _ in sections]
    out = []
    for title in SECTIONS:
        if titles.count(title) == 0:
            out.append(("brief", "section `## %s` is missing" % title))
        elif titles.count(title) > 1:
            out.append(("brief", "section `## %s` appears %d times" % (title, titles.count(title))))
    for title in titles:
        if title not in SECTIONS:
            out.append(("brief", "section `## %s` is not one of the seven" % title))
    present = [title for title in titles if title in SECTIONS]
    expected = [title for title in SECTIONS if title in present]
    if present != expected and not any(message.endswith("times") for _, message in out):
        out.append(("brief", "sections are out of order: %s" % ", ".join(present)))
    return out


def check_task(lines):
    if is_empty(lines):
        return [("Task", "the task paragraph and the write zone are missing")]
    if not PATH.search(body_text(lines)):
        return [("Task", "no write-zone path is named")]
    return []


def check_stack(lines):
    if is_empty(lines):
        return []
    if not PATH.search(body_text(lines)):
        return [("Stack", "no fact is read from a named file")]
    return []


def check_design(lines):
    out = []
    before, decisions, seen = [], [], False
    for line in lines:
        heading = H3.match(line)
        if heading and heading.group(1) == DECISIONS and not seen:
            seen = True
            continue
        if heading and seen:
            out.append(("Design", "`### %s` sits after `### %s`" % (heading.group(1), DECISIONS)))
            continue
        (decisions if seen else before).append(line)
    if is_empty(before):
        out.append(("Design", "the solution is missing"))
    elif not ANCHOR.search(body_text(before)):
        out.append(("Design", "no module or type is anchored by `path:Symbol`"))
    if not seen:
        out.append(("Design", "`### %s` is missing" % DECISIONS))
        return out
    if is_empty(decisions):
        return out
    items = items_of(decisions)
    if not items:
        out.append(("Design", "`### %s` holds text that is not a numbered item" % DECISIONS))
    for index, (text, _) in enumerate(items, 1):
        missing = [name for name, pattern in (("chosen:", CHOSEN), ("alternative:", ALTERNATIVE))
                   if not pattern.search(text)]
        if missing:
            out.append(("Design", "decision %d lacks %s" % (index, " and ".join(missing))))
    return out


def check_failure_paths(lines):
    if is_empty(lines):
        return []
    out = []
    items = items_of(lines)
    if not items:
        return [("Failure paths", "the paths are not list items")]
    for index, (_, continuation) in enumerate(items, 1):
        if continuation:
            out.append(("Failure paths", "path %d spans %d lines" % (index, continuation + 1)))
    return out


def check_tests(lines):
    if is_empty(lines):
        return []
    items = items_of(lines)
    if not items:
        return [("Tests", "the behaviours are not list items")]
    return [("Tests", "entry %d names no test location" % index)
            for index, (text, _) in enumerate(items, 1) if not PATH.search(text)]


def check_steps(lines):
    if is_empty(lines):
        return [("Steps", "no step is listed")]
    out = []
    non_blank = [line for line in lines if line.strip()]
    items = items_of(lines)
    if not items or not any(NUMBERED.match(line) for line in non_blank):
        return [("Steps", "the steps are not numbered items")]
    for index, (text, _) in enumerate(items, 1):
        if not KIND.search(text):
            out.append(("Steps", "step %d names no kind (%s)" % (index, ", ".join(STEP_KINDS))))
        if not PATH.search(text):
            out.append(("Steps", "step %d names no file" % index))
    return out


def check_out_of_scope(lines):
    if not body_text(lines):
        return [("Out of scope", "the section is empty; an empty one says none")]
    return []


CHECKS = {"Task": check_task, "Stack": check_stack, "Design": check_design,
          "Failure paths": check_failure_paths, "Tests": check_tests, "Steps": check_steps,
          "Out of scope": check_out_of_scope}


def defects(text):
    sections = split_sections(text)
    out = check_order(sections)
    seen = set()
    for title, lines in sections:
        if title in CHECKS and title not in seen:
            seen.add(title)
            if not body_text(lines) and title != "Out of scope":
                out.append((title, "the section is empty; an empty one says none"))
            else:
                out.extend(CHECKS[title](lines))
    return out


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    if len(args) != 1:
        sys.stderr.write(__doc__)
        return 2
    path = args[0]
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        sys.stderr.write("brief-gate: cannot read %s: %s\n" % (path, error))
        return 2
    found = defects(text)
    if as_json:
        print(json.dumps({"path": path, "defects": [{"section": s, "message": m} for s, m in found]}, indent=1))
    else:
        for section, message in found:
            print("%s: %s: %s" % (path, section, message))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
