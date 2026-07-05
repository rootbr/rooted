#!/usr/bin/env python3
"""Static (no-LLM) pre-pass of the auditing-ai-context workflow.

Covers the statically checkable validators so their cards need no LLM sub-agent:
R-01 (name platform spec), R-02 (description platform spec), R-10 (line budget),
R-20 (heading depth), R-27 (emphasis-density trigger — judging the flagged spans
rides the needs_human review), R-42 (absolute / backslash paths), R-62 (ALL-CAPS
marker count). Findings that need judgment carry needs_human=true; the LLM
dispatch omits R-20 / R-27 / R-42 / R-62 when this pre-pass has run, and still
runs R-01 / R-02 / R-10 for their semantic halves.

Usage:  python3 static-audit.py <context-file.md> [...]
Reads only the files passed as arguments; writes nothing; no network; stdlib only.
Emits {"patches": [...], "files_scanned": N} on stdout in the workflow patch shape.
"""
import json
import re
import sys

CAPS = re.compile(r"\b(MUST NOT|MUST|NEVER|ALWAYS|ONLY|SHALL)\b")
XML_TAG = re.compile(r"<[a-zA-Z/][^<>]*>")
ABS_PATH = re.compile(r"(/Users/|/home/|/opt/|C:\\)")
BACKSLASH_REL = re.compile(r"\b[\w.-]+\\[\w.-]+")
BOLD = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
NAME_OK = re.compile(r"[a-z0-9-]+\Z")


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    fm = m.group(1)
    out = {}
    for key in ("name", "description", "title"):
        km = re.search(rf"^{key}: (.+?)(?=\n[a-zA-Z_-]+:|\Z)", fm, re.M | re.S)
        if km:
            val = km.group(1).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            out[key] = val
    return out


def patch(rule, section, line, current, justification, severity, needs_human):
    return {
        "rule_id": rule,
        "location": {"section": section, "line_hint": line},
        "current": current,
        "proposed": None,
        "justification": justification,
        "severity": severity,
        "needs_human": needs_human,
        "meta": {"static": True},
    }


def scan(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    fm = frontmatter(text)
    patches = []

    name = fm.get("name")
    if name is not None:
        bad = []
        if len(name) > 64:
            bad.append(f"{len(name)} chars > 64")
        if not NAME_OK.fullmatch(name):
            bad.append("chars outside [a-z0-9-]")
        if XML_TAG.search(name):
            bad.append("XML tag")
        if "anthropic" in name or "claude" in name:
            bad.append("reserved word")
        if bad:
            patches.append(patch("R-01", "frontmatter", 2, name,
                                 f"name violates platform spec: {'; '.join(bad)}", "high", True))

    desc = fm.get("description")
    if desc is not None:
        bad = []
        if not desc:
            bad.append("empty")
        if len(desc) > 1024:
            bad.append(f"{len(desc)} chars > 1024")
        if XML_TAG.search(desc):
            bad.append(f"XML tag {XML_TAG.search(desc).group(0)!r}")
        if bad:
            patches.append(patch("R-02", "frontmatter", 3, desc[:80],
                                 f"description violates platform spec: {'; '.join(bad)}", "high", True))

    if len(lines) > 500:
        patches.append(patch("R-10", "(whole file)", 1, f"{len(lines)} lines",
                             "file exceeds the 500-line skill budget (95% of Skills fit it)",
                             "medium", True))

    in_fence = False
    section = "(preamble)"
    caps_hits = []
    bold_count = 0
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            m = ABS_PATH.search(line) or BACKSLASH_REL.search(line)
            if m and "good:" in line:
                patches.append(patch("R-42", section, i, line.strip(),
                                     "absolute/backslash path inside a fenced block marked as a good example",
                                     "high", True))
            continue
        hm = re.match(r"(#{1,6}) (.+)", line)
        if hm:
            section = hm.group(2)
            if len(hm.group(1)) >= 4:
                patches.append(patch("R-20", section, i, line.strip(),
                                     f"heading depth H{len(hm.group(1))} — hierarchy should stay flat (≤H3)",
                                     "low", True))
            continue
        caps_hits.extend((i, w) for w in CAPS.findall(line))
        bold_count += len(BOLD.findall(line))
        pm = ABS_PATH.search(line)
        if pm:
            patches.append(patch("R-42", section, i, line.strip(),
                                 f"absolute path {pm.group(0)!r} in instruction prose",
                                 "high", True))
        bm = BACKSLASH_REL.search(line)
        if bm and "\\n" not in bm.group(0):
            patches.append(patch("R-42", section, i, line.strip(),
                                 f"backslash path {bm.group(0)!r} — forward slashes required",
                                 "high", True))

    if len(caps_hits) > 3:
        first = caps_hits[0][0]
        patches.append(patch("R-62", "(whole file)", first,
                             f"{len(caps_hits)} ALL-CAPS markers",
                             f"{len(caps_hits)} ALL-CAPS prohibition markers exceed the ≤3 ceiling",
                             "medium", True))
    density = bold_count * 100 / max(len(lines), 1)
    if density > 10:
        patches.append(patch("R-27", "(whole file)", 1,
                             f"{bold_count} bold spans / {len(lines)} lines",
                             f"emphasis density {density:.0f} per 100 lines exceeds the ~10 house threshold",
                             "low", True))
    return patches


def main():
    all_patches = []
    for path in sys.argv[1:]:
        for p in scan(path):
            p["file"] = path
            all_patches.append(p)
    json.dump({"patches": all_patches, "files_scanned": len(sys.argv) - 1}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
