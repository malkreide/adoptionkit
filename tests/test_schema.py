from pathlib import Path

import adoptionkit
from adoptionkit.schema_gen import build_schema, render_schema

SCHEMA = Path(adoptionkit.__file__).parent / "schema" / "engagement.schema.json"


def test_schema_header():
    s = build_schema()
    assert s["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert s["title"] == "adoptionkit engagement"


def test_checked_in_schema_has_no_drift():
    assert SCHEMA.read_text(encoding="utf-8") == render_schema()
