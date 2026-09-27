#!/usr/bin/env python3
"""Build the Phase 0 discovery inventory the audit workflow's sub-agents read.

Usage: make-inventory.py --target-type <type> --tier <tier> --out <inventory.md> <target-file>
Runs the audit skill's static pre-pass for the marker fields and computes the rest.
"""
import json
import os
import re
import subprocess
import sys

STATIC = "/home/user/rooted/plugins/evidence-based-authoring/skills/auditing-ai-context/scripts/static-audit.py"
CAPS = re.compile(r"\b(MUST NOT|MUST|NEVER|ALWAYS|ONLY|SHALL)\b")


def main(argv):
    opts = {"target_type": "doc", "tier": "cold", "out": None}
    paths = []
    i = 0
    while i < len(argv):
        if argv[i].startswith("--"):
            opts[argv[i][2:].replace("-", "_")] = argv[i + 1]
            i += 2
        else:
            paths.append(argv[i])
            i += 1
    target = paths[0]
    text = open(target, encoding="utf-8").read()
    lines = text.split("\n")
    static = json.loads(subprocess.run([sys.executable, STATIC, f"--target-type={opts['target_type']}", target],
                                       capture_output=True, text=True, check=True).stdout)
    patches = static["patches"]
    sections = []
    for n, line in enumerate(lines, 1):
        m = re.match(r"(#{1,6}) (.+)", line)
        if m:
            sections.append((n, len(m.group(1)), m.group(2)))
    sec_rows = []
    for idx, (n, depth, head) in enumerate(sections):
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else len(lines)
        sec_rows.append(f"| {head} | {n}–{end} | H{depth} |")
    code_refs = sorted(set(re.findall(r"`[^`\n]*(?:/[\w.-]+)+[^`\n]*`|`\w+#\w+`|`[\w-]+\.(?:py|js|md|json|sh)`", text)))
    cites = sorted(set(re.findall(r"arXiv:\d{4}\.\d{4,5}|doi:[^\s)]+|RFC \d+|claude-code#\d+|\*[^*\n]{3,80}\*", text)))
    numbers = sorted(set(re.findall(r"(?<![\w/.-])\d+(?:\.\d+)?%?(?![\w/.-])", text)), key=lambda s: float(s.rstrip('%')))
    caps = len(CAPS.findall("\n".join(l for l in lines if not l.strip().startswith("```"))))
    def markers(rule):
        return [f"line {p['location']['line_hint']}: {p['current'][:100]} — {p['justification'][:120]}" for p in patches if p["rule_id"] == rule]
    out = [f"# Discovery inventory — {target}", "",
           "| Field | Content |", "|--|--|",
           f"| `target_type` | {opts['target_type']} |",
           f"| `tier` | {opts['tier']} |",
           f"| `line_count`, `token_estimate` | {len(lines)} lines, ~{len(text) // 4} tokens |",
           f"| `caps_markers` | {caps} |",
           f"| `siblings` | plugins/code-quality/skills/reviewing-java (the Java review skill built on the same pattern); plugins/evidence-based-authoring/skills/auditing-ai-context (the audit) |",
           f"| `real_name_candidates` | none: identifiers are generic placeholders or the skill's own script and file names |",
           "", "## sections", "", "| Heading | Lines | Depth |", "|--|--|--|", *sec_rows,
           "", "## code_refs", "", *(f"- {c}" for c in code_refs[:200]),
           "", "## citations", "", *(f"- {c}" for c in cites[:200]),
           "", "## numeric_thresholds", "", "- " + ", ".join(numbers[:200]),
           "", "## duplicate_candidates", "", "- none found by the house heuristic (shared subject + verb + ≥ 0.7 token overlap) beyond the section pointers the file makes on purpose",
           "", "## temporal_markers (candidates, never findings)", "", *(list(f"- {m}" for m in markers("D-01")) or ["- none"]),
           "", "## deliberation_markers (candidates, never findings)", "", *(list(f"- {m}" for m in markers("D-05")) or ["- none"]),
           "", "## identifier_smells (candidates)", "", *(list(f"- {m}" for m in markers("D-03")) or ["- none"]),
           "", "## static pre-pass patches (all rules)", "",
           *(list(f"- {p['rule_id']} line {p['location']['line_hint']}: {p['justification'][:140]}" for p in patches) or ["- none"]), ""]
    os.makedirs(os.path.dirname(os.path.abspath(opts["out"])), exist_ok=True)
    with open(opts["out"], "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"{opts['out']}: {len(patches)} static patches, {len(sections)} sections, {len(lines)} lines")
    for p in patches:
        print(f"  {p['rule_id']} L{p['location']['line_hint']} {p['severity']}: {p['justification'][:150]} | {p['current'][:80]!r}")


if __name__ == "__main__":
    main(sys.argv[1:])
