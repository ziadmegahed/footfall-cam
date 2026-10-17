import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts/events/event.schema.json"
EXAMPLES_DIR = ROOT / "contracts/events/examples"


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    example_files = sorted(EXAMPLES_DIR.glob("*.json"))
    if not example_files:
        raise SystemExit("No event examples found.")

    failed = False

    for path in example_files:
        event = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(
            validator.iter_errors(event),
            key=lambda error: list(error.absolute_path),
        )

        if errors:
            failed = True
            for error in errors:
                location = ".".join(map(str, error.absolute_path)) or "<root>"
                print(f"FAIL {path.name}: {location}: {error.message}")
        else:
            print(f"PASS {path.name}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
