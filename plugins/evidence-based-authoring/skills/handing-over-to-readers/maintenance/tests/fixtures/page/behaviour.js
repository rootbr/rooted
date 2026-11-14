/* The scripted reader of test_page_behaviour.py: it acts on a built page in headless Chrome and writes what it saw as JSON
   into a pre element of the id behaviour-out, appended to the body.
   Real audio does not advance under virtual time, so the audio element's paused, ended, currentTime, play and pause are
   stubbed; the stubs fire the same events a real element fires, and the page's listeners answer them synchronously.
   The one asynchronous step of the page is the comment window a mouseup opens on a timer: the reader polls for it.
   A page with voice runs the voiced scenario, a page without runs the silent one. */
window.addEventListener("load", async function () {
  var out = {};
  function tick() { return new Promise(function (resolve) { setTimeout(resolve, 10); }); }
  /* Re-tests the condition every 10 ms for at most 2 s; the expectation that follows reports a condition never met. */
  async function until(condition) { for (var waited = 0; waited < 2000 && !condition(); waited += 10) { await tick(); } }
  function key(code) { document.dispatchEvent(new KeyboardEvent("keydown", { code: code, key: code === "Space" ? " " : "c", bubbles: true })); }
  function click(target, rect) {
    var box = rect || target.getBoundingClientRect();
    target.dispatchEvent(new MouseEvent("click", { bubbles: true, clientX: box.left + box.width / 2, clientY: box.top + box.height / 2 }));
  }
  function textRange(span, from, to) { var r = document.createRange(); r.setStart(span.firstChild, from); r.setEnd(span.firstChild, to); return r; }
  try {
    var data = JSON.parse(document.getElementById("page-data").textContent);
    var article = document.getElementById("article"), voice = document.getElementById("voice");
    var pop = document.querySelector(".note-pop"), area = pop.querySelector("textarea");
    var bar = document.querySelector(".answer");
    function sentence(id) { return article.querySelector('.s[data-lit="' + id + '"]'); }
    async function select(span, from, to) {
      var selection = getSelection();
      selection.removeAllRanges();
      selection.addRange(textRange(span, from, to));
      span.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
      await until(function () { return !pop.hidden; });
    }
    function enter() { area.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true })); }
    function escape() { area.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); }
    function noteCount() { return document.querySelectorAll(".notes ol > li").length; }
    function stored() { return JSON.parse(localStorage.getItem(data.id) || "null"); }
    function copied() {
      document.querySelector(".answer .primary").click();
      return document.querySelector(".answer-text").textContent;
    }
    out.hint = document.querySelector(".hint") ? document.querySelector(".hint").textContent : null;
    out.sideExists = !!document.querySelector(".side-tools");
    out.cornerExists = !!document.querySelector(".corner-pause, [data-proto]");

    if (!data.voice) {
      out.barHiddenBefore = bar.hidden;
      await select(sentence("1.2"), 0, 13);
      out.popShown = !pop.hidden;
      out.focusInPop = document.activeElement === area;
      area.value = "a comment without voice";
      enter();
      out.popClosed = pop.hidden;
      out.barShownAfter = !bar.hidden;
      out.barBeforeLook = !!bar.nextElementSibling && bar.nextElementSibling.matches("section.look");
      out.listed = noteCount();
      out.composed = copied();
    } else {
      var state = { paused: true, t: 0 };
      Object.defineProperty(voice, "paused", { get: function () { return state.paused; } });
      Object.defineProperty(voice, "ended", { get: function () { return false; } });
      Object.defineProperty(voice, "currentTime", {
        get: function () { return state.t; },
        set: function (v) { state.t = v; voice.dispatchEvent(new Event("seeked")); }
      });
      voice.play = function () { state.paused = false; voice.dispatchEvent(new Event("play")); return Promise.resolve(); };
      voice.pause = function () { state.paused = true; voice.dispatchEvent(new Event("pause")); };
      var side = document.querySelector(".side-tools"), sidePause = side.querySelector(".round:not(.note)");

      // 1. a selection opens the window with the cursor in its field; Enter saves it
      var commented = sentence("3.6");
      await select(commented, 4, 25);
      out.popShown = !pop.hidden;
      out.quote = pop.querySelector(".note-quote").textContent;
      out.focusInPop = document.activeElement === area;
      area.value = "first comment";
      enter();
      out.popClosed = pop.hidden;
      out.highlight = !!(window.CSS && CSS.highlights && CSS.highlights.has("note"));
      out.listed = noteCount();

      // 2. while the voice plays: the side group stands beside the spoken sentence; a click pauses, Space resumes
      state.t = 30;
      voice.play();
      var lit = article.querySelector(".s.lit");
      out.lit = lit ? lit.getAttribute("data-lit") : null;
      out.sideShown = !side.hidden;
      var line = lit.getClientRects()[0], button = sidePause.getBoundingClientRect();
      out.sideOffset = Math.abs((button.top + button.height / 2) - (line.top + line.height / 2));
      out.sideLeftOfText = button.right <= line.left;
      out.labelPlaying = sidePause.getAttribute("aria-label");
      click(lit, line);
      out.pausedByClick = state.paused;
      out.labelPaused = sidePause.getAttribute("aria-label");
      key("Space");
      out.resumedBySpace = !state.paused;

      // 3. the key C opens the window for the spoken sentence and pauses; after Enter the voice goes on from its start
      state.t = 33.5;
      voice.dispatchEvent(new Event("timeupdate"));
      key("KeyC");
      out.popForSpoken = !pop.hidden;
      out.spokenQuote = pop.querySelector(".note-quote").textContent;
      out.pausedForNote = state.paused;
      area.value = "second comment";
      enter();
      out.resumedAfterNote = !state.paused;
      out.timeAfterNote = state.t;

      // 4. a comment opened while the voice is paused leaves it paused
      voice.pause();
      voice.currentTime = 44;
      key("KeyC");
      out.pausedPopShown = !pop.hidden;
      area.value = "third comment";
      enter();
      out.stillPausedAfterNote = state.paused;

      // 5. Escape closes without saving
      voice.currentTime = 50.3;
      key("KeyC");
      out.escapePopShown = !pop.hidden;
      area.value = "never kept";
      escape();
      out.escapeClosed = pop.hidden;
      out.notesAfterEscape = noteCount();
      out.stillPausedAfterEscape = state.paused;

      // 6. a click on a commented piece opens it with its text
      click(commented, textRange(commented, 4, 25).getClientRects()[0]);
      out.editOpens = !pop.hidden;
      out.editText = area.value;
      escape();

      // 7. putting the cursor into a part's words field pauses the voice
      voice.play();
      var field = document.getElementById("part-words-1");
      field.focus();
      out.pausedByField = state.paused;
      field.value = "words on the opening";
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.blur();

      // 8. the copied text ends with the comment lines in page order; the stored answer holds the comments
      out.composed = copied();
      var answer = stored();
      out.storedNotes = answer && Array.isArray(answer.notes) ? answer.notes : null;
    }
  } catch (e) { out.error = String(e && e.stack || e); }
  var pre = document.createElement("pre");
  pre.id = "behaviour-out";
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
