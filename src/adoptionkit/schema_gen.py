"""Generate the JSON Schema for the engagement file from the pydantic models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from adoptionkit.models import Engagement

SCHEMA_PATH = Path(__file__).parent / "schema" / "engagement.schema.json"


def build_schema() -> dict[str, Any]:
    schema = Engagement.model_json_schema()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/malkreide/adoptionkit/schema/engagement.schema.json",
        **schema,
        "title": "adoptionkit engagement",
    }


def render_schema() -> str:
    return json.dumps(build_schema(), indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCHEMA_PATH.open("w", encoding="utf-8", newline="\n") as f:
        f.write(render_schema())


if __name__ == "__main__":
    main()
