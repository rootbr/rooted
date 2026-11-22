/* The scripted reader of test_page_behaviour.py: it acts on a built page in headless Chrome and writes what it saw as JSON
   into a pre element of the id behaviour-out, appended to the body.
   Real audio does not advance under virtual time, so the audio element's paused, ended, currentTime, play and pause are
   stubbed; the stubs fire the same events a real element fires, and the page's listeners answer them synchronously.
   The clipboard is stubbed as well: it records every text written to it and, when told to, refuses.
   The asynchronous steps of the page are the tools a mouseup shows on a timer, the toggle event of an opened answer, the
   current place of the map, which follows a scroll on the next frame, and the preview a pointer leaves: the reader polls
   for them. Under virtual time headless Chrome draws no frame after the first, so it runs no requestAnimationFrame
   callback, dispatches no scroll event and advances no CSS animation; the map scenarios give the page a frame clock on
   timers, dispatch the scroll event themselves and finish the panel's animation before measuring it.
   window.behaviourScenario, set by the test before this script, names the scenario: "silent", "voice", "selection",
   "quiz", "pseudocode", "map", "narrowMap", "refs", "refsOver" or "refsPlain". */
window.addEventListener("load", async function () {
  var out = {};
  function tick() { return new Promise(function (resolve) { setTimeout(resolve, 10); }); }
  /* Re-tests the condition every 10 ms for at most 2 s; the expectation that follows reports a condition never met. */
  async function until(condition) { for (var waited = 0; waited < 2000 && !condition(); waited += 10) { await tick(); } }
  function all(root, selector) { return Array.prototype.slice.call(root.querySelectorAll(selector)); }
  /* A keydown on the target, the body when none is given; returns the event, so its defaultPrevented can be read. */
  function key(code, target) {
    var names = { Space: " ", KeyC: "c", Escape: "Escape", Enter: "Enter" };
    var e = new KeyboardEvent("keydown", { code: code, key: names[code], bubbles: true, cancelable: true });
    (target || document.body).dispatchEvent(e);
    return e;
  }
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
    var bar = document.querySelector(".answer-bar"), tools = document.querySelector(".sel-tools");
    var copyButton = tools.querySelectorAll("button")[0], commentButton = tools.querySelectorAll("button")[1], said = tools.querySelector("[aria-live]");
    function sentence(id) { return article.querySelector('.s[data-lit="' + id + '"]'); }
    /* Selects a piece of a node's text as a mouse does and waits for the tools of the selection. */
    async function select(node, from, to) {
      var selection = getSelection();
      selection.removeAllRanges();
      selection.addRange(textRange(node, from, to));
      node.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
      await tick();  // the page reads the selection on a timer after the mouseup: tools still shown belong to the last one
      await until(function () { return !tools.hidden; });
    }
    /* Selects a piece and opens the comment window on it from the tools. */
    async function noteOn(node, from, to) {
      await select(node, from, to);
      commentButton.click();
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
    /* The stubbed audio element; state.paused and state.t are what the page set last, state.plays counts the starts. */
    function stubVoice() {
      var state = { paused: true, t: 0, plays: 0 };
      Object.defineProperty(voice, "paused", { get: function () { return state.paused; } });
      Object.defineProperty(voice, "ended", { get: function () { return false; } });
      Object.defineProperty(voice, "currentTime", {
        get: function () { return state.t; },
        set: function (v) { state.t = v; voice.dispatchEvent(new Event("seeked")); }
      });
      voice.play = function () { state.paused = false; state.plays += 1; voice.dispatchEvent(new Event("play")); return Promise.resolve(); };
      voice.pause = function () { state.paused = true; voice.dispatchEvent(new Event("pause")); };
      return state;
    }
    /* The stubbed clipboard: writes holds every text the page wrote, execs counts the copy commands; refuse makes both fail. */
    function stubClipboard() {
      var clip = { writes: [], execs: 0, refuse: false }, exec = document.execCommand.bind(document);
      Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText: function (text) {
        if (clip.refuse) { return Promise.reject(new Error("refused")); }
        clip.writes.push(text);
        return Promise.resolve();
      } } });
      document.execCommand = function (command) {
        if (command !== "copy") { return exec.apply(null, arguments); }
        clip.execs += 1;
        return !clip.refuse;
      };
      return clip;
    }
    /* The frame clock and the scroll of the map scenarios; see the head of this file. */
    function frameClock() {
      window.requestAnimationFrame = function (callback) { return setTimeout(function () { callback(performance.now()); }, 16); };
    }
    function scrollToY(y) { window.scrollTo(0, y); window.dispatchEvent(new Event("scroll")); }
    function settled(e) { e.getAnimations().forEach(function (a) { a.finish(); }); return e; }
    function rectOf(e) { var r = e.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom }; }
    function overlaps(a, b) { return a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom; }
    out.sideExists = !!document.querySelector(".side-tools");
    out.playerExists = !!document.querySelector(".player, #now, #parts, .hint, .parts-toggle");
    out.audioControls = voice.hasAttribute("controls");
    out.mapExists = !!document.querySelector(".page-map, .map-toggle");
    out.noAudioShown = !document.getElementById("no-audio").hidden;
    out.partButtons = all(article, ".part-voice").map(function (b) {
      return { in: b.parentElement.tagName.toLowerCase(), label: b.getAttribute("data-label"), name: b.getAttribute("aria-label"), text: b.textContent };
    });

    async function silent() {
      out.barHiddenBefore = bar.hidden;
      await noteOn(sentence("1.2"), 0, 13);
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

    /* The example page with its voice: the buttons at the parts' headings, the stop at a part's end, Space, a comment. */
    async function voiceByPart() {
      var state = stubVoice(), buttons = article.querySelectorAll(".part-voice");
      function seen(b) { return { label: b.getAttribute("data-label"), playing: b.classList.contains("is-playing"), next: b.classList.contains("is-next") }; }

      // 1. nothing starts the voice at load, and Space before the first start is left to the browser
      out.playsAtLoad = state.plays;
      out.earlySpacePrevented = key("Space").defaultPrevented;
      out.pausedAfterEarlySpace = state.paused;

      // 2. the button of the part "How it broke" plays that part
      buttons[1].click();
      out.timeAfterPress = state.t;
      out.playingAfterPress = !state.paused;
      out.secondWhilePlaying = seen(buttons[1]);
      out.secondNameWhilePlaying = buttons[1].getAttribute("aria-label");

      // 3. a click on the text and the key C leave the voice running and open no window
      click(sentence("2.3"));
      out.playingAfterTextClick = !state.paused;
      key("KeyC");
      out.popAfterC = !pop.hidden;
      out.playingAfterC = !state.paused;

      // 4. the voice stops where the next part starts, and that part's button is marked as the way on
      state.t = data.parts[2].start + 0.01;
      voice.dispatchEvent(new Event("timeupdate"));
      out.pausedAtEnd = state.paused;
      out.timeAtEnd = state.t;
      out.secondAfterEnd = seen(buttons[1]);
      out.thirdAfterEnd = seen(buttons[2]);

      // 5. after the first start Space resumes, and the voice speaks the next part
      out.lateSpacePrevented = key("Space").defaultPrevented;
      out.playingAfterSpace = !state.paused;
      out.thirdAfterSpace = seen(buttons[2]);

      // 6. the button of the part being spoken pauses and resumes it
      buttons[2].click();
      out.pausedByButton = state.paused;
      out.thirdWhilePaused = seen(buttons[2]);
      buttons[2].click();
      out.resumedByButton = !state.paused;
      out.timeAfterResume = state.t;

      // 7. Space pauses; a press on another part's button moves the voice there and plays
      key("Space");
      out.pausedBySpace = state.paused;
      buttons[1].click();
      out.timeAfterOther = state.t;
      out.playingAfterOther = !state.paused;
      out.otherWhilePlaying = seen(buttons[1]);
      out.thirdAfterOther = seen(buttons[2]);

      // 8. a comment pauses the running voice; after Enter it goes on from the start of the interrupted sentence
      state.t = 32.8;
      voice.dispatchEvent(new Event("timeupdate"));
      await noteOn(sentence("3.3"), 0, 9);
      out.pausedForNote = state.paused;
      area.value = "a comment while the voice ran";
      enter();
      out.resumedAfterNote = !state.paused;
      out.timeAfterNote = state.t;

      // 9. putting the cursor into a part's words field pauses the voice
      var field = document.getElementById("part-words-1");
      field.focus();
      out.pausedByField = state.paused;
      field.blur();
      out.playsAtEnd = state.plays;
    }

    /* The example page: the tools of a selection, the clipboard, the comments made from the tools. */
    async function selection() {
      stubVoice();
      var clip = stubClipboard(), piece = sentence("3.6");

      // 1. a selection shows the tools beside it and no window; nothing is copied
      await select(piece, 4, 25);
      out.toolsShown = !tools.hidden;
      out.popAfterSelect = !pop.hidden;
      out.toolsRole = tools.getAttribute("role");
      out.toolsLabel = tools.getAttribute("aria-label");
      out.toolsButtons = texts([copyButton, commentButton]);
      var lines = textRange(piece, 4, 25).getClientRects(), box = rectOf(tools);
      out.toolsAboveFirstLine = box.bottom <= lines[0].top;
      out.toolsCoverText = Array.prototype.some.call(lines, function (r) { return overlaps(box, r); });
      out.clipboardBeforeCopy = clip.writes.length + clip.execs;

      // 2. the copy button writes the selected text, says so, and keeps the selection
      copyButton.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, cancelable: true }));
      copyButton.click();
      await until(function () { return said.textContent; });
      out.clipboardWrites = clip.writes.slice();
      out.copyStatus = said.textContent;
      out.selectionKept = getSelection().toString();

      // 3. the comment button opens the window on that piece with the cursor in its field; Enter keeps the comment
      commentButton.click();
      await until(function () { return !pop.hidden; });
      out.popShown = !pop.hidden;
      out.quote = pop.querySelector(".note-quote").textContent;
      out.focusInPop = document.activeElement === area;
      out.toolsHiddenWithPop = tools.hidden;
      area.value = "first comment";
      enter();
      out.popClosed = pop.hidden;
      out.highlight = !!(window.CSS && CSS.highlights && CSS.highlights.has("note"));
      out.listed = noteCount();

      // 4. a click on the commented piece opens its comment again
      click(piece, textRange(piece, 4, 25).getClientRects()[0]);
      out.editOpens = !pop.hidden;
      out.editText = area.value;
      escape();

      // 5. Escape hides the tools, and so does a selection that collapses
      await select(sentence("2.5"), 0, 9);
      out.toolsBeforeEscape = !tools.hidden;
      key("Escape");
      out.toolsAfterEscape = tools.hidden;
      await select(sentence("2.5"), 0, 9);
      getSelection().collapseToStart();
      await until(function () { return tools.hidden; });
      out.toolsAfterCollapse = tools.hidden;

      // 6. a selection in the page's own controls shows no tools
      var label = document.querySelector(".part-words label");
      getSelection().removeAllRanges();
      getSelection().addRange(textRange(label, 0, 10));
      label.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
      await tick();
      await tick();
      out.toolsOnControl = !tools.hidden;

      // 7. a selection at the top of the window takes the tools under its last line
      var top = sentence("2.2");
      window.scrollTo(0, top.getBoundingClientRect().top + window.scrollY - 4);
      await select(top, 0, 11);
      var first = textRange(top, 0, 11).getClientRects(), under = rectOf(tools);
      out.toolsUnderLastLine = under.top >= first[first.length - 1].bottom;

      // 8. a copy the clipboard and the browser both refuse is said in the tools
      clip.refuse = true;
      copyButton.click();
      await until(function () { return said.textContent; });
      out.failedStatus = said.textContent;
      clip.refuse = false;
      getSelection().removeAllRanges();

      // 9. two more comments: the copied answer carries them in page order, and the stored answer holds them
      await noteOn(sentence("2.5"), 0, sentence("2.5").textContent.length);
      area.value = "second comment";
      enter();
      await noteOn(sentence("3.2"), 0, sentence("3.2").textContent.length);
      area.value = "third comment";
      enter();
      var field = document.getElementById("part-words-1");
      field.value = "words on the opening";
      field.dispatchEvent(new Event("input", { bubbles: true }));
      out.composed = copied();
      var answer = stored();
      out.storedNotes = answer && Array.isArray(answer.notes) ? answer.notes : null;
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
      await noteOn(answerText, 0, 9);
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

    /* An explanation's page: a comment on a piece of a pseudocode line, one on a paragraph after it, a click on the link
       at the end of a line. */
    async function pseudocode() {
      var keyLine = article.querySelector('figure.pseudo pre [data-lit="2.3"]'), partLink = article.querySelector("figure.pseudo pre a");

      // 1. a selection inside a line opens the window from the tools; Enter keeps the comment
      await noteOn(keyLine, 0, 12);
      out.linePopShown = !pop.hidden;
      out.lineFocusInPop = document.activeElement === area;
      out.lineQuote = pop.querySelector(".note-quote").textContent;
      area.value = "a comment on a line";
      enter();
      var answer = stored();
      out.notesAfterLine = answer && Array.isArray(answer.notes) ? answer.notes : null;

      // 2. a selection in a paragraph opens the window the same way and keeps its comment
      await noteOn(sentence("4.2"), 0, 19);
      out.paragraphPopShown = !pop.hidden;
      out.paragraphQuote = pop.querySelector(".note-quote").textContent;
      area.value = "a comment on a paragraph";
      enter();

      // 3. a click on the link of a line follows it and opens no window
      click(partLink);
      await until(function () { return location.hash === "#h-miss"; });
      out.hashAfterLink = location.hash;
      out.popHiddenAfterLink = pop.hidden;

      // 4. the copied answer holds both comment lines in page order
      out.composed = copied();
    }

    /* The map's groups as the reader sees them: each part's title and its entries as [kind, name]. */
    function mapGroups(nav) {
      return all(nav, ".map-group").map(function (g) {
        return { title: g.querySelector(".map-part").textContent, entries: all(g, ".map-entries a").map(function (a) {
          var kind = a.querySelector(".map-kind").textContent;
          return [kind, a.textContent.slice(kind.length)];
        }) };
      });
    }
    function mapState(nav, toggle) {
      return { expanded: toggle.getAttribute("aria-expanded"), label: toggle.textContent, hidden: nav.hidden };
    }
    function expandedOf(nav, title) {
      var group = all(nav, ".map-group").filter(function (g) { return g.querySelector(".map-part").textContent === title; })[0];
      return group.querySelector(".map-disclose").getAttribute("aria-expanded");
    }
    function currentLinks(nav) { return all(nav, "[aria-current]").map(function (a) { return [a.getAttribute("aria-current"), a.textContent]; }); }

    /* An explanation in a wide window: the map beside the text, the current place, the toggle, the place kept. */
    async function map() {
      var nav = document.querySelector(".page-map"), toggle = document.querySelector(".map-toggle");
      frameClock();
      out.groups = mapGroups(nav);
      out.navLabel = nav.getAttribute("aria-label");
      out.atStart = mapState(nav, toggle);
      out.toggleControls = toggle.getAttribute("aria-controls") === nav.id;
      out.figureLabels = all(article, "figure").map(function (f) { return f.getAttribute("aria-label"); });
      out.linksResolve = all(nav, ".map-entries a").every(function (a) {
        var target = document.getElementById(a.getAttribute("href").slice(1));
        return !!target && (target.matches("figure") || target.hasAttribute("data-nav"));
      });
      out.besideText = rectOf(settled(nav)).right <= rectOf(article).left;
      out.filterShown = !!nav.querySelector("input[type=search]");

      // 1. after a scroll that brings the factor table just above a third of the window, its entry is the one current
      //    link, and the page shows its group
      var factor = article.querySelector("figure.factor");
      out.missBeforeScroll = expandedOf(nav, "A miss");
      scrollToY(factor.getBoundingClientRect().top + window.scrollY - (window.innerHeight / 3 - 20));
      await until(function () { return currentLinks(nav).length && currentLinks(nav)[0][1].indexOf("The key without") >= 0; });
      out.currentAfterScroll = currentLinks(nav);
      out.missExpanded = expandedOf(nav, "A miss");

      // 2. leaving the part closes the group the page opened; a group the reader opened stays open
      nav.querySelectorAll(".map-disclose")[2].click();
      scrollToY(0);
      await until(function () { return expandedOf(nav, "A miss") === "false"; });
      out.afterLeaving = { miss: expandedOf(nav, "A miss"), questions: expandedOf(nav, "Your questions"), current: currentLinks(nav).length };

      // 3. the toggle hides the map and keeps the reader's choice; it shows it again
      toggle.click();
      out.afterClose = mapState(nav, toggle);
      out.storedAfterClose = localStorage.getItem(data.id + ":map");
      out.textLeftClosed = rectOf(article).left;

      // 4. the block at the top keeps its distance from the top of the window when the panel opens and moves the text
      var block = sentence("2.2").parentElement;
      scrollToY(block.getBoundingClientRect().top + window.scrollY - 4);
      var before = block.getBoundingClientRect().top;
      toggle.click();
      out.offsetShift = block.getBoundingClientRect().top - before;
      out.afterOpen = mapState(nav, toggle);
      out.storedAfterOpen = localStorage.getItem(data.id + ":map");
      out.textLeftOpen = rectOf(article).left;
    }

    /* An explanation in a narrow window: the map over the text, closed at the start and after a jump, Escape, a click outside. */
    async function narrowMap() {
      var nav = document.querySelector(".page-map"), toggle = document.querySelector(".map-toggle");
      frameClock();
      out.width = window.innerWidth;
      out.atStart = mapState(nav, toggle);
      var textBefore = rectOf(article);
      toggle.click();
      out.afterOpen = mapState(nav, toggle);
      out.overText = overlaps(rectOf(settled(nav)), rectOf(article)) && Math.abs(rectOf(article).left - textBefore.left) < 1;
      out.pageFitsWidth = document.documentElement.scrollWidth <= window.innerWidth;
      out.toggleFitsWidth = rectOf(toggle).right <= window.innerWidth && rectOf(nav).right <= window.innerWidth;

      // 1. a jump closes the map and hands the focus to the toggle
      nav.querySelectorAll(".map-entries a")[1].click();
      out.afterJump = mapState(nav, toggle);
      out.focusAfterJump = document.activeElement === toggle;

      // 2. Escape closes it
      toggle.click();
      key("Escape");
      out.afterEscape = mapState(nav, toggle);
      out.focusAfterEscape = document.activeElement === toggle;

      // 3. a click outside it closes it
      toggle.click();
      click(article.querySelector("h1"));
      out.afterClickOutside = mapState(nav, toggle);
      out.stored = localStorage.getItem(data.id + ":map");
    }

    function previewState(preview, owner) {
      return { shown: !preview.hidden, where: preview.querySelector("code") ? preview.querySelector("code").textContent : null,
               lines: texts(preview.querySelectorAll(".ln")).map(function (n) { return Number(n.trim()); }),
               hit: preview.querySelector(".hit .ln") ? Number(preview.querySelector(".hit .ln").textContent.trim()) : null,
               describedBy: owner.getAttribute("aria-describedby") === preview.id };
    }

    /* An explanation with a code reference and a source reference: the preview, the panel, the focus. */
    async function refs() {
      var code = article.querySelector('[data-ref="key-value"]'), source = article.querySelector('[data-ref="generation"]');
      var preview = document.querySelector(".ref-pop"), panel = document.querySelector(".ref-panel");
      out.controls = all(article, "[data-ref]").map(function (e) {
        return { tabindex: e.getAttribute("tabindex"), role: e.getAttribute("role"), expanded: e.getAttribute("aria-expanded"),
                 underlined: e.classList.contains("ref"), title: e.hasAttribute("title") };
      });

      // 1. the keyboard focus shows the preview; Escape hides it and leaves the focus; leaving the focus hides it
      code.focus();
      out.previewOnFocus = previewState(preview, code);
      key("Escape", code);
      out.afterEscape = { shown: !preview.hidden, focusKept: document.activeElement === code };
      code.blur();
      code.focus();
      out.shownAgain = !preview.hidden;
      code.blur();
      out.hiddenOnBlur = preview.hidden;

      // 2. the pointer shows the preview of a source; it goes a short time after the pointer leaves
      source.dispatchEvent(new MouseEvent("mouseenter"));
      out.sourcePreview = { shown: !preview.hidden, text: preview.textContent };
      source.dispatchEvent(new MouseEvent("mouseleave"));
      out.shownJustAfterLeaving = !preview.hidden;
      await until(function () { return preview.hidden; });
      out.hiddenAfterLeaving = preview.hidden;

      // 3. a click opens the panel with the whole excerpt, its line marked, and the link into the editor; in a window
      //    whose text keeps room beside the open map and the panel, the panel stands beside the text and the reference
      //    keeps its place on the screen
      var textBefore = rectOf(article), codeTop = code.getBoundingClientRect().top;
      click(code);
      var links = all(panel, "a");
      out.panel = { shown: !panel.hidden, label: panel.getAttribute("aria-label"), heading: panel.querySelector("h2").textContent,
                    where: panel.querySelector("code").textContent, lines: panel.querySelectorAll(".ln").length,
                    hit: Number(panel.querySelector(".hit .ln").textContent.trim()), links: links.map(function (a) { return [a.textContent, a.getAttribute("href")]; }),
                    focusInPanel: panel.contains(document.activeElement), expanded: code.getAttribute("aria-expanded"), previewShown: !preview.hidden };
      out.panelBesideText = rectOf(panel).left >= rectOf(article).right - 1;
      out.beside = { mapBeside: document.documentElement.classList.contains("map-beside"), textBefore: Math.round(textBefore.right - textBefore.left),
                     textAfter: Math.round(rectOf(article).right - rectOf(article).left), refShift: Math.round(code.getBoundingClientRect().top - codeTop) };

      // 4. the close button closes it and hands the focus back to the reference, which shows no preview then
      panel.querySelector(".ref-close").click();
      out.afterClose = { hidden: panel.hidden, focusBack: document.activeElement === code, expanded: code.getAttribute("aria-expanded"),
                         previewShown: !preview.hidden };

      // 5. Enter on the source opens its panel with its title, note and link; Escape closes it and returns the focus
      source.focus();
      key("Enter", source);
      var sourceLinks = all(panel, "a");
      out.sourcePanel = { shown: !panel.hidden, texts: texts(panel.querySelectorAll("p")),
                          links: sourceLinks.map(function (a) { return [a.textContent, a.getAttribute("href"), a.target, a.rel]; }) };
      key("Escape", document.activeElement);
      out.afterSourceEscape = { hidden: panel.hidden, focusBack: document.activeElement === source };

      // 6. Space on a reference opens its panel too
      key("Space", code);
      out.spaceOpens = !panel.hidden && code.getAttribute("aria-expanded") === "true";
    }

    /* A window where the map stands open beside the text and leaves it too little room for the panel beside it too: the
       panel lies over the text, which keeps its width. */
    async function refsOver() {
      var code = article.querySelector('[data-ref="key-value"]'), panel = document.querySelector(".ref-panel"), root = document.documentElement;
      var before = rectOf(article);
      out.mapBeside = root.classList.contains("map-beside");
      click(code);
      var after = rectOf(article);
      out.over = { shown: !panel.hidden, besideClass: root.classList.contains("ref-beside"), overText: overlaps(rectOf(panel), after),
                   textBefore: Math.round(before.right - before.left), textAfter: Math.round(after.right - after.left) };
    }

    /* A code reference on a page built without --editor-url: its panel has no link into the editor. */
    async function refsPlain() {
      click(article.querySelector('[data-ref="key-value"]'));
      out.panelLinks = all(document.querySelector(".ref-panel"), "a").length;
    }

    var scenarios = { silent: silent, voice: voiceByPart, selection: selection, quiz: quiz, pseudocode: pseudocode, map: map,
                      narrowMap: narrowMap, refs: refs, refsOver: refsOver, refsPlain: refsPlain };
    await scenarios[window.behaviourScenario]();
  } catch (e) { out.error = String(e && e.stack || e); }
  var pre = document.createElement("pre");
  pre.id = "behaviour-out";
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
