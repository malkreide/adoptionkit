import pytest
from conftest import make_engagement
from pydantic import ValidationError

from adoptionkit.models import DISCLAIMER, PHASE_ORDER, Engagement, Gate


def _atom(**kw):
    a = {
        "id": "A-001",
        "type": "requirement",
        "statement": "Synthetic statement",
        "source": {"kind": "interview"},
        "status": "evidenced",
    }
    a.update(kw)
    return a


def test_minimal_engagement_parses():
    e = Engagement.model_validate(make_engagement())
    assert e.meta.id == "demo-engagement"
    assert e.atoms == [] and e.evals.runs == []
    assert e.atom("A-001") is None and e.gate("G0") is None


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        Engagement.model_validate(make_engagement(bogus=1))


def test_wrong_atom_type_rejected():
    with pytest.raises(ValidationError):
        Engagement.model_validate(make_engagement(atoms=[_atom(type="wish")]))


def test_bad_atom_id_rejected():
    with pytest.raises(ValidationError):
        Engagement.model_validate(make_engagement(atoms=[_atom(id="A-1")]))


def test_lookup_helpers():
    e = Engagement.model_validate(make_engagement(atoms=[_atom()]))
    assert e.atom("A-001") is not None


def test_gate_disclaimer_default():
    g = Gate(id="G0", title="t")
    assert g.disclaimer == DISCLAIMER
    assert DISCLAIMER == (
        "Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären."
    )


def test_gate_disclaimer_must_be_exact():
    for bad in ("", "anders", DISCLAIMER + " "):
        with pytest.raises(ValidationError):
            Gate.model_validate({"id": "G0", "title": "t", "disclaimer": bad})


def test_phase_order():
    assert PHASE_ORDER[0] == "discovery" and len(PHASE_ORDER) == 5
