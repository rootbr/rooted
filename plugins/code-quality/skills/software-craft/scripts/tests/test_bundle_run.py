"""Tests for scripts/bundle-run.py: the bundle is the workflow script with the run's arguments
embedded after the meta block, nothing of the plan is lost on the way, and the bundle parses as
the runtime sees it (wrapped in an async function, the export keyword removed)."""
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

PLAN = {"inventory": {"mode": "worktree", "base_sha": "a", "head_sha": "worktree", "files": []}, "cards": [], "jobs": [], "slices": [],
        "candidates": [], "project_cards": {"cards": [], "card_paths": []}}


def wrap(src):
    return "async function __w(args, agent, parallel, pipeline, phase, log, budget, workflow){" + src.replace("export const meta", "const meta", 1) + "\n}"


class Bundle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(self.repo, "craft"))
        with open(os.path.join(self.repo, "craft", "plan.json"), "w") as fh:
            json.dump(PLAN, fh)
        with open(os.path.join(self.tmp, "intent.txt"), "w") as fh:
            fh.write("Adds a cache.\n")

    def read_args(self):
        with open(os.path.join(self.repo, "craft", "run.js")) as fh:
            out = fh.read()
        line = out[out.index("\nconst EMBEDDED_ARGS = ") + 1:].split("\n", 1)[0]
        return out, json.loads(line[len("const EMBEDDED_ARGS = "):])

    def test_embedded_after_meta(self):
        rc = br.main(["--root", self.repo, "--intent", os.path.join(self.tmp, "intent.txt")])
        self.assertEqual(rc, 0)
        out, args = self.read_args()
        self.assertLess(out.index("export const meta = {"), out.index("\nconst EMBEDDED_ARGS = "))
        self.assertLess(out.index("\nconst EMBEDDED_ARGS = "), out.index("let A = args"))
        self.assertEqual(args["plan"], PLAN)
        self.assertEqual(args["root"], self.repo)
        self.assertEqual(args["stage"], "all")
        self.assertEqual(args["design_intent"], "Adds a cache.")
        self.assertEqual(args["project_context"], "")
        self.assertNotIn("findings", args)

    def test_verify_needs_findings(self):
        with self.assertRaises(SystemExit):
            br.main(["--root", self.repo, "--stage", "verify"])
        with open(os.path.join(self.repo, "craft", "findings.json"), "w") as fh:
            json.dump([{"id": "CODE-01.1"}], fh)
        rc = br.main(["--root", self.repo, "--stage", "verify", "--findings", "craft/findings.json"])
        self.assertEqual(rc, 0)
        _, args = self.read_args()
        self.assertEqual(args["stage"], "verify")
        self.assertEqual(args["findings"], [{"id": "CODE-01.1"}])

    def test_malformed_plan_exits_2(self):
        with open(os.path.join(self.repo, "craft", "plan.json"), "w") as fh:
            fh.write("{}")
        with self.assertRaises(SystemExit):
            br.main(["--root", self.repo])

    def test_bundle_and_workflow_scripts_parse_as_javascript(self):
        node = subprocess.run(["node", "--version"], capture_output=True)
        if node.returncode != 0:
            self.skipTest("node is not installed")
        rc = br.main(["--root", self.repo])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.repo, "craft", "run.js")) as fh:
            bundle_src = fh.read()
        with open(os.path.join(SCRIPTS, "research-topic-workflow.js")) as fh:
            research_src = fh.read()
        for name, src in (("run.mjs", bundle_src), ("research.mjs", research_src)):
            path = os.path.join(self.tmp, name)
            with open(path, "w") as fh:
                fh.write(wrap(src))
            res = subprocess.run(["node", "--check", path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)


if __name__ == "__main__":
    unittest.main()
