"""Render an engagement as a single self-contained HTML file."""

from __future__ import annotations

import html
import json
from importlib import resources

from adoptionkit.models import DISCLAIMER, Engagement

PLACEHOLDER = "/*__ENGAGEMENT_JSON__*/null"
DISCLAIMER_PLACEHOLDER = "/*__DISCLAIMER_JSON__*/null"


def _template() -> str:
    return resources.files("adoptionkit").joinpath("templates/viewer.html").read_text("utf-8")


def _embed_json(eng: Engagement) -> str:
    text = json.dumps(eng.model_dump(mode="json", exclude_none=True), ensure_ascii=False)
    return (
        text.replace("</", r"<\/")
        .replace("<!--", "<" + chr(92) + "u0021--")
        .replace("\u2028", r"\u2028")
        .replace("\u2029", r"\u2029")
    )


def render_html(eng: Engagement) -> str:
    template = _template()
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("viewer template must contain the placeholder exactly once")
    title = html.escape(eng.meta.title, quote=True)
    head, tail = template.split(PLACEHOLDER)
    head = head.replace("__ENGAGEMENT_TITLE__", title)
    tail = tail.replace("__ENGAGEMENT_TITLE__", title)
    # The disclaimer is always the constant from the code, never the value stored in the file.
    tail = tail.replace(DISCLAIMER_PLACEHOLDER, json.dumps(DISCLAIMER, ensure_ascii=False))
    return head + _embed_json(eng) + tail
