"""CLI tests for `adoptionkit init` (synthetic data only)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from adoptionkit.cli import app
from adoptionkit.models import DISCLAIMER

runner = CliRunner()


def _load(folder: Path) -> dict[str, Any]:
    return json.loads((folder / "engagement.json").read_text(encoding="utf-8"))


def test_init_creates_files_and_validates(tmp_path: Path) -> None:
    target = tmp_path / "Mein_Fall 1"
    result = runner.invoke(app, ["init", str(target)])
    assert result.exit_code == 0
    assert (target / "evidence").is_dir()
    data = _load(target)
    assert data["meta"]["id"] == "mein-fall-1"
    assert data["meta"]["created"] == date.today().isoformat()
    assert data["meta"]["updated"] == date.today().isoformat()
    assert data["meta"]["schema_version"] == "0.1"
    assert data["meta"]["profile"] == "generic"
    assert data["parties"]["client"] == "" and data["parties"]["contractor"] == ""
    assert data["solution"]["name"] == "" and data["solution"]["vendor"] == ""
    assert [p["id"] for p in data["phases"]] == [
        "discovery",
        "prototype",
        "value_proof",
        "hardening",
        "handover",
    ]
    assert all(p["status"] == "planned" and p["budget_days"] == 0 for p in data["phases"])
    assert [g["id"] for g in data["gates"]] == ["G0", "G3", "G4"]
    assert all(c["answer"] == "unclear" for g in data["gates"] for c in g["checks"])
    assert data["gates"][0]["disclaimer"] == DISCLAIMER
    check = runner.invoke(app, ["validate", str(target / "engagement.json")])
    assert check.exit_code == 0, check.output


def test_init_options(tmp_path: Path) -> None:
    target = tmp_path / "x"
    result = runner.invoke(
        app,
        ["init", str(target), "--title", "Mein Titel", "--id", "fall-7", "--profile", "generic"],
    )
    assert result.exit_code == 0
    data = _load(target)
    assert data["meta"]["id"] == "fall-7" and data["meta"]["title"] == "Mein Titel"


def test_init_default_id_stripped_and_fallback(tmp_path: Path) -> None:
    runner.invoke(app, ["init", str(tmp_path / "..Foo")])
    assert _load(tmp_path / "..Foo")["meta"]["id"] == "foo"
    runner.invoke(app, ["init", str(tmp_path / "___")])
    assert _load(tmp_path / "___")["meta"]["id"] == "engagement"


def test_init_existing_file_fails_unchanged(tmp_path: Path) -> None:
    target = tmp_path / "fall"
    target.mkdir()
    (target / "engagement.json").write_text("{}", encoding="utf-8")
    result = runner.invoke(app, ["init", str(target)])
    assert result.exit_code == 1
    assert (target / "engagement.json").read_text(encoding="utf-8") == "{}"


def test_init_unknown_profile(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path / "x"), "--profile", "gibt-es-nicht"])
    assert result.exit_code == 1
    assert not (tmp_path / "x" / "engagement.json").exists()


def test_init_invalid_id(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path / "x"), "--id", "Falsch Ä"])
    assert result.exit_code == 1


def test_init_then_gate_blocked_by_l005_until_abort_criteria_set(tmp_path: Path) -> None:
    """Fresh init has no abort criteria; L005 (error) blocks gates until they are filled in."""
    target = tmp_path / "fall"
    runner.invoke(app, ["init", str(target)])
    file = target / "engagement.json"
    result = runner.invoke(app, ["gate", str(file), "G0"])
    assert result.exit_code == 1 and "L005" in result.output
    data = _load(target)
    for p in data["phases"]:
        p["abort_criterion"] = "Abbruch bei fehlendem Nutzen"
    file.write_text(json.dumps(data), encoding="utf-8")
    result = runner.invoke(app, ["gate", str(file), "G0"])
    assert result.exit_code == 0
    assert "G0: open" in result.output
