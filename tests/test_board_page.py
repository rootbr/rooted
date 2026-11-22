#!/usr/bin/env python3
"""Browser tests of the decision board page research/board/rooted-board.html: the header's button
"Скопировать состояние доски" hands the board's state over as one JSON text.

Each scenario wraps the page content in a document with a stub of window.claude.use("db") and of the
clipboard, presses the button from a script once the stub database has subscribed or delivered, and
reads what that script wrote into the DOM the browser dumps. Chrome or Chromium is found as
check_page.py of handing-over-to-readers finds it; without one every test here is skipped.

Run:  python3 -m unittest discover -s tests -p 'test_*.py'   (from the repository root)
"""
import html
import importlib.util
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "research" / "board" / "rooted-board.html"
CHECK_PAGE = ROOT / "plugins" / "evidence-based-authoring" / "skills" / "handing-over-to-readers" / "scripts" / "check_page.py"

spec = importlib.util.spec_from_file_location("check_page", CHECK_PAGE)
check_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_page)
BROWSER = check_page.find_browser(None, os.environ)

WINDOW = "500,900"  # pixels: headless Chrome widens a narrower window to 500
PROBE = re.compile(r'<pre id="board-probe">(.*?)</pre>', re.S)

HEADLINE = "Тестовый заголовок доски"
CARDS = {
    "open-card": {"order": 10, "kind": "decision", "title": "Открытое решение", "question": "Делать ли?",
                  "options": [{"key": "yes", "label": "Да"}, {"key": "no", "label": "Нет"}], "recommend": "yes",
                  "status": "open", "answer": None},
    "answered-card": {"order": 20, "kind": "default", "title": "Отвеченное решение", "question": "Оставить ли?",
                      "options": [{"key": "keep", "label": "Оставить"}, {"key": "overturn", "label": "Отменить"}],
                      "recommend": "keep", "status": "answered",
                      "answer": {"key": "keep", "text": "оставить, но сверять вручную", "at": "2026-11-22T08:58:05.062Z"}},
}
UNITS = {"01-scientific-method": {"order": 1, "title": "scientific-method", "state": "done", "note": "закоммичен"}}
EXPORTED_CARDS = [dict(CARDS["open-card"], id="open-card"), dict(CARDS["answered-card"], id="answered-card")]
EXPORTED_UNITS = [dict(UNITS["01-scientific-method"], id="01-scientific-method")]

COPIED = "Состояние доски скопировано в буфер обмена (карточек: 2, единиц плана: 1)."
SELECTED = "Буфер обмена недоступен в этом окне: текст выделен в поле ниже, скопируйте его клавишами Ctrl+C или ⌘C."
NOT_LOADED = "Данные доски не загружены: копировать нечего."

# Runs before the page's script. DATABASE is "fed" (every subscription gets one snapshot), "pending" (subscriptions
# get none) or "none" (no window.claude, so the page starts without a database); CLIPBOARD is "accept" or "refuse".
# The copy command is always refused, as a browser refuses it to a script-made press.
STUB = """
(function () {
  var DATABASE = __DATABASE__, CLIPBOARD = __CLIPBOARD__, CARDS = __CARDS__, UNITS = __UNITS__, HEADLINE = __HEADLINE__;
  var stub = window.boardStub = { errors: [], subscribed: 0, delivered: 0, clipboard: [], copyCommands: 0 };
  window.addEventListener("error", function (e) { stub.errors.push(e.message); });
  window.addEventListener("unhandledrejection", function (e) { stub.errors.push("unhandled rejection: " + String(e.reason)); });
  function deepFreeze(o) { if (o && typeof o === "object") { Object.keys(o).forEach(function (k) { deepFreeze(o[k]); }); Object.freeze(o); } return o; }
  function docSnap(id, data) { return { id: id, exists: true, data: function () { return deepFreeze(JSON.parse(JSON.stringify(data))); } }; }
  function source(snapshot) {
    return { onSnapshot: function (next) {
      stub.subscribed += 1;
      if (DATABASE === "fed") { setTimeout(function () { next(snapshot()); stub.delivered += 1; }, 0); }
      return function () {};
    } };
  }
  function collection(rows) { return source(function () { return { docs: Object.keys(rows).map(function (id) { return docSnap(id, rows[id]); }) }; }); }
  var db = {
    collection: function (name) { return collection(name === "cards" ? CARDS : name === "units" ? UNITS : {}); },
    doc: function () { return source(function () { return docSnap("board", { headline: HEADLINE }); }); }
  };
  if (DATABASE !== "none") { window.claude = { use: function () { return Promise.resolve(db); } }; }
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText: function (text) {
    stub.clipboard.push(text);
    return CLIPBOARD === "accept" ? Promise.resolve() : Promise.reject(new DOMException("Write permission denied.", "NotAllowedError"));
  } } });
  document.execCommand = function (command) { if (command === "copy") { stub.copyCommands += 1; } return false; };
  stub.ready = function () { return DATABASE === "fed" ? stub.delivered === 3 : DATABASE === "pending" ? stub.subscribed === 3 : true; };
})();
"""

# Runs after the page's script: waits for the stub, presses the button, waits for the status line, and writes what it
# found into <pre id="board-probe">; "stage" names the wait that ran out when one did.
DRIVER = """
(function () {
  var stub = window.boardStub, DEADLINE = 3000, PAUSE = 10, started = Date.now();
  var $ = function (id) { return document.getElementById(id); };
  function finish(stage) {
    var field = $("state-text"), active = document.activeElement;
    var pre = document.createElement("pre");
    pre.id = "board-probe";
    pre.textContent = JSON.stringify({
      stage: stage, errors: stub.errors, say: $("state-say").textContent, field: field.textContent, fieldShown: !$("state-box").hidden,
      focused: active ? active.id : "", selectedText: field.value.substring(field.selectionStart, field.selectionEnd),
      clipboard: stub.clipboard, copyCommands: stub.copyCommands
    });
    document.body.appendChild(pre);
  }
  function waitFor(condition, then, stage) {
    (function poll() {
      if (condition()) { then(); }
      else if (Date.now() - started > DEADLINE) { finish(stage); }
      else { setTimeout(poll, PAUSE); }
    })();
  }
  waitFor(stub.ready, function () {
    $("state-copy").click();
    waitFor(function () { return $("state-say").textContent !== ""; }, function () { finish("done"); }, "no status line after the press");
  }, "the stub database was not ready");
})();
"""


def script_value(value):
    """`value` as a JavaScript literal that cannot close the <script> element holding it."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def harness(page, database, clipboard):
    stub = STUB
    for token, value in (("__DATABASE__", database), ("__CLIPBOARD__", clipboard), ("__CARDS__", CARDS), ("__UNITS__", UNITS),
                         ("__HEADLINE__", HEADLINE)):
        stub = stub.replace(token, script_value(value))
    return f'<!doctype html><meta charset="utf-8"><script>{stub}</script>\n{page}\n<script>{DRIVER}</script>\n'


def run_scenario(database, clipboard):
    """What the driver found after the press; AssertionError when the browser left no probe or a wait ran out."""
    document = harness(PAGE.read_text(encoding="utf-8"), database, clipboard)
    with tempfile.TemporaryDirectory(prefix="board-page-", ignore_cleanup_errors=True) as folder:
        work = Path(folder)
        copy = work / "board.html"
        copy.write_text(document, encoding="utf-8")
        command = [BROWSER, *check_page.FLAGS, f"--user-data-dir={work / 'profile'}", f"--window-size={WINDOW}", "--dump-dom",
                   copy.as_uri()]
        done = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=check_page.TIMEOUT, check=False)
    found = PROBE.search(done.stdout)
    if not found:
        raise AssertionError(f"the page left no probe (browser exit {done.returncode}): {done.stderr[-400:]}")
    probe = json.loads(html.unescape(found.group(1)))
    if probe["stage"] != "done":
        raise AssertionError(f"the harness stopped: {probe['stage']}; script errors: {probe['errors']}")
    return probe


@unittest.skipUnless(BROWSER, "no Chrome or Chromium found where check_page.py looks: the board page runs only in a browser")
class Scenario(unittest.TestCase):
    """One browser run per subclass, which names its `database` and `clipboard`; its tests share the probe read-only."""
    database = clipboard = None

    @classmethod
    def setUpClass(cls):
        cls.probe = run_scenario(cls.database, cls.clipboard)


class LoadedBoard(Scenario):
    database = "fed"
    clipboard = "accept"

    def test_the_field_holds_the_board_state_as_json(self):
        self.assertEqual(self.probe["errors"], [])
        self.assertTrue(self.probe["fieldShown"])
        state = json.loads(self.probe["field"])
        self.assertEqual(sorted(state), ["cards", "exportedAt", "headline", "units"])
        self.assertRegex(state["exportedAt"], r"\A\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z\Z")
        self.assertEqual(state["headline"], HEADLINE)
        self.assertEqual(state["cards"], EXPORTED_CARDS)
        self.assertEqual(state["units"], EXPORTED_UNITS)

    def test_the_clipboard_takes_the_same_text_and_the_status_says_copied(self):
        self.assertEqual(self.probe["clipboard"], [self.probe["field"]])
        self.assertEqual(self.probe["copyCommands"], 0)
        self.assertEqual(self.probe["say"], COPIED)

    def test_the_field_is_focused_with_its_whole_text_selected(self):
        self.assertEqual(self.probe["focused"], "state-text")
        self.assertEqual(self.probe["selectedText"], self.probe["field"])


class RefusedClipboard(Scenario):
    database = "fed"
    clipboard = "refuse"

    def test_the_text_stays_selected_for_the_keyboard_after_both_copies_are_refused(self):
        self.assertEqual(self.probe["errors"], [])
        self.assertEqual(self.probe["clipboard"], [self.probe["field"]])
        self.assertEqual(self.probe["copyCommands"], 1)
        self.assertEqual(self.probe["say"], SELECTED)
        self.assertTrue(self.probe["fieldShown"])
        self.assertEqual(self.probe["focused"], "state-text")
        self.assertEqual(self.probe["selectedText"], self.probe["field"])
        self.assertEqual(json.loads(self.probe["field"])["cards"], EXPORTED_CARDS)


@unittest.skipUnless(BROWSER, "no Chrome or Chromium found where check_page.py looks: the board page runs only in a browser")
class NothingLoaded(unittest.TestCase):
    def test_a_press_before_the_first_snapshot_reports_it_and_copies_nothing(self):
        for database in ("pending", "none"):
            with self.subTest(database=database):
                probe = run_scenario(database, "accept")
                self.assertEqual(probe["errors"], [])
                self.assertEqual(probe["say"], NOT_LOADED)
                self.assertEqual((probe["field"], probe["fieldShown"], probe["clipboard"], probe["copyCommands"]), ("", False, [], 0))


if __name__ == "__main__":
    unittest.main()
