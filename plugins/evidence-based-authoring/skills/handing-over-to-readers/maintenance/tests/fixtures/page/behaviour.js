/* The scripted reader of test_page_behaviour.py: it acts on a built page in headless Chrome and writes what it saw as JSON
   into a pre element of the id behaviour-out, appended to the body.
   Real audio does not advance under virtual time, so the audio element's paused, ended, currentTime, play and pause are
   stubbed; the stubs fire the same events a real element fires, and the page's listeners answer them synchronously.
   The asynchronous steps of the page are the comment window a mouseup opens on a timer and the toggle event of an opened
   answer: the reader polls for them.
   window.behaviourScenario, set by the test before this script, names the scenario: "silent", "voiced", "parts", "quiz",
   or "observe", which records only what every scenario records first. */
window.addEventListener("load", async function () {
  var out = {};
  function tick() { return new Promise(function (resolve) { setTimeout(resolve, 10); }); }
  /* Re-tests the condition every 10 ms for at most 2 s; the expectation that follows reports a condition never met. */
  async function until(condition) { for (var waited = 0; waited < 2000 && !condition(); waited += 10) { await tick(); } }
  function key(code) { document.dispatchEvent(new KeyboardEvent("keydown", { code: code, key: code === "Space" ? " " : "c", bubbles: true })); }
  function click(target, rect) {
    var box = rect || target.getBoundingClientRect();
    target.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, clientX: box.left + box.width / 2, clientY: box.top + box.height / 2 }));
  }
  function textRange(node, from, to) { var r = document.createRange(); r.setStart(node.firstChild, from); r.setEnd(node.firstChild, to); return r; }
  function texts(nodes) { return Array.prototype.map.call(nodes, function (n) { return n.textContent; }); }
  function pressed(nodes) { return Array.prototype.map.call(nodes, function (n) { return n.getAttribute("aria-pressed"); }); }
  try {
    var data = JSON.parse(document.getElementById("page-data").textContent);
    var article = document.getElementById("article"), voice = document.getElementById("voice");
    var pop = document.querySelector(".note-pop"), area = pop.querySelector("textarea");
    var bar = document.querySelector(".answer-bar"), partList = document.getElementById("parts");
    function sentence(id) { return article.querySelector('.s[data-lit="' + id + '"]'); }
    async function select(node, from, to) {
      var selection = getSelection();
      selection.removeAllRanges();
      selection.addRange(textRange(node, from, to));
      node.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
      await until(function () { return !pop.hidden; });
    }
    function enter() { area.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true })); }
    function escape() { area.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); }
    function noteCount() { return document.querySelectorAll(".notes ol > li").length; }
    function stored() { return JSON.parse(localStorage.getItem(data.id) || "null"); }
    function copied() {
      document.querySelector(".answer-bar .primary").click();
      return document.querySelector(".answer-text").textContent;
    }
    /* The stubbed audio element; state.paused and state.t are what the page set last. */
    function stubVoice() {
      var state = { paused: true, t: 0 };
      Object.defineProperty(voice, "paused", { get: function () { return state.paused; } });
      Object.defineProperty(voice, "ended", { get: function () { return false; } });
      Object.defineProperty(voice, "currentTime", {
        get: function () { return state.t; },
        set: function (v) { state.t = v; voice.dispatchEvent(new Event("seeked")); }
      });
      voice.play = function () { state.paused = false; voice.dispatchEvent(new Event("play")); return Promise.resolve(); };
      voice.pause = function () { state.paused = true; voice.dispatchEvent(new Event("pause")); };
      return state;
    }
    out.hint = document.querySelector(".hint") ? document.querySelector(".hint").textContent : null;
    out.sideExists = !!document.querySelector(".side-tools");
    out.cornerExists = !!document.querySelector(".corner-pause, [data-proto]");
    out.partsToggleExists = !!document.querySelector(".parts-toggle");
    out.partListHidden = partList.hidden;
    out.partButtons = partList.querySelectorAll("button").length;

    async function silent() {
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
    }

    async function voiced() {
      var state = stubVoice();
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
      out.nowPart = document.getElementById("now-part").textContent;
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

    /* A page of more than six parts: the list opens from its control and closes on a choice, on Escape and on a click elsewhere. */
    async function parts() {
      var state = stubVoice(), toggle = document.querySelector(".parts-toggle");
      function seen() { return { hidden: partList.hidden, expanded: toggle.getAttribute("aria-expanded") }; }
      out.toggleText = toggle.textContent;
      out.toggleControls = toggle.getAttribute("aria-controls");
      out.toggleBeforeList = toggle.nextElementSibling === partList;
      out.atStart = seen();
      toggle.click();
      out.afterOpen = seen();
      var fourth = partList.querySelectorAll("button")[3];
      fourth.click();
      out.afterChoice = seen();
      out.timeAfterChoice = state.t;
      out.playingAfterChoice = !state.paused;
      toggle.click();
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true }));
      out.afterEscape = seen();
      toggle.click();
      click(article.querySelector("h1"));
      out.afterClickElsewhere = seen();
    }

    /* A page with two questions, in the parts "How it broke" and "What is left". */
    async function quiz() {
      var state = stubVoice(), questions = article.querySelectorAll("figure.quiz details.q"), first = questions[0], second = questions[1];
      var returnBox = document.querySelector(".return-to");
      function digits(text) { return text.match(/\d+/g) || []; }
      function marksOf(q) { return q.querySelectorAll(".marks button"); }
      function returns() { return { hidden: returnBox.hidden, lead: returnBox.querySelector("p").textContent, parts: texts(returnBox.querySelectorAll("button")) }; }
      var articleDigits = digits(article.innerText);

      // 1. a closed answer has no marks; an opened one has the two buttons from the strings, neither pressed
      out.marksWhileClosed = marksOf(first).length;
      first.querySelector("summary").click();
      await until(function () { return marksOf(first).length; });
      out.markLabels = texts(marksOf(first));
      out.pressedAtOpen = pressed(marksOf(first));
      out.returnsBefore = returns();

      // 2. "missed" lists the question's part; "knew" after it empties the list
      marksOf(first)[1].click();
      out.pressedAfterMissed = pressed(marksOf(first));
      out.returnsAfterMissed = returns();
      marksOf(first)[0].click();
      out.pressedAfterKnew = pressed(marksOf(first));
      out.returnsAfterKnew = returns();

      // 3. a click on a question, its answer or its marks leaves the voice as it was, playing or paused
      state.t = 30;
      voice.play();
      click(second.querySelector("summary"));
      await until(function () { return marksOf(second).length; });
      out.openedByClick = second.open;
      out.playingAfterQuestion = !state.paused;
      click(second.querySelector(".answer"));
      out.playingAfterAnswer = !state.paused;
      voice.pause();
      click(second.querySelector(".answer"));
      out.pausedAfterAnswer = state.paused;
      marksOf(second)[1].click();
      out.pausedAfterMark = state.paused;
      out.returnsAtEnd = returns();

      // 4. no count: the marks change no number in the article, and the marks and the list hold none
      out.articleDigitsKept = JSON.stringify(digits(article.innerText)) === JSON.stringify(articleDigits);
      out.quizDigits = digits(texts(document.querySelectorAll(".marks, .return-to")).join(" "));

      // 5. a comment on a piece of an answer keeps working: it opens the window, keeps the comment and names the part
      var answerText = second.querySelector(".answer");
      await select(answerText, 0, 9);
      out.answerPopShown = !pop.hidden;
      out.answerQuote = pop.querySelector(".note-quote").textContent;
      area.value = "a comment in an answer";
      enter();
      out.answerNoteListed = noteCount();

      // 6. the marks stay out of the copied answer and the stored one, and stay in the browser under their own key
      var field = document.getElementById("part-words-1");
      field.value = "words on the opening";
      field.dispatchEvent(new Event("input", { bubbles: true }));
      out.composed = copied();
      out.storedAnswer = localStorage.getItem(data.id);
      out.storedMarks = JSON.parse(localStorage.getItem(data.id + ":marks") || "null");
      out.questionTexts = texts([first.querySelector("summary"), second.querySelector("summary")]);
    }

    var scenarios = { silent: silent, voiced: voiced, parts: parts, quiz: quiz, observe: async function () {} };
    await scenarios[window.behaviourScenario]();
  } catch (e) { out.error = String(e && e.stack || e); }
  var pre = document.createElement("pre");
  pre.id = "behaviour-out";
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
