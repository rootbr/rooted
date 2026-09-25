#!/usr/bin/env python3
"""Pre-pass of the reviewing-java workflow: no LLM, standard library only.

Reads `git diff -U0 <diff_ref> -- '*.java' [path_filter]`, the frontmatter of
every review card, and the project's `.claude/reviewing-java/config.md`, and
writes `review/plan.json` plus `review/plan.log`. Nothing else is written; no
network is opened.

plan.json carries:
  inventory     base_sha, head_sha, changed files with packages and hunks (added
                lines with line numbers), size class, build files, config state
  cards         the card index: rule_id, path, domain, triggers, scope,
                check_kind, severity_default, title
  jobs          one per (card x slice): the files whose added lines match the
                card's triggers, with the matching hunks only
  slices        three to eight file groups for the always-on logic pass
  candidates    mechanical hits named outright, tagged needs_verification
  project_cards PROJ-N cards parsed from config.md, plus project card files
  meta_run      whether the META cards run (config.md changed, or --meta)

Usage:
  python3 static-review.py --diff-ref <base...head | a..b | commit> --cards-dir <dir>
         [--path-filter <subtree>] [--repo <root>] [--out-dir review] [--meta]
         [--max-job-lines 400] [--max-jobs 96] [--config .claude/reviewing-java/config.md]
Exit status: 0 with a plan; 2 when the diff holds no Java change (an empty plan
is still written, so the caller can tell "nothing to review" from a crash).
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import read_card  # noqa: E402

BUILD_FILES = ("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts")
DEFAULT_CONFIG = os.path.join(".claude", "reviewing-java", "config.md")
PROJECT_CARDS_DIR = os.path.join(".claude", "reviewing-java", "cards")
SIZE_SMALL_MAX, SIZE_MEDIUM_MAX = 19, 49
MIN_SLICES, MAX_SLICES = 3, 8

# Mechanical hits the regexes can name outright. `rule_id` names the card that
# owns the pattern once it exists; a hit stays a candidate either way, and the
# finder confirms it instead of searching for it.
CANDIDATES = [
    {"id": "pattern-compile-in-method", "rule_id": "PF-16",
     "test": lambda line, ctx: "Pattern.compile(" in line and "static" not in line},
    {"id": "simple-date-format", "rule_id": "PF-17",
     "test": lambda line, ctx: "new SimpleDateFormat(" in line},
    {"id": "runtime-exec", "rule_id": "SEC-04",
     "test": lambda line, ctx: "Runtime.getRuntime().exec(" in line},
    {"id": "weak-message-digest", "rule_id": "SEC-49",
     "test": lambda line, ctx: re.search(r'MessageDigest\.getInstance\(\s*"(MD5|SHA1|SHA-1)"', line) is not None},
    {"id": "jackson-default-typing", "rule_id": "SEC-38",
     "test": lambda line, ctx: "enableDefaultTyping(" in line or "activateDefaultTyping(" in line},
    {"id": "random-for-secret", "rule_id": "SEC-31",
     "test": lambda line, ctx: "new Random(" in line and re.search(r"token|secret|password|nonce|salt|otp", ctx["window"], re.I) is not None},
    {"id": "synchronized-wrapper-on-concurrent-map", "rule_id": "PF-10",
     "test": lambda line, ctx: re.search(r"Collections\.synchronized\w+\(\s*new Concurrent", line) is not None},
    {"id": "print-stack-trace", "rule_id": None,
     "test": lambda line, ctx: ".printStackTrace()" in line},
    {"id": "empty-catch", "rule_id": None,
     "test": lambda line, ctx: re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", line) is not None
     or (re.search(r"catch\s*\([^)]*\)\s*\{\s*$", line) is not None and re.match(r"\s*\}\s*$", ctx["next"]) is not None)},
]


class Log:
    def __init__(self):
        self.lines = []

    def __call__(self, msg):
        self.lines.append(msg)


def die(msg):
    sys.exit(f"static-review: {msg}")


def git(repo, *args):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if out.returncode != 0:
        die(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def resolve_refs(repo, diff_ref):
    """Return (base_sha, head_sha) for the three accepted forms."""
    if "..." in diff_ref:
        a, b = diff_ref.split("...", 1)
        b = b or "HEAD"
        base = git(repo, "merge-base", a, b).strip()
        head = git(repo, "rev-parse", b).strip()
    elif ".." in diff_ref:
        a, b = diff_ref.split("..", 1)
        b = b or "HEAD"
        base = git(repo, "rev-parse", a).strip()
        head = git(repo, "rev-parse", b).strip()
    else:
        head = git(repo, "rev-parse", diff_ref).strip()
        base = git(repo, "rev-parse", f"{diff_ref}~1").strip()
    return base, head


HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse_diff(text):
    """Parse `git diff -U0` output into file records with added-line hunks."""
    files, cur, hunk, new_no = [], None, None, 0
    for raw in text.split("\n"):
        if raw.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*) b/(.*)$", raw)
            cur = {"path": m.group(2) if m else raw[11:], "status": "modified", "hunks": [],
                   "added_lines": 0, "removed_lines": 0}
            files.append(cur)
            hunk = None
            continue
        if cur is None:
            continue
        if raw.startswith("new file mode"):
            cur["status"] = "added"
            continue
        if raw.startswith("deleted file mode"):
            cur["status"] = "deleted"
            continue
        if raw.startswith("rename from"):
            cur["status"] = "renamed"
            continue
        if raw.startswith("+++ ") or raw.startswith("--- ") or raw.startswith("index "):
            continue
        hm = HUNK.match(raw)
        if hm:
            new_no = int(hm.group(3))
            hunk = {"start": new_no, "old_start": int(hm.group(1)), "lines": []}
            cur["hunks"].append(hunk)
            continue
        if hunk is None:
            continue
        if raw.startswith("+"):
            hunk["lines"].append({"no": new_no, "text": raw[1:]})
            cur["added_lines"] += 1
            new_no += 1
        elif raw.startswith("-"):
            cur["removed_lines"] += 1
    for f in files:
        f["hunks"] = [h for h in f["hunks"] if h["lines"]]
    return [f for f in files if f["status"] != "deleted"]


def package_of(repo, head_sha, path):
    """The Java package of a changed file: read from the file at HEAD, else from the path."""
    try:
        src = subprocess.run(["git", "-C", repo, "show", f"{head_sha}:{path}"],
                             capture_output=True, text=True, errors="replace").stdout
        m = re.search(r"^\s*package\s+([\w.]+)\s*;", src, re.M)
        if m:
            return m.group(1)
    except OSError:
        pass
    m = re.search(r"(?:^|/)java/(.+)/[^/]+\.java$", path)
    return m.group(1).replace("/", ".") if m else ""


def config_file_record(repo, config_path, config_rel, base_sha, head_sha, changed):
    """The config as a file record for the META cards: its diff hunks when the diff
    changed it, else the whole file as one hunk so a --meta run reads all of it."""
    if changed:
        parsed = parse_diff(git(repo, "diff", "-U0", "--no-color", "--no-ext-diff", base_sha, head_sha, "--", config_rel))
        rec = parsed[0] if parsed else {"status": "modified", "hunks": [], "added_lines": 0, "removed_lines": 0}
    else:
        with open(config_path, encoding="utf-8") as handle:
            lines = handle.read().split("\n")
        rec = {"status": "unchanged", "removed_lines": 0, "added_lines": len(lines),
               "hunks": [{"start": 1, "old_start": 1, "lines": [{"no": i + 1, "text": l} for i, l in enumerate(lines)]}]}
    rec.update({"path": config_rel, "package": "", "group": "(config)", "kind": "config"})
    return rec


def size_class(n):
    if n == 0:
        return None
    if n <= SIZE_SMALL_MAX:
        return "SMALL"
    if n <= SIZE_MEDIUM_MAX:
        return "MEDIUM"
    return "LARGE"


def parse_config(text):
    """Return (frontmatter dict, body) of config.md; a malformed file yields ({}, text)."""
    m = re.match(r"---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).split("\n"):
        km = re.match(r"^([\w-]+):\s*(.*)$", line)
        if km:
            v = km.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                v = v[1:-1]
            fm[km.group(1)] = v
    return fm, m.group(2)


def parse_modules(fm):
    """`modules: [{name, packages: [..]}]` in the config frontmatter; JSON-shaped or absent."""
    raw = fm.get("modules")
    if not raw:
        return []
    try:
        mods = json.loads(raw)
    except ValueError:
        return []
    out = []
    for m in mods if isinstance(mods, list) else []:
        if isinstance(m, dict) and m.get("name") and isinstance(m.get("packages"), list):
            out.append({"name": str(m["name"]), "packages": [str(p) for p in m["packages"]]})
    return out


INVARIANT = re.compile(r"^\s*(\d+)\.\s+\*\*(.+?)\*\*\s*:\s*(.*)$")


def parse_invariants(body):
    """Numbered invariants `N. **Title**: rule. Violation: consequence.` → PROJ-N cards."""
    cards, cur = [], None
    for line in body.split("\n"):
        im = INVARIANT.match(line)
        if im:
            cur = {"n": int(im.group(1)), "title": im.group(2).strip(), "text": im.group(3).strip()}
            cards.append(cur)
            continue
        if cur is not None and line.strip() and not line.startswith("#") and re.match(r"^\s+\S", line):
            cur["text"] += " " + line.strip()
            continue
        cur = None
    out = []
    for c in cards:
        text = c["text"]
        vm = re.search(r"\bViolation\s*:\s*(.*)$", text)
        rule = text[:vm.start()].strip() if vm else text.strip()
        violation = vm.group(1).strip() if vm else ""
        numbers = [s.strip() for s in re.split(r"(?<=[.;])\s+", text) if re.search(r"\d", s)]
        out.append({
            "rule_id": f"PROJ-{c['n']}",
            "title": c["title"],
            "thesis": rule,
            "validator": violation or f"The diff shows the forbidden state of: {rule}",
            "rationale": " ".join(numbers) if numbers else "",
        })
    return out


def matches(card, line):
    if not card["triggers"]:
        return True
    return any(re.search(t, line) for t in card["_compiled"])


def build_jobs(cards, files, modules, max_job_lines, max_jobs, log, config_files=()):
    """One job per (card x slice). A `meta` card reads the project config, so its
    slice is drawn from `config_files`; every other card reads the Java files."""
    jobs = []
    for card in cards:
        card["_compiled"] = [re.compile(t) for t in card["triggers"]]
        slice_files = []
        for f in (config_files if card["domain"] == "meta" else files):
            hunks = [h for h in f["hunks"] if any(matches(card, ln["text"]) for ln in h["lines"])]
            if hunks:
                slice_files.append({"path": f["path"], "package": f["package"], "group": f["group"],
                                    "hunks": hunks,
                                    "added_lines": sum(len(h["lines"]) for h in hunks)})
        if not slice_files:
            continue
        total = sum(sf["added_lines"] for sf in slice_files)
        rec = {k: v for k, v in card.items() if not k.startswith("_")}
        if total <= max_job_lines:
            jobs.append(make_job(rec, "all", slice_files))
            continue
        groups = {}
        for sf in slice_files:
            groups.setdefault(sf["group"], []).append(sf)
        log(f"{card['rule_id']}: {total} matching added lines exceed {max_job_lines}; split into {len(groups)} job(s) by {'module' if modules else 'package'}")
        for name, sfs in sorted(groups.items()):
            jobs.append(make_job(rec, name, sfs))
    # cap: merge one card's jobs back first, then drop suggestion jobs, then minor jobs
    while len(jobs) > max_jobs:
        per_card = {}
        for j in jobs:
            per_card.setdefault(j["card"]["rule_id"], []).append(j)
        multi = sorted((v for v in per_card.values() if len(v) > 1), key=len, reverse=True)
        if multi:
            group = multi[0]
            merged_files = [sf for j in group for sf in j["slice"]["files"]]
            jobs = [j for j in jobs if j not in group] + [make_job(group[0]["card"], "all", merged_files)]
            log(f"cap {max_jobs}: merged {len(group)} jobs of {group[0]['card']['rule_id']} back into one")
            continue
        dropped = False
        for sev in ("suggestion", "minor"):
            cands = sorted((j for j in jobs if j["card"]["severity_default"] == sev), key=lambda j: j["slice"]["added_lines"])
            if cands:
                jobs.remove(cands[0])
                log(f"cap {max_jobs}: dropped job {cands[0]['id']} ({sev}, {cands[0]['slice']['added_lines']} lines)")
                dropped = True
                break
        if not dropped:
            log(f"cap {max_jobs}: exceeded by {len(jobs) - max_jobs} with no droppable job left; all {len(jobs)} kept")
            break
    return jobs


def make_job(card, name, slice_files):
    return {"id": f"{card['rule_id']}:{name}", "card": card,
            "slice": {"name": name, "files": slice_files,
                      "added_lines": sum(sf["added_lines"] for sf in slice_files)}}


def common_prefix(packages):
    segs = [p.split(".") for p in packages if p]
    if not segs:
        return []
    prefix = segs[0]
    for s in segs[1:]:
        i = 0
        while i < min(len(prefix), len(s)) and prefix[i] == s[i]:
            i += 1
        prefix = prefix[:i]
    return prefix


def assign_groups(files, modules):
    """Group key per file: the config module whose package prefix matches, else the
    package prefix one segment below the common root of all changed files (at least
    two segments, so a bare `com` or `org` never names a group)."""
    prefix = common_prefix([f["package"] for f in files])
    for f in files:
        f["group"] = None
        for m in modules:
            if any(f["package"] == p or f["package"].startswith(p + ".") for p in m["packages"]):
                f["group"] = m["name"]
                break
        if f["group"] is None:
            segs = f["package"].split(".") if f["package"] else []
            # the package prefix one segment below the common root, at least two segments long
            f["group"] = ".".join(segs[:max(len(prefix) + 1, 2)]) or "(default)"


def build_slices(files, log):
    """Three to eight file groups for the logic pass; fewer than three files → one per file."""
    if len(files) < MIN_SLICES:
        return [{"name": os.path.basename(f["path"]), "packages": [f["package"]], "files": [f["path"]],
                 "added_lines": f["added_lines"]} for f in files]
    groups = {}
    for f in files:
        groups.setdefault(f["group"], []).append(f)
    slices = [{"name": k, "files": v} for k, v in sorted(groups.items())]
    while len(slices) > MAX_SLICES:
        slices.sort(key=lambda s: len(s["files"]))
        a, b = slices[0], slices[1]
        merged = {"name": f"{a['name']}+{b['name']}", "files": a["files"] + b["files"]}
        slices = [merged] + slices[2:]
        log(f"slices: merged {a['name']} and {b['name']} to stay within {MAX_SLICES}")
    while len(slices) < MIN_SLICES:
        slices.sort(key=lambda s: len(s["files"]), reverse=True)
        big = slices[0]
        if len(big["files"]) < 2:
            break
        # split the largest group by the package segment below its own common root
        root = common_prefix([f["package"] for f in big["files"]])
        sub = {}
        for f in big["files"]:
            rest = f["package"].split(".")[len(root):] if f["package"] else []
            key = f"{big['name']}/{rest[0]}" if rest else f"{big['name']}/(root)"
            sub.setdefault(key, []).append(f)
        if len(sub) < 2:
            half = len(big["files"]) // 2
            sub = {f"{big['name']}/1": big["files"][:half], f"{big['name']}/2": big["files"][half:]}
        slices = slices[1:] + [{"name": k, "files": v} for k, v in sorted(sub.items())]
        log(f"slices: split {big['name']} into {len(sub)} to reach {MIN_SLICES}")
    out = []
    for s in sorted(slices, key=lambda s: s["name"]):
        out.append({"name": s["name"], "packages": sorted({f["package"] for f in s["files"]}),
                    "files": [f["path"] for f in s["files"]],
                    "added_lines": sum(f["added_lines"] for f in s["files"])})
    return out


def find_candidates(files):
    out = []
    for f in files:
        for h in f["hunks"]:
            lines = h["lines"]
            for i, ln in enumerate(lines):
                ctx = {"window": "\n".join(x["text"] for x in lines[max(0, i - 5):i + 6]),
                       "next": lines[i + 1]["text"] if i + 1 < len(lines) else ""}
                for c in CANDIDATES:
                    try:
                        hit = c["test"](ln["text"], ctx)
                    except Exception:  # a heuristic never aborts the plan
                        hit = False
                    if hit:
                        out.append({"id": c["id"], "rule_id": c["rule_id"], "file": f["path"],
                                    "line": ln["no"], "text": ln["text"].strip(), "status": "needs_verification"})
    return out


def load_cards(cards_dir, log):
    cards = []
    for name in sorted(os.listdir(cards_dir)):
        if not name.endswith(".md"):
            continue
        rec, err = read_card(os.path.join(cards_dir, name))
        if err:
            log(f"card {name} skipped: {err}")
            continue
        rec["path"] = os.path.abspath(rec["path"])
        cards.append(rec)
    return cards


def parse_args(argv):
    opts = {"diff_ref": None, "cards_dir": None, "path_filter": "", "repo": ".", "out_dir": "review",
            "meta": False, "max_job_lines": 400, "max_jobs": 96, "config": DEFAULT_CONFIG}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--meta":
            opts["meta"] = True
            i += 1
            continue
        if a.startswith("--") and i + 1 < len(argv):
            key = a[2:].replace("-", "_")
            if key not in opts:
                die(f"unknown option {a}")
            val = argv[i + 1]
            opts[key] = int(val) if key in ("max_job_lines", "max_jobs") else val
            i += 2
            continue
        die(f"unexpected argument {a!r}")
    if not opts["diff_ref"] or not opts["cards_dir"]:
        die("--diff-ref and --cards-dir are required")
    return opts


def build_plan(opts, log):
    repo = os.path.abspath(opts["repo"])
    base_sha, head_sha = resolve_refs(repo, opts["diff_ref"])
    args = ["diff", "-U0", "--no-color", "--no-ext-diff", base_sha, head_sha, "--", "*.java"]
    if opts["path_filter"]:
        args.append(opts["path_filter"])
    files = parse_diff(git(repo, *args))
    for f in files:
        f["package"] = package_of(repo, head_sha, f["path"])
    config_path = os.path.join(repo, opts["config"])
    config, body, invariants, modules = None, "", [], []
    if os.path.isfile(config_path):
        with open(config_path, encoding="utf-8") as handle:
            config, body = parse_config(handle.read())
        invariants = parse_invariants(body)
        modules = parse_modules(config)
    changed_all = git(repo, "diff", "--name-only", base_sha, head_sha).split("\n")
    config_rel = os.path.relpath(config_path, repo).replace(os.sep, "/")
    config_changed = config_rel in changed_all
    assign_groups(files, modules)
    cards = load_cards(opts["cards_dir"], log)
    project_dir = os.path.join(repo, PROJECT_CARDS_DIR)
    card_paths = []
    if os.path.isdir(project_dir):
        for name in sorted(os.listdir(project_dir)):
            if name.endswith(".md"):
                p = os.path.join(project_dir, name)
                rec, err = read_card(p)
                if err:
                    log(f"project card {name} skipped: {err}")
                    continue
                rec["path"] = os.path.abspath(p)
                cards.append(rec)
                card_paths.append(os.path.relpath(p, repo).replace(os.sep, "/"))
    meta_run = (config_changed or opts["meta"]) and config is not None
    active = [c for c in cards if c["domain"] != "meta" or meta_run]
    if not meta_run:
        skipped = [c["rule_id"] for c in cards if c["domain"] == "meta"]
        if skipped:
            log(f"META cards {skipped} not run: " + ("no config.md" if config is None else "config.md unchanged and --meta not passed"))
    config_files = [config_file_record(repo, config_path, config_rel, base_sha, head_sha, config_changed)] if meta_run else []
    jobs = build_jobs(active, files, modules, opts["max_job_lines"], opts["max_jobs"], log, config_files) if (files or config_files) else []
    slices = build_slices(files, log) if files else []
    build_files = [b for b in BUILD_FILES if os.path.isfile(os.path.join(repo, b))]
    plan = {
        "inventory": {
            "diff_ref": f"{base_sha}...{head_sha}", "base_sha": base_sha, "head_sha": head_sha,
            "path_filter": opts["path_filter"], "size_class": size_class(len(files)),
            "file_count": len(files),
            "files": [{"path": f["path"], "package": f["package"], "group": f["group"], "status": f["status"],
                       "hunks": f["hunks"], "added_lines": f["added_lines"], "removed_lines": f["removed_lines"]}
                      for f in files],
            "build_files": build_files,
            "config_path": config_rel if config is not None else None,
            "config_changed": config_changed,
            "config": config,
            "config_file": config_files[0] if config_files else None,
        },
        "cards": [{k: v for k, v in c.items() if not k.startswith("_")} for c in cards],
        "jobs": jobs,
        "slices": slices,
        "candidates": find_candidates(files),
        "project_cards": {"cards": invariants, "card_paths": card_paths},
        "meta_run": meta_run,
    }
    if not files:
        log("No Java changes in this scope")
    log(f"{len(files)} file(s), size {plan['inventory']['size_class']}, {len(cards)} card(s), {len(jobs)} job(s), {len(slices)} slice(s), {len(plan['candidates'])} candidate(s)")
    return plan


def main(argv):
    opts = parse_args(argv)
    log = Log()
    plan = build_plan(opts, log)
    out_dir = os.path.join(os.path.abspath(opts["repo"]), opts["out_dir"])
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "plan.json"), "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=1)
    with open(os.path.join(out_dir, "plan.log"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(log.lines) + "\n")
    print("\n".join(log.lines))
    return 2 if not plan["inventory"]["files"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
