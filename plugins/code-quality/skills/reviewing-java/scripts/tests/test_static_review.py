#!/usr/bin/env python3
"""Unit tests for static-review.py: hunk parsing, trigger selection, slice merge and
split, the job cap and its log, config.md invariant parsing, candidates, and the
empty-diff case, plus one end-to-end run on a temporary git repository.

Run:  python3 -m unittest discover -s scripts/tests   (from the skill directory)
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location("static_review", os.path.join(SCRIPTS, "static-review.py"))
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)

DIFF = """diff --git a/src/main/java/com/acme/core/Cache.java b/src/main/java/com/acme/core/Cache.java
index 1111111..2222222 100644
--- a/src/main/java/com/acme/core/Cache.java
+++ b/src/main/java/com/acme/core/Cache.java
@@ -10,0 +11,2 @@ public class Cache {
+    if (!cache.containsKey(k)) cache.put(k, load(k));
+    counter++;
@@ -30 +32 @@ public class Cache {
-    old line
+    new line
diff --git a/src/main/java/com/acme/web/Api.java b/src/main/java/com/acme/web/Api.java
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/src/main/java/com/acme/web/Api.java
@@ -0,0 +1,3 @@
+package com.acme.web;
+public class Api {
+}
diff --git a/src/main/java/com/acme/core/Gone.java b/src/main/java/com/acme/core/Gone.java
deleted file mode 100644
index 4444444..0000000
--- a/src/main/java/com/acme/core/Gone.java
+++ /dev/null
@@ -1,2 +0,0 @@
-package com.acme.core;
-class Gone {}
"""

CONFIG = """---
project_name: Demo
base_branch: main
modules: [{"name": "core", "packages": ["com.acme.core"]}, {"name": "web", "packages": ["com.acme.web"]}]
---
# Demo context

## Invariants

### Data
1. **Sentinel at index 0**: Index 0 is reserved and never holds data; iterations use `> 0`.
   Violation: reads garbage.
2. **Allocation-free onEvent**: `Dispatcher#onEvent` runs ~50 M times/day and allocates nothing. Violation: G1 mixed collections every minute.

Prose that is not an invariant.
3. **No violation clause**: rule text only
"""


def card(rule_id, domain, triggers, severity="major", scope="file", kind="mechanical"):
    return {"rule_id": rule_id, "path": f"/cards/{rule_id.lower()}.md", "title": rule_id, "domain": domain,
            "triggers": triggers, "scope": scope, "check_kind": kind, "severity_default": severity}


def fake_file(path, package, n_lines, text="x = y;"):
    return {"path": path, "package": package, "status": "modified", "removed_lines": 0,
            "hunks": [{"start": 1, "old_start": 1, "lines": [{"no": i + 1, "text": text} for i in range(n_lines)]}],
            "added_lines": n_lines}


class ParseDiff(unittest.TestCase):
    def test_hunks_and_statuses(self):
        files = sr.parse_diff(DIFF)
        self.assertEqual([f["path"] for f in files],
                         ["src/main/java/com/acme/core/Cache.java", "src/main/java/com/acme/web/Api.java"])
        cache = files[0]
        self.assertEqual(cache["status"], "modified")
        self.assertEqual(len(cache["hunks"]), 2)
        self.assertEqual(cache["hunks"][0]["start"], 11)
        self.assertEqual([l["no"] for l in cache["hunks"][0]["lines"]], [11, 12])
        self.assertEqual(cache["hunks"][1]["lines"][0], {"no": 32, "text": "    new line"})
        self.assertEqual(cache["added_lines"], 3)
        self.assertEqual(cache["removed_lines"], 1)
        self.assertEqual(files[1]["status"], "added")
        self.assertEqual(files[1]["added_lines"], 3)


class TriggerSelection(unittest.TestCase):
    def setUp(self):
        self.files = sr.parse_diff(DIFF)
        for f in self.files:
            f["package"] = "com.acme.core" if "core" in f["path"] else "com.acme.web"
        sr.assign_groups(self.files, [])

    def test_matching_hunks_only(self):
        log = sr.Log()
        jobs = sr.build_jobs([card("CC-08", "concurrency", [r"containsKey\("])], self.files, [], 400, 96, log)
        self.assertEqual(len(jobs), 1)
        job = jobs[0]
        self.assertEqual(job["id"], "CC-08:all")
        self.assertEqual([sf["path"] for sf in job["slice"]["files"]], ["src/main/java/com/acme/core/Cache.java"])
        self.assertEqual(job["slice"]["files"][0]["hunks"], [0])
        self.assertEqual(self.files[0]["hunks"][0]["start"], 11)
        self.assertEqual(job["rule_id"], "CC-08")

    def test_no_match_no_job(self):
        jobs = sr.build_jobs([card("SEC-01", "security", [r"executeQuery\("])], self.files, [], 400, 96, sr.Log())
        self.assertEqual(jobs, [])

    def test_empty_triggers_match_every_file(self):
        jobs = sr.build_jobs([card("MNT-01", "maintainability", [])], self.files, [], 400, 96, sr.Log())
        self.assertEqual(len(jobs), 1)
        self.assertEqual(len(jobs[0]["slice"]["files"]), 2)
        self.assertEqual(jobs[0]["slice"]["files"][0]["hunks"], [0, 1])


class SliceMergeAndSplit(unittest.TestCase):
    def test_split_when_over_line_budget(self):
        files = [fake_file(f"src/main/java/com/acme/{pkg}/F{i}.java", f"com.acme.{pkg}", 150, "foo();")
                 for i, pkg in enumerate(["a", "b", "c"])]
        sr.assign_groups(files, [])
        log = sr.Log()
        jobs = sr.build_jobs([card("PF-01", "performance", [r"foo\("])], files, [], 400, 96, log)
        self.assertEqual(sorted(j["id"] for j in jobs), ["PF-01:com.acme.a", "PF-01:com.acme.b", "PF-01:com.acme.c"])
        self.assertTrue(any("split into 3" in l for l in log.lines))

    def test_modules_drive_grouping(self):
        files = [fake_file("src/main/java/com/acme/core/A.java", "com.acme.core.deep", 1),
                 fake_file("src/main/java/com/acme/web/B.java", "com.acme.web", 1),
                 fake_file("src/main/java/org/other/C.java", "org.other", 1)]
        sr.assign_groups(files, [{"name": "kernel", "packages": ["com.acme.core"]}])
        self.assertEqual([f["group"] for f in files], ["kernel", "com.acme", "org.other"])

    def test_logic_slices_between_three_and_eight(self):
        files = [fake_file(f"src/main/java/com/acme/p{i}/F.java", f"com.acme.p{i}", 1) for i in range(12)]
        sr.assign_groups(files, [])
        log = sr.Log()
        slices = sr.build_slices(files, log)
        self.assertLessEqual(len(slices), 8)
        self.assertGreaterEqual(len(slices), 3)
        self.assertEqual(sum(len(s["files"]) for s in slices), 12)
        self.assertTrue(any("merged" in l for l in log.lines))

    def test_logic_slices_split_single_package(self):
        files = [fake_file(f"src/main/java/com/acme/core/{sub}/F{i}.java", f"com.acme.core.{sub}", 1)
                 for i, sub in enumerate(["a", "a", "b", "b", "c", "c"])]
        sr.assign_groups(files, [])
        slices = sr.build_slices(files, sr.Log())
        self.assertGreaterEqual(len(slices), 3)
        self.assertEqual(sum(len(s["files"]) for s in slices), 6)

    def test_fewer_than_three_files_one_slice_each(self):
        files = [fake_file("A.java", "a", 1), fake_file("B.java", "b", 1)]
        sr.assign_groups(files, [])
        slices = sr.build_slices(files, sr.Log())
        self.assertEqual([s["files"] for s in slices], [["A.java"], ["B.java"]])


class JobCap(unittest.TestCase):
    def test_merge_then_drop_with_log(self):
        files = [fake_file(f"src/main/java/com/acme/{pkg}/F.java", f"com.acme.{pkg}", 300, "foo();")
                 for pkg in ["a", "b", "c"]]
        sr.assign_groups(files, [])
        cards = [card("PF-01", "performance", [r"foo\("]),               # splits into 3 jobs
                 card("MNT-01", "maintainability", [r"foo\("], "suggestion"),
                 card("MNT-02", "maintainability", [r"foo\("], "minor"),
                 card("CC-01", "concurrency", [r"foo\("], "major")]
        log = sr.Log()
        jobs = sr.build_jobs(cards, files, [], 400, 2, log)
        self.assertEqual(len(jobs), 2)
        ids = {j["rule_id"] for j in jobs}
        self.assertIn("CC-01", ids)
        self.assertIn("PF-01", ids)
        self.assertTrue(any("merged 3 jobs of PF-01" in l for l in log.lines))
        self.assertTrue(any("dropped job MNT-01:all (suggestion" in l for l in log.lines))
        self.assertTrue(any("dropped job MNT-02:all (minor" in l for l in log.lines))

    def test_cap_never_drops_major_silently(self):
        files = [fake_file("A.java", "a", 1, "foo();")]
        sr.assign_groups(files, [])
        cards = [card(f"CC-0{i}", "concurrency", [r"foo\("], "major") for i in range(1, 5)]
        log = sr.Log()
        jobs = sr.build_jobs(cards, files, [], 400, 2, log)
        self.assertEqual(len(jobs), 4)
        self.assertTrue(any("exceeded by 2" in l for l in log.lines))


class ConfigParsing(unittest.TestCase):
    def test_frontmatter_and_modules(self):
        fm, body = sr.parse_config(CONFIG)
        self.assertEqual(fm["project_name"], "Demo")
        self.assertEqual(sr.parse_modules(fm), [{"name": "core", "packages": ["com.acme.core"]},
                                                {"name": "web", "packages": ["com.acme.web"]}])
        self.assertIn("## Invariants", body)

    def test_invariants_become_proj_cards(self):
        _, body = sr.parse_config(CONFIG)
        cards = sr.parse_invariants(body)
        self.assertEqual([c["rule_id"] for c in cards], ["PROJ-1", "PROJ-2", "PROJ-3"])
        self.assertEqual(cards[0]["title"], "Sentinel at index 0")
        self.assertTrue(cards[0]["thesis"].startswith("Index 0 is reserved"))
        self.assertEqual(cards[0]["validator"], "reads garbage.")
        self.assertIn("50 M", cards[1]["rationale"])
        self.assertEqual(cards[1]["validator"], "G1 mixed collections every minute.")
        self.assertTrue(cards[2]["validator"].startswith("The diff shows the forbidden state of"))

    def test_malformed_config_is_tolerated(self):
        fm, body = sr.parse_config("no frontmatter here\n1. **X**: y. Violation: z.")
        self.assertEqual(fm, {})
        self.assertEqual(len(sr.parse_invariants(body)), 1)


class Candidates(unittest.TestCase):
    def test_named_hits(self):
        text = ["Pattern p = Pattern.compile(\"x\");", "private static final Pattern P = Pattern.compile(\"y\");",
                "Random r = new Random();", "String token = Long.toHexString(r.nextLong());",
                "Map<K,V> m = Collections.synchronizedMap(new ConcurrentHashMap<>());",
                "} catch (IOException e) {", "}"]
        f = {"path": "A.java", "hunks": [{"start": 1, "lines": [{"no": i + 1, "text": t} for i, t in enumerate(text)]}]}
        ids = [(c["id"], c["line"]) for c in sr.find_candidates([f])]
        self.assertIn(("pattern-compile-in-method", 1), ids)
        self.assertNotIn(("pattern-compile-in-method", 2), ids)
        self.assertIn(("random-for-secret", 3), ids)
        self.assertIn(("synchronized-wrapper-on-concurrent-map", 5), ids)
        self.assertIn(("empty-catch", 6), ids)
        self.assertTrue(all(c["status"] == "needs_verification" for c in sr.find_candidates([f])))


def make_repo(tmp, with_java_change=True):
    subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x",
           "PATH": os.environ["PATH"], "HOME": tmp}
    src = os.path.join(tmp, "src", "main", "java", "com", "acme")
    os.makedirs(src)
    os.makedirs(os.path.join(tmp, ".claude", "reviewing-java"))
    with open(os.path.join(tmp, "pom.xml"), "w") as h:
        h.write("<project/>")
    with open(os.path.join(src, "Cache.java"), "w") as h:
        h.write("package com.acme;\npublic class Cache {\n}\n")
    with open(os.path.join(tmp, ".claude", "reviewing-java", "config.md"), "w") as h:
        h.write(CONFIG)
    subprocess.run(["git", "-C", tmp, "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", tmp, "commit", "-q", "-m", "base"], check=True, env=env)
    if with_java_change:
        with open(os.path.join(src, "Cache.java"), "w") as h:
            h.write("package com.acme;\nimport java.util.concurrent.*;\npublic class Cache {\n"
                    "  ConcurrentMap<String,String> cache = new ConcurrentHashMap<>();\n"
                    "  void put(String k) { if (!cache.containsKey(k)) cache.put(k, k); }\n}\n")
    else:
        with open(os.path.join(tmp, "README.md"), "w") as h:
            h.write("docs only\n")
    subprocess.run(["git", "-C", tmp, "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", tmp, "commit", "-q", "-m", "head"], check=True, env=env)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cards = os.path.join(self.tmp, "cards")
        os.makedirs(self.cards)
        with open(os.path.join(self.cards, "cc-08--x.md"), "w") as h:
            h.write("---\ntitle: T\nrule_id: CC-08\ndomain: concurrency\ntriggers: ['containsKey\\(']\n"
                    "scope: file\ncheck_kind: semantic\nseverity_default: major\n---\n# T\n")
        with open(os.path.join(self.cards, "meta-01--x.md"), "w") as h:
            h.write("---\ntitle: M\nrule_id: META-01\ndomain: meta\ntriggers: []\n"
                    "scope: file\ncheck_kind: semantic\nseverity_default: minor\n---\n# M\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_plan_on_real_repo(self):
        repo = os.path.join(self.tmp, "repo")
        make_repo(repo)
        rc = sr.main(["--diff-ref", "HEAD~1..HEAD", "--cards-dir", self.cards, "--repo", repo])
        self.assertEqual(rc, 0)
        plan = json.load(open(os.path.join(repo, "review", "plan.json")))
        inv = plan["inventory"]
        self.assertEqual(inv["size_class"], "SMALL")
        self.assertEqual(inv["files"][0]["package"], "com.acme")
        self.assertEqual(inv["build_files"], ["pom.xml"])
        self.assertFalse(inv["config_changed"])
        self.assertEqual(inv["config"]["project_name"], "Demo")
        self.assertEqual([j["id"] for j in plan["jobs"]], ["CC-08:all"])
        self.assertFalse(plan["meta_run"])
        self.assertEqual([c["rule_id"] for c in plan["project_cards"]["cards"]], ["PROJ-1", "PROJ-2", "PROJ-3"])
        self.assertEqual(len(plan["slices"]), 1)
        log = open(os.path.join(repo, "review", "plan.log")).read()
        self.assertIn("META cards ['META-01'] not run", log)

    def test_meta_cards_read_the_config(self):
        repo = os.path.join(self.tmp, "repo3")
        make_repo(repo)
        # --meta with an unchanged config: the whole config is one hunk for the META card
        rc = sr.main(["--diff-ref", "HEAD~1..HEAD", "--cards-dir", self.cards, "--repo", repo, "--meta"])
        self.assertEqual(rc, 0)
        plan = json.load(open(os.path.join(repo, "review", "plan.json")))
        self.assertTrue(plan["meta_run"])
        meta_jobs = [j for j in plan["jobs"] if j["rule_id"] == "META-01"]
        self.assertEqual(len(meta_jobs), 1)
        sf = meta_jobs[0]["slice"]["files"][0]
        self.assertEqual(sf["path"], ".claude/reviewing-java/config.md")
        self.assertEqual(plan["inventory"]["config_file"]["status"], "unchanged")
        cfg = plan["inventory"]["config_file"]
        self.assertIn("**Sentinel at index 0**", "\n".join(l["text"] for l in cfg["hunks"][sf["hunks"][0]]["lines"]))
        self.assertEqual({c["rule_id"] for c in plan["cards"]}, {j["rule_id"] for j in plan["jobs"]} | {c["rule_id"] for c in plan["candidates"] if c.get("rule_id")})
        # the Java card never sees the config
        cc = [j for j in plan["jobs"] if j["rule_id"] == "CC-08"]
        self.assertEqual([f["path"] for f in cc[0]["slice"]["files"]], ["src/main/java/com/acme/Cache.java"])
        self.assertEqual(plan["inventory"]["file_count"], 1)

    def test_empty_diff(self):
        repo = os.path.join(self.tmp, "repo2")
        make_repo(repo, with_java_change=False)
        rc = sr.main(["--diff-ref", "HEAD~1..HEAD", "--cards-dir", self.cards, "--repo", repo])
        self.assertEqual(rc, 2)
        plan = json.load(open(os.path.join(repo, "review", "plan.json")))
        self.assertEqual(plan["inventory"]["files"], [])
        self.assertIsNone(plan["inventory"]["size_class"])
        self.assertEqual(plan["jobs"], [])
        self.assertIn("No Java changes in this scope", open(os.path.join(repo, "review", "plan.log")).read())


if __name__ == "__main__":
    unittest.main()
