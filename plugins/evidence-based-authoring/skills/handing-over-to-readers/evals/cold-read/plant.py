#!/usr/bin/env python3
"""Write the planted reports of the cold-read measurement, and sort the answers of a blind run.

    plant.py PLANTS.json                       write every variant's report beside PLANTS.json
    plant.py PLANTS.json --blind DIR           also copy every report to DIR as <case>-<k>.md, and DIR/key.json
    plant.py PLANTS.json --collect DIR RUNS    copy RUNS/_blind/<case>-<k>/cold.json to RUNS/<case>--<variant>/cold.json

A variant of PLANTS.json carries `remove`, a list of operations applied in order to the intact report:
{"sentence": PREFIX} takes out the sentence that starts with PREFIX; {"section": HEADING} takes out the
part from that heading line to the next `## ` heading; {"line": TEXT} takes out the one line holding
TEXT. An operation that does not match exactly once stops the run with exit 2, so a changed report
cannot be planted silently. The blind names keep the kind of a variant out of the path a reader sees;
key.json maps each blind name to its case and variant.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ORDERS = ([2, 0, 3, 1], [1, 3, 0, 2], [3, 1, 2, 0], [0, 2, 1, 3])
SENTENCE_END = re.compile(r"[.?](?: |\n|$)")


def apply(text: str, op: dict) -> str:
    (kind, value), = op.items()
    if kind == "sentence":
        if text.count(value) != 1:
            raise ValueError(f"sentence {value!r}: {text.count(value)} matches")
        start = text.index(value)
        end = SENTENCE_END.search(text, start + len(value) - 1)
        stop = end.end() if end and text[end.end() - 1] == " " else (end.start() + 1 if end else len(text))
        return text[:start] + text[stop:]
    if kind == "section":
        lines = text.split("\n")
        starts = [i for i, line in enumerate(lines) if line.strip() == value]
        if len(starts) != 1:
            raise ValueError(f"section {value!r}: {len(starts)} matches")
        after = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        return "\n".join(lines[:starts[0]] + lines[after:])
    if kind == "line":
        lines = text.split("\n")
        hits = [i for i, line in enumerate(lines) if value in line]
        if len(hits) != 1:
            raise ValueError(f"line {value!r}: {len(hits)} matches")
        return "\n".join(lines[:hits[0]] + lines[hits[0] + 1:])
    raise ValueError(f"unknown operation {kind!r}")


def reports(plants: dict):
    """(case, variant, path relative to PLANTS.json) for the intact report and every variant, in file order."""
    for case in plants["cases"]:
        yield case["case"], "intact", case["report_intact"]
        for variant in case["variants"]:
            yield case["case"], variant["variant"], variant["report"]


def blind_names(plants: dict) -> dict:
    names = {}
    for index, case in enumerate(plants["cases"]):
        variants = ["intact"] + [v["variant"] for v in case["variants"]]
        order = ORDERS[index % len(ORDERS)]
        for k, variant in enumerate(variants):
            names[f"{case['case']}-{order[k % len(order)] + 1}"] = {"case": case["case"], "variant": variant}
    return names


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    manifest = Path(argv[1])
    base = manifest.parent
    try:
        plants = json.loads(manifest.read_text(encoding="utf-8"))
        if "--collect" in argv:
            blind, runs = Path(argv[argv.index("--collect") + 1]), Path(argv[argv.index("--collect") + 2])
            key = json.loads((blind / "key.json").read_text(encoding="utf-8"))
            for name, where in key.items():
                source = runs / "_blind" / name / "cold.json"
                target = runs / f"{where['case']}--{where['variant']}" / "cold.json"
                if source.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
                print(f"{name} -> {target.parent.name}: {'copied' if source.exists() else 'absent'}")
            return 0
        for case in plants["cases"]:
            intact = (base / case["report_intact"]).read_text(encoding="utf-8")
            for variant in case["variants"]:
                text = intact
                for op in variant["remove"]:
                    text = apply(text, op)
                (base / variant["report"]).write_text(re.sub(r"\n{3,}", "\n\n", text), encoding="utf-8")
                print(f"{case['case']}--{variant['variant']}: {len(intact.split()) - len(text.split())} words out")
        if "--blind" in argv:
            blind = Path(argv[argv.index("--blind") + 1])
            blind.mkdir(parents=True, exist_ok=True)
            key = blind_names(plants)
            paths = {(c, v): p for c, v, p in reports(plants)}
            for name, where in key.items():
                shutil.copyfile(base / paths[(where["case"], where["variant"])], blind / f"{name}.md")
            (blind / "key.json").write_text(json.dumps(key, indent=1) + "\n", encoding="utf-8")
            print(f"{len(key)} blind copies in {blind}")
    except (OSError, ValueError, KeyError, IndexError) as e:
        print(f"plant: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
