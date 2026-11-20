"""Tests for lints L001-L005 (synthetic data only)."""

from __future__ import annotations

from typing import Any

from conftest import make_engagement

from adoptionkit.lints import RULES, Finding, lint
from adoptionkit.models import Engagement
from adoptionkit.profiles import load_profile


def atom(
    id_: str, type_: str = "requirement", status: str = "evidenced", ref: Any = "doc-1"
) -> dict[str, Any]:
    source: dict[str, Any] = {"kind": "document"}
    if ref is not None:
        source["ref"] = ref
    return {"id": id_, "type": type_, "statement": "s", "source": source, "status": status}


def measure(id_: str, **kw: Any) -> dict[str, Any]:
    m: dict[str, Any] = {
        "id": id_,
        "description": "d",
        "change_type": "configuration",
        "atom_refs": ["A-001"],
    }
    m.update(kw)
    return m


def eng(**kw: Any) -> Engagement:
    return Engagement.model_validate(make_engagement(**kw))


def codes(findings: list[Finding], code: str) -> list[Finding]:
    return [f for f in findings if f.code == code]


def test_rules_table() -> None:
    assert set(RULES) == {"L001", "L002", "L003", "L004", "L005", "L007"}
    assert RULES["L001"][0] == "error"
    assert RULES["L002"][0] == "warning"


def test_finding_to_dict() -> None:
    f = Finding("L001", "error", "atoms/A-001", "m")
    assert f.to_dict() == {
        "code": "L001",
        "severity": "error",
        "path": "atoms/A-001",
        "message": "m",
    }


def test_clean_engagement_has_no_findings() -> None:
    e = eng(atoms=[atom("A-001")], measures=[measure("M-001")])
    assert lint(e) == []


# L001
def test_l001_missing_ref() -> None:
    f = codes(lint(eng(atoms=[atom("A-001", ref=None)])), "L001")
    assert [(x.severity, x.path) for x in f] == [("error", "atoms/A-001")]


def test_l001_blank_ref() -> None:
    assert len(codes(lint(eng(atoms=[atom("A-001", ref="   ")])), "L001")) == 1


def test_l001_not_triggered_with_ref() -> None:
    assert codes(lint(eng(atoms=[atom("A-001")])), "L001") == []


# L002
def test_l002_assumed_requirement() -> None:
    e = eng(atoms=[atom("A-001", status="assumed")], measures=[measure("M-001")])
    f = codes(lint(e), "L002")
    assert [(x.severity, x.path) for x in f] == [("warning", "measures/M-001")]
    assert "A-001" in f[0].message


def test_l002_one_finding_per_atom() -> None:
    e = eng(
        atoms=[atom("A-001", status="assumed"), atom("A-002", status="assumed")],
        measures=[measure("M-001", atom_refs=["A-001", "A-002"])],
    )
    assert len(codes(lint(e), "L002")) == 2


def test_l002_not_triggered_for_evidenced_or_other_type() -> None:
    e = eng(
        atoms=[atom("A-001"), atom("A-002", type_="risk", status="assumed")],
        measures=[measure("M-001", atom_refs=["A-001", "A-002"])],
    )
    assert codes(lint(e), "L002") == []


# L003
def test_l003_measure_without_atoms() -> None:
    e = eng(measures=[measure("M-001", atom_refs=[])])
    f = codes(lint(e), "L003")
    assert [(x.severity, x.path) for x in f] == [("warning", "measures/M-001")]


def test_l003_not_triggered_with_atoms() -> None:
    e = eng(atoms=[atom("A-001")], measures=[measure("M-001")])
    assert codes(lint(e), "L003") == []


# L004
def test_l004_new_development_without_decision() -> None:
    e = eng(atoms=[atom("A-001")], measures=[measure("M-001", change_type="new_development")])
    f = codes(lint(e), "L004")
    assert [(x.severity, x.path) for x in f] == [("error", "measures/M-001")]


def test_l004_decision_ref_wrong_type() -> None:
    e = eng(
        atoms=[atom("A-001")],
        measures=[measure("M-001", change_type="new_development", product_decision_ref="A-001")],
    )
    assert len(codes(lint(e), "L004")) == 1


def test_l004_not_triggered_with_decision_atom() -> None:
    e = eng(
        atoms=[atom("A-001"), atom("A-002", type_="decision")],
        measures=[measure("M-001", change_type="new_development", product_decision_ref="A-002")],
    )
    assert codes(lint(e), "L004") == []


def test_l004_not_triggered_for_configuration() -> None:
    e = eng(atoms=[atom("A-001")], measures=[measure("M-001")])
    assert codes(lint(e), "L004") == []


# L005
def _phase(id_: str, **kw: Any) -> dict[str, Any]:
    p: dict[str, Any] = {"id": id_, "budget_days": 5}
    p.update(kw)
    return p


def test_l005_missing_abort_criterion() -> None:
    e = eng(phases=[_phase("discovery"), _phase("prototype")])
    f = codes(lint(e), "L005")
    assert [(x.severity, x.path) for x in f] == [("error", "phases/prototype")]


def test_l005_blank_abort_criterion() -> None:
    e = eng(phases=[_phase("hardening", abort_criterion="  ")])
    assert len(codes(lint(e), "L005")) == 1


def test_l005_not_triggered_for_discovery_or_with_criterion() -> None:
    e = eng(phases=[_phase("discovery"), _phase("prototype", abort_criterion="stop if X")])
    assert codes(lint(e), "L005") == []


def test_findings_sorted_by_code_then_path() -> None:
    e = eng(
        atoms=[atom("A-002", ref=None), atom("A-001", ref=None)],
        measures=[measure("M-001", atom_refs=[])],
    )
    result = lint(e)
    assert [(f.code, f.path) for f in result] == sorted((f.code, f.path) for f in result)


# --- L007: Gate-Pflicht vor/zum Abschluss einer Phase ---


def _ph(id_: str, status: str) -> dict[str, Any]:
    return {"id": id_, "budget_days": 1, "status": status, "abort_criterion": "stop"}


def _gt(id_: str, result: str | None) -> dict[str, Any]:
    g: dict[str, Any] = {"id": id_, "title": "t", "checks": []}
    if result is not None:
        g["result"] = result
    return g


def test_l007_running_phase_without_gate() -> None:
    e = eng(phases=[_ph("discovery", "running")])
    f = codes(lint(e, load_profile("generic")), "L007")
    assert len(f) == 1
    assert f[0].severity == "error"
    assert f[0].path == "phases/discovery"
    assert "G0" in f[0].message


def test_l007_done_phase_with_open_gate() -> None:
    e = eng(phases=[_ph("discovery", "done")], gates=[_gt("G0", "open")])
    assert len(codes(lint(e, load_profile("generic")), "L007")) == 1


def test_l007_passed_gate_ok() -> None:
    e = eng(phases=[_ph("discovery", "running")], gates=[_gt("G0", "passed")])
    assert codes(lint(e, load_profile("generic")), "L007") == []


def test_l007_planned_phase_ok() -> None:
    e = eng(phases=[_ph("discovery", "planned")])
    assert codes(lint(e, load_profile("generic")), "L007") == []


def test_l007_aborted_phase_ok() -> None:
    e = eng(phases=[_ph("discovery", "aborted")])
    assert codes(lint(e, load_profile("generic")), "L007") == []


def test_l007_required_to_complete() -> None:
    p = load_profile("generic")
    running = eng(phases=[_ph("handover", "running")])
    assert codes(lint(running, p), "L007") == []
    done = eng(phases=[_ph("handover", "done")])
    f = codes(lint(done, p), "L007")
    assert len(f) == 1 and "G4" in f[0].message and f[0].path == "phases/handover"
    ok = eng(phases=[_ph("handover", "done")], gates=[_gt("G4", "passed")])
    assert codes(lint(ok, p), "L007") == []


def test_l007_without_profile_not_checked() -> None:
    e = eng(phases=[_ph("discovery", "running")])
    assert codes(lint(e), "L007") == []
