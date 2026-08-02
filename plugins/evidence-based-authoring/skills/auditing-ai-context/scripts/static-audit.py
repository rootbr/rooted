#!/usr/bin/env python3
"""Static (no-LLM) pre-pass of the auditing-ai-context workflow.

Covers the statically checkable validators so their cards need no LLM sub-agent:
R-01 (name platform spec), R-02 (description platform spec), R-10 (line budget),
R-20 (heading depth), R-27 (emphasis-density trigger — judging the flagged spans
rides the needs_human review), R-42 (absolute / backslash paths), R-62 (ALL-CAPS
marker count). Findings that need judgment carry needs_human=true; the LLM
dispatch omits R-20 / R-27 / R-42 / R-62 when this pre-pass has run, and still
runs R-01 / R-02 / R-10 for their semantic halves.

It also fills the Phase 0 marker inventory: D-01 temporal / contrast markers,
D-05 deliberation markers, D-03 identifier smells, D-04 commented-out code, and
R-57's dates, version numbers and ticket ids attached to a line. A marker emitter
locates a candidate and never rules on it — "legacy" and "considered" have
innocent present-tense uses, and the systematic error on this axis is
over-flagging — so every marker patch carries proposed=null and needs_human=true
and its card still dispatches to decide the disposition.

Each check belongs to a target type, and a marker emitter runs only on the target
types its card's applies_to_target facet lists. A Markdown target — every type
but `code` — runs the Markdown check set, over prose outside fenced blocks. A
`code` target runs R-42, D-01, D-04 and R-57 over its comment spans, and D-03
over the whole source, because an identifier is code rather than prose. The
remaining checks read Markdown syntax that a source file does not carry, so a `#`
comment would parse as a heading (R-20), a MUST inside a string literal would
count toward the caps ceiling (R-62), and the 500-line skill budget (R-10) does
not govern source files.

Usage:  python3 static-audit.py [--target-type=<type>] <file> [...]
The flag applies to every path after it and may be repeated to mix target types in
one run; it defaults to `context-file`. Types are the workflow's own vocabulary:
context-file, skill, agent-prompt, kb-card, kb-corpus, doc, answer, code.
Reads only the files passed as arguments; writes nothing; no network; stdlib only.
Emits {"patches": [...], "files_scanned": N} on stdout in the workflow patch shape.
"""
import json
import os
import re
import sys

CAPS = re.compile(r"\b(MUST NOT|MUST|NEVER|ALWAYS|ONLY|SHALL)\b")
XML_TAG = re.compile(r"<[a-zA-Z/][^<>]*>")
ABS_PATH = re.compile(r"(/Users/|/home/|/opt/|C:\\)")
BACKSLASH_REL = re.compile(r"\b[\w.-]+\\[\w.-]+")
BOLD = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
NAME_OK = re.compile(r"[a-z0-9-]+\Z")

MARKDOWN_TARGETS = ("context-file", "skill", "agent-prompt", "kb-card", "kb-corpus",
                    "doc", "answer")
CODE_TARGETS = ("code",)
TARGET_TYPES = MARKDOWN_TARGETS + CODE_TARGETS

# One gate per marker emitter, copied from that card's applies_to_target facet.
# An emitter that fires on a type its card excludes hands the audit a finding no
# sub-agent will ever adjudicate, so the gate is the emitter's precondition rather
# than a filter applied to its output.
D01_TARGETS = ("context-file", "skill", "agent-prompt", "doc", "code")
D03_TARGETS = ("code", "doc")
D04_TARGETS = ("code",)
D05_TARGETS = ("doc", "context-file", "skill", "agent-prompt")
R57_TARGETS = ("context-file", "skill", "agent-prompt", "doc", "code")
MARKER_GATES = (("D-01", D01_TARGETS), ("D-03", D03_TARGETS), ("D-04", D04_TARGETS),
                ("D-05", D05_TARGETS), ("R-57", R57_TARGETS))

LINE_COMMENT_PREFIXES = {
    ".py": ("#",), ".rb": ("#",), ".pl": ("#",), ".r": ("#",),
    ".sh": ("#",), ".bash": ("#",), ".zsh": ("#",),
    ".yml": ("#",), ".yaml": ("#",), ".toml": ("#",),
    ".c": ("//",), ".h": ("//",), ".cc": ("//",), ".cpp": ("//",), ".hpp": ("//",),
    ".cs": ("//",), ".go": ("//",), ".java": ("//",), ".js": ("//",), ".jsx": ("//",),
    ".kt": ("//",), ".mjs": ("//",), ".php": ("//", "#"), ".rs": ("//",),
    ".scala": ("//",), ".swift": ("//",), ".ts": ("//",), ".tsx": ("//",),
    ".hs": ("--",), ".lua": ("--",), ".sql": ("--",),
}
# An extension the table does not name falls back to the union of the three prefixes.
# The widened scan costs a stray false positive; the alternative — treating an unknown
# extension as commentless — returns an empty patch list no reader can tell from a
# clean file, the one audit outcome that hides a miss.
FALLBACK_PREFIXES = ("#", "//", "--")
BLOCK_DELIMITERS = (("/*", "*/"), ('"""', '"""'), ("'''", "'''"))


def word_alt(phrases):
    """A word-boundary-anchored alternation over the given phrases.

    The boundaries are the point. A bare substring needle matches `old` inside
    `threshold`, `since` inside `sincerely` and `legacy` inside `LegacyMode`,
    which is how a marker list turns into noise the reader learns to skip.
    Whitespace inside a phrase is matched as a run, so "used  to" hits as well.
    """
    joined = "|".join(r"\s+".join(re.escape(w) for w in p.split()) for p in phrases)
    return rf"\b(?:{joined})\b"


def ident_smell_pattern(prefixes, suffixes):
    """Identifier smells, in the casings a codebase actually writes them in —
    Pascal and camel for both halves, snake and screaming-snake beside them.

    Case is load-bearing rather than incidental: requiring an upper-case or digit
    after the prefix separates `TempFile` from `Template` and `NewParser` from
    `Newton`, and the leading boundary separates `Old*` from `threshold`.
    """
    alts = []
    for prefix in prefixes:
        alts += [rf"{prefix}[A-Z0-9]\w*", rf"{prefix.lower()}[A-Z0-9]\w*",
                 rf"{prefix.lower()}_\w+", rf"{prefix.upper()}_\w+"]
    for suffix in suffixes:
        alts += [rf"\w+{suffix}\b", rf"\w+_{suffix.lower()}\b",
                 rf"\w+_{suffix.upper()}\b"]
    alts.append(r"\w+V[23]\b")
    return re.compile(r"\b(?:" + "|".join(alts) + r")")


# Each vocabulary is copied from the Validator of the card that names it, so a
# card edit maps to one line here. Every needle is boundary-anchored.
TEMPORAL_WORDS = ("previously", "formerly", "originally", "in the past",
                  "historically", "used to", "no longer", "not anymore", "we now",
                  "instead of", "replaced", "switched from", "migrated from",
                  "changed from", "rewrote", "deprecated", "legacy", "old-style",
                  "modified by")
DELIBERATION_WORDS = ("chosen", "adopted", "deliberately", "consciously",
                      "intentionally", "considered", "rejected", "alternative",
                      "alternatives", "if needed", "in case")
IDENT_PREFIXES = ("New", "Old", "Legacy", "Temp")
IDENT_SUFFIXES = ("Improved", "Refactored", "Compat", "Shim")

# Three of D-01's markers are patterns rather than words. `was` counts only where a
# contrasting `now` follows it inside the same sentence — a bare `was` is the
# innocent past tense the card's own Limits warn about — so the span is bounded by
# sentence punctuation instead of running to the end of the line. `before` takes the
# same treatment for the same reason, and it is the stronger case: bare, it matched
# 331 lines of this repository's own Markdown against 2 for the contrastive form, so
# 99% of its output would have been the temporal-ordering sense ("close before
# flush"), which states nothing about a superseded design.
TEMPORAL_MARKER = re.compile(word_alt(TEMPORAL_WORDS)
                             + r"|\b(?:was|were)\b[^.!?\n]{0,120}\bnow\b"
                             + r"|(?:^|[.!?]\s+)Before,"
                             + r"|\bbefore\b[^.!?\n]{0,120}\bnow\b"
                             + r"|\bnow\b[^.!?\n]{0,120}\bbefore\b"
                             + r"|\bdoesn[’']t\s+suit\s+us\b", re.I)
# "options:" keeps its colon and the requirement verbs stay bound to their noun.
# Each bare word names a live thing as often as a catalogue, so the punctuation
# and the noun are what make the hit a candidate rather than a dictionary lookup.
DELIBERATION_MARKER = re.compile(word_alt(DELIBERATION_WORDS)
                                 + r"|\boptions:"
                                 + r"|\brequirements?\s+(?:lifted|relaxed|dropped)\b",
                                 re.I)
IDENT_SMELL = ident_smell_pattern(IDENT_PREFIXES, IDENT_SUFFIXES)
# A ticket id is upper-case by construction, so the class stays case-sensitive
# while the word in front of it accepts a sentence-initial capital.
PROVENANCE_TAG = re.compile(r"\b[Ss]ince\s+[A-Z][A-Z0-9]*-\d+\b"
                            r"|\b[Aa]dded\s+in\s+v\d"
                            r"|\((?:[Pp]ost-refactor|[Ll]egacy)\)")
# The call form binds the paren to the name, as the card writes it. A space in
# front makes it a prose parenthetical — "the heading (R-20)" — and admitting one
# turns every cross-reference in a doc-comment into a disabled-code candidate.
STATEMENT_SYNTAX = re.compile(r";\s*$|[{}]|=|\b[A-Za-z_]\w*\(")


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


def die(message):
    sys.exit(f"static-audit: {message}")


def check_marker_gates():
    """Reject a gate naming a target type the workflow does not have.

    A typo in a gate silently disables its emitter, and an emitter that produces
    nothing is indistinguishable from a clean file — the one audit outcome that
    hides a miss. Run at import so the run dies instead."""
    for rule, types in MARKER_GATES:
        unknown = [t for t in types if t not in TARGET_TYPES]
        if unknown:
            die(f"{rule} gate names unknown target type(s) {', '.join(unknown)} "
                f"(expected from {'|'.join(TARGET_TYPES)})")


check_marker_gates()


def scan(path, target_type="context-file"):
    """Run the check set the target type earns. A source file and a Markdown
    document share no syntax, so they share no check set."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if target_type in MARKDOWN_TARGETS:
        return scan_markdown(text, target_type)
    if target_type in CODE_TARGETS:
        return scan_code(path, text, target_type)
    die(f"unknown target type {target_type!r} (expected one of {'|'.join(TARGET_TYPES)})")


def block_comment_state(line):
    """Return (the line opens a block comment, the delimiter still to close it).

    The opener has to start the line. A `/*` or `\"\"\"` further in is more often a
    glob or a string literal, and reading one as an opener starts a block that
    never closes — every following line of the file would then count as a comment.
    """
    stripped = line.lstrip()
    for opener, closer in BLOCK_DELIMITERS:
        if not stripped.startswith(opener):
            continue
        if stripped.find(closer, len(opener)) < 0:
            return True, closer
        return True, None
    return False, None


def comment_prefixes(path):
    """The line-comment markers for a path's language, or the union fallback."""
    return LINE_COMMENT_PREFIXES.get(os.path.splitext(path)[1].lower(), FALLBACK_PREFIXES)


def comment_lines(path, text):
    """Yield (line number, line) for every comment and doc-comment line.

    Deliberately syntax-light, and it errs in both directions: a comment trailing
    code on the same line is skipped, because the `//` in `"http://x"` is
    indistinguishable from a comment marker without parsing string literals; a
    whole-line delimiter inside a multi-line string reads as a comment. Both keep
    the extractor short of a per-language parser, at the cost of missing a path
    that appears only in a trailing comment.
    """
    prefixes = comment_prefixes(path)
    pending = None
    for i, line in enumerate(text.split("\n"), 1):
        if pending is not None:
            yield i, line
            if pending in line:
                pending = None
            continue
        if line.lstrip().startswith(prefixes):
            yield i, line
            continue
        opens, pending = block_comment_state(line)
        if opens:
            yield i, line


def strip_marker(line, prefixes):
    """A comment line's text with its marker removed. A block-comment body carries
    no marker of its own and comes back with only its indentation gone."""
    stripped = line.strip()
    for marker in tuple(prefixes) + ("/*", "*/", '"""', "'''"):
        if stripped.startswith(marker):
            return stripped[len(marker):]
    return stripped


def hits(pattern, line):
    """Every distinct match on the line, in the order the line carries them."""
    found = []
    for m in pattern.finditer(line):
        if m.group(0) not in found:
            found.append(m.group(0))
    return found


def marker_patches(rule, pattern, section, i, line, kind, severity):
    """One patch per line carrying markers of one class, naming each needle that hit.

    The patch reports a located candidate, not a verdict: the card's binary
    question is a reading call, so the disposition stays with the sub-agent that
    owns the card and the patch proposes nothing.
    """
    found = hits(pattern, line)
    if not found:
        return []
    listed = ", ".join(repr(h) for h in found)
    return [patch(rule, section, i, line.strip(),
                  f"{kind}: {listed} — a candidate for review, not a finding",
                  severity, True)]


def identifier_patches(section, i, line):
    """D-03 candidates: one patch per name, since that card's `current` is the
    identifier rather than the line it sits on."""
    return [patch("D-03", section, i, name,
                  f"identifier {name!r} may encode a superseded design — confirm the "
                  "version, twin or original it contrasts with still exists in the repo",
                  "low", True)
            for name in hits(IDENT_SMELL, line)]


def line_marker_patches(target_type, section, i, line):
    """The three prose-marker emitters, each gated by its own card's facet. A
    sentence earns the same three checks whether it sits in a Markdown body or in
    a source file's comment span, so both scanners route through here."""
    found = []
    if target_type in D01_TARGETS:
        found += marker_patches("D-01", TEMPORAL_MARKER, section, i, line,
                                "temporal / contrast marker", "medium")
    if target_type in D05_TARGETS:
        found += marker_patches("D-05", DELIBERATION_MARKER, section, i, line,
                                "deliberation / search marker", "medium")
    if target_type in R57_TARGETS:
        found += marker_patches("R-57", PROVENANCE_TAG, section, i, line,
                                "date / version / ticket id attached to a line", "low")
    return found


def markdown_marker_patches(target_type, section, i, line):
    """Every marker emitter one line of a Markdown target earns. D-03 joins the
    three prose checks here because on a `doc` its subject is the identifier as
    the prose names it."""
    found = line_marker_patches(target_type, section, i, line)
    if target_type in D03_TARGETS:
        found += identifier_patches(section, i, line)
    return found


def commented_out_runs(path, text):
    """Yield each run of two or more consecutive comment lines carrying statement
    syntax, as a list of (line number, line).

    Two consecutive lines is what separates disabled code from prose: a single
    comment mentioning `foo(x)` is a reference, while two in a row that each end
    in `;` or carry a brace or an assignment are a block someone switched off.
    """
    prefixes = comment_prefixes(path)
    run = []
    for i, line in comment_lines(path, text):
        body = strip_marker(line, prefixes)
        carries = bool(body.strip()) and bool(STATEMENT_SYNTAX.search(body))
        if carries and (not run or i == run[-1][0] + 1):
            run.append((i, line))
            continue
        if len(run) > 1:
            yield run
        run = [(i, line)] if carries else []
    if len(run) > 1:
        yield run


def commented_out_patches(path, text):
    """D-04 candidates. The pre-pass reads syntax and cannot answer the card's
    question — would this compile with the markers removed — for a usage example
    inside a doc-comment, which is the ambiguity the card reserves needs_human
    for. So every static hit carries it, and D-04 still dispatches."""
    return [patch("D-04", "(comments)", run[0][0],
                  "\n".join(line for _, line in run),
                  f"{len(run)} consecutive comment lines carry statement syntax — "
                  "disabled code, or an interface example that stays",
                  "medium", True)
            for run in commented_out_runs(path, text)]


def scan_code(path, text, target_type="code"):
    """R-42, D-01 and R-57 over the prose attached to code, plus D-04 over its
    comment runs. A path or a marker in a string literal is data the program uses,
    not an instruction a reader follows, so those three read comments only. D-03
    is the exception its card states: an identifier is code, so it reads the whole
    source, and each patch records which half of the file the name came from."""
    patches = []
    for i, line in comment_lines(path, text):
        pm = ABS_PATH.search(line)
        if pm:
            patches.append(patch("R-42", "(comments)", i, line.strip(),
                                 f"absolute path {pm.group(0)!r} in a comment",
                                 "high", True))
        bm = BACKSLASH_REL.search(line)
        if bm and "\\n" not in bm.group(0):
            patches.append(patch("R-42", "(comments)", i, line.strip(),
                                 f"backslash path {bm.group(0)!r} — forward slashes required",
                                 "high", True))
        patches += line_marker_patches(target_type, "(comments)", i, line)
    if target_type in D04_TARGETS:
        patches += commented_out_patches(path, text)
    if target_type in D03_TARGETS:
        for i, line in enumerate(text.split("\n"), 1):
            patches += identifier_patches("(source)", i, line)
    return patches


def scan_markdown(text, target_type="context-file"):
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
            if target_type in D03_TARGETS:
                patches += identifier_patches(section, i, line)
            continue
        hm = re.match(r"(#{1,6}) (.+)", line)
        if hm:
            section = hm.group(2)
            if len(hm.group(1)) >= 4:
                patches.append(patch("R-20", section, i, line.strip(),
                                     f"heading depth H{len(hm.group(1))} — hierarchy should stay flat (≤H3)",
                                     "low", True))
            patches += markdown_marker_patches(target_type, section, i, line)
            continue
        patches += markdown_marker_patches(target_type, section, i, line)
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


def parse_argv(argv):
    """Pair each path with the target type in force when it was named."""
    target_type = "context-file"
    targets = []
    for arg in argv:
        if arg.startswith("--target-type="):
            target_type = arg.split("=", 1)[1]
            if target_type not in TARGET_TYPES:
                die(f"unknown --target-type {target_type!r} "
                    f"(expected one of {'|'.join(TARGET_TYPES)})")
            continue
        targets.append((arg, target_type))
    return targets


def main():
    targets = parse_argv(sys.argv[1:])
    all_patches = []
    for path, target_type in targets:
        for p in scan(path, target_type):
            p["file"] = path
            all_patches.append(p)
    json.dump({"patches": all_patches, "files_scanned": len(targets)}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
