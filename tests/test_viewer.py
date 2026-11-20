"""Tests for the single-file HTML viewer (synthetic data only)."""

from __future__ import annotations

import json
import re
from importlib import resources
from pathlib import Path
from typing import Any

from conftest import make_engagement
from typer.testing import CliRunner

from adoptionkit.cli import app
from adoptionkit.models import Engagement
from adoptionkit.viewer import PLACEHOLDER, render_html

runner = CliRunner()


def _template() -> str:
    return resources.files("adoptionkit").joinpath("templates/viewer.html").read_text("utf-8")


def _eng(**overrides: Any) -> Engagement:
    return Engagement.model_validate(make_engagement(**overrides))


def _atom(statement: str) -> dict[str, Any]:
    return {
        "id": "A-001",
        "type": "risk",
        "statement": statement,
        "source": {"kind": "interview"},
        "status": "assumed",
    }


def _data_block(html: str) -> str:
    m = re.search(r'<script type="application/json" id="engagement-data">(.*?)</script>', html, re.S)
    assert m is not None
    return m.group(1)


def test_placeholder_once_in_template() -> None:
    assert _template().count(PLACEHOLDER) == 1
    assert PLACEHOLDER == "/*__ENGAGEMENT_JSON__*/null"


def test_template_has_no_external_or_unsafe_constructs() -> None:
    t = _template()
    for forbidden in ("http", "<script src", "<link", "@import", "url(", "innerHTML", "eval("):
        assert forbidden not in t
    assert 'lang="de-CH"' in t


def test_render_has_no_placeholder_or_external() -> None:
    html = render_html(_eng())
    assert PLACEHOLDER not in html
    assert "<script src" not in html
    assert "<link" not in html


def test_script_breakout_is_escaped() -> None:
    evil = "x</script><script>alert(1)</script><!-- y \u2028 z \u2029"
    html = render_html(_eng(atoms=[_atom(evil)]))
    block = _data_block(html)
    assert "</" not in block
    assert "<!--" not in block
    assert "\u2028" not in html and "\u2029" not in html
    assert html.count("</script>") == _template().count("</script>")
    data = json.loads(block)
    assert data["atoms"][0]["statement"] == evil


def test_title_is_escaped() -> None:
    html = render_html(_eng(meta={**make_engagement()["meta"], "title": "<b>&\"x\""}))
    assert "<title>&lt;b&gt;&amp;&quot;x&quot;</title>" in html


def test_cli_view_writes_file(tmp_path: Path) -> None:
    src = tmp_path / "engagement.json"
    src.write_text(json.dumps(make_engagement()), encoding="utf-8")
    out = tmp_path / "dossier.html"
    result = runner.invoke(app, ["view", str(src), "-o", str(out)])
    assert result.exit_code == 0
    assert str(out) in result.output
    assert "<html" in out.read_text(encoding="utf-8")


def test_cli_view_invalid_file(tmp_path: Path) -> None:
    src = tmp_path / "bad.json"
    src.write_text("{}", encoding="utf-8")
    result = runner.invoke(app, ["view", str(src), "-o", str(tmp_path / "o.html")])
    assert result.exit_code == 1
    assert not (tmp_path / "o.html").exists()


def test_cli_view_unwritable_output(tmp_path: Path) -> None:
    src = tmp_path / "engagement.json"
    src.write_text(json.dumps(make_engagement()), encoding="utf-8")
    result = runner.invoke(app, ["view", str(src), "-o", str(tmp_path / "no" / "dir" / "o.html")])
    assert result.exit_code == 1
