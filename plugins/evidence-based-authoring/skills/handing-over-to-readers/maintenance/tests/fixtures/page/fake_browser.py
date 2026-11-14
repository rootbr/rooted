"""A stand-in for Chrome in the tests of check_page.py: it records its arguments and answers --dump-dom and --screenshot
as the environment says, without loading the page.

FAKE_BROWSER_LOG      a file to which each run appends its arguments as one JSON line
FAKE_BROWSER_PROBE    the JSON text the measuring script would write, printed inside its pre element for --dump-dom;
                      absent: the run prints nothing
FAKE_BROWSER_PICTURE  present: --screenshot=FILE writes a few bytes of PNG signature into FILE; absent: it writes nothing
"""
import html
import json
import os
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

arguments = sys.argv[1:]
with open(os.environ["FAKE_BROWSER_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(arguments) + "\n")
if "--dump-dom" in arguments and "FAKE_BROWSER_PROBE" in os.environ:
    print(f'<html><body><pre id="check-page-out">{html.escape(os.environ["FAKE_BROWSER_PROBE"], quote=False)}</pre></body></html>')
for argument in arguments:
    if argument.startswith("--screenshot=") and "FAKE_BROWSER_PICTURE" in os.environ:
        with open(argument.split("=", 1)[1], "wb") as picture:
            picture.write(PNG_SIGNATURE)
