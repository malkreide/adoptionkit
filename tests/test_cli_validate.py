"""CLI tests for `adoptionkit validate`."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import make_engagement
from typer.testing import CliRunner

from adoptionkit.cli import app

runner = CliRunner()


def test_validate_ok(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text(json.dumps(make_engagement()), encoding="utf-8")
    result = runner.invoke(app, ["validate", str(f)])
    assert result.exit_code == 0
    assert result.output.strip() == f"ok: {f}"


def test_validate_issues_exit_1(tmp_path: Path) -> None:
    atom = {
        "id": "A-001",
        "type": "requirement",
        "statement": "s",
        "source": {"kind": "interview"},
        "status": "evidenced",
    }
    f = tmp_path / "e.json"
    f.write_text(json.dumps(make_engagement(atoms=[atom, dict(atom)])), encoding="utf-8")
    result = runner.invoke(app, ["validate", str(f)])
    assert result.exit_code == 1
    assert "atoms/1/id: doppelte ID A-001" in result.output


def test_validate_bad_json_exit_1_no_traceback(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text("{ nope", encoding="utf-8")
    result = runner.invoke(app, ["validate", str(f)])
    assert result.exit_code == 1
    assert "Traceback" not in result.output
    assert "Zeile 1" in result.output


def test_validate_missing_file_exit_1(tmp_path: Path) -> None:
    result = runner.invoke(app, ["validate", str(tmp_path / "nope.json")])
    assert result.exit_code == 1
