"""CLI tests for `adoptionkit lint`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from conftest import make_engagement
from typer.testing import CliRunner

from adoptionkit.cli import app

runner = CliRunner()


def _atom(ref: str | None) -> dict[str, Any]:
    source: dict[str, Any] = {"kind": "document"}
    if ref is not None:
        source["ref"] = ref
    return {
        "id": "A-001",
        "type": "requirement",
        "statement": "s",
        "source": source,
        "status": "evidenced",
    }


def _write(tmp_path: Path, **kw: Any) -> Path:
    f = tmp_path / "e.json"
    f.write_text(json.dumps(make_engagement(**kw)), encoding="utf-8")
    return f


def test_lint_clean_exit_0(tmp_path: Path) -> None:
    f = _write(tmp_path, atoms=[_atom("doc-1")])
    result = runner.invoke(app, ["lint", str(f)])
    assert result.exit_code == 0
    assert "0 Befunde (0 error, 0 warning)" in result.output


def test_lint_error_exit_1_text(tmp_path: Path) -> None:
    f = _write(tmp_path, atoms=[_atom(None)])
    result = runner.invoke(app, ["lint", str(f)])
    assert result.exit_code == 1
    assert "L001 error atoms/A-001: " in result.output
    assert "1 Befunde (1 error, 0 warning)" in result.output


def test_lint_warning_only_exit_0(tmp_path: Path) -> None:
    m = {"id": "M-001", "description": "d", "change_type": "configuration"}
    f = _write(tmp_path, measures=[m])
    result = runner.invoke(app, ["lint", str(f)])
    assert result.exit_code == 0
    assert "L003 warning measures/M-001: " in result.output
    assert "1 Befunde (0 error, 1 warning)" in result.output


def test_lint_json(tmp_path: Path) -> None:
    f = _write(tmp_path, atoms=[_atom(None)])
    result = runner.invoke(app, ["lint", str(f), "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["summary"] == {"error": 1, "warning": 0}
    assert data["findings"][0]["code"] == "L001"


def test_lint_invalid_file_exit_1(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text("{ nope", encoding="utf-8")
    result = runner.invoke(app, ["lint", str(f)])
    assert result.exit_code == 1
    assert "Traceback" not in result.output


def test_lint_schema_issues_exit_1(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text(json.dumps({"meta": {}}), encoding="utf-8")
    result = runner.invoke(app, ["lint", str(f)])
    assert result.exit_code == 1
