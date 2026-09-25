"""Tests for scripts/bundle-run.py: the bundle is the workflow script with the run's arguments
embedded after the meta block, and nothing of the plan is lost on the way."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("bundle_run", os.path.join(SCRIPTS, "bundle-run.py"))
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)

PLAN = {"inventory": {"base_sha": "a", "head_sha": "b", "files": []}, "cards": [], "jobs": [], "slices": [],
        "candidates": [], "project_cards": {"cards": [], "card_paths": []}, "meta_run": False}


class Bundle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(self.repo, "review"))
        with open(os.path.join(self.repo, "review", "plan.json"), "w") as fh:
            json.dump(PLAN, fh)
        with open(os.path.join(self.tmp, "intent.txt"), "w") as fh:
            fh.write("Adds a cache.\n")

    def test_embedded_after_meta(self):
        rc = br.main(["--root", self.repo, "--intent", os.path.join(self.tmp, "intent.txt")])
        self.assertEqual(rc, 0)
        out = open(os.path.join(self.repo, "review", "run.js")).read()
        meta_at = out.index("export const meta = {")
        embed_at = out.index("\nconst EMBEDDED_ARGS = ") + 1
        self.assertLess(meta_at, embed_at)
        self.assertLess(embed_at, out.index("let A = args"))
        line = out[embed_at:].split("\n", 1)[0]
        args = json.loads(line[len("const EMBEDDED_ARGS = "):])
        self.assertEqual(args["plan"], PLAN)
        self.assertEqual(args["root"], self.repo)
        self.assertEqual(args["stage"], "all")
        self.assertEqual(args["design_intent"], "Adds a cache.")
        self.assertEqual(args["project_context"], "")
        self.assertNotIn("findings", args)

    def test_verify_needs_findings(self):
        with self.assertRaises(SystemExit):
            br.main(["--root", self.repo, "--stage", "verify"])
        with open(os.path.join(self.repo, "review", "findings.json"), "w") as fh:
            json.dump([{"id": "CC-08.1"}], fh)
        rc = br.main(["--root", self.repo, "--stage", "verify", "--findings", "review/findings.json"])
        self.assertEqual(rc, 0)
        out = open(os.path.join(self.repo, "review", "run.js")).read()
        line = out[out.index("\nconst EMBEDDED_ARGS = ") + 1:].split("\n", 1)[0]
        args = json.loads(line[len("const EMBEDDED_ARGS = "):])
        self.assertEqual(args["stage"], "verify")
        self.assertEqual(args["findings"], [{"id": "CC-08.1"}])

    def test_malformed_plan_exits_2(self):
        with open(os.path.join(self.repo, "review", "plan.json"), "w") as fh:
            fh.write("{}")
        with self.assertRaises(SystemExit):
            br.main(["--root", self.repo])

    def test_bundle_parses_as_javascript(self):
        rc = br.main(["--root", self.repo])
        self.assertEqual(rc, 0)
        node = subprocess.run(["node", "--version"], capture_output=True)
        if node.returncode != 0:
            self.skipTest("node is not installed")
        src = open(os.path.join(self.repo, "review", "run.js")).read()
        wrapped = "async function __w(args, agent, parallel, pipeline, phase, log, budget, workflow){" + src.replace("export const meta", "const meta", 1) + "\n}"
        path = os.path.join(self.tmp, "check.mjs")
        with open(path, "w") as fh:
            fh.write(wrapped)
        self.assertEqual(subprocess.run(["node", "--check", path], capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
