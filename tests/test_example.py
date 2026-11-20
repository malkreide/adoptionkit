"""The synthetic example case stays valid, lint-stable and gate-consistent."""

from __future__ import annotations

from pathlib import Path

import pytest

from adoptionkit.gates import evaluate_gate
from adoptionkit.io import load_engagement, load_json, validate_data
from adoptionkit.lints import lint
from adoptionkit.models import Engagement
from adoptionkit.profiles import load_profile

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-municipality"
ENGAGEMENT = EXAMPLE / "engagement.json"
NOTICE = "SYNTHETISCH – erfundene Daten zu Demonstrationszwecken."


def test_example_validates() -> None:
    assert validate_data(load_json(ENGAGEMENT)) == []


def test_example_lint_yields_exactly_l002_and_l003() -> None:
    findings = lint(load_engagement(ENGAGEMENT), load_profile("generic"))
    assert [f.code for f in findings] == ["L002", "L003"]
    assert all(f.severity == "warning" for f in findings)


def test_example_g0_evaluates_guided_rollout() -> None:
    ev = evaluate_gate(load_engagement(ENGAGEMENT), load_profile("generic"), "G0")
    assert ev.result == "passed"
    assert ev.recommendation == "guided_rollout"


def test_example_stores_g0_result() -> None:
    gate = load_engagement(ENGAGEMENT).gate("G0")
    assert gate is not None
    assert gate.result == "passed"
    assert gate.recommendation == "guided_rollout"


def test_example_is_marked_synthetic() -> None:
    eng = load_engagement(ENGAGEMENT)
    assert eng.meta.synthetic is True
    assert eng.meta.id == "seewil-askdesk"


def test_evidence_files_start_with_notice() -> None:
    files = sorted((EXAMPLE / "evidence").glob("*.md"))
    assert 4 <= len(files) <= 6
    for f in files:
        assert f.read_text(encoding="utf-8").startswith(NOTICE), f.name


def test_atom_source_refs_exist() -> None:
    eng = load_engagement(ENGAGEMENT)
    refs = [a.source.ref for a in eng.atoms if a.source.ref and a.source.ref.startswith("evidence/")]
    assert refs
    for ref in refs:
        assert (EXAMPLE / ref).is_file(), ref


@pytest.mark.parametrize("name", ["README.md"])
def test_readme_exists(name: str) -> None:
    assert (EXAMPLE / name).is_file()


def test_example_l007_with_unclear_answers_despite_stored_passed() -> None:
    data = load_json(ENGAGEMENT)
    for gate in data["gates"]:
        if gate["id"] == "G0":
            for c in gate["checks"]:
                c["answer"] = "unclear"
            assert gate["result"] == "passed"
    eng = Engagement.model_validate(data)
    findings = [f for f in lint(eng, load_profile(eng.meta.profile)) if f.code == "L007"]
    assert [f.gate_id for f in findings] == ["G0"]
