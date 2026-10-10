"""Tests for maintenance/scripts/harvest-python-sources.py, offline: the Ruff filter and default set, the
Pylint item assembled from a cached message directory, Sonar's HTML-to-text and its profile,
Bandit's codes, bugbear's README paragraphs, the retry classification and the rule that a
cached text is never fetched again.

Run:  python3 -m unittest discover -s maintenance/tests -p 'test_*.py'   (from the skill directory)
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "maintenance", "scripts")
spec = importlib.util.spec_from_file_location("harvest_python_sources",
                                              os.path.join(SCRIPTS, "harvest-python-sources.py"))
hp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hp)


def no_fetch(url, headers=None):
    raise AssertionError(f"fetched {url} although the run must read only the cache")


def ruff_rule(code, linter, status, name="rule", summary="Summary."):
    return {"name": name, "code": code, "linter": linter, "summary": summary,
            "explanation": f"## What it does\nChecks {code}.\n\n## Why is this bad?\nBecause.\n",
            "preview": status == "Preview", "status": {status: {"since": "0.1"}}, "category": "correctness",
            "source_location": {"file": f"crates/ruff_linter/src/rules/{code}.rs", "line": 1}}


class Workdir(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.out)

    def put(self, rel, text):
        path = os.path.join(self.out, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def tree(self, source, repo, branch, paths):
        self.put(f"src/{source}/tree.json", json.dumps({"repo": repo, "branch": branch, "listing": "tree",
                                                        "response": {"tree": [{"path": p, "type": "blob"} for p in paths],
                                                                     "truncated": False}}))

    def run_main(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = hp.main(["--out", self.out, *argv], fetch=no_fetch)
        with open(os.path.join(self.out, "items.jsonl"), encoding="utf-8") as fh:
            items = [json.loads(line) for line in fh]
        with open(os.path.join(self.out, "summary.json"), encoding="utf-8") as fh:
            summary = json.load(fh)
        return status, items, summary


class RuffFilter(Workdir):
    def test_keeps_stable_and_preview_and_drops_by_status_linter_and_code(self):
        rules = [ruff_rule("B006", "flake8-bugbear", "Stable"), ruff_rule("RUF900", "Ruff-specific rules", "Preview"),
                 ruff_rule("UP001", "pyupgrade", "Removed"), ruff_rule("PLR0000", "Pylint", "Deprecated"),
                 ruff_rule("D100", "pydocstyle", "Stable"), ruff_rule("E201", "pycodestyle", "Stable"),
                 ruff_rule("E402", "pycodestyle", "Stable"), ruff_rule("F401", "Pyflakes", "Stable")]
        catalog = os.path.join(self.out, "catalog.json")
        with open(catalog, "w", encoding="utf-8") as fh:
            json.dump(rules, fh)

        status, items, summary = self.run_main("--only", "ruff", "--ruff-json", catalog, "--offline")

        self.assertEqual(0, status)
        self.assertEqual([("B006", "stable", False), ("E402", "stable", True), ("F401", "stable", True),
                          ("RUF900", "preview", False)],
                         [(i["code"], i["status"], i["default_on"]) for i in items])
        self.assertEqual({"status:Removed": 1, "status:Deprecated": 1, "linter:pydocstyle": 1, "code:E2": 1},
                         summary["ruff"]["dropped"]["reasons"])
        b006 = items[0]
        self.assertEqual("flake8-bugbear/correctness", b006["category"])
        self.assertEqual("Checks B006.", b006["summary"])
        self.assertEqual("https://raw.githubusercontent.com/astral-sh/ruff/main/crates/ruff_linter/src/rules/B006.rs",
                         b006["url"])
        self.assertEqual("src/ruff/rules.json", b006["cache_path"])
        self.assertTrue(os.path.isfile(os.path.join(self.out, "src/ruff/rules.json")))

    def test_selector_prefix_matches_letters_exactly_and_digits_by_prefix(self):
        cases = [("D100", "D", True), ("DTZ001", "D", False), ("DOC201", "D", False), ("T201", "T20", True),
                 ("T100", "T20", False), ("E402", "E4", True), ("E501", "E4", False), ("FURB101", "F", False),
                 ("", "F", False)]
        for code, prefix, expected in cases:
            with self.subTest(code=code, prefix=prefix):
                self.assertEqual(expected, hp.code_matches(code, prefix))


class PylintOffline(Workdir):
    def test_item_joins_details_bad_and_good_and_takes_the_code_from_the_index(self):
        base = "doc/data/messages/d/dangerous-default-value/"
        self.tree("pylint", "pylint-dev/pylint", "main",
                  [base + "details.rst", base + "bad.py", base + "good.py", base + "related.rst",
                   "doc/data/messages/c/consider-using-tuple/bad.py", "doc/data/messages/s/syntax-error/details.rst"])
        self.put("src/pylint/messages_overview.rst", ".. toctree::\n\n   error/syntax-error\n"
                                                     "   warning/dangerous-default-value\n")
        self.put("src/pylint/syntax-error/details.rst", "The ast module cannot parse the code.\n")
        self.put("src/pylint/features.rst",
                 ":dangerous-default-value (W0102): *Dangerous default value %s as argument*\n"
                 "  Used when a mutable value is a default.\n")
        self.put("src/pylint/extensions.rst",
                 ":consider-using-tuple (R6102): *Consider using an in-place tuple instead of list*\n")
        self.put("src/pylint/dangerous-default-value/details.rst", "A mutable default is shared.\n\nSecond.\n")
        self.put("src/pylint/dangerous-default-value/bad.py", "def f(x=[]):\n    pass\n")
        self.put("src/pylint/dangerous-default-value/good.py", "def f(x=None):\n    pass\n")
        self.put("src/pylint/consider-using-tuple/bad.py", "for x in [1, 2]:\n    pass\n")

        status, items, _ = self.run_main("--only", "pylint", "--offline")

        self.assertEqual(0, status)
        by_name = {i["name"]: i for i in items}
        ddv = by_name["dangerous-default-value"]
        self.assertEqual("W0102", ddv["code"])
        self.assertEqual("W", ddv["category"])
        self.assertEqual("Dangerous default value %s as argument", ddv["title"])
        self.assertEqual("A mutable default is shared.", ddv["summary"])
        self.assertEqual("A mutable default is shared.\n\nSecond.\n\n"
                         "--- bad.py ---\ndef f(x=[]):\n    pass\n\n"
                         "--- good.py ---\ndef f(x=None):\n    pass", ddv["explanation"])
        self.assertTrue(ddv["default_on"])
        self.assertEqual("src/pylint/dangerous-default-value", ddv["cache_path"])
        self.assertEqual("https://raw.githubusercontent.com/pylint-dev/pylint/main/" + base + "details.rst", ddv["url"])
        self.assertFalse(by_name["consider-using-tuple"]["default_on"])
        syntax_error = by_name["syntax-error"]
        self.assertEqual(("", "E", "The ast module cannot parse the code."),
                         (syntax_error["code"], syntax_error["category"], syntax_error["title"]))


class SonarOffline(Workdir):
    def test_html_to_text_keeps_paragraphs_list_items_and_pre_blocks(self):
        html = ("<p>Default values are\n evaluated <code>once</code> &amp; shared.</p>\n"
                "<ul>\n  <li>one</li>\n  <li>two</li>\n</ul>\n"
                "<pre>\ndef f(x=[]):\n    x.append(1)\n</pre>\n<h2>Why</h2>")

        self.assertEqual("Default values are evaluated once & shared.\n\n- one\n\n- two\n\n"
                         "    def f(x=[]):\n        x.append(1)\n\nWhy", hp.html_to_text(html))

    def test_default_on_follows_the_profile_and_deprecated_rules_drop(self):
        rules_dir = "python-checks/src/main/resources/org/sonar/l10n/py/rules/python/"
        names = ["S5717.json", "S5717.html", "S100.json", "S100.html", "S1.json", "Sonar_way_profile.json",
                 "Sonar_agentic_AI_profile.json"]
        self.tree("sonar", "SonarSource/sonar-python", "master", [rules_dir + n for n in names])
        self.put("src/sonar/Sonar_way_profile.json", json.dumps({"name": "Sonar way", "ruleKeys": ["S5717"]}))
        self.put("src/sonar/S5717.json", json.dumps({"title": "Defaults should not be modified", "type": "CODE_SMELL",
                                                     "defaultSeverity": "Critical", "status": "ready"}))
        self.put("src/sonar/S5717.html", "<p>This rule raises an issue.</p>")
        self.put("src/sonar/S100.json", json.dumps({"title": "Names", "type": "CODE_SMELL",
                                                    "defaultSeverity": "Minor", "status": "ready"}))
        self.put("src/sonar/S100.html", "<p>Naming.</p>")
        self.put("src/sonar/S1.json", json.dumps({"title": "Old", "status": "deprecated"}))

        status, items, summary = self.run_main("--only", "sonar", "--offline")

        self.assertEqual(0, status)
        self.assertEqual([("S100", False), ("S5717", True)], [(i["code"], i["default_on"]) for i in items])
        s5717 = items[1]
        self.assertEqual(("defaults-should-not-be-modified", "CODE_SMELL/Critical", "This rule raises an issue."),
                         (s5717["name"], s5717["category"], s5717["explanation"]))
        self.assertEqual({"status:deprecated": 1}, summary["sonar"]["dropped"]["reasons"])


class Bandit(unittest.TestCase):
    def test_code_comes_from_the_plugin_file_name(self):
        cases = [("b602_subprocess_popen_with_shell_equals_true.rst", "B602"),
                 ("doc/source/plugins/b101_assert_used.rst", "B101"), ("blacklist_calls.rst", "")]
        for filename, code in cases:
            with self.subTest(filename=filename):
                self.assertEqual(code, hp.bandit_code_from_filename(filename))

    def test_blacklist_docstring_splits_by_heading_and_expands_a_code_range(self):
        docstring = ("Intro.\n\nB301: pickle\n------------\n\nPickle is unsafe. More text.\n\n"
                     "B304 - B305: ciphers and modes\n------------------------------\n\nUse AES.\n\n"
                     "| B304 | ciphers             | - Crypto.Cipher.ARC2.new  | High |\n"
                     "| B305 | cipher_modes        | - modes.ECB               | Medium |\n")

        items = hp.bandit_blacklist_items("blacklist_calls.rst", docstring, "u", "c")

        self.assertEqual([("B301", "pickle", "Pickle is unsafe."), ("B304", "ciphers", "Use AES."),
                          ("B305", "cipher_modes", "Use AES.")],
                         [(i.code, i.name, i.title) for i in items])

    def test_plugin_item_reads_the_function_docstring_the_stub_names(self):
        rst = ("-----\nB602: subprocess_popen_with_shell_equals_true\n-----\n\n"
               ".. currentmodule:: bandit.plugins.injection_shell\n\n"
               ".. autofunction:: subprocess_popen_with_shell_equals_true\n")
        source = ('def subprocess_popen_with_shell_equals_true(context, config):\n'
                  '    """**B602: Test for use of popen with shell equals true**\n\n'
                  '    Python possesses many mechanisms.\n    """\n')
        module, function = hp.bandit_stub_target(rst)

        plugin = hp.bandit_plugin_item("b602_subprocess_popen_with_shell_equals_true.rst", rst,
                                       hp.python_docstring(source, function), "u", "c")

        self.assertEqual(("bandit.plugins.injection_shell", "subprocess_popen_with_shell_equals_true"),
                         (module, function))
        self.assertEqual(("B602", "subprocess_popen_with_shell_equals_true",
                          "Test for use of popen with shell equals true", "Python possesses many mechanisms."),
                         (plugin.code, plugin.name, plugin.title, plugin.summary))


class BanditDocstring(unittest.TestCase):
    def test_a_function_the_module_does_not_define_has_no_docstring(self):
        self.assertIsNone(hp.python_docstring('def present():\n    """Doc."""\n', "absent"))


class BanditOffline(Workdir):
    def test_plugin_pages_resolve_to_module_docstrings_and_removed_plugins_drop(self):
        self.tree("bandit", "PyCQA/bandit", "main",
                  ["doc/source/plugins/b101_assert_used.rst", "doc/source/plugins/b109_password_option.rst",
                   "doc/source/plugins/index.rst", "doc/source/blacklists/blacklist_calls.rst"])
        self.put("src/bandit/b101_assert_used.rst",
                 "-----\nB101: assert_used\n-----\n\n.. automodule:: bandit.plugins.asserts\n   :no-index:\n")
        self.put("src/bandit/py/bandit/plugins/asserts.py",
                 'r"""\n=====\nB101: Test for use of assert\n=====\n\nThis plugin checks assert.\n"""\n')
        self.put("src/bandit/b109_password_option.rst",
                 "-----\nB109: password_option\n-----\n\nThis plugin has been removed.\n\n"
                 ".. deprecated:: 1.5.0\n   This plugin was removed\n")
        self.put("src/bandit/blacklist_calls.rst",
                 "-----\nblacklist_calls\n-----\n\n.. automodule:: bandit.blacklists.calls\n")
        self.put("src/bandit/py/bandit/blacklists/calls.py",
                 '"""\nIntro.\n\nB301: pickle\n------------\n\nPickle is unsafe.\n"""\n')

        status, items, summary = self.run_main("--only", "bandit", "--offline")

        self.assertEqual(0, status)
        self.assertEqual([("B101", "assert_used", "Test for use of assert", "This plugin checks assert."),
                          ("B301", "pickle", "Pickle is unsafe.", "Pickle is unsafe.")],
                         [(i["code"], i["name"], i["title"], i["summary"]) for i in items])
        self.assertEqual("src/bandit/py/bandit/plugins/asserts.py", items[0]["cache_path"])
        self.assertEqual({"status:deprecated": 1}, summary["bandit"]["dropped"]["reasons"])


class Bugbear(unittest.TestCase):
    README = (".. _B006:\n\n**B006**: Do not use mutable data structures for argument defaults.  They\n"
              "are created during function definition time.\n\n.. _B007:\n\n"
              "**B007**: Loop control variable not used within the loop body.\n\n"
              "Opinionated warnings\n~~~~~~~~~~~~~~~~~~~~\n\nDisabled by default.\n\n.. _B950:\n\n"
              "**B950**: Line too long. More.\n\nSecond paragraph of B950.\n\n\n"
              "How to enable opinionated warnings\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nText.\n")

    def test_one_item_per_code_paragraph_ending_at_the_next_rule_or_heading(self):
        items = hp.bugbear_items(self.README)

        self.assertEqual([("B006", "Do not use mutable data structures for argument defaults.", True),
                          ("B007", "Loop control variable not used within the loop body.", True),
                          ("B950", "Line too long.", False)],
                         [(i.code, i.title, i.default_on) for i in items])
        self.assertEqual("Loop control variable not used within the loop body.", items[1].explanation)
        self.assertEqual("Line too long. More.\n\nSecond paragraph of B950.", items[2].explanation)


class Network(Workdir):
    def http_error(self, status):
        err = urllib.error.HTTPError("https://example.invalid/", status, "status", {}, io.BytesIO(b""))
        self.addCleanup(err.close)
        return err

    def test_a_cached_text_is_never_fetched_again(self):
        self.put("src/bugbear/README.rst", "cached\n")
        cache = hp.Cache(self.out, offline=False, fetch=no_fetch)

        self.assertEqual("cached\n", cache.fetch_once("https://example.invalid/README.rst", "src/bugbear/README.rst"))

    def test_a_fetched_text_is_written_once_and_read_from_disk_afterwards(self):
        calls = []

        def fetch(url, headers=None):
            calls.append(url)
            return "body"

        cache = hp.Cache(self.out, offline=False, fetch=fetch)
        texts = [cache.fetch_once("https://example.invalid/a", "src/x/a.txt") for _ in range(2)]

        self.assertEqual((["body", "body"], ["https://example.invalid/a"]), (texts, calls))
        self.assertFalse(os.path.exists(os.path.join(self.out, "src/x/a.txt.part")))

    def test_offline_cache_miss_is_a_fetch_failure(self):
        cache = hp.Cache(self.out, offline=True, fetch=no_fetch)

        with self.assertRaises(hp.FetchError) as caught:
            cache.fetch_once("https://example.invalid/a", "src/x/a.txt")
        self.assertEqual(None, caught.exception.status)

    def test_offline_source_without_its_listing_fails_the_run(self):
        status, items, summary = self.run_main("--only", "bandit", "--offline")

        self.assertEqual((1, []), (status, items))
        self.assertIn("offline and not cached", summary["bandit"]["error"])

    def test_raw_url_percent_encodes_a_non_ascii_tree_path(self):
        self.assertEqual("https://raw.githubusercontent.com/pylint-dev/pylint/main/doc/m/bad/na%C3%AFve%20x.py",
                         hp.raw_url("pylint-dev/pylint", "main", "doc/m/bad/naïve x.py"))

    def test_only_a_5xx_or_a_timeout_is_retried(self):
        cases = [(self.http_error(503), True),
                 (self.http_error(404), False),
                 (self.http_error(403), False),
                 (urllib.error.URLError(TimeoutError("timed out")), True),
                 (TimeoutError("timed out"), True),
                 (urllib.error.URLError(ConnectionRefusedError("refused")), False)]
        for err, expected in cases:
            with self.subTest(err=repr(err)):
                self.assertEqual(expected, hp._transient(err))


if __name__ == "__main__":
    unittest.main()
