#!/usr/bin/env python3
"""Prepare the inputs of the two Python-corpus Workflow scripts and merge their outputs.

Subcommands:

  triage-briefs --harvest <dir> --state <STATE> --topics <topics.json> --universal <universal.json>
                [--batch-size 80] [--explanation-chars 500]
      Reads <harvest>/items.jsonl, the topic list, the universal card index and the verdict
      definitions in maintenance/scripts/python-triage-workflow.js. One check is one item: a Ruff item absorbs
      the Pylint item it reimplements (PLW0102 absorbs W0102), the bugbear item of its code (B006)
      and the Bandit item of its digits (S602 absorbs B602); the absorbed item's locator goes into
      the Ruff item's `also` list. Dropped by script: every item whose status is neither stable
      nor preview (before merging, so a dropped item hosts nothing), then, among the items left
      standing, Pylint messages of type E and F and Pylint codes C01xx and C03xx. The rest is
      ordered by source, then by code (a Ruff code sorts by its linter prefix), and cut into
      batches batch-01, batch-02, ...
      Writes STATE/triage/briefs/<id>.md (criteria and verdict definitions, topics, universal
      cards by domain, items), STATE/triage/batches.json ([{id, brief_path, item_count, codes}])
      and STATE/triage/args.json (the triage workflow's args: {state_dir, batches, done}, where
      done lists the batches whose STATE/triage/<id>.json parses and holds a verdicts list).
      Removes briefs of an earlier cut that the current cut no longer produces.

  triage-merge --state <STATE> --harvest <dir> --topics <topics.json>
      Reads STATE/triage/batches.json, every STATE/triage/batch-*.json result and items.jsonl.
      Writes STATE/candidates.json: one candidate per (topic, rule_key) over the
      python-specific-new verdicts, {key, topic, statement, items, notes, codes}, sorted by topic
      order then key; a rule_key used by two topics takes the suffix -<topic slug> in every topic
      after the first; a verdict whose topic is no slug of topics.json goes to topic
      "unassigned". A duplicate-of verdict whose target item is python-specific-new adds its
      item to the target's candidate. Writes STATE/triage/summary.json: counts per verdict and
      per topic, the universal-instance list, the duplicate-of pairs, the not-checkable and
      out-of-scope items, the batch notes, the expected batches without a result file, the
      result files that do not parse, the verdicts naming no harvested item and the batch items
      that received no verdict.

  topic-args --state <STATE> --topic <slug> --topics <topics.json> --universal <universal.json>
             --harvest <dir> --skill <skill dir> --root <repo root> --cards-dir <dir>
             [--papers STATE/harvest/papers.json] [--max-rules 10] [--pack-size 5]
             [--skeptic-model claude-fable-5-1] [--skeptic-effort high] [--closing-effort high]
             [--only-keys k1,k2]
      Reads STATE/candidates.json, the topic list, the universal index, the papers file, the
      cards directory and the restart files STATE/<slug>/{spine/*.json, draft/*.json,
      verdict/*.json, closing/*.json}. Writes STATE/<slug>/candidates.json, the topic's candidates
      (the spine judge reads it in one call), and STATE/<slug>/args.json, the args of
      maintenance/scripts/python-topic-workflow.js, which name that file as candidates_path; next_id is one
      past the highest py-NN-- card in the cards directory. A restart file that does not parse is
      reported and skipped.

  save-run --state <STATE> --topic <slug> --from <workflow output json>
      Copies the Workflow tool's task output to STATE/<slug>/run.json once it parses and holds
      result.cards.

Every path written into an output file is absolute. A missing or unreadable input ends the run
with one line on standard error and exit status 1. Standard library only; no network.
"""
import argparse
import collections
import dataclasses
import glob
import importlib.util
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAGE_WORKFLOW = os.path.join(HERE, "python-triage-workflow.js")
SOURCES = ("ruff", "pylint", "sonar", "bandit", "bugbear")
KEPT_STATUSES = ("stable", "preview")
VERDICTS = ("python-specific-new", "universal-instance", "formatting", "not-checkable", "not-a-craft-rule",
            "out-of-scope", "duplicate-of")
DOMAIN_ORDER = ("code", "design", "interface", "errors", "tests", "change", "performance", "tooling", "docs", "input")
UNASSIGNED = "unassigned"
LOCATOR_FIELDS = ("source", "code", "name", "url", "cache_path")
CANDIDATE_ITEM_FIELDS = ("source", "code", "name", "title", "summary", "url", "cache_path")

CRITERIA = """A catalog item becomes a corpus card only when all four hold:
1. It holds because of Python — its data model, scoping, exception model, typing, standard library, packaging or tooling.
2. No universal card states it for every language.
3. A finder holding the card and one diff hunk can check it with one binary question.
4. It is not layout, naming style or quoting."""


class CorpusError(Exception):
    """An input is missing or unreadable; main reports it in one line."""


# ---- reading -----------------------------------------------------------------------------------

def read_json(path, what):
    if not os.path.isfile(path):
        raise CorpusError(f"{what} not found: {path}")
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusError(f"{what} does not parse: {path}: {exc}") from exc


def try_read_json(path):
    """Return (object, error) for a restart or result file that may be absent or half-written."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_items(harvest_dir):
    path = os.path.join(harvest_dir, "items.jsonl")
    if not os.path.isfile(path):
        raise CorpusError(f"items.jsonl not found: {path}")
    items = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise CorpusError(f"{path}:{number} does not parse: {exc}") from exc
    return items


def item_id(item):
    """The identifier a verdict names an item by: its code, or its name where the catalog gives no code."""
    return item.get("code") or item.get("name") or ""


def absolute_cache(harvest_dir, cache_path):
    if not cache_path or os.path.isabs(cache_path):
        return cache_path or ""
    return os.path.join(harvest_dir, cache_path)


# ---- merging, dropping, ordering -----------------------------------------------------------------

def absorbed_key(ruff_code):
    """The (source, code) of the catalog item a Ruff rule reimplements, or None."""
    m = re.fullmatch(r"PL([A-Z])(\d{4})", ruff_code)
    if m:
        return "pylint", m.group(1) + m.group(2)
    m = re.fullmatch(r"B(\d{3})", ruff_code)
    if m:
        return "bugbear", ruff_code
    m = re.fullmatch(r"S(\d{3})", ruff_code)
    if m:
        return "bandit", "B" + m.group(1)
    return None


def pylint_type(item):
    """The Pylint message type letter: the code's first letter, else the harvested category."""
    return (item.get("code") or item.get("category") or " ")[0]


def pylint_drop_reason(item):
    kind = pylint_type(item)
    if kind in ("E", "F"):
        return f"pylint type {kind}"
    code = item.get("code") or ""
    if re.fullmatch(r"C01\d\d", code):
        return "pylint C01xx"
    if re.fullmatch(r"C03\d\d", code):
        return "pylint C03xx"
    return None


def prepare_items(items):
    """Merge reimplementations and drop by rule. Returns (kept, absorbed, dropped) where kept are
    copies carrying an `also` list, absorbed maps (source, id) of an absorbed item to the
    (source, id) of its host, and dropped counts per reason."""
    dropped = collections.Counter()
    live = []
    for item in items:
        status = item.get("status", "")
        if status not in KEPT_STATUSES:
            dropped[f"status {status or '(none)'}"] += 1
            continue
        live.append(dict(item, also=[]))
    index = {(i["source"], item_id(i)): i for i in live}
    absorbed = {}
    for host in live:
        if host["source"] != "ruff" or not host.get("code"):
            continue
        target = absorbed_key(host["code"])
        if target is None or target not in index or target in absorbed:
            continue
        guest = index[target]
        host["also"].append({k: guest.get(k, "") for k in LOCATOR_FIELDS})
        absorbed[target] = ("ruff", item_id(host))
    kept = []
    for item in live:
        if (item["source"], item_id(item)) in absorbed:
            continue
        reason = pylint_drop_reason(item) if item["source"] == "pylint" else None
        if reason:
            dropped[reason] += 1
            continue
        kept.append(item)
    kept.sort(key=sort_key)
    return kept, absorbed, dropped


def sort_key(item):
    source_rank = SOURCES.index(item["source"]) if item["source"] in SOURCES else len(SOURCES)
    code = item.get("code") or ""
    m = re.fullmatch(r"([A-Za-z]*)(\d*)(.*)", code)
    if code and m:
        return source_rank, 0, m.group(1), int(m.group(2)) if m.group(2) else -1, m.group(3), item.get("name", "")
    return source_rank, 1, "", -1, "", item.get("name", "")


def cut_batches(items, size):
    if size < 1:
        raise CorpusError(f"--batch-size must be at least 1, got {size}")
    return [(f"batch-{n:02d}", items[start:start + size]) for n, start in enumerate(range(0, len(items), size), 1)]


# ---- the brief -------------------------------------------------------------------------------------

def collapse_head(text, limit):
    """Collapse whitespace and cut at the last word boundary within `limit` characters."""
    flat = " ".join((text or "").split())
    if len(flat) <= limit:
        return flat
    cut = flat[:limit]
    if flat[limit] != " " and " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip() + " …"


def verdict_definitions(workflow_path=TRIAGE_WORKFLOW):
    """The verdict lines of the triage workflow's prompt, read from the script so both texts agree."""
    if not os.path.isfile(workflow_path):
        raise CorpusError(f"triage workflow not found: {workflow_path}")
    with open(workflow_path, encoding="utf-8") as handle:
        text = handle.read()
    lines = []
    for verdict in VERDICTS:
        m = re.search(rf"^- {re.escape(verdict)} — .*$", text, re.M)
        if not m:
            raise CorpusError(f"verdict {verdict} has no definition line in {workflow_path}")
        lines.append(m.group(0))
    partial = re.search(r"^A rule the universal corpus states only in part.*$", text, re.M)
    if partial:
        lines.append(partial.group(0))
    return lines


@dataclasses.dataclass(frozen=True)
class BriefContext:
    """What every brief of one run carries besides its items."""
    topics: list
    universal: list
    definitions: list
    explanation_chars: int
    harvest_dir: str


def render_brief(batch_id, items, context):
    out = [f"# Triage brief {batch_id} — {len(items)} item(s)", "", "## Criteria of a corpus card", "", CRITERIA, "",
           "## Verdicts", "", *context.definitions, "", "## Topics", ""]
    for t in context.topics:
        out.append(f"- {t['number']}. `{t['slug']}` · domain {t['domain']} · owns: {t.get('owns', '')}")
    out += ["", "## Universal cards", ""]
    by_domain = collections.defaultdict(list)
    for card in context.universal:
        by_domain[card.get("domain", "")].append(card)
    for domain in sorted(by_domain, key=lambda d: (DOMAIN_ORDER.index(d) if d in DOMAIN_ORDER else len(DOMAIN_ORDER), d)):
        out += [f"### {domain}", ""]
        out += [f"- {c['rule_id']} · {c['title']}" for c in sorted(by_domain[domain], key=lambda c: c["rule_id"])]
        out.append("")
    out += ["## Items", ""]
    for item in items:
        name = item.get("name", "") if item.get("code") else ""
        out.append(f"### {item['source']} {item_id(item)} {name}".rstrip())
        out.append(f"title: {item.get('title', '')}")
        out.append(f"summary: {' '.join((item.get('summary') or '').split())}")
        if item.get("also"):
            locators = "; ".join(
                " ".join(part for part in (a["source"], item_id(a), a.get("name", "") if a.get("code") else "",
                                           a.get("url", ""), absolute_cache(context.harvest_dir, a.get("cache_path", ""))) if part)
                for a in item["also"])
            out.append(f"also: {locators}")
        out.append(f"explanation: {collapse_head(item.get('explanation', ''), context.explanation_chars)}")
        out.append("")
    return "\n".join(out)


def done_batches(triage_dir, batch_ids):
    done = []
    for batch_id in batch_ids:
        obj, err = try_read_json(os.path.join(triage_dir, f"{batch_id}.json"))
        if err is None and isinstance(obj, dict) and isinstance(obj.get("verdicts"), list):
            done.append(batch_id)
    return done


def cmd_triage_briefs(opts):
    harvest = os.path.abspath(opts.harvest)
    state = os.path.abspath(opts.state)
    topics = read_json(opts.topics, "topics file")
    universal = read_json(opts.universal, "universal index")
    context = BriefContext(topics, universal, verdict_definitions(), opts.explanation_chars, harvest)
    kept, absorbed, dropped = prepare_items(load_items(harvest))
    batches = cut_batches(kept, opts.batch_size)
    triage_dir = os.path.join(state, "triage")
    brief_dir = os.path.join(triage_dir, "briefs")
    os.makedirs(brief_dir, exist_ok=True)
    produced = set()
    records = []
    for batch_id, items in batches:
        path = os.path.join(brief_dir, f"{batch_id}.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_brief(batch_id, items, context))
        produced.add(path)
        records.append({"id": batch_id, "brief_path": path, "item_count": len(items),
                        "codes": [f"{i['source']} {item_id(i)}" for i in items]})
        print(f"{batch_id}: {len(items)} item(s), {os.path.getsize(path) / 1024:.0f} KB — {path}")
    for stale in glob.glob(os.path.join(brief_dir, "batch-*.md")):
        if stale not in produced:
            os.remove(stale)
    write_json(os.path.join(triage_dir, "batches.json"), records)
    done = done_batches(triage_dir, [r["id"] for r in records])
    args = {"state_dir": state,
            "batches": [{k: r[k] for k in ("id", "brief_path", "item_count")} for r in records],
            "done": done}
    write_json(os.path.join(triage_dir, "args.json"), args)
    drops = ", ".join(f"{reason} {n}" for reason, n in sorted(dropped.items())) or "none"
    print(f"triage-briefs: {len(records)} batch(es), {len(kept)} item(s) kept, {len(absorbed)} merged, "
          f"{sum(dropped.values())} dropped ({drops}); {len(done)} batch(es) done on disk")
    return {"batches": len(records), "items_kept": len(kept), "merged": len(absorbed), "dropped": dict(dropped)}


# ---- triage-merge ------------------------------------------------------------------------------------

def candidate_items(host, raw_index, harvest_dir):
    """The host item and each of its `also` locators, with the fields a candidate carries."""
    out = []
    for ref in [host, *host.get("also", [])]:
        full = raw_index.get((ref["source"], item_id(ref)), ref)
        entry = {k: full.get(k, "") for k in CANDIDATE_ITEM_FIELDS}
        entry["cache_path"] = absolute_cache(harvest_dir, entry["cache_path"])
        out.append(entry)
    return out


def read_results(triage_dir):
    """Return ([(batch id, result object)], [unreadable file records]) of the triage result files."""
    results, unreadable = [], []
    for path in sorted(glob.glob(os.path.join(triage_dir, "batch-*.json"))):
        obj, err = try_read_json(path)
        if err is not None or not isinstance(obj, dict) or not isinstance(obj.get("verdicts"), list):
            unreadable.append({"path": path, "error": err or "no verdicts list"})
            continue
        results.append((os.path.basename(path)[:-len(".json")], obj))
    return results, unreadable


class VerdictCollector:
    """Folds the triage verdicts into candidate groups and the summary lists."""

    def __init__(self, raw_items, slug_order, harvest_dir):
        kept, self.absorbed, _ = prepare_items(raw_items)
        self.raw_index = {(i["source"], item_id(i)): i for i in raw_items}
        self.kept_index = {(i["source"], item_id(i)): i for i in kept}
        self.slug_order = slug_order
        self.harvest_dir = harvest_dir
        self.verdict_counts, self.topic_counts = collections.Counter(), collections.Counter()
        self.groups = {}  # (topic, rule_key) -> candidate under construction
        self.group_of = {}  # (batch, code) -> group key of a python-specific-new verdict
        self.lists = {name: [] for name in ("universal_instances", "duplicates", "not_checkable", "out_of_scope",
                                            "unresolved_verdicts", "batch_notes", "unjudged_items")}

    def resolve(self, source, code):
        key = self.absorbed.get((source, code), (source, code))
        return self.kept_index.get(key)

    def add_items(self, group, source, code):
        host = self.resolve(source, code)
        if host is None:
            self.lists["unresolved_verdicts"].append({"source": source, "code": code})
            entries = [dict.fromkeys(CANDIDATE_ITEM_FIELDS, "") | {"source": source, "code": code}]
        else:
            entries = candidate_items(host, self.raw_index, self.harvest_dir)
        seen = {(e["source"], e["code"] or e["name"]) for e in group["items"]}
        for e in entries:
            if (e["source"], e["code"] or e["name"]) not in seen:
                group["items"].append(e)
                seen.add((e["source"], e["code"] or e["name"]))

    def add_batch(self, batch_id, result, expected_codes):
        if result.get("batch_note"):
            self.lists["batch_notes"].append({"batch": batch_id, "note": result["batch_note"]})
        judged = {f"{v.get('source', '')} {v.get('code', '')}" for v in result["verdicts"]}
        self.lists["unjudged_items"] += [{"batch": batch_id, "item": c} for c in expected_codes if c not in judged]
        for v in result["verdicts"]:
            self.add_verdict(batch_id, v)

    def add_verdict(self, batch_id, v):
        verdict, source, code, note = v.get("verdict", ""), v.get("source", ""), v.get("code", ""), v.get("note", "")
        self.verdict_counts[verdict] += 1
        host = self.resolve(source, code)
        name = host.get("name", "") if host else ""
        if verdict == "python-specific-new":
            topic = v.get("topic", "") if v.get("topic", "") in self.slug_order else UNASSIGNED
            self.topic_counts[topic] += 1
            rule_key = v.get("rule_key") or f"{source}-{code}".lower()
            group = self.groups.setdefault((topic, rule_key), {"rule_key": rule_key, "topic": topic,
                                                               "statement": v.get("statement", ""), "items": [], "notes": []})
            self.add_items(group, source, code)
            if note:
                group["notes"].append(note)
            self.group_of[(batch_id, code)] = (topic, rule_key)
        elif verdict == "universal-instance":
            self.lists["universal_instances"].append({"code": code, "source": source, "name": name,
                                                      "universal_id": v.get("universal_id", ""), "note": note})
        elif verdict == "duplicate-of":
            self.lists["duplicates"].append({"batch": batch_id, "source": source, "code": code,
                                             "duplicate_of": v.get("duplicate_of", ""), "note": note})
        elif verdict in ("not-checkable", "out-of-scope"):
            self.lists[verdict.replace("-", "_")].append({"source": source, "code": code, "name": name, "note": note})

    def attach_duplicates(self):
        """A duplicate of a python-specific-new item is one more catalog entry of the same check."""
        for d in self.lists["duplicates"]:
            gkey = self.group_of.get((d["batch"], d["duplicate_of"]))
            if gkey:
                self.add_items(self.groups[gkey], d["source"], d["code"])

    def topic_rank(self, topic):
        return self.slug_order.get(topic, len(self.slug_order) + 1)

    def candidates(self):
        """One candidate per group; a rule_key that an earlier topic holds takes the suffix -<topic>."""
        ordered = sorted(self.groups.values(), key=lambda g: (self.topic_rank(g["topic"]), g["rule_key"]))
        first_topic, used, out = {}, set(), []
        for g in ordered:
            key = g["rule_key"]
            if first_topic.setdefault(key, g["topic"]) != g["topic"]:
                key = f"{key}-{g['topic']}"
            while key in used:
                key += "-2"
            used.add(key)
            out.append({"key": key, "topic": g["topic"], "statement": g["statement"], "items": g["items"],
                        "notes": " | ".join(g["notes"]), "codes": [e["code"] or e["name"] for e in g["items"]]})
        return sorted(out, key=lambda c: (self.topic_rank(c["topic"]), c["key"]))


def cmd_triage_merge(opts):
    harvest = os.path.abspath(opts.harvest)
    triage_dir = os.path.join(os.path.abspath(opts.state), "triage")
    topics = read_json(opts.topics, "topics file")
    expected = read_json(os.path.join(triage_dir, "batches.json"), "batches.json (run triage-briefs first)")
    collector = VerdictCollector(load_items(harvest), {t["slug"]: t["number"] for t in topics}, harvest)
    results, unreadable = read_results(triage_dir)
    expected_codes = {b["id"]: b.get("codes", []) for b in expected}
    for batch_id, result in results:
        collector.add_batch(batch_id, result, expected_codes.get(batch_id, []))
    collector.attach_duplicates()
    candidates = collector.candidates()
    write_json(os.path.join(os.path.abspath(opts.state), "candidates.json"), candidates)

    present = {batch_id for batch_id, _ in results}
    missing = [b["id"] for b in expected if b["id"] not in present]
    unassigned = collector.topic_counts.get(UNASSIGNED, 0)
    summary = {"verdicts": dict(collector.verdict_counts), "python_specific_per_topic": dict(collector.topic_counts),
               "candidates": len(candidates), "unassigned": unassigned, **collector.lists,
               "missing_batches": missing, "unreadable": unreadable}
    write_json(os.path.join(triage_dir, "summary.json"), summary)
    counts = ", ".join(f"{k} {n}" for k, n in sorted(collector.verdict_counts.items())) or "none"
    print(f"triage-merge: {len(results)} batch file(s); verdicts: {counts}")
    print(f"triage-merge: {len(candidates)} candidate(s) in {len({c['topic'] for c in candidates})} topic(s), "
          f"{unassigned} unassigned verdict(s); missing batches: {', '.join(missing) or 'none'}; "
          f"unreadable: {len(unreadable)}; unresolved: {len(summary['unresolved_verdicts'])}; "
          f"unjudged: {len(summary['unjudged_items'])}")
    return summary


# ---- topic-args --------------------------------------------------------------------------------------

def load_existing_max():
    path = os.path.join(HERE, "write-topic-result.py")
    if not os.path.isfile(path):
        raise CorpusError(f"write-topic-result.py not found beside this script: {path}")
    spec = importlib.util.spec_from_file_location("write_topic_result", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.existing_max


def scan_restart_dir(directory, problems):
    """{key: object} of the *.json files in a restart directory; a file that does not parse is
    appended to `problems` and skipped."""
    found = {}
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        obj, err = try_read_json(path)
        if err is not None or not isinstance(obj, dict):
            problems.append(f"{path}: {err or 'not a JSON object'}")
            continue
        found[obj.get("key") or os.path.basename(path)[:-len(".json")]] = obj
    return found


def scan_spine(directory, problems):
    preferred = os.path.join(directory, "spine.json")
    paths = [preferred] + [p for p in sorted(glob.glob(os.path.join(directory, "*.json"))) if p != preferred]
    for path in paths:
        if not os.path.isfile(path):
            continue
        obj, err = try_read_json(path)
        if err is not None:
            problems.append(f"{path}: {err}")
            continue
        if isinstance(obj, dict) and isinstance(obj.get("spine"), dict):
            return obj["spine"]
    return None


def scan_done(topic_dir, problems):
    """The restart records of a topic run: the spine, the drafts, the verdicts and the closing edits."""
    return {
        "spine": scan_spine(os.path.join(topic_dir, "spine"), problems),
        "drafts": scan_restart_dir(os.path.join(topic_dir, "draft"), problems),
        "verdicts": scan_restart_dir(os.path.join(topic_dir, "verdict"), problems),
        "closing": scan_restart_dir(os.path.join(topic_dir, "closing"), problems),
    }


def cmd_topic_args(opts):
    state = os.path.abspath(opts.state)
    topics = read_json(opts.topics, "topics file")
    topic = next((t for t in topics if t["slug"] == opts.topic), None)
    if topic is None:
        raise CorpusError(f"topic {opts.topic!r} is not in {opts.topics}")
    universal = read_json(opts.universal, "universal index")
    candidates = read_json(os.path.join(state, "candidates.json"), "candidates.json (run triage-merge first)")
    papers_path = opts.papers or os.path.join(state, "harvest", "papers.json")
    papers = read_json(papers_path, "papers file")
    papers = papers.get("papers", []) if isinstance(papers, dict) else papers
    topic_dir = os.path.join(state, opts.topic)
    problems = []
    done = scan_done(topic_dir, problems)
    only_keys = [k for k in (opts.only_keys or "").split(",") if k] or None
    # The topic's candidates go to their own file: the spine judge reads it in one call, and the
    # Workflow args stay small enough to pass inline.
    topic_candidates = [c for c in candidates if c.get("topic") == opts.topic]
    candidates_path = os.path.join(topic_dir, "candidates.json")
    write_json(candidates_path, topic_candidates)
    args = {
        "root": os.path.abspath(opts.root),
        "skill_dir": os.path.abspath(opts.skill),
        "state_dir": topic_dir,
        "harvest_dir": os.path.abspath(opts.harvest),
        "topic": {"slug": topic["slug"], "title": topic["title"], "domain": topic["domain"], "prefix": "PY",
                  "group": "python", "owns": topic.get("owns", ""), "catalogs": topic.get("catalogs", ""), "notes": ""},
        "candidates_path": candidates_path,
        "candidates_count": len(topic_candidates),
        "universal_titles": [f"{c['rule_id']} · {c['title']}"
                             for c in sorted(universal, key=lambda c: c["rule_id"]) if c.get("domain") == topic["domain"]],
        "papers": [p for p in papers if opts.topic in p.get("topics", [])],
        "next_id": load_existing_max()(os.path.abspath(opts.cards_dir), "PY") + 1,
        "max_rules": opts.max_rules,
        "pack_size": opts.pack_size,
        "skeptic_model": opts.skeptic_model,
        "skeptic_effort": opts.skeptic_effort,
        "closing_effort": opts.closing_effort,
        "only_keys": only_keys,
        "done": done,
    }
    path = os.path.join(topic_dir, "args.json")
    write_json(path, args)
    for problem in problems:
        print(f"topic-args: skipped, does not parse: {problem}", file=sys.stderr)
    print(f"topic-args: {path}: {args['candidates_count']} candidate(s) in {candidates_path},{len(args['universal_titles'])} universal title(s), "
          f"{len(args['papers'])} paper(s), next_id {args['next_id']}; done: spine {'yes' if done['spine'] else 'no'}, "
          f"{len(done['drafts'])} draft(s), {len(done['verdicts'])} verdict(s), {len(done['closing'])} closing; "
          f"{len(problems)} unparseable file(s) skipped")
    return args


# ---- save-run ----------------------------------------------------------------------------------------

def cmd_save_run(opts):
    run = read_json(opts.source, "workflow output")
    cards = run.get("result", {}).get("cards") if isinstance(run, dict) and isinstance(run.get("result"), dict) else None
    if not isinstance(cards, list):
        raise CorpusError(f"{opts.source} holds no result.cards list")
    target = os.path.join(os.path.abspath(opts.state), opts.topic, "run.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(opts.source, target)
    print(f"save-run: {target}: {len(cards)} card(s)")
    return target


# ---- command line ------------------------------------------------------------------------------------

def parse_args(argv):
    parser = argparse.ArgumentParser(prog="python-corpus.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("triage-briefs")
    p.add_argument("--harvest", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--topics", required=True)
    p.add_argument("--universal", required=True)
    p.add_argument("--batch-size", type=int, default=80)
    p.add_argument("--explanation-chars", type=int, default=500)
    p = sub.add_parser("triage-merge")
    p.add_argument("--state", required=True)
    p.add_argument("--harvest", required=True)
    p.add_argument("--topics", required=True)
    p = sub.add_parser("topic-args")
    for flag in ("--state", "--topic", "--topics", "--universal", "--harvest", "--skill", "--root", "--cards-dir"):
        p.add_argument(flag, required=True)
    p.add_argument("--papers")
    p.add_argument("--max-rules", type=int, default=10)
    p.add_argument("--pack-size", type=int, default=5)
    p.add_argument("--skeptic-model", default="claude-fable-5-1")
    p.add_argument("--skeptic-effort", default="high")
    p.add_argument("--closing-effort", default="high")
    p.add_argument("--only-keys")
    p = sub.add_parser("save-run")
    p.add_argument("--state", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--from", dest="source", required=True)
    return parser.parse_args(argv)


COMMANDS = {"triage-briefs": cmd_triage_briefs, "triage-merge": cmd_triage_merge,
            "topic-args": cmd_topic_args, "save-run": cmd_save_run}


def main(argv):
    opts = parse_args(argv)
    try:
        COMMANDS[opts.command](opts)
    except CorpusError as exc:
        print(f"python-corpus {opts.command}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
