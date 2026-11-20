"""Tests for gate evaluation rules R1-R9 (synthetic data only)."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from conftest import make_engagement

from adoptionkit.errors import AdoptionkitError
from adoptionkit.gates import GateBlocked, evaluate_gate, run_gate
from adoptionkit.models import DISCLAIMER, Engagement
from adoptionkit.profiles import load_profile

PROFILE = load_profile("generic")
G0_IDS = [f"G0-0{i}" for i in range(1, 6)]
TODAY = date(2026, 3, 1)


def atom(id_: str, status: str = "evidenced") -> dict[str, Any]:
    return {
        "id": id_,
        "type": "requirement",
        "statement": "s",
        "source": {"kind": "document", "ref": "doc-1"},
        "status": status,
    }


def check(id_: str, answer: str, refs: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": id_,
        "question": "q",
        "answer": answer,
        "atom_refs": refs if refs is not None else [],
        "source_ref": "S03",
    }


def eng(
    checks: list[dict[str, Any]], atoms: list[dict[str, Any]] | None = None, **kw: Any
) -> Engagement:
    gates = [{"id": "G0", "title": "Eignung", "checks": checks}]
    base = make_engagement(atoms=atoms if atoms is not None else [atom("A-001")], gates=gates)
    base.update(kw)
    return Engagement.model_validate(base)


def all_yes_but(overrides: dict[str, str]) -> list[dict[str, Any]]:
    """All G0 checks answered with evidence; `overrides` change answers."""
    good = {"G0-01": "yes", "G0-02": "yes", "G0-03": "yes", "G0-04": "yes", "G0-05": "yes"}
    good.update(overrides)
    return [check(i, a, ["A-001"]) for i, a in good.items()]


def test_r1_unknown_gate() -> None:
    with pytest.raises(AdoptionkitError, match="G1"):
        evaluate_gate(eng([]), PROFILE, "G1")


def test_r2_missing_check_counts_as_unclear() -> None:
    ev = evaluate_gate(eng([]), PROFILE, "G0")
    assert ev.result == "open"
    assert "G0-01: nicht beantwortet" in ev.reasons
    assert len([r for r in ev.reasons if r.endswith("nicht beantwortet")]) == 5


def test_r2_missing_gate_entirely() -> None:
    e = Engagement.model_validate(make_engagement())
    ev = evaluate_gate(e, PROFILE, "G0")
    assert ev.result == "open"
    assert "G0-03: nicht beantwortet" in ev.reasons


def test_r3_unclear_is_open() -> None:
    cs = all_yes_but({})
    cs[4] = check("G0-05", "unclear")
    ev = evaluate_gate(eng(cs), PROFILE, "G0")
    assert ev.result == "open"
    assert ev.reasons == ["G0-05: unklar"]


def test_r4_yes_without_atom_refs_is_open() -> None:
    cs = all_yes_but({})
    cs[0] = check("G0-01", "yes", [])
    ev = evaluate_gate(eng(cs), PROFILE, "G0")
    assert ev.result == "open"
    assert ev.reasons == ["G0-01: nicht belegt"]


@pytest.mark.parametrize("status", ["assumed", "refuted"])
def test_r4_non_evidenced_atom_does_not_count(status: str) -> None:
    cs = all_yes_but({})
    cs[1] = check("G0-02", "yes", ["A-002"])
    e = eng(cs, atoms=[atom("A-001"), atom("A-002", status)])
    ev = evaluate_gate(e, PROFILE, "G0")
    assert ev.result == "open"
    assert ev.reasons == ["G0-02: nicht belegt"]


def test_r4_dangling_ref_does_not_count() -> None:
    cs = all_yes_but({})
    cs[1] = check("G0-02", "no", ["A-099"])
    ev = evaluate_gate(eng(cs), PROFILE, "G0")
    assert ev.result == "open"
    assert ev.reasons == ["G0-02: nicht belegt"]


def test_r4_one_evidenced_among_others_suffices() -> None:
    cs = all_yes_but({})
    cs[1] = check("G0-02", "yes", ["A-002", "A-001"])
    e = eng(cs, atoms=[atom("A-001"), atom("A-002", "assumed")])
    assert evaluate_gate(e, PROFILE, "G0").result == "passed"


def test_r5_na_needs_no_atoms() -> None:
    cs = all_yes_but({})
    cs[0] = check("G0-01", "n/a", [])
    ev = evaluate_gate(eng(cs), PROFILE, "G0")
    assert ev.result == "passed"
    assert ev.reasons == []


def test_r6_stop_if_met_with_evidence() -> None:
    ev = evaluate_gate(eng(all_yes_but({"G0-01": "no"})), PROFILE, "G0")
    assert ev.result == "stopped"
    assert ev.reasons == ["G0-01: Abbruchbedingung erfüllt"]


def test_r6_stopped_beats_open() -> None:
    cs = all_yes_but({"G0-03": "no"})
    cs[4] = check("G0-05", "unclear")
    ev = evaluate_gate(eng(cs), PROFILE, "G0")
    assert ev.result == "stopped"
    assert "G0-03: Abbruchbedingung erfüllt" in ev.reasons


def test_r6_stop_without_evidence_is_only_open() -> None:
    cs = all_yes_but({})
    cs[0] = check("G0-01", "no", [])
    ev = evaluate_gate(eng(cs), PROFILE, "G0")
    assert ev.result == "open"
    assert ev.recommendation is None


def test_r6_guided_condition_is_no_stop() -> None:
    ev = evaluate_gate(eng(all_yes_but({"G0-02": "no"})), PROFILE, "G0")
    assert ev.result == "passed"


def test_r7_passed() -> None:
    ev = evaluate_gate(eng(all_yes_but({})), PROFILE, "G0")
    assert ev.result == "passed"
    assert ev.reasons == []


def test_r8_recommendations() -> None:
    standard = evaluate_gate(eng(all_yes_but({})), PROFILE, "G0")
    assert standard.recommendation == "standard_rollout"
    guided = evaluate_gate(eng(all_yes_but({"G0-05": "no"})), PROFILE, "G0")
    assert guided.recommendation == "guided_rollout"
    declined = evaluate_gate(eng(all_yes_but({"G0-04": "no"})), PROFILE, "G0")
    assert declined.recommendation == "decline"
    opened = evaluate_gate(eng([]), PROFILE, "G0")
    assert opened.recommendation is None


def test_r8_other_gates_have_no_recommendation() -> None:
    cs = [check(f"G3-0{i}", "n/a") for i in range(1, 5)]
    g3 = Engagement.model_validate(
        make_engagement(gates=[{"id": "G3", "title": "Evaluation", "checks": cs}])
    )
    ev = evaluate_gate(g3, PROFILE, "G3")
    assert ev.result == "passed" and ev.recommendation is None


def test_unknown_checks_in_engagement_ignored() -> None:
    cs = all_yes_but({}) + [check("G0-09", "no", ["A-001"])]
    assert evaluate_gate(eng(cs), PROFILE, "G0").result == "passed"


def test_evaluate_does_not_mutate() -> None:
    e = eng(all_yes_but({}))
    before = e.model_dump()
    evaluate_gate(e, PROFILE, "G0")
    assert e.model_dump() == before


# --- run_gate (R9) ---


def test_r9_blocked_by_lint_error() -> None:
    e = Engagement.model_validate(
        make_engagement(
            atoms=[atom("A-001")],
            phases=[{"id": "discovery", "budget_days": 1, "status": "running"}],
        )
    )
    with pytest.raises(GateBlocked) as exc:
        run_gate(e, PROFILE, "G0", TODAY)
    assert [f.code for f in exc.value.findings] == ["L007"]


def test_r9_warnings_do_not_block() -> None:
    e = Engagement.model_validate(
        make_engagement(
            atoms=[atom("A-001")],
            measures=[
                {"id": "M-001", "description": "d", "change_type": "configuration", "atom_refs": []}
            ],
        )
    )
    new, ev = run_gate(e, PROFILE, "G0", TODAY)
    assert ev.result == "open"
    assert new.gate("G0") is not None


def test_run_gate_creates_gate_and_fills_checks() -> None:
    e = Engagement.model_validate(make_engagement())
    new, ev = run_gate(e, PROFILE, "G0", TODAY)
    g = new.gate("G0")
    assert g is not None
    assert g.title == "Eignung"
    assert [c.id for c in g.checks] == G0_IDS
    assert all(c.answer == "unclear" for c in g.checks)
    assert g.result == "open" and g.recommendation is None
    assert g.evaluated_on == TODAY and g.disclaimer == DISCLAIMER
    assert new.meta.updated == TODAY
    assert e.gate("G0") is None  # input untouched
    assert ev.gate_id == "G0"


def test_run_gate_keeps_answers_and_refreshes_text() -> None:
    cs = all_yes_but({"G0-05": "no"})
    cs[0]["question"] = "alt"
    cs[0]["source_ref"] = "S99"
    e = eng(cs)
    new, ev = run_gate(e, PROFILE, "G0", TODAY)
    g = new.gate("G0")
    assert g is not None
    assert g.result == "passed" and g.recommendation == "guided_rollout"
    c1 = next(c for c in g.checks if c.id == "G0-01")
    assert c1.question.startswith("Betrifft das Problem") and c1.source_ref == "S03"
    assert c1.answer == "yes" and c1.atom_refs == ["A-001"]
    assert ev.recommendation == "guided_rollout"
    assert e.meta.updated != TODAY
