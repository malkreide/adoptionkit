"""Repository rules: spelling, vocabulary, no network imports, licence holder."""

import ast
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".json", ".html", ".toml", ".yml"}
SHARP_S = chr(0xDF)


def _tracked_files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git ist nicht verfügbar")
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


NETWORK_MODULES = {
    "socket", "ssl", "urllib", "http", "requests", "httpx", "ftplib", "smtplib", "telnetlib",
    "xmlrpc",
}


def _network_offences(source: str) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name.split(".")[0] in NETWORK_MODULES]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and (node.module or "").split(".")[0] in NETWORK_MODULES:
                found.append(node.module or "")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "__import__"
        ):
            found.append("__import__")
    return found


def test_network_check_detects_offences() -> None:
    assert _network_offences("import os, socket") == ["socket"]
    assert _network_offences("from urllib.request import urlopen") == ["urllib.request"]
    assert _network_offences("def f():" + chr(10) + "    import requests as r") == ["requests"]
    assert _network_offences("__import__('http.client')") == ["__import__"]
    assert _network_offences("from . import http" + chr(10) + "import json") == []


def test_no_network_imports_in_src() -> None:
    offenders = {}
    for path in (ROOT / "src").rglob("*.py"):
        found = _network_offences(path.read_text(encoding="utf-8"))
        if found:
            offenders[_rel(path)] = found
    assert offenders == {}


def test_license_names_holder() -> None:
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Hayal Özkan" in text
