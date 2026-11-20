"""Structural checks for the ai-rollout skill (no effectiveness test in Stage 0)."""

from pathlib import Path

import yaml

from adoptionkit.models import DISCLAIMER

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "ai-rollout"
SKILL = SKILL_DIR / "SKILL.md"


def _frontmatter() -> dict:
    parts = SKILL.read_text(encoding="utf-8").split("---\n")
    assert parts[0] == "", "SKILL.md must start with a frontmatter block"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict)
    return data


def test_frontmatter_name() -> None:
    assert _frontmatter()["name"] == "ai-rollout"


def test_description_present_and_short() -> None:
    desc = _frontmatter()["description"]
    assert isinstance(desc, str) and desc.strip()
    assert len(desc) <= 1024


def test_no_sharp_s() -> None:
    for path in [SKILL, *SKILL_DIR.glob("references/*.md")]:
        assert "ß" not in path.read_text(encoding="utf-8"), path


def test_disclaimer_and_v0_marker() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert DISCLAIMER in text
    assert "v0 – Wirksamkeitstest folgt in Stufe 3" in text


def test_references_exist() -> None:
    assert (SKILL_DIR / "references" / "atom-format.md").is_file()
