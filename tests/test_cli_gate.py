"""CLI tests for `adoptionkit gate` (synthetic data only)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from conftest import make_engagement
from typer.testing import CliRunner

from adoptionkit.cli import app
from adoptionkit.models import DISCLAIMER

runner = CliRunner()

ATOM = {
    "id": "A-001",
    "type": "requirement",
    "statement": "s",
    "source": {"kind": "document", "ref": "doc-1"},
    "status": "evidenced",
}


def _checks(overrides: dict[str, str] | None = None) -> list[dict[str, Any]]:
    answers = {f"G0-0{i}": "yes" for i in range(1, 6)}
    answers.update(overrides or {})
    return [
        {"id": i, "question": "q", "answer": a, "atom_refs": ["A-001"], "source_ref": "S03"}
        for i, a in answers.items()
    ]


def _write(tmp_path: Path, **kw: Any) -> Path:
    f = tmp_path / "e.json"
    f.write_text(json.dumps(make_engagement(**kw)), encoding="utf-8")
    return f


def _gate_eng(tmp_path: Path, overrides: dict[str, str] | None = None) -> Path:
    gates = [{"id": "G0", "title": "Eignung", "checks": _checks(overrides)}]
    return _write(tmp_path, atoms=[ATOM], gates=gates)


def test_gate_passed_writes_file(tmp_path: Path) -> None:
    f = _gate_eng(tmp_path)
    result = runner.invoke(app, ["gate", str(f), "G0", "--today", "2026-05-04"])
    assert result.exit_code == 0
    assert "G0: passed" in result.output
    assert "Empfehlung: standard_rollout" in result.output
    assert result.output.strip().endswith(DISCLAIMER)
    saved = json.loads(f.read_text(encoding="utf-8"))
    g = saved["gates"][0]
    assert g["result"] == "passed" and g["evaluated_on"] == "2026-05-04"
    assert saved["meta"]["updated"] == "2026-05-04"


def test_gate_guided_recommendation(tmp_path: Path) -> None:
    f = _gate_eng(tmp_path, {"G0-05": "no"})
    result = runner.invoke(app, ["gate", str(f), "G0", "--today", "2026-05-04"])
    assert "Empfehlung: guided_rollout" in result.output


def test_gate_open_lists_reasons_and_no_recommendation(tmp_path: Path) -> None:
    f = _write(tmp_path)
    result = runner.invoke(app, ["gate", str(f), "G0", "--today", "2026-05-04"])
    assert result.exit_code == 0
    assert "G0: open" in result.output
    assert "Empfehlung" not in result.output
    assert "- G0-01: nicht beantwortet" in result.output
    assert json.loads(f.read_text(encoding="utf-8"))["gates"][0]["result"] == "open"


def test_gate_stopped_decline(tmp_path: Path) -> None:
    f = _gate_eng(tmp_path, {"G0-01": "no"})
    result = runner.invoke(app, ["gate", str(f), "G0", "--today", "2026-05-04"])
    assert "G0: stopped" in result.output
    assert "Empfehlung: decline" in result.output


def test_gate_blocked_leaves_file_unchanged(tmp_path: Path) -> None:
    f = _write(tmp_path, phases=[{"id": "discovery", "budget_days": 1, "status": "running"}])
    before = f.read_bytes()
    result = runner.invoke(app, ["gate", str(f), "G0", "--today", "2026-05-04"])
    assert result.exit_code == 1
    assert "L007" in result.output
    assert f.read_bytes() == before


def test_gate_invalid_today(tmp_path: Path) -> None:
    f = _write(tmp_path)
    result = runner.invoke(app, ["gate", str(f), "G0", "--today", "morgen"])
    assert result.exit_code == 1
    assert "Traceback" not in result.output


def test_gate_unknown_gate_id(tmp_path: Path) -> None:
    f = _write(tmp_path)
    result = runner.invoke(app, ["gate", str(f), "G9"])
    assert result.exit_code == 1


def test_gate_not_in_profile(tmp_path: Path) -> None:
    f = _write(tmp_path)
    before = f.read_bytes()
    result = runner.invoke(app, ["gate", str(f), "G1"])
    assert result.exit_code == 1
    assert f.read_bytes() == before


def test_gate_unknown_profile(tmp_path: Path) -> None:
    f = _write(tmp_path)
    result = runner.invoke(app, ["gate", str(f), "G0", "--profile", "gibt-es-nicht"])
    assert result.exit_code == 1
    assert "gibt-es-nicht" in result.output


def test_gate_invalid_file(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text(json.dumps({"meta": {}}), encoding="utf-8")
    result = runner.invoke(app, ["gate", str(f), "G0"])
    assert result.exit_code == 1


def test_gate_default_today_is_used(tmp_path: Path) -> None:
    f = _write(tmp_path)
    result = runner.invoke(app, ["gate", str(f), "G0"])
    assert result.exit_code == 0
    saved = json.loads(f.read_text(encoding="utf-8"))
    assert saved["gates"][0]["evaluated_on"] == date.today().isoformat()
