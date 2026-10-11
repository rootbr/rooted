#!/usr/bin/env python3
"""Bundle one craft review run: write craft/run.js = scripts/craft-review-workflow.js with the
run's arguments embedded as `const EMBEDDED_ARGS = {...}` right after the `meta` block.

The Workflow tool takes a script path and, optionally, an args object; the plan a real diff
produces is far too large to retype into a tool call, so the bundle carries it verbatim and
the main agent calls `Workflow({ scriptPath: "<repo>/craft/run.js" })` with no args.

Usage:
  bundle-run.py --root <repo> --plan craft/plan.json --intent <file|-> --context <file|->
                [--stage all|find|aggregate|verify] [--findings craft/findings.json]
                [--part <i>/<n>] [--raw <find-part-output.json> ...]
                [--tiers <json-file>] [--agent-types <json-file>] [--out craft/run.js]

Standard library only. Exit status 2 on a malformed input."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def read_text(path):
    if path is None:
        return ""
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_json(path, what):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        sys.exit(f"bundle-run: {what} {path}: {exc}")


def bundle(script, args_obj):
    """Insert `const EMBEDDED_ARGS = <json>` after the `export const meta = { ... }` block."""
    lines = script.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if l.startswith("export const meta = {")), None)
    if start is None:
        sys.exit("bundle-run: craft-review-workflow.js has no `export const meta = {` line")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].rstrip("\n") == "}"), None)
    if end is None:
        sys.exit("bundle-run: the meta block never closes")
    embedded = "const EMBEDDED_ARGS = " + json.dumps(args_obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    return "".join(lines[: end + 1]) + "// Embedded by scripts/bundle-run.py — the plan verbatim from craft/plan.json.\n" + embedded + "".join(lines[end + 1:])


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="absolute path of the repository under review")
    ap.add_argument("--plan", default="craft/plan.json")
    ap.add_argument("--intent", default=None, help="file holding design_intent, or - for stdin")
    ap.add_argument("--context", default=None, help="file holding project_context (the config.md body)")
    ap.add_argument("--stage", default="all", choices=["all", "find", "aggregate", "verify"])
    ap.add_argument("--part", default=None, help="i/n: this bundle runs every n-th finder job (stage find) or finding (stage verify)")
    ap.add_argument("--raw", action="append", default=[], help="stage aggregate: a find part's task output (its result.raw) or a JSON array of {source, findings}")
    ap.add_argument("--findings", default=None, help="craft/findings.json (stage verify)")
    ap.add_argument("--tiers", default=None, help="JSON file overriding the tiers")
    ap.add_argument("--agent-types", default=None, help="JSON file naming the agent types")
    ap.add_argument("--script", default=os.path.join(HERE, "craft-review-workflow.js"))
    ap.add_argument("--out", default="craft/run.js")
    opts = ap.parse_args(argv)
    root = os.path.abspath(opts.root)
    plan_path = opts.plan if os.path.isabs(opts.plan) else os.path.join(root, opts.plan)
    plan = read_json(plan_path, "plan")
    for key in ("inventory", "cards", "jobs", "slices"):
        if key not in plan:
            sys.exit(f"bundle-run: plan lacks \"{key}\" (the plan is written by scripts/static-craft.py)")
    args_obj = {
        "root": root,
        "stage": opts.stage,
        "plan": plan,
        "design_intent": read_text(opts.intent).strip(),
        "project_context": read_text(opts.context).strip(),
    }
    if opts.part:
        try:
            i, n = (int(x) for x in opts.part.split("/"))
        except ValueError:
            sys.exit("bundle-run: --part takes i/n")
        if not (1 <= i <= n):
            sys.exit("bundle-run: --part i/n needs 1 <= i <= n")
        args_obj["part"] = {"index": i, "of": n}
    if opts.stage == "aggregate":
        if not opts.raw:
            sys.exit("bundle-run: stage aggregate needs --raw")
        raw = []
        for rp in opts.raw:
            d = read_json(rp if os.path.isabs(rp) else os.path.join(root, rp), "raw")
            if isinstance(d, dict):
                d = (d.get("result") or {}).get("raw", d.get("raw"))
            if not isinstance(d, list):
                sys.exit(f"bundle-run: {rp} holds no raw findings")
            raw.extend(d)
        args_obj["raw"] = raw
    if opts.stage == "verify":
        if not opts.findings:
            sys.exit("bundle-run: stage verify needs --findings")
        fpath = opts.findings if os.path.isabs(opts.findings) else os.path.join(root, opts.findings)
        findings = read_json(fpath, "findings")
        if isinstance(findings, dict):
            findings = findings.get("findings")
        if not isinstance(findings, list):
            sys.exit(f"bundle-run: {opts.findings} holds no findings array")
        args_obj["findings"] = findings
    if opts.tiers:
        args_obj["tiers"] = read_json(opts.tiers, "tiers")
    if opts.agent_types:
        args_obj["agentTypes"] = read_json(opts.agent_types, "agent types")
    script = read_text(opts.script)
    out_path = opts.out if os.path.isabs(opts.out) else os.path.join(root, opts.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(bundle(script, args_obj))
    print(f"{out_path}: {len(plan['jobs'])} job(s), {len(plan['slices'])} slice(s), stage {opts.stage}, {os.path.getsize(out_path)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
