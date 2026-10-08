#!/usr/bin/env python3
"""The generator that appends the series rows of evals/expected.json: three seeds and three controls per
domain the pilot fixture did not cover (design, interface, change, performance), on the same (rule_id, file,
symbol) triples as pilot-expected-gen.py writes. Usage: python3 extended-expected-gen.py <evals/expected.json>
(rewrites the file, keeping the pilot rows first; idempotent on the ids it adds)."""
import json, sys

def it(name, *extra):
    return list(extra) + [name, f'"{name}"', f"'{name}'", f'it("{name}")', f"it('{name}')", f'it.only("{name}")', f"it.only('{name}')"]

seeds = [
    ("dsn-37-seed", "DSN-37", "design/java/Circle.java", "Circle#area"),
    ("dsn-65-seed", "DSN-65", "design/go/server.go", ["Server.SetAddr", "SetAddr", "Server.addr", "addr", "func (s *Server) SetAddr"]),
    ("dsn-72-seed", "DSN-72", "design/py/tagging.py", ["add_tag", "DEFAULT_TAGS", "file:design/py/tagging.py"]),
    ("api-08-seed", "API-08", "interface/ts/labels.ts", "normalizeLabel"),
    ("api-27-seed", "API-27", "interface/py/cache.py", "ConfigCache#fetch"),
    ("api-15-seed", "API-15", "interface/rust/ports.rs", "Registry::port_of"),
    ("chg-11-seed", "CHG-11", "change/go/writer.go", ["Writer.flushBatch", "flushBatch", "func (w *Writer) flushBatch"]),
    ("chg-10-seed", "CHG-10", "change/ts/reader.ts", ["file:change/ts/reader.ts", "format", "read", "reader.ts"]),
    ("chg-08-seed", "CHG-08", "change/java/Pricing.java", "Pricing#legacyPrice"),
    ("prf-04-seed", "PRF-04", "performance/py/totals.py", ["total", "file:performance/py/totals.py", "totals.py"]),
    ("prf-05-seed", "PRF-05", "performance/go/report.go", ["summarize", "func summarize"]),
    ("prf-06-seed", "PRF-06", "performance/ts/parser.test.ts", it("rejectsEmptyInput", 'describe("parseAmount")', "parseAmount")),
]
controls = [
    ("dsn-37-control", "DSN-37", "design/java/Square.java", "Square#area"),
    ("dsn-65-control", "DSN-65", "design/go/server.go", ["Server.SetTimeout", "SetTimeout", "Server.timeout", "timeout", "func (s *Server) SetTimeout"]),
    ("dsn-72-control", "DSN-72", "design/py/tagging.py", ["labels_for", "DEFAULT_LABELS"]),
    ("api-08-control", "API-08", "interface/ts/labels.ts", "watchPrices"),
    ("api-27-control", "API-27", "interface/py/cache.py", "ConfigCache#lookup"),
    ("api-15-control", "API-15", "interface/rust/ports.rs", "Registry::restarts_of"),
    ("chg-11-control", "CHG-11", "change/go/writer.go", ["Writer.writeRecord", "writeRecord", "func (w *Writer) writeRecord"]),
    ("chg-10-control", "CHG-10", "change/ts/registry.ts", ["file:change/ts/registry.ts", "pluginNames", "registry.ts"]),
    ("chg-08-control", "CHG-08", "change/java/Pricing.java", ["Pricing#Pricing", "Pricing#<init>", "Pricing"]),
    ("prf-04-control", "PRF-04", "performance/py/totals.py", "subtotal"),
    ("prf-05-control", "PRF-05", "performance/go/report.go", ["PrintReport", "func PrintReport"]),
    ("prf-06-control", "PRF-06", "performance/ts/parser.test.ts", it("acceptsOnlyAsciiDigits")),
]
path = sys.argv[1]
d = json.load(open(path, encoding="utf-8"))
have = {r["id"] for r in d["seeds"]} | {r["id"] for r in d["controls"]}
d["seeds"] += [{"id": i, "rule_id": r, "file": f, "symbol": s} for i, r, f, s in seeds if i not in have]
d["controls"] += [{"id": i, "silent": [r], "file": f, "symbol": s} for i, r, f, s in controls if i not in have]
out = ['{', ' "seeds": [', ",\n".join("  " + json.dumps(x) for x in d["seeds"]), ' ],', ' "controls": [', ",\n".join("  " + json.dumps(x) for x in d["controls"]), ' ]', '}']
text = "\n".join(out) + "\n"
json.loads(text)
open(path, "w", encoding="utf-8").write(text)
print(f"{path}: {len(d['seeds'])} seeds, {len(d['controls'])} controls")
