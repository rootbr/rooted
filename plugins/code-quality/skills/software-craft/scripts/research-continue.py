#!/usr/bin/env python3
"""Continue a research-topic run from its journal: write bundles of
scripts/research-topic-workflow.js that carry the finished stages as `resume_state`, so
only the unfinished drafts, verdicts, fixes and second verdicts run live.

The workflow runtime's own resume replays the unchanged prefix of agent calls and runs
everything after the first divergence live; a pipeline's call order diverges after the
drafts, so a resumed topic re-runs every skeptic. This script reads the journal instead:
each `started` line maps a key to its label (`sources:<layer>`, `spine`, `draft:<key>`,
`verify:<key>`), each `result` line carries that agent's return value, and the bundle
embeds them as the state the workflow takes without an agent.

Usage:
  research-continue.py --journal <transcript-dir>/journal.jsonl --from-output <task-output.json>
                       [--rotation-start N] [--max-rules N] [--split N] [--out-dir <dir>] [--root <repo>]
    --from-output   the Workflow tool's task output of the cut-short run (its result.topic and
                    result.next_id are the topic arguments)
    --split N       write N bundles, each drafting an interleaved subset of the rule keys, so a
                    topic runs on N workflows at once; the first bundle reports the held rules
Writes the bundle files and prints their paths; standard library only."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "research-topic-workflow.js")


def read_journal(path):
    key2label, results = {}, {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get("type") == "started":
                key2label[e["key"]] = e.get("label", "")
            elif e.get("type") == "result" and e.get("result") is not None:
                label = key2label.get(e["key"])
                if label and label not in results:
                    results[label] = e["result"]
    return results


def bundle(script, args_obj):
    lines = script.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if l.startswith("export const meta = {")), None)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].rstrip("\n") == "}"), None) if start is not None else None
    if start is None or end is None:
        sys.exit("research-continue: research-topic-workflow.js has no closed `export const meta = {` block")
    embedded = "const EMBEDDED_ARGS = " + json.dumps(args_obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    return "".join(lines[: end + 1]) + "// Embedded by scripts/research-continue.py — the finished stages of a cut-short run.\n" + embedded + "".join(lines[end + 1:])


def main(argv):
    opts = {"journal": None, "from_output": None, "rotation_start": "0", "max_rules": "12", "split": "1", "out_dir": None, "root": None}
    i = 0
    while i < len(argv):
        key = argv[i][2:].replace("-", "_")
        if not argv[i].startswith("--") or key not in opts or i + 1 >= len(argv):
            sys.exit(f"research-continue: unexpected argument {argv[i]!r}\n{__doc__}")
        opts[key] = argv[i + 1]
        i += 2
    if not opts["journal"] or not opts["from_output"]:
        sys.exit("research-continue: --journal and --from-output are required")
    with open(opts["from_output"], encoding="utf-8") as fh:
        out = json.load(fh)
    result = out["result"] if "result" in out else out
    topic = result["topic"]
    root = opts["root"] or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    results = read_journal(opts["journal"])
    sources = [results[k] for k in ("sources:formulation", "sources:reception", "sources:evidence") if k in results]
    spine = results.get("spine")
    if not spine or not sources:
        sys.exit("research-continue: the journal holds no spine or no source layer; run the topic afresh")
    drafts = {k[len("draft:"):]: v for k, v in results.items() if k.startswith("draft:") and v.get("status") == "card"}
    verdicts = {k[len("verify:"):]: v for k, v in results.items() if k.startswith("verify:")}
    max_rules = int(opts["max_rules"])
    card_keys = [r["key"] for r in spine["rules"] if r.get("disposition") == "card"][:max_rules]
    n = max(1, int(opts["split"]))
    out_dir = opts["out_dir"] or os.path.dirname(os.path.abspath(opts["from_output"]))
    os.makedirs(out_dir, exist_ok=True)
    with open(SCRIPT, encoding="utf-8") as fh:
        script = fh.read()
    paths = []
    for part in range(n):
        keys = card_keys[part::n]
        if not keys:
            continue
        # the bundle stays under the runtime's 512 KiB script limit: it carries the spine and only its own
        # keys' drafts and verdicts, and no source layer — the note takes the sources from the cut-short
        # run's own output when the writer merges the runs
        args_obj = {
            "root": root, "topic": topic, "next_id": result.get("next_id", 1), "existing_titles": [],
            "max_rules": max_rules, "rotation_start": int(opts["rotation_start"]),
            "resume_state": {"sources": [], "spine": spine,
                             "drafts": {k: v for k, v in drafts.items() if k in keys},
                             "verdicts": {k: v for k, v in verdicts.items() if k in keys}},
            "only_keys": keys, "include_held": part == 0,
        }
        path = os.path.join(out_dir, f"continue-{topic['slug']}-{part + 1}of{n}.js")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(bundle(script, args_obj))
        paths.append(path)
        size = os.path.getsize(path)
        if size > 524288:
            sys.exit(f"research-continue: {path} is {size} bytes, above the runtime's 524288-byte script limit; raise --split")
        print(f"{path}: {len(keys)} rule(s), {size} bytes — {', '.join(keys)}")
    print(f"state: {len(sources)} source layer(s), {len(spine['rules'])} spine rule(s), {len(drafts)} draft(s), {len(verdicts)} first verdict(s); {len(card_keys)} card rule(s) across {len(paths)} bundle(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
