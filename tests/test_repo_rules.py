"""Repository rules: spelling, vocabulary, no network imports, licence holder."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".json", ".html", ".toml", ".yml"}
SHARP_S = "ß"


def _tracked_files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git ist nicht verfuegbar")
    return [ROOT / line for line in out.splitlines() if line]


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _text_files() -> list[Path]:
    return [p for p in _tracked_files() if p.suffix in TEXT_SUFFIXES and p.is_file()]


def test_no_sharp_s_in_tracked_text_files() -> None:
    offenders = []
    for path in _text_files():
        rel = _rel(path)
        if rel == "docs/BAUPLAN.md" or rel.startswith("docs/plans/"):
            continue
        if SHARP_S in path.read_text(encoding="utf-8"):
            offenders.append(rel)
    assert offenders == []


def test_role_title_only_in_sources_and_bauplan() -> None:
    pattern = re.compile("for" + "ward[ -]" + "de" + "ployed[ -]" + "eng" + "ineer", re.IGNORECASE)
    allowed = {"docs/SOURCES.md", "docs/BAUPLAN.md"}
    offenders = []
    for path in _tracked_files():
        rel = _rel(path)
        if rel in allowed or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if pattern.search(text):
            offenders.append(rel)
    assert offenders == []


def test_no_network_imports_in_src() -> None:
    pattern = re.compile(
        r"^\s*(?:import|from)\s+(socket|urllib|http|requests|httpx)\b", re.MULTILINE
    )
    offenders = []
    for path in (ROOT / "src").rglob("*.py"):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(_rel(path))
    assert offenders == []


def test_license_names_holder() -> None:
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Hayal Özkan" in text
