"""check_quotes.py: whether the words each citation quotes stand in the source it cites."""
from __future__ import annotations

import contextlib
import hashlib
import http.server
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "maintenance" / "scripts" / "check_quotes.py"
sys.path.insert(0, str(SCRIPT.parent))
import check_quotes as cq  # noqa: E402

USER_AGENT = "Mozilla/5.0 (compatible; quote-check)"
JSON_FIELDS = ["id", "source", "status", "case_differs", "ratio", "source_words", "context", "content_type",
               "http_status", "final_url", "error"]
THIRTY_WORDS = ("A rule that claims a technique works rests on a test that could have refuted the claim, "
                "and a claim with no test yet waits in the list of hypotheses")
PAGE = ("<!DOCTYPE html><html><head><title>Method</title><style>p { color: red }</style>"
        "<script>var hidden = 'words only a script holds';</script></head><body>"
        "<p>He wrote &ldquo;a <em>test</em> that could have <a href=\"#r\">refuted</a> the claim&rdquo; "
        "&mdash; and ran&nbsp;it.</p><p>The method admits a rule by its test.</p></body></html>")


def setUpModule() -> None:
    """Every request of this module goes straight to 127.0.0.1, whatever proxy the environment names."""
    environment = mock.patch.dict(os.environ, {"no_proxy": "*", "NO_PROXY": "*"})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


def citation(source: str, quote: str, cid: str = "Q-1") -> dict:
    return {"id": cid, "source": source, "quote": quote}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.server.requests.append((self.path, self.headers.get("User-Agent")))
        status, headers, body = self.server.routes.get(self.path, (404, {"Content-Type": "text/plain"}, b"no page"))
        self.send_response(status)
        for name, value in {**headers, "Content-Length": str(len(body))}.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """The server writes no access log into the test output."""


Routes = dict[str, tuple[int, dict[str, str], bytes]]


class RouteServer(http.server.ThreadingHTTPServer):
    """Each path answers from its route, any other with a 404; every request is recorded with its User-Agent."""

    def __init__(self, routes: Routes) -> None:
        super().__init__(("127.0.0.1", 0), Handler)
        self.routes = routes
        self.requests: list[tuple[str, str]] = []


class Server:
    """A RouteServer on 127.0.0.1, served from a thread until stop()."""

    def __init__(self, routes: Routes) -> None:
        self.httpd = RouteServer(routes)
        # A short poll interval lets stop() return within 50 ms instead of the default half second.
        self.thread = threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        self.running = True

    @property
    def requests(self) -> list[tuple[str, str]]:
        return self.httpd.requests

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.httpd.server_address[1]}{path}"

    def stop(self) -> None:
        if self.running:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.thread.join()
            self.running = False


class Base(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="check-quotes-")
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def write(self, name: str, content: str | bytes) -> str:
        path = self.dir / name
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return str(path)

    def run_main(self, *args: str) -> tuple[int, list[str], str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cq.main(list(args))
            except SystemExit as usage:
                code = usage.code
        return code, out.getvalue().splitlines(), err.getvalue()

    def check(self, *citations: dict, args: tuple[str, ...] = ()) -> tuple[int, list[str], list[dict]]:
        """The exit status, the stdout lines and the --json entries of one run over the citations."""
        path, out = self.write("citations.json", json.dumps(list(citations))), self.dir / "out.json"
        code, lines, err = self.run_main("--json", str(out), *args, path)
        self.assertIn(code, (0, 1), err)
        entries = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(code, 0 if all(e["status"] == "found" for e in entries) else 1)
        self.assertEqual(lines[-1], f"{sum(e['status'] != 'found' for e in entries)} of {len(entries)} not found")
        return code, lines, entries

    def result(self, source: str, quote: str, *args: str) -> dict:
        return self.check(citation(source, quote), args=args)[2][0]


class Matching(Base):
    def test_an_exact_quote_in_plain_text_is_found(self):
        source = self.write("plain.txt", "Intro.\nThe method admits a rule\n  only when a test could refute it.\n")
        found = self.result(source, "The method admits a rule only when a test could refute it.")
        self.assertEqual((found["status"], found["case_differs"], found["ratio"]), ("found", False, None))
        self.assertEqual(found["context"], "Intro. The method admits a rule only when a test could refute it.")

    def test_an_exact_quote_in_html_is_found_across_entities_tags_curly_quotes_and_an_em_dash(self):
        source = self.write("page.html", PAGE)
        quote = 'He wrote "a test that could have refuted the claim" - and ran it.'
        found = self.result(source, quote, "--context", "0")
        self.assertEqual((found["status"], found["context"]), ("found", quote))

    def test_curly_quotes_and_a_dash_in_the_quote_match_straight_ones_in_the_source(self):
        source = self.write("plain.txt", 'She said "one test - one claim" twice.')
        found = self.result(source, "She said “one test — one claim” twice.")
        self.assertEqual(found["status"], "found")

    def test_soft_hyphens_and_zero_width_characters_are_removed(self):
        source = self.write("plain.txt", "Co\u00adoperation of zero\u200bwidth joiners.")
        self.assertEqual(self.result(source, "Cooperation of zerowidth joiners.")["status"], "found")

    def test_script_and_style_contents_are_not_source_text(self):
        source = self.write("page.html", PAGE)
        for quote in ("words only a script holds", "p { color: red }"):
            with self.subTest(quote=quote):
                self.assertEqual(self.result(source, quote)["status"], "absent")

    def test_an_ellipsis_quote_is_found_when_its_fragments_stand_in_order(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        for ellipsis in ("…", "...", "[...]", "[…]"):
            with self.subTest(ellipsis=ellipsis):
                found = self.result(source, f"A rule that claims {ellipsis} waits in the list", "--context", "0")
                self.assertEqual((found["status"], found["context"]), ("found", "A rule that claims ... waits in the list"))

    def test_the_same_fragments_in_reverse_order_are_not_found(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        self.assertEqual(self.result(source, "waits in the list … A rule that claims")["status"], "absent")

    def test_a_quote_differing_only_in_case_is_found_with_case_differs(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        found = self.result(source, "a RULE that claims a Technique works")
        self.assertEqual((found["status"], found["case_differs"]), ("found", True))

    def test_one_changed_word_in_a_thirty_word_quote_is_near_with_the_source_words(self):
        source = self.write("plain.txt", f"Before it. {THIRTY_WORDS}. After it.")
        self.assertEqual(len(THIRTY_WORDS.split()), 30)
        near = self.result(source, THIRTY_WORDS.replace("refuted", "confirmed"))
        self.assertEqual((near["status"], near["source_words"], near["case_differs"]), ("near", THIRTY_WORDS, None))
        self.assertGreaterEqual(near["ratio"], 0.9)
        self.assertEqual(near["context"], f"Before it. {THIRTY_WORDS}. After it.")

    def test_an_unrelated_sentence_is_absent(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        absent = self.result(source, "Bananas ripen faster beside apples in a paper bag.")
        self.assertEqual((absent["status"], absent["source_words"], absent["context"]), ("absent", None, None))
        self.assertLess(absent["ratio"], 0.9)

    def test_a_megabyte_page_with_a_forty_word_quote_resolves_in_a_few_seconds(self):
        rng = random.Random(1)
        vocabulary = THIRTY_WORDS.lower().replace(",", "").split() + "of to in is for as with on by at from".split()
        sentence = " ".join(rng.choice(vocabulary) for _ in range(40))
        paragraphs = [f"<p>{' '.join(rng.choice(vocabulary) for _ in range(80))}.</p>\n" for _ in range(2800)]
        paragraphs.insert(2000, f"<p>{sentence}.</p>\n")
        page = "<html><body>" + "".join(paragraphs) + "</body></html>"
        self.assertGreater(len(page), 1_000_000)
        words = sentence.split()
        words[20] = "elephant"
        source = self.write("big.html", page)
        started = time.monotonic()
        near = self.result(source, " ".join(words))
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual((near["status"], near["source_words"]), ("near", sentence))

    def test_a_local_file_that_cannot_be_read_is_unfetched(self):
        missing = str(self.dir / "missing.txt")
        unfetched = self.result(missing, "any words")
        self.assertEqual(unfetched["status"], "unfetched")
        self.assertIn(f"cannot read {missing}", unfetched["error"])


class Normalising(unittest.TestCase):
    def test_every_dash_and_minus_sign_reads_as_a_hyphen(self):
        dashes = [chr(c) for c in range(sys.maxunicode + 1) if unicodedata.category(chr(c)) == "Pd"] + list(cq.MINUS_SIGNS)
        self.assertEqual({char: cq.normalise(f"a{char}b") for char in dashes}, {char: "a-b" for char in dashes})

    def test_quotation_marks_primes_and_guillemets_read_as_straight_quotes(self):
        self.assertEqual(cq.normalise("‘a’ “b” „c‟ «d» ‹e› 5′"), "'a' \"b\" \"c\" \"d\" 'e' 5'")

    def test_white_space_runs_become_one_space(self):
        self.assertEqual(cq.normalise(" \ta \n b c  "), "a b c")


class Fetching(Base):
    def setUp(self) -> None:
        super().setUp()
        html = {"Content-Type": "text/html; charset=utf-8"}
        self.server = Server({
            "/page.html": (200, html, PAGE.encode("utf-8")),
            "/latin1": (200, {"Content-Type": "text/plain; charset=iso-8859-1"}, "Café crème".encode("iso-8859-1")),
            "/moved": (302, {"Location": "/page.html"}, b""),
            "/to-file": (302, {"Location": "file:///etc/hosts"}, b""),
            "/paper.pdf": (200, {"Content-Type": "application/pdf"}, b"%PDF-1.7 The method admits a rule by its test."),
        })
        self.addCleanup(self.server.stop)

    def test_a_page_cited_twice_is_fetched_once_with_a_generic_user_agent(self):
        url = self.server.url("/page.html")
        _, _, entries = self.check(citation(url, "The method admits a rule"), citation(url, "by its test", "Q-2"))
        self.assertEqual([e["status"] for e in entries], ["found", "found"])
        self.assertEqual((entries[0]["content_type"], entries[0]["http_status"], entries[0]["final_url"]),
                         ("text/html; charset=utf-8", 200, url))
        self.assertEqual(self.server.requests, [("/page.html", USER_AGENT)])

    def test_the_charset_of_the_content_type_decodes_the_body(self):
        self.assertEqual(self.result(self.server.url("/latin1"), "Café crème")["status"], "found")

    def test_a_redirect_is_followed_and_its_target_is_the_final_url(self):
        found = self.result(self.server.url("/moved"), "The method admits a rule")
        self.assertEqual((found["status"], found["final_url"]), ("found", self.server.url("/page.html")))

    def test_a_redirect_to_a_file_url_is_not_followed(self):
        self.assertEqual(self.result(self.server.url("/to-file"), "localhost")["status"], "unfetched")

    def test_a_pdf_is_unreadable_with_its_content_type(self):
        _, lines, entries = self.check(citation(self.server.url("/paper.pdf"), "The method admits a rule"))
        self.assertEqual((entries[0]["status"], entries[0]["content_type"]), ("unreadable", "application/pdf"))
        self.assertEqual(lines[0], "Q-1: UNREADABLE: content type application/pdf is neither HTML nor text")

    def test_a_404_is_unfetched_with_its_status(self):
        _, lines, entries = self.check(citation(self.server.url("/absent"), "any words"))
        self.assertEqual((entries[0]["status"], entries[0]["http_status"]), ("unfetched", 404))
        self.assertEqual(lines[0], "Q-1: UNFETCHED: HTTP 404 Not Found")

    def test_a_refused_connection_is_unfetched(self):
        url = self.server.url("/page.html")
        self.server.stop()
        unfetched = self.result(url, "The method admits a rule")
        self.assertEqual((unfetched["status"], unfetched["http_status"]), ("unfetched", None))
        self.assertIn("refused", unfetched["error"].lower())

    def test_the_cache_answers_the_second_run_with_the_server_stopped(self):
        url, cache = self.server.url("/page.html"), self.dir / "cache"
        first = self.check(citation(url, "The method admits a rule"), args=("--cache", str(cache)))[2]
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        self.assertEqual(sorted(p.name for p in cache.iterdir()), [f"{key}.body", f"{key}.json"])
        self.server.stop()
        second = self.check(citation(url, "The method admits a rule"), args=("--cache", str(cache)))[2]
        self.assertEqual(second, first)
        self.assertEqual(second[0]["status"], "found")
        self.assertEqual(len(self.server.requests), 1)


class CommandLine(Base):
    def test_the_output_has_one_line_per_citation_and_a_last_line(self):
        source = self.write("plain.txt", "naïve café — the rule holds — fin")
        code, lines, _ = self.check(citation(source, "the rule holds"),
                                    citation(source, "Bananas ripen faster", "Q-2"), args=("--context", "4"))
        self.assertEqual(code, 1)
        self.assertEqual(lines[0], "Q-1: FOUND: é - the rule holds - f")
        self.assertRegex(lines[1], r"^Q-2: ABSENT: no window of the source reaches 0\.9; the best similarity is 0\.\d{3}$")
        self.assertEqual(lines[2:], ["1 of 2 not found"])

    def test_every_citation_found_exits_0(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        code, _, _ = self.check(citation(source, "A rule that claims"), citation(source, "list of hypotheses", "Q-2"))
        self.assertEqual(code, 0)

    def test_the_json_objects_carry_the_fields_in_order(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        entry = self.check(citation(source, "A rule that claims"))[2][0]
        self.assertEqual(list(entry), JSON_FIELDS)
        self.assertEqual({k: entry[k] for k in ("content_type", "http_status", "final_url", "error", "source_words")},
                         dict.fromkeys(("content_type", "http_status", "final_url", "error", "source_words")))

    def test_a_malformed_citations_file_exits_2(self):
        good = {"id": "Q-1", "source": "a.txt", "quote": "words"}
        cases = {
            "not JSON": b"[{",
            "not UTF-8": b'[{"id": "Q-1", "source": "a.txt", "quote": "\xff"}]',
            "top level not an array": json.dumps(good).encode(),
            "item not an object": b'["Q-1"]',
            "quote missing": json.dumps([{"id": "Q-1", "source": "a.txt"}]).encode(),
            "id not a string": json.dumps([{**good, "id": 7}]).encode(),
            "source empty": json.dumps([{**good, "source": " "}]).encode(),
            "quote of ellipses alone": json.dumps([{**good, "quote": "… [...]"}]).encode(),
        }
        for name, content in cases.items():
            with self.subTest(name):
                code, lines, err = self.run_main(self.write("citations.json", content))
                self.assertEqual((code, lines), (2, []))
                self.assertIn("citations.json", err)

    def test_a_missing_citations_file_exits_2(self):
        code, lines, err = self.run_main(str(self.dir / "absent.json"))
        self.assertEqual((code, lines), (2, []))
        self.assertIn("cannot read", err)

    def test_a_duplicate_id_exits_2(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        path = self.write("citations.json", json.dumps([citation(source, "A rule"), citation(source, "a claim")]))
        code, lines, err = self.run_main(path)
        self.assertEqual((code, lines), (2, []))
        self.assertIn("id 'Q-1' repeats the id of item 1", err)

    def test_wrong_usage_exits_2(self):
        path = self.write("citations.json", "[]")
        for args in (("--context", "-1", path), ("--timeout", "0", path), ("--timeout", "inf", path), ()):
            with self.subTest(args=args):
                self.assertEqual(self.run_main(*args)[0], 2)

    def test_a_cache_directory_that_cannot_be_created_exits_2(self):
        blocker = self.write("blocker", "a file where the cache directory would go")
        code, lines, err = self.run_main("--cache", blocker, self.write("citations.json", "[]"))
        self.assertEqual((code, lines), (2, []))
        self.assertIn("cannot create the cache directory", err)

    def test_the_script_runs_under_python_isolated_as_a_subprocess(self):
        source = self.write("plain.txt", THIRTY_WORDS)
        path = self.write("citations.json", json.dumps([citation(source, "a claim with no test yet")]))
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--context", "0", path],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.splitlines(), ["Q-1: FOUND: a claim with no test yet", "0 of 1 not found"])


if __name__ == "__main__":
    unittest.main()
