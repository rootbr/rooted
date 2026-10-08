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
  research-continue.py --journal <transcript-dir>/journal.jsonl [--journal ...] (--from-output <task-output.json> | --from-bundle <run.js>)
                       [--round N] [--rotation-start N] [--max-rules N] [--split N] [--out-dir <dir>] [--root <repo>]
                       [--write-output <path>]
    --journal       a journal of the topic; repeatable, so a topic split over several bundles continues
                    from all of them
    --from-output   the Workflow tool's task output of the cut-short run (its result.topic and
                    result.next_id are the topic arguments)
    --from-bundle   the bundle the cut-short run was launched from (its EMBEDDED_ARGS supply the topic,
                    next_id, rotation_start, max_rules, channel_note and closing_edit); the way to continue
                    a run that left no task output, in another session or another checkout. With both,
                    the output supplies the topic and the bundle the remaining arguments
    --write-output  write a task-output file for the cut-short run from the journal (its sources and spine,
                    no cards), so scripts/write-topic-result.py can merge it as the run's first output
    --round N       the fix round the bundles perform (default 1). Round 1 continues a cut-short run:
                    drafts from `draft:` and first verdicts from `verify:`. Round N above 1 carries the
                    previous round's fixed drafts (`fix:` for round 2, `fix<N-1>:` after) and its verdicts
                    (`verify<N>:`), and drafts only the rules that verdict sent back with "revise"; a
                    rule with verdict "accept" is done and one with "reject" stays pending
    --split N       write N bundles, each drafting an interleaved subset of the rule keys, so a
                    topic runs on N workflows at once; the first bundle reports the held rules
    --closing-edit  the bundle ships a rule the last verdict sends back with "revise" after the drafter
                    applies that verdict's required edits verbatim (the workflow's closing_edit)
    --resume-cut-short
                    finish round N whose fixes ran and whose skeptics were cut short: the bundle
                    carries every `fix<N>:` draft (`fix:` for N = 1... see stage_labels) as its state
                    with the `verify<N+1>:` verdicts already recorded, runs only the missing verdicts,
                    and ends a rule the verdict does not accept as pending (fix_after_verify false);
                    a rule with no fix<N> draft is left to a plain --round N bundle
    --skip-fixed    in a plain --round N bundle, leave out every rule whose round-N fix (`fix:`, `fix<N>:`)
                    the journals already hold, whatever its status: a --resume-cut-short bundle finishes
                    those, and a fix that sent the rule to pending is already in the cut-short run's output
    --write-carded <out.json>
                    write the cards a stopped run's journal already finished (a closing edit that returned
                    a card, or a fix draft the round's second verdict accepted) as a task output with
                    `result.cards`, `provenance_lines` and `outcomes`, then stop; the writer merges it as
                    one of the topic's runs and a rebuilt bundle leaves those rules out with --skip-carded.
                    The cards come from the journals given with --carded-journal (the stopped run's own),
                    the spine from every --journal
    --carded-journal <journal.jsonl>
                    a journal whose finished cards --write-carded collects; repeatable
    --skip-carded <task-output.json>
                    leave out every rule the given output already ships as a card (its result.cards keys);
                    repeatable, so the outputs of every earlier bundle of the topic count. A continuation
                    of a continuation (a run cut short twice) passes every journal with --journal and the
                    earlier bundles' outputs here, and the writer merges all of the outputs
Writes the bundle files and prints their paths; standard library only."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "research-topic-workflow.js")


def read_journal(path, results=None):
    """Label -> the agent's result, for every agent the journal records; a repeated label keeps its
    first result. Several journals of one topic accumulate into one map."""
    key2label = {}
    results = {} if results is None else results
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


def summarize_verdict(v):
    if not isinstance(v, dict):
        return ""
    return f"{v.get('verdict', '')}: {len(v.get('problems') or [])} problem(s)"


def carded_from_journals(paths, rnd):
    """The cards the given journals already finished in fix round rnd: a closing edit (`close<N>:`) that
    returned a card, or a `fix:`/`fix<N>:` draft the round's second verdict accepted. rule_id, title and the
    example language are read from the card itself (the writer renumbers ids anyway)."""
    import re
    results = {}
    for p in paths:
        read_journal(p, results)
    fix_label, verify2_label = stage_labels(rnd + 1)
    cards, prov, outcomes, seen = [], [], [], set()

    def add(key, d, closing, verdict):
        md = d["card_markdown"]
        fm = md.split("---")[1] if md.startswith("---") else ""
        rid = re.search(r"^rule_id:\s*(\S+)", fm, re.M)
        title = re.search(r"^title:\s*(.+)$", fm, re.M)
        lang = re.search(r"^```(\w+)", md, re.M)
        rule_id = rid.group(1) if rid else ""
        t = title.group(1).strip() if title else ""
        cards.append({"rule_id": rule_id, "key": key, "title": t, "filename": d.get("filename", ""),
                      "example_language": lang.group(1) if lang else "", "markdown": md})
        prov.append(d.get("provenance_line", ""))
        outcomes.append({"key": key, "rule_id": rule_id, "title": t, "final": "card", "reason": "", "round": rnd,
                         "fix_rounds": rnd, "closing_edit": closing,
                         "last_verdict": summarize_verdict(verdict) if closing else "",
                         "verdict1": "", "verdict2": "" if closing else summarize_verdict(verdict)})
        seen.add(key)

    for label, d in results.items():
        stage, _, key = label.partition(":")
        if key and stage.startswith("close") and isinstance(d, dict) and d.get("status") == "card" and d.get("card_markdown"):
            add(key, d, True, results.get(f"{verify2_label}:{key}"))
    for label, d in results.items():
        stage, _, key = label.partition(":")
        if key and stage == fix_label and key not in seen and isinstance(d, dict) and d.get("status") == "card" and d.get("card_markdown"):
            v = results.get(f"{verify2_label}:{key}")
            if isinstance(v, dict) and v.get("verdict") == "accept":
                add(key, d, False, v)
    return cards, prov, outcomes


def stage_labels(rnd):
    """The journal labels of the draft and the verdict a round starts from."""
    draft = "draft" if rnd == 1 else ("fix" if rnd == 2 else f"fix{rnd - 1}")
    verify = "verify" if rnd == 1 else f"verify{rnd}"
    return draft, verify


def bundle(script, args_obj):
    lines = script.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if l.startswith("export const meta = {")), None)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].rstrip("\n") == "}"), None) if start is not None else None
    if start is None or end is None:
        sys.exit("research-continue: research-topic-workflow.js has no closed `export const meta = {` block")
    embedded = "const EMBEDDED_ARGS = " + json.dumps(args_obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    return "".join(lines[: end + 1]) + "// Embedded by scripts/research-continue.py — the finished stages of a cut-short run.\n" + embedded + "".join(lines[end + 1:])


def read_bundle_args(path):
    """The EMBEDDED_ARGS object of a bundle (one line after the meta block)."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("const EMBEDDED_ARGS = "):
                return json.loads(line[len("const EMBEDDED_ARGS = "):])
    sys.exit(f"research-continue: {path} holds no EMBEDDED_ARGS line")


def main(argv):
    opts = {"journal": [], "from_output": None, "from_bundle": None, "write_output": None, "round": "1", "rotation_start": None, "max_rules": None, "split": "1", "out_dir": None, "root": None, "resume_cut_short": False, "closing_edit": False, "skip_fixed": False, "skip_carded": [], "write_carded": None, "carded_journal": []}
    i = 0
    while i < len(argv):
        key = argv[i][2:].replace("-", "_")
        if key in ("resume_cut_short", "closing_edit", "skip_fixed"):
            opts[key] = True
            i += 1
            continue
        if not argv[i].startswith("--") or key not in opts or i + 1 >= len(argv):
            sys.exit(f"research-continue: unexpected argument {argv[i]!r}\n{__doc__}")
        if key in ("journal", "skip_carded", "carded_journal"):
            opts[key].append(argv[i + 1])
        else:
            opts[key] = argv[i + 1]
        i += 2
    if not opts["journal"] or not (opts["from_output"] or opts["from_bundle"]):
        sys.exit("research-continue: --journal and one of --from-output / --from-bundle are required")
    rnd = int(opts["round"])
    if rnd < 1:
        sys.exit("research-continue: --round must be 1 or more")
    launched = read_bundle_args(opts["from_bundle"]) if opts["from_bundle"] else {}
    if opts["from_output"]:
        with open(opts["from_output"], encoding="utf-8") as fh:
            out = json.load(fh)
        result = out["result"] if "result" in out else out
    else:
        result = {"topic": launched["topic"], "next_id": launched.get("next_id", 1)}
    topic = result["topic"]
    rotation_start = int(opts["rotation_start"] if opts["rotation_start"] is not None else launched.get("rotation_start", 0))
    max_rules = int(opts["max_rules"] if opts["max_rules"] is not None else launched.get("max_rules", 12))
    closing_edit = bool(opts["closing_edit"] or launched.get("closing_edit", False))
    channel_note = launched.get("channel_note")
    root = opts["root"] or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    results = {}
    for j in opts["journal"]:
        read_journal(j, results)
    sources = [results[k] for k in ("sources:formulation", "sources:reception", "sources:evidence") if k in results]
    spine = results.get("spine") or (result.get("spine") if rnd > 1 else None)
    if rnd == 1 and (not spine or not sources):
        sys.exit("research-continue: the journal holds no spine or no source layer; run the topic afresh")
    if not spine:
        sys.exit("research-continue: no spine in the journals or the output; run the topic afresh")
    if opts["write_carded"]:
        if not opts["carded_journal"]:
            sys.exit("research-continue: --write-carded needs at least one --carded-journal")
        cards, prov, outcomes = carded_from_journals(opts["carded_journal"], rnd)
        synthetic = {"result": {"topic": topic, "next_id": result.get("next_id", 1), "sources": sources, "spine": spine,
                                "outcomes": outcomes, "cards": cards, "provenance_lines": prov, "pending_entries": [], "held": [], "round": rnd},
                     "workflowProgress": [], "agentCount": 0, "totalTokens": 0,
                     "note": "written by scripts/research-continue.py --write-carded from the journal of a stopped run: the cards its closing edits and accepted fixes finished"}
        with open(opts["write_carded"], "w", encoding="utf-8") as fh:
            json.dump(synthetic, fh, ensure_ascii=False)
        print(f"{opts['write_carded']}: {len(cards)} finished card(s) from {len(opts['carded_journal'])} journal(s): {', '.join(c['key'] for c in cards)}")
        return
    cut_short = opts["resume_cut_short"]
    if cut_short:
        # the round's own fix label is the draft, its own second-verdict label the verdict
        draft_label, verify_label = stage_labels(rnd + 1)
    else:
        draft_label, verify_label = stage_labels(rnd)
    drafts = {k[len(draft_label) + 1:]: v for k, v in results.items() if k.startswith(draft_label + ":") and v.get("status") == "card"}
    verdicts = {k[len(verify_label) + 1:]: v for k, v in results.items() if k.startswith(verify_label + ":")}
    if opts["write_output"]:
        synthetic = {"result": {"topic": topic, "next_id": result.get("next_id", 1), "sources": sources, "spine": spine,
                                "cards": [], "provenance_lines": [], "outcomes": [], "pending_entries": [], "held": [], "round": rnd},
                     "workflowProgress": [], "agentCount": 0, "totalTokens": 0,
                     "note": "written by scripts/research-continue.py --write-output from the journal of a cut-short run: its sources and spine, no cards"}
        with open(opts["write_output"], "w", encoding="utf-8") as fh:
            json.dump(synthetic, fh, ensure_ascii=False)
        print(f"{opts['write_output']}: cut-short output with {len(sources)} source layer(s) and {len(spine.get('rules', []))} spine rule(s)")
    card_keys = [r["key"] for r in spine["rules"] if r.get("disposition") == "card"][:max_rules]
    if cut_short:
        card_keys = [k for k in card_keys if k in drafts]
        missing = [k for k in card_keys if k not in verdicts]
        print(f"round {rnd} cut short: {len(drafts)} `{draft_label}:` draft(s), {len(verdicts)} `{verify_label}:` verdict(s) recorded, {len(missing)} verdict(s) to run")
        if not card_keys:
            sys.exit("research-continue: no fixed draft of this round in the journals")
    elif rnd > 1:
        # a further round carries only the rules the last verdict sent back with exact edits
        accepted = [k for k in card_keys if verdicts.get(k, {}).get("verdict") == "accept"]
        rejected = [k for k in card_keys if verdicts.get(k, {}).get("verdict") == "reject"]
        own_fix = stage_labels(rnd + 1)[0]
        done = [k for k in card_keys if (own_fix + ":" + k) in results]
        card_keys = [k for k in card_keys if k in drafts and verdicts.get(k, {}).get("verdict") == "revise" and k not in done]
        print(f"round {rnd}: {len(accepted)} accepted, {len(rejected)} rejected, {len(done)} already fixed in this round (see --resume-cut-short), {len(card_keys)} sent back with revise -> continue")
        if not card_keys:
            sys.exit("research-continue: no rule to carry into this round")
    carded = set()
    for path in opts["skip_carded"]:
        with open(path, encoding="utf-8") as fh:
            out = json.load(fh)
        carded |= {c["key"] for c in (out.get("result", out)).get("cards", [])}
    if carded:
        before = len(card_keys)
        card_keys = [k for k in card_keys if k not in carded]
        print(f"skip-carded: {before - len(card_keys)} rule(s) already shipped by the given output(s) left out")
    if opts["skip_fixed"] and not cut_short:
        own_fix = stage_labels(rnd + 1)[0]
        fixed = [k for k in card_keys if (own_fix + ":" + k) in results]
        card_keys = [k for k in card_keys if k not in fixed]
        print(f"skip-fixed: {len(fixed)} rule(s) whose `{own_fix}:` result the journals hold left out")
    if not card_keys:
        sys.exit("research-continue: no rule left to run after the skips; nothing to write")
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
            "max_rules": max_rules, "rotation_start": rotation_start,
            "resume_state": {"sources": [], "spine": spine,
                             "drafts": {k: v for k, v in drafts.items() if k in keys},
                             "verdicts": {k: v for k, v in verdicts.items() if k in keys}},
            "only_keys": keys, "include_held": rnd == 1 and part == 0, "round": rnd + 1 if cut_short else rnd,
            "fix_after_verify": not cut_short, "closing_edit": closing_edit,
        }
        if channel_note:
            args_obj["channel_note"] = channel_note
        suffix = ("" if rnd == 1 else f"-round{rnd}") + ("-finish" if cut_short else "")
        path = os.path.join(out_dir, f"continue-{topic['slug']}{suffix}-{part + 1}of{n}.js")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(bundle(script, args_obj))
        paths.append(path)
        size = os.path.getsize(path)
        if size > 524288:
            sys.exit(f"research-continue: {path} is {size} bytes, above the runtime's 524288-byte script limit; raise --split")
        print(f"{path}: {len(keys)} rule(s), {size} bytes — {', '.join(keys)}")
    print(f"state: round {rnd}, {len(sources)} source layer(s), {len(spine['rules'])} spine rule(s), {len(drafts)} draft(s) from `{draft_label}:`, {len(verdicts)} verdict(s) from `{verify_label}:`; {len(card_keys)} card rule(s) across {len(paths)} bundle(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
