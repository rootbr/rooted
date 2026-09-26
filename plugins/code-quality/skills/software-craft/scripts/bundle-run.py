#!/usr/bin/env python3
"""Bundle one craft review run: write craft/run.js = scripts/craft-review-workflow.js with the
run's arguments embedded as `const EMBEDDED_ARGS = {...}` right after the `meta` block.

The Workflow tool takes a script path and, optionally, an args object; the plan a real diff
produces is far too large to retype into a tool call, so the bundle carries it verbatim and
the main agent calls `Workflow({ scriptPath: "<repo>/craft/run.js" })` with no args.

Usage:
  bundle-run.py --root <repo> --plan craft/plan.json --intent <file|-> --context <file|->
                [--stage all|find|verify] [--findings craft/findings.json]
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
    ap.add_argument("--stage", default="all", choices=["all", "find", "verify"])
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
    if opts.stage == "verify":
        if not opts.findings:
            sys.exit("bundle-run: stage verify needs --findings")
        fpath = opts.findings if os.path.isabs(opts.findings) else os.path.join(root, opts.findings)
        args_obj["findings"] = read_json(fpath, "findings")
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
