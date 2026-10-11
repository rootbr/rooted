"""Export of account records to the archive format."""
import json

Settings = dict[str, object]


def load_legacy(path: str, settings: Settings) -> list[dict]:
    with open(path, "rb") as fh:
        records = json.loads(fh.read())
    limit = settings["batch_size"] + 1  # type: ignore[operator]
    return [r for r in records if r.get("active")][:limit]


def export_batch(records: list[dict], settings: Settings) -> bytes:
    text = json.dumps(records, indent=settings["indent"])  # type: ignore[arg-type]  # the settings type is object-valued; the settings schema fixes indent as an int
    return text.encode("utf-8")
