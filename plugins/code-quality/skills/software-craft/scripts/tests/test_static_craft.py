#!/usr/bin/env python3
"""Unit tests for static-craft.py: hunk parsing in each fixture language, language
detection and the deny-list, trigger and signal selection, every structural signal per
language, slice merge and split, the job cap and its log, the working-tree mode, and
the empty-diff case, plus end-to-end runs on a temporary git repository.

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
spec = importlib.util.spec_from_file_location("static_craft", os.path.join(SCRIPTS, "static-craft.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

DIFF = """diff --git a/src/app/cache.py b/src/app/cache.py
index 1111111..2222222 100644
--- a/src/app/cache.py
+++ b/src/app/cache.py
@@ -10,0 +11,2 @@ class Cache:
+    if key not in self.store: self.store[key] = load(key)
+    self.counter += 1
@@ -30 +32 @@ class Cache:
-    old line
+    new line
diff --git a/src/web/api.ts b/src/web/api.ts
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/src/web/api.ts
@@ -0,0 +1,3 @@
+export function api(): void {
+  render(order, true);
+}
diff --git a/src/app/gone.go b/src/app/gone.go
deleted file mode 100644
index 4444444..0000000
--- a/src/app/gone.go
+++ /dev/null
@@ -1,2 +0,0 @@
-package app
-func gone() {}
diff --git a/img/logo.png b/img/logo.png
new file mode 100644
index 0000000..5555555
Binary files /dev/null and b/img/logo.png differ
"""

CONFIG = """---
project_name: Demo
base_branch: main
modules: [{"name": "core", "paths": ["src/app"]}, {"name": "web", "paths": ["src/web"]}]
---
# Demo context

## Invariants

1. **Sentinel at index 0**: Index 0 is reserved and never holds data; iterations use `> 0`.
   Violation: reads garbage.
2. **Allocation-free onEvent**: `Dispatcher#onEvent` runs ~50 M times/day and allocates nothing. Violation: G1 mixed collections every minute.

Prose that is not an invariant.
3. **No violation clause**: rule text only
"""

JAVA = """package app;

public class Orders {
    private static final int LIMIT = 3;

    public int total(List<Order> orders, boolean rush, int a, int b, int c) {
        int sum = 0;
        for (Order o : orders) {
            if (o.isOpen()) {
                if (o.total() > 7) {
                    if (rush) {
                        if (o.priority() > 2) {
                            sum += 42;
                        }
                    }
                }
            }
        }
        try {
            save(sum);
        } catch (IOException e) {
        }
        render(sum, true);
        // int old = sum * 2;
        // save(old);
        return sum; // TODO drop the magic
    }
}
"""

PYTHON = """import json


def total(orders, rush, a, b, c):
    total = 0
    for o in orders:
        if o.open:
            if o.total > 7:
                if rush:
                    if o.priority > 2:
                        total += 42
    try:
        save(total)
    except Exception:
        pass
    render(total, True)
    # old = total * 2
    # save(old)
    return total  # FIXME magic


def tiny(x):
    return x
"""

TYPESCRIPT = """export function total(orders: Order[], rush: boolean, a: number, b: number, c: number): number {
  let sum = 0;
  for (const o of orders) {
    if (o.open) {
      if (o.total > 7) {
        if (rush) {
          if (o.priority > 2) {
            sum += 42;
          }
        }
      }
    }
  }
  try {
    save(sum);
  } catch (e) {
  }
  render(sum, true);
  // const old = sum * 2;
  // save(old);
  return sum; // HACK
}
"""

GO = """package app

func (s *Service) Total(orders []Order, rush bool, a int, b int, c int) int {
	sum := 0
	for _, o := range orders {
		if o.Open {
			if o.Total > 7 {
				if rush {
					if o.Priority > 2 {
						sum += 42
					}
				}
			}
		}
	}
	err := save(sum)
	if err != nil {
	}
	render(sum, true)
	// old := sum * 2
	// save(old)
	return sum // TODO
}
"""

RUST = """pub fn total(orders: &[Order], rush: bool, a: i32, b: i32, c: i32) -> i32 {
    let mut sum = 0;
    for o in orders {
        if o.open {
            if o.total > 7 {
                if rush {
                    if o.priority > 2 {
                        sum += 42;
                    }
                }
            }
        }
    }
    let _ = save(sum);
    render(sum, true);
    // let old = sum * 2;
    // save(old);
    sum // XXX
}
"""

SOURCES = {"java": ("src/Orders.java", JAVA), "python": ("src/orders.py", PYTHON), "typescript": ("src/orders.ts", TYPESCRIPT),
           "go": ("src/orders.go", GO), "rust": ("src/orders.rs", RUST)}


def card(rule_id, domain, triggers, severity="major", scope="file", kind="mechanical"):
    return {"rule_id": rule_id, "path": f"/cards/{rule_id.lower()}.md", "title": rule_id, "domain": domain,
            "step": ["implement"], "applies_to": ["universal"], "triggers": triggers, "scope": scope,
            "check_kind": kind, "severity_default": severity}


def fake_file(path, n_lines, text="x = y;", kind="source", language="python"):
    return {"path": path, "language": language, "kind": kind, "status": "modified", "removed_lines": 0, "binary": False,
            "hunks": [{"start": 1, "base_start": 1, "lines": [{"no": i + 1, "text": text} for i in range(n_lines)], "signals": {}}],
            "added_lines": n_lines, "signals": {"test_file": kind == "test", "added_file": False, "duplicate_block": 0}}


def whole_file_record(path, text, language):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    hunk = {"start": 1, "base_start": 0, "lines": [{"no": i + 1, "text": l} for i, l in enumerate(lines)]}
    return {"path": path, "language": language, "kind": "source", "status": "added", "removed_lines": 0, "binary": False,
            "hunks": [hunk], "added_lines": len(lines), "signals": {"test_file": False, "added_file": True, "duplicate_block": 0}}, lines


class ParseDiff(unittest.TestCase):
    def test_hunks_statuses_and_binary(self):
        files = sc.parse_diff(DIFF)
        self.assertEqual([f["path"] for f in files], ["src/app/cache.py", "src/web/api.ts", "img/logo.png"])
        cache = files[0]
        self.assertEqual(cache["status"], "modified")
        self.assertEqual(len(cache["hunks"]), 2)
        self.assertEqual(cache["hunks"][0]["start"], 11)
        self.assertEqual(cache["hunks"][0]["base_start"], 10)
        self.assertEqual([l["no"] for l in cache["hunks"][0]["lines"]], [11, 12])
        self.assertEqual(cache["hunks"][1]["lines"][0], {"no": 32, "text": "    new line"})
        self.assertEqual(cache["added_lines"], 3)
        self.assertEqual(cache["removed_lines"], 1)
        self.assertEqual(files[1]["status"], "added")
        self.assertEqual(files[1]["added_lines"], 3)
        self.assertTrue(files[2]["binary"])


class LanguagesAndDenyList(unittest.TestCase):
    def test_language_and_kind(self):
        self.assertEqual(sc.language_of("a/b.java"), "java")
        self.assertEqual(sc.language_of("a/b.py"), "python")
        self.assertEqual(sc.language_of("a/b.tsx"), "typescript")
        self.assertEqual(sc.language_of("a/b.go"), "go")
        self.assertEqual(sc.language_of("a/b.rs"), "rust")
        self.assertIsNone(sc.language_of("a/b.unknownext"))
        self.assertEqual(sc.kind_of("src/x_test.go", "go"), "test")
        self.assertEqual(sc.kind_of("tests/test_x.py", "python"), "test")
        self.assertEqual(sc.kind_of("src/main/java/OrdersTest.java", "java"), "test")
        self.assertEqual(sc.kind_of("src/x.spec.ts", "typescript"), "test")
        self.assertEqual(sc.kind_of("src/x.py", "python"), "source")
        self.assertEqual(sc.kind_of("pom.xml", "xml"), "build")
        self.assertEqual(sc.kind_of("config/app.yaml", "yaml"), "config")
        self.assertEqual(sc.kind_of("README.md", "markdown"), "docs")

    def test_deny_reasons(self):
        self.assertEqual(sc.deny_reason("vendor/lib.go", "package lib"), "vendored")
        self.assertEqual(sc.deny_reason("web/node_modules/x/index.js", "x"), "vendored")
        self.assertEqual(sc.deny_reason("package-lock.json", "{}"), "lock")
        self.assertEqual(sc.deny_reason("api_pb2.py", "x"), "generated")
        self.assertEqual(sc.deny_reason("gen/model.go", "// Code generated by protoc. DO NOT EDIT.\npackage gen"), "generated")
        self.assertEqual(sc.deny_reason("app.min.js", "x"), "generated")
        self.assertEqual(sc.deny_reason("bundle.js", "x" * 900 + "\n" + "y" * 900), "minified")
        self.assertEqual(sc.deny_reason("data.bin.weird", "x"), "unknown-language")
        self.assertIsNone(sc.deny_reason("src/app.py", "import os\n"))


class Signals(unittest.TestCase):
    def signals_for(self, language):
        path, text = SOURCES[language]
        rec, lines = whole_file_record(path, text, language)
        return sc.hunk_signals(lines, rec["hunks"][0], language, "source")

    def test_every_signal_in_every_language(self):
        for language in SOURCES:
            with self.subTest(language=language):
                sig = self.signals_for(language)
                self.assertGreaterEqual(sig.get("deep_nesting", 0), 4, sig)
                self.assertEqual(sig.get("many_parameters"), 5, sig)
                self.assertEqual(sig.get("boolean_argument"), 1, sig)
                self.assertEqual(sig.get("empty_handler"), 1, sig)
                self.assertGreaterEqual(sig.get("magic_number", 0), 2, sig)   # 7 and 42; 2 and 3 (the constant) do not count
                self.assertEqual(sig.get("commented_out_code"), 1, sig)
                self.assertEqual(sig.get("todo_marker"), 1, sig)
                self.assertNotIn("long_routine", sig)

    def test_long_routine_and_no_false_signals(self):
        body = "\n".join(f"    x{i} = {i % 2}" for i in range(50))
        text = f"def big(a):\n{body}\n    return a\n"
        rec, lines = whole_file_record("src/big.py", text, "python")
        sig = sc.hunk_signals(lines, rec["hunks"][0], "python", "source")
        self.assertEqual(sig.get("long_routine"), 52)
        self.assertNotIn("deep_nesting", sig)
        self.assertNotIn("many_parameters", sig)
        self.assertNotIn("boolean_argument", sig)
        self.assertNotIn("empty_handler", sig)
        self.assertNotIn("magic_number", sig)

    def test_long_routine_brace(self):
        body = "\n".join(f"        int x{i} = {i % 2};" for i in range(45))
        text = f"class A {{\n    void big(int a) {{\n{body}\n    }}\n}}\n"
        rec, lines = whole_file_record("src/A.java", text, "java")
        sig = sc.hunk_signals(lines, rec["hunks"][0], "java", "source")
        self.assertEqual(sig.get("long_routine"), 47)

    def test_magic_number_skips_tests_constants_and_allowed_values(self):
        rec, lines = whole_file_record("src/t.py", "LIMIT = 42\nx = 0\ny = 1\nz = 100\nw = 2\n", "python")
        self.assertNotIn("magic_number", sc.hunk_signals(lines, rec["hunks"][0], "python", "source"))
        rec, lines = whole_file_record("tests/test_t.py", "assert f(3) == 99\n", "python")
        self.assertNotIn("magic_number", sc.hunk_signals(lines, rec["hunks"][0], "python", "test"))
        rec, lines = whole_file_record("src/t.py", "x = f(99)\n", "python")
        self.assertEqual(sc.hunk_signals(lines, rec["hunks"][0], "python", "source").get("magic_number"), 1)

    def test_boolean_argument_excludes_conditions_and_returns(self):
        for line in ("if (x == true) {", "return true;", "while (true) {", "flag = true;"):
            rec, lines = whole_file_record("src/A.java", line + "\n", "java")
            self.assertNotIn("boolean_argument", sc.hunk_signals(lines, rec["hunks"][0], "java", "source"), line)

    def test_empty_handler_shapes(self):
        cases = {"java": "try { a(); } catch (Exception e) {}\n", "python": "try:\n    a()\nexcept ValueError:\n    pass\n",
                 "typescript": "promise.catch((e) => {\n});\n", "go": "if err != nil {\n}\n", "rust": "let _ = save(x);\n"}
        for language, text in cases.items():
            rec, lines = whole_file_record(SOURCES[language][0], text, language)
            self.assertEqual(sc.hunk_signals(lines, rec["hunks"][0], language, "source").get("empty_handler"), 1, language)
        rec, lines = whole_file_record("src/a.py", "try:\n    a()\nexcept ValueError:\n    log.warning('x')\n", "python")
        self.assertNotIn("empty_handler", sc.hunk_signals(lines, rec["hunks"][0], "python", "source"))

    def test_duplicate_block_across_files(self):
        block = "\n".join(f"line{i} = compute({i})" for i in range(7))
        a, _ = whole_file_record("src/a.py", block + "\n", "python")
        b, _ = whole_file_record("src/b.py", block + "\n", "python")
        dup = sc.duplicate_blocks([a, b])
        self.assertGreaterEqual(dup["src/a.py"], 1)
        self.assertGreaterEqual(dup["src/b.py"], 1)
        c, _ = whole_file_record("src/c.py", "\n".join(f"other{i} = {i}" for i in range(7)) + "\n", "python")
        self.assertEqual(sc.duplicate_blocks([a, c])["src/c.py"], 0)


class TriggerSelection(unittest.TestCase):
    def setUp(self):
        self.files = sc.parse_diff(DIFF)[:2]
        for f in self.files:
            f["language"] = sc.language_of(f["path"])
            f["kind"] = "source"
            f["signals"] = {"test_file": False, "added_file": f["status"] == "added", "duplicate_block": 0}
            for h in f["hunks"]:
                h["signals"] = sc.hunk_signals([l["text"] for l in h["lines"]], h, f["language"], "source") if f["status"] == "added" else {}
        sc.assign_groups(self.files, [])

    def test_pattern_matches_hunks_only(self):
        log = sc.Log()
        jobs = sc.build_jobs([card("DSN-01", "design", [r"not in .*\[\w+\] = "])], self.files, [], 400, 96, log)
        self.assertEqual(len(jobs), 1)
        job = jobs[0]
        self.assertEqual(job["id"], "DSN-01:all")
        self.assertEqual([sf["path"] for sf in job["slice"]["files"]], ["src/app/cache.py"])
        self.assertEqual(job["slice"]["files"][0]["hunks"], [0])
        self.assertEqual(job["slice"]["files"][0]["matched"]["patterns"], [r"not in .*\[\w+\] = "])

    def test_signal_trigger_selects_the_hunk_carrying_it(self):
        jobs = sc.build_jobs([card("CODE-07", "code", ["signal:boolean_argument"])], self.files, [], 400, 96, sc.Log())
        self.assertEqual(len(jobs), 1)
        self.assertEqual([sf["path"] for sf in jobs[0]["slice"]["files"]], ["src/web/api.ts"])
        self.assertEqual(jobs[0]["slice"]["files"][0]["matched"]["signals"], ["boolean_argument"])

    def test_file_signal_trigger(self):
        jobs = sc.build_jobs([card("DSN-02", "design", ["signal:added_file"])], self.files, [], 400, 96, sc.Log())
        self.assertEqual([sf["path"] for sf in jobs[0]["slice"]["files"]], ["src/web/api.ts"])

    def test_no_match_no_job(self):
        self.assertEqual(sc.build_jobs([card("INP-01", "input", [r"executeQuery\("])], self.files, [], 400, 96, sc.Log()), [])

    def test_empty_triggers_match_every_file(self):
        jobs = sc.build_jobs([card("DOC-01", "docs", [])], self.files, [], 400, 96, sc.Log())
        self.assertEqual(len(jobs[0]["slice"]["files"]), 2)
        self.assertEqual(jobs[0]["slice"]["files"][0]["hunks"], [0, 1])


class SlicesAndCap(unittest.TestCase):
    def test_split_when_over_line_budget(self):
        files = [fake_file(f"src/{d}/f{i}.py", 150, "foo();") for i, d in enumerate(["a", "b", "c"])]
        sc.assign_groups(files, [])
        log = sc.Log()
        jobs = sc.build_jobs([card("PRF-01", "performance", [r"foo\("])], files, [], 400, 96, log)
        self.assertEqual(sorted(j["id"] for j in jobs), ["PRF-01:src/a", "PRF-01:src/b", "PRF-01:src/c"])
        self.assertTrue(any("split into 3" in l for l in log.lines))

    def test_modules_and_tests_drive_grouping(self):
        files = [fake_file("src/app/deep/a.py", 1), fake_file("src/web/b.py", 1), fake_file("lib/other/c.py", 1),
                 fake_file("src/app/tests/test_a.py", 1, kind="test")]
        sc.assign_groups(files, [{"name": "kernel", "paths": ["src/app"]}])
        self.assertEqual([f["group"] for f in files], ["kernel", "src/web", "lib/other", "tests:kernel"])

    def test_logic_slices_between_three_and_eight(self):
        files = [fake_file(f"src/p{i}/f.py", 1) for i in range(12)]
        sc.assign_groups(files, [])
        log = sc.Log()
        slices = sc.build_slices(files, log)
        self.assertLessEqual(len(slices), 8)
        self.assertGreaterEqual(len(slices), 3)
        self.assertEqual(sum(len(s["files"]) for s in slices), 12)
        self.assertTrue(any("merged" in l for l in log.lines))

    def test_logic_slices_split_single_directory(self):
        files = [fake_file(f"src/core/{sub}/f{i}.py", 1) for i, sub in enumerate(["a", "a", "b", "b", "c", "c"])]
        sc.assign_groups(files, [])
        slices = sc.build_slices(files, sc.Log())
        self.assertGreaterEqual(len(slices), 3)
        self.assertEqual(sum(len(s["files"]) for s in slices), 6)

    def test_fewer_than_three_files_one_slice_each(self):
        files = [fake_file("a.py", 1), fake_file("b.py", 1)]
        sc.assign_groups(files, [])
        self.assertEqual([s["files"] for s in sc.build_slices(files, sc.Log())], [["a.py"], ["b.py"]])

    def test_cap_merges_then_drops_with_log(self):
        files = [fake_file(f"src/{d}/f.py", 300, "foo();") for d in ["a", "b", "c"]]
        sc.assign_groups(files, [])
        cards = [card("PRF-01", "performance", [r"foo\("]), card("CODE-01", "code", [r"foo\("], "suggestion"),
                 card("CODE-02", "code", [r"foo\("], "minor"), card("ERR-01", "errors", [r"foo\("], "major")]
        log = sc.Log()
        jobs = sc.build_jobs(cards, files, [], 400, 2, log)
        self.assertEqual(len(jobs), 2)
        self.assertEqual({j["rule_id"] for j in jobs}, {"ERR-01", "PRF-01"})
        self.assertTrue(any("merged 3 jobs of PRF-01" in l for l in log.lines))
        self.assertTrue(any("dropped job CODE-01:all (suggestion" in l for l in log.lines))
        self.assertTrue(any("dropped job CODE-02:all (minor" in l for l in log.lines))

    def test_cap_never_drops_major_silently(self):
        files = [fake_file("a.py", 1, "foo();")]
        sc.assign_groups(files, [])
        cards = [card(f"ERR-0{i}", "errors", [r"foo\("], "major") for i in range(1, 5)]
        log = sc.Log()
        self.assertEqual(len(sc.build_jobs(cards, files, [], 400, 2, log)), 4)
        self.assertTrue(any("exceeded by 2" in l for l in log.lines))


class ConfigParsing(unittest.TestCase):
    def test_frontmatter_modules_and_invariants(self):
        fm, body = sc.parse_config(CONFIG)
        self.assertEqual(fm["project_name"], "Demo")
        self.assertEqual(sc.parse_modules(fm), [{"name": "core", "paths": ["src/app"]}, {"name": "web", "paths": ["src/web"]}])
        cards = sc.parse_invariants(body)
        self.assertEqual([c["rule_id"] for c in cards], ["PROJ-1", "PROJ-2", "PROJ-3"])
        self.assertEqual(cards[0]["validator"], "reads garbage.")
        self.assertIn("50 M", cards[1]["rationale"])
        self.assertTrue(cards[2]["validator"].startswith("The diff shows the forbidden state of"))

    def test_malformed_config_is_tolerated(self):
        fm, body = sc.parse_config("no frontmatter here\n1. **X**: y. Violation: z.")
        self.assertEqual(fm, {})
        self.assertEqual(len(sc.parse_invariants(body)), 1)


class Candidates(unittest.TestCase):
    def test_named_hits(self):
        text = ["def names(self) -> list[str]:", "    if not self.ok:", "        return None", "    print('x')",
                "    render(a, True)", "    try:", "        a()", "    except Exception:", "        pass", "    # x = 1", "    # y = f(2)", "    return []  # TODO later"]
        f = {"path": "src/a.py", "language": "python", "kind": "source",
             "hunks": [{"start": 1, "lines": [{"no": i + 1, "text": t} for i, t in enumerate(text)]}]}
        ids = [(c["id"], c["line"]) for c in sc.find_candidates([f], {"src/a.py": text})]
        self.assertIn(("null-for-collection", 3), ids)
        self.assertIn(("print-in-production", 4), ids)
        self.assertIn(("boolean-argument", 5), ids)
        self.assertIn(("empty-handler", 8), ids)
        self.assertIn(("commented-out-code", 10), ids)
        self.assertIn(("todo-marker", 12), ids)
        self.assertTrue(all(c["status"] == "needs_verification" for c in sc.find_candidates([f], {"src/a.py": text})))


def make_repo(tmp, with_change=True, leave_uncommitted=False):
    subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x",
           "PATH": os.environ["PATH"], "HOME": tmp}
    src = os.path.join(tmp, "src", "app")
    os.makedirs(src)
    os.makedirs(os.path.join(tmp, ".claude", "software-craft"))
    with open(os.path.join(src, "cache.py"), "w") as h:
        h.write("class Cache:\n    pass\n")
    with open(os.path.join(tmp, ".claude", "software-craft", "config.md"), "w") as h:
        h.write(CONFIG)
    with open(os.path.join(tmp, "vendor", "lib.js") if os.makedirs(os.path.join(tmp, "vendor"), exist_ok=True) is None else "", "w") as h:
        h.write("var x = 1;\n")
    subprocess.run(["git", "-C", tmp, "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", tmp, "commit", "-q", "-m", "base"], check=True, env=env)
    if with_change:
        with open(os.path.join(src, "cache.py"), "w") as h:
            h.write("class Cache:\n    def get(self, key):\n        if key not in self.store: self.store[key] = load(key)\n        return self.store[key]\n")
        with open(os.path.join(src, "new_module.go"), "w") as h:
            h.write("package app\n\nfunc Render(sum int) {\n\trender(sum, true)\n}\n")
        with open(os.path.join(tmp, "vendor", "lib.js"), "w") as h:
            h.write("var x = 2;\n")
    else:
        with open(os.path.join(tmp, "README.md"), "w") as h:
            h.write("docs only\n")
    if not leave_uncommitted:
        subprocess.run(["git", "-C", tmp, "add", "."], check=True, env=env)
        subprocess.run(["git", "-C", tmp, "commit", "-q", "-m", "head"], check=True, env=env)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cards = os.path.join(self.tmp, "cards")
        os.makedirs(self.cards)
        with open(os.path.join(self.cards, "dsn-01--x.md"), "w") as h:
            h.write("---\ntitle: T\nrule_id: DSN-01\ndomain: design\nstep: [implement]\napplies_to: [universal]\n"
                    "triggers: ['not in .*\\[\\w+\\] = ']\nscope: file\ncheck_kind: semantic\nseverity_default: major\n---\n# T\n")
        with open(os.path.join(self.cards, "code-07--x.md"), "w") as h:
            h.write("---\ntitle: B\nrule_id: CODE-07\ndomain: code\nstep: [implement]\napplies_to: [universal]\n"
                    "triggers: ['signal:boolean_argument']\nscope: hunk\ncheck_kind: mechanical\nseverity_default: minor\n---\n# B\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def plan_of(self, repo, *extra):
        rc = sc.main(["--cards-dir", self.cards, "--repo", repo, *extra])
        with open(os.path.join(repo, "craft", "plan.json")) as fh:
            plan = json.load(fh)
        with open(os.path.join(repo, "craft", "plan.log")) as fh:
            log = fh.read()
        return rc, plan, log

    def test_committed_mode(self):
        repo = os.path.join(self.tmp, "repo")
        make_repo(repo)
        rc, plan, log = self.plan_of(repo, "--diff-ref", "HEAD~1..HEAD")
        self.assertEqual(rc, 0)
        inv = plan["inventory"]
        self.assertEqual(inv["mode"], "committed")
        self.assertEqual(inv["size_class"], "SMALL")
        self.assertEqual({f["path"]: f["language"] for f in inv["files"]}, {"src/app/cache.py": "python", "src/app/new_module.go": "go"})
        self.assertEqual([s["path"] for s in inv["skipped"]], ["vendor/lib.js"])
        self.assertEqual(inv["config"]["project_name"], "Demo")
        self.assertEqual(sorted(j["id"] for j in plan["jobs"]), ["CODE-07:all", "DSN-01:all"])
        self.assertEqual([c["rule_id"] for c in plan["project_cards"]["cards"]], ["PROJ-1", "PROJ-2", "PROJ-3"])
        self.assertEqual(len(plan["slices"]), 2)
        go = next(f for f in inv["files"] if f["path"].endswith(".go"))
        self.assertTrue(go["signals"]["added_file"])
        self.assertEqual(go["hunks"][0]["signals"].get("boolean_argument"), 1)
        self.assertIn("skipped vendor/lib.js: vendored", log)
        self.assertEqual([c["id"] for c in plan["candidates"]], ["boolean-argument"])

    def test_worktree_mode_sees_uncommitted_and_untracked(self):
        repo = os.path.join(self.tmp, "repo2")
        make_repo(repo, leave_uncommitted=True)
        rc, plan, log = self.plan_of(repo)
        self.assertEqual(rc, 0)
        inv = plan["inventory"]
        self.assertEqual(inv["mode"], "worktree")
        self.assertEqual(inv["head_sha"], "worktree")
        self.assertTrue(inv["diff_ref"].endswith("...worktree"))
        self.assertEqual({f["path"]: f["status"] for f in inv["files"]}, {"src/app/cache.py": "modified", "src/app/new_module.go": "added"})
        self.assertEqual(sorted(j["id"] for j in plan["jobs"]), ["CODE-07:all", "DSN-01:all"])
        # the tree is untouched: nothing staged by the pre-pass
        status = subprocess.run(["git", "-C", repo, "status", "--porcelain"], capture_output=True, text=True).stdout
        self.assertIn("?? src/app/new_module.go", status)
        self.assertNotIn("A  src/app/new_module.go", status)

    def test_empty_diff(self):
        repo = os.path.join(self.tmp, "repo3")
        make_repo(repo, with_change=False)
        rc, plan, log = self.plan_of(repo, "--diff-ref", "HEAD~1..HEAD")
        self.assertEqual(rc, 0)   # README.md is a docs file with one added line: reviewable
        self.assertEqual([f["kind"] for f in plan["inventory"]["files"]], ["docs"])
        rc, plan, log = self.plan_of(repo, "--diff-ref", "HEAD~1..HEAD", "--path-filter", "src")
        self.assertEqual(rc, 2)
        self.assertEqual(plan["inventory"]["files"], [])
        self.assertIsNone(plan["inventory"]["size_class"])
        self.assertEqual(plan["jobs"], [])
        self.assertIn("No reviewable changes in this scope", log)


if __name__ == "__main__":
    unittest.main()
