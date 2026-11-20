"""Tests for io: loading, schema validation, integrity rules, roundtrip."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from conftest import make_engagement

from adoptionkit.errors import AdoptionkitError
from adoptionkit.io import (
    load_engagement,
    load_json,
    load_schema,
    save_engagement,
    validate_data,
)


def atom(id: str) -> dict[str, Any]:
    return {
        "id": id,
        "type": "requirement",
        "statement": "Synthetic statement",
        "source": {"kind": "interview"},
        "status": "evidenced",
    }


def check(id: str, refs: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": id,
        "question": "Synthetic question?",
        "answer": "yes",
        "atom_refs": refs or [],
        "source_ref": "S-001",
    }


def measure(id: str, **kw: Any) -> dict[str, Any]:
    return {"id": id, "description": "Synthetic", "change_type": "configuration", **kw}


def messages(data: dict[str, Any]) -> list[tuple[str, str]]:
    return [(i.path, i.message) for i in validate_data(data)]


def test_valid_minimal_has_no_issues() -> None:
    assert validate_data(make_engagement()) == []


def test_load_schema_returns_dict() -> None:
    assert load_schema()["type"] == "object"


def test_schema_issue_has_slash_path() -> None:
    bad = atom("A-001")
    bad["source"] = {"kind": "nonsense"}
    issues = validate_data(make_engagement(atoms=[bad]))
    assert any(i.path == "atoms/0/source/kind" for i in issues)


def test_root_issue_uses_root_marker() -> None:
    data = make_engagement()
    del data["meta"]
    assert any(i.path == "(root)" for i in validate_data(data))


def test_issues_sorted_by_path() -> None:
    issues = validate_data(make_engagement(atoms=[atom("bad"), atom("worse")]))
    paths = [i.path for i in issues]
    assert paths == sorted(paths)


def test_duplicate_atom_ids() -> None:
    assert ("atoms/1/id", "doppelte ID A-001") in messages(
        make_engagement(atoms=[atom("A-001"), atom("A-001")])
    )


def test_duplicate_phase_ids() -> None:
    phase = {"id": "discovery", "budget_days": 1}
    assert ("phases/1/id", "doppelte ID discovery") in messages(
        make_engagement(phases=[phase, dict(phase)])
    )


def test_duplicate_gate_ids() -> None:
    gate = {"id": "G0", "title": "t"}
    assert ("gates/1/id", "doppelte ID G0") in messages(make_engagement(gates=[gate, dict(gate)]))


def test_duplicate_check_ids_within_gate() -> None:
    gate = {"id": "G0", "title": "t", "checks": [check("G0-01"), check("G0-01")]}
    assert ("gates/0/checks/1/id", "doppelte ID G0-01") in messages(make_engagement(gates=[gate]))


def test_duplicate_measure_ids() -> None:
    assert ("measures/1/id", "doppelte ID M-001") in messages(
        make_engagement(measures=[measure("M-001"), measure("M-001")])
    )


def test_duplicate_artefact_ids() -> None:
    art = {"id": "X-001", "description": "d", "origin_measure": "M-001"}
    data = make_engagement(measures=[measure("M-001")], artefacts=[art, dict(art)])
    assert ("artefacts/1/id", "doppelte ID X-001") in messages(data)


def test_duplicate_run_ids() -> None:
    run = {"id": "R-001", "date": "2026-01-01", "metric": "acc", "value": 0.5}
    data = make_engagement(evals={"runs": [run, dict(run)]})
    assert ("evals/runs/1/id", "doppelte ID R-001") in messages(data)


def test_check_atom_ref_missing() -> None:
    gate = {"id": "G0", "title": "t", "checks": [check("G0-01", ["A-099"])]}
    assert ("gates/0/checks/0/atom_refs/0", "Atom A-099 existiert nicht") in messages(
        make_engagement(gates=[gate])
    )


def test_measure_atom_ref_missing() -> None:
    data = make_engagement(measures=[measure("M-001", atom_refs=["A-099"])])
    assert ("measures/0/atom_refs/0", "Atom A-099 existiert nicht") in messages(data)


def test_product_decision_ref_missing() -> None:
    data = make_engagement(measures=[measure("M-001", product_decision_ref="A-099")])
    assert ("measures/0/product_decision_ref", "Atom A-099 existiert nicht") in messages(data)


def test_origin_measure_missing() -> None:
    art = {"id": "X-001", "description": "d", "origin_measure": "M-099"}
    assert ("artefacts/0/origin_measure", "Measure M-099 existiert nicht") in messages(
        make_engagement(artefacts=[art])
    )


def test_valid_references_pass() -> None:
    gate = {"id": "G0", "title": "t", "checks": [check("G0-01", ["A-001"])]}
    data = make_engagement(
        atoms=[atom("A-001")],
        gates=[gate],
        measures=[measure("M-001", atom_refs=["A-001"], product_decision_ref="A-001")],
        artefacts=[{"id": "X-001", "description": "d", "origin_measure": "M-001"}],
    )
    assert validate_data(data) == []


def test_load_json_invalid_reports_position(tmp_path: Path) -> None:
    f = tmp_path / "bad.json"
    f.write_text('{\n  "a": ,\n}', encoding="utf-8")
    with pytest.raises(AdoptionkitError, match=r"Zeile 2"):
        load_json(f)


def test_load_engagement_invalid_raises(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text(json.dumps(make_engagement(atoms=[atom("A-001"), atom("A-001")])))
    with pytest.raises(AdoptionkitError, match="doppelte ID A-001"):
        load_engagement(f)


def test_roundtrip(tmp_path: Path) -> None:
    f = tmp_path / "e.json"
    f.write_text(json.dumps(make_engagement(atoms=[atom("A-001")])), encoding="utf-8")
    eng = load_engagement(f)
    out = tmp_path / "out.json"
    save_engagement(eng, out)
    assert out.read_text(encoding="utf-8").endswith("}\n")
    assert load_engagement(out) == eng
    save_engagement(load_engagement(out), tmp_path / "out2.json")
    assert out.read_text(encoding="utf-8") == (tmp_path / "out2.json").read_text(encoding="utf-8")
