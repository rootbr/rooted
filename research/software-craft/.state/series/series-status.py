#!/usr/bin/env python3
"""Status of the series research runs, and a snapshot of their journals and outputs into the
repository, so another session (or another checkout) continues them without re-running agents.

Usage:
  series-status.py [--batches <batchN.json> ...] [--workflows-dir <dir>] [--tasks-dir <dir>] [--snapshot]
    --batches        the batch records (default: every batch*.json beside this script, then round2.json); each names a topic's
                     workflow run id (`wf`) and its latest task id (`task`), or, for a topic continued over
                     several bundles, a `runs` list of {part, task, wf} (one row, one journal and one output per run)
    --workflows-dir  the runtime's workflow transcripts: <dir>/<wf id>/journal.jsonl (default: found under
                     ~/.claude/projects/*/*/subagents/workflows)
    --tasks-dir      the runtime's task outputs: <dir>/<task id>.output (default: found under /tmp/claude-0/*/*/tasks)
    --snapshot       copy each topic's journal to ../journals/<slug>.journal.jsonl.gz and its task output, when
                     the run finished, to ../outputs/<slug>.output.json.gz (a continuation run's files carry
                     `--<part>` before the extension); write status.json and STATUS.md here

A journal is append-only and every finished agent writes one `result` line, so the snapshot taken after a
usage-limit stop holds everything a continuation needs (scripts/research-continue.py --from-bundle).
The gzip members carry no timestamp (mtime 0), so an unchanged journal or output snapshots to identical bytes.
Standard library only."""
import glob
import gzip
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.dirname(HERE)
STAGES = ["sources", "spine", "draft", "verify", "fix", "verify2", "close1"]


def journal_stats(path):
    labels, done, failed, spine_rules = {}, {}, {}, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "started":
                labels[e["key"]] = e.get("label", "?")
            elif e.get("type") == "result" and e.get("result") is not None:
                st = labels.get(e["key"], "?").split(":")[0]
                done[st] = done.get(st, 0) + 1
                if st == "spine" and isinstance(e["result"], dict) and spine_rules is None:
                    spine_rules = len([r for r in e["result"].get("rules", []) if r.get("disposition") == "card"])
            elif e.get("type") == "failed":
                st = labels.get(e.get("key"), "?").split(":")[0]
                failed[st] = failed.get(st, 0) + 1
    return done, failed, spine_rules


def main(argv):
    opts = {"batches": [], "workflows_dir": None, "tasks_dir": None, "snapshot": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--snapshot":
            opts["snapshot"] = True; i += 1
        elif a == "--batches":
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                opts["batches"].append(argv[i]); i += 1
        elif a in ("--workflows-dir", "--tasks-dir") and i + 1 < len(argv):
            opts[a[2:].replace("-", "_")] = argv[i + 1]; i += 2
        else:
            sys.exit(f"series-status: unexpected argument {a!r}\n{__doc__}")
    batches = opts["batches"] or sorted(glob.glob(os.path.join(HERE, "batch*.json"))) + [p for p in [os.path.join(HERE, "round2.json")] if os.path.exists(p)]
    topics = []
    for bf in batches:
        b = json.load(open(bf, encoding="utf-8"))
        for slug, v in b["topics"].items():
            for run in v.get("runs") or [v]:
                topics.append((b.get("batch"), slug, run))
    wdir = opts["workflows_dir"]
    tdir = opts["tasks_dir"]
    if topics and not wdir:
        # the runtime directory that holds any of the batches' runs (an older batch's runs may live only in the snapshots)
        wdir = next((d for d in glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/workflows"))
                     if any(glob.glob(os.path.join(d, v["wf"] + "*")) for _, _, v in topics)), None)
    if topics and not tdir:
        tdir = next((d for d in glob.glob("/tmp/claude-0/*/*/tasks")
                     if any(os.path.exists(os.path.join(d, v["task"] + ".output")) for _, _, v in topics)), None)
    status, rows = {}, []
    now = time.strftime("%Y-%m-%dT%H:%M UTC", time.gmtime())
    if opts["snapshot"]:
        os.makedirs(os.path.join(STATE, "journals"), exist_ok=True)
        os.makedirs(os.path.join(STATE, "outputs"), exist_ok=True)
    for batch, slug, v in topics:
        part = v.get("part")
        name = f"{slug}--{part}" if part else slug
        wf_dirs = glob.glob(os.path.join(wdir, v["wf"] + "*")) if wdir else []
        journal = os.path.join(wf_dirs[0], "journal.jsonl") if wf_dirs else None
        snap_j = os.path.join(STATE, "journals", f"{name}.journal.jsonl.gz")
        if not (journal and os.path.exists(journal)) and os.path.exists(snap_j):
            journal = snap_j
        done, failed, spine = {}, {}, None
        if journal and os.path.exists(journal):
            if journal.endswith(".gz"):
                with gzip.open(journal, "rt", encoding="utf-8") as fh, open(os.path.join(HERE, ".tmp-journal.jsonl"), "w", encoding="utf-8") as out:
                    shutil.copyfileobj(fh, out)
                done, failed, spine = journal_stats(os.path.join(HERE, ".tmp-journal.jsonl"))
                os.remove(os.path.join(HERE, ".tmp-journal.jsonl"))
            else:
                done, failed, spine = journal_stats(journal)
        out_path = os.path.join(tdir, v["task"] + ".output") if tdir else None
        finished = bool(out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0)
        cards = errors = None
        if finished:
            try:
                o = json.load(open(out_path, encoding="utf-8"))
                r = o.get("result", o)
                cards = len(r.get("cards", []))
                spine = spine or len([x for x in r.get("spine", {}).get("rules", []) if x.get("disposition") == "card"])
                errors = sum(1 for a in (o.get("workflowProgress") or []) if isinstance(a, dict) and a.get("status") == "error")
            except ValueError:
                finished = False
        rec = {"batch": batch, "part": part, "wf": v["wf"], "task": v["task"], "journal": journal, "done": done, "failed": failed,
               "finished": finished, "cards": cards, "spine_card_rules": spine, "checked": now}
        if opts["snapshot"]:
            if journal and os.path.exists(journal) and not journal.endswith(".gz"):
                with open(journal, "rb") as src, gzip.GzipFile(snap_j, "wb", mtime=0) as dst:
                    shutil.copyfileobj(src, dst)
                rec["snapshot_journal"] = os.path.relpath(snap_j, STATE)
            elif os.path.exists(snap_j):
                rec["snapshot_journal"] = os.path.relpath(snap_j, STATE)
            if finished:
                snap_o = os.path.join(STATE, "outputs", f"{name}.output.json.gz")
                with open(out_path, "rb") as src, gzip.GzipFile(snap_o, "wb", mtime=0) as dst:
                    shutil.copyfileobj(src, dst)
                rec["snapshot_output"] = os.path.relpath(snap_o, STATE)
        status[name] = rec
        d = ", ".join(f"{k} {done[k]}" for k in STAGES if k in done) or "-"
        f = ", ".join(f"{k} {failed[k]}" for k in STAGES if k in failed) or "-"
        state = "run complete" if finished and not failed else ("run ended, agents failed" if finished else "running or stopped")
        rows.append(f"| {batch} | `{slug}`{' ' + part if part else ''} | {spine if spine is not None else '?'} | {d} | {f} | {cards if cards is not None else '-'} | {state} |")
        print(f"{name:52s} done=[{d}] failed=[{f}] {'FINISHED cards=' + str(cards) if finished else ''}")
    if opts["snapshot"]:
        json.dump(status, open(os.path.join(HERE, "status.json"), "w", encoding="utf-8"), indent=1)
        table = ["# Series status", "", f"Snapshot taken {now} by `series/series-status.py --snapshot`. Journals under `journals/`, finished runs' outputs under `outputs/`.", "",
                 "`done` counts the agents whose results the journal holds (cached for a continuation); `failed` the agents a usage-limit stop or an error ended, which a continuation re-runs. "
                 "`cards` is the count in the run's own output; a run whose agents failed shipped none, and its cards come from the continuation. "
                 "A continuation run (batch 3 and later) is one bundle of a topic, named by its part; a topic is finished when every part's run is complete.", "",
                 "| Batch | Topic | Spine card rules | Done | Failed | Cards in output | State |", "|--|--|--|--|--|--|--|"] + rows
        open(os.path.join(HERE, "STATUS.md"), "w", encoding="utf-8").write("\n".join(table) + "\n")
        print(f"status.json and STATUS.md written; journals and outputs under {STATE}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
