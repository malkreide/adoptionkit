"""Tests for profile loading (synthetic data only)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from adoptionkit.errors import AdoptionkitError
from adoptionkit.models import DISCLAIMER
from adoptionkit.profiles import gate_from_profile, load_profile, load_profile_file

SOURCES = Path(__file__).parents[1] / "docs" / "SOURCES.md"


def test_generic_loads() -> None:
    p = load_profile("generic")
    assert p.name == "generic"
    assert p.version == 1
    assert set(p.gates) == {"G0", "G3", "G4"}
    assert p.gates["G0"].required_before == "discovery"
    assert p.gates["G4"].required_to_complete == "handover"
    assert [c.id for c in p.gates["G0"].checks] == [f"G0-0{i}" for i in range(1, 6)]
    assert p.disclaimer == DISCLAIMER


def test_unknown_profile_lists_available() -> None:
    with pytest.raises(AdoptionkitError, match="generic"):
        load_profile("does-not-exist")


def test_disclaimer_required(tmp_path: Path) -> None:
    raw = yaml.safe_load(
        (Path(__file__).parents[1] / "src/adoptionkit/profiles/generic.yaml").read_text("utf-8")
    )
    raw["disclaimer"] = "anders"
    f = tmp_path / "bad.yaml"
    f.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AdoptionkitError, match="disclaimer"):
        load_profile_file(f)


def test_every_source_ref_exists_in_sources() -> None:
    ids = set(re.findall(r"^\|\s*([SU]\d{2})\s*\|", SOURCES.read_text("utf-8"), re.M))
    assert len(ids) == 12
    p = load_profile("generic")
    for gate in p.gates.values():
        for c in gate.checks:
            assert c.source_ref in ids, c.id


def test_no_sharp_s_in_questions() -> None:
    p = load_profile("generic")
    for gate in p.gates.values():
        assert chr(0xDF) not in gate.title
        for c in gate.checks:
            assert chr(0xDF) not in c.question


def test_gate_from_profile() -> None:
    p = load_profile("generic")
    g = gate_from_profile(p, "G0")
    assert g.id == "G0"
    assert g.title == "Eignung"
    assert len(g.checks) == 5
    assert all(c.answer == "unclear" and c.atom_refs == [] for c in g.checks)
    assert g.result is None and g.recommendation is None and g.evaluated_on is None
    assert g.disclaimer == DISCLAIMER


@pytest.mark.parametrize("name", ["../x.yaml", r"\\server\share\p.yaml", "Generic", "a/b", ""])
def test_load_profile_bundled_only_rejects_paths(name: str) -> None:
    with pytest.raises(AdoptionkitError):
        load_profile(name)


def test_load_profile_does_not_touch_existing_file(tmp_path: Path) -> None:
    f = tmp_path / "generic.yaml"
    f.write_text("name: evil", encoding="utf-8")
    with pytest.raises(AdoptionkitError):
        load_profile(str(f))


def test_load_profile_file_explicit(tmp_path: Path) -> None:
    from adoptionkit.profiles import load_profile_file

    raw = (Path(__file__).parents[1] / "src/adoptionkit/profiles/generic.yaml").read_text("utf-8")
    f = tmp_path / "p.yaml"
    f.write_text(raw.replace("name: generic", "name: custom"), encoding="utf-8")
    assert load_profile_file(f).name == "custom"
    with pytest.raises(AdoptionkitError):
        load_profile_file(tmp_path / "missing.yaml")
