"""Shared test helpers (synthetic data only)."""

from __future__ import annotations

from typing import Any

import pytest


def make_engagement(**overrides: Any) -> dict[str, Any]:
    """Return a minimal valid engagement dict; overrides replace top-level keys."""
    data: dict[str, Any] = {
        "meta": {
            "id": "demo-engagement",
            "title": "Synthetic demo engagement",
            "created": "2026-01-01",
            "updated": "2026-01-02",
            "schema_version": "0.1",
            "profile": "default",
            "synthetic": True,
        },
        "parties": {"client": "Synthetic Client", "contractor": "Synthetic Contractor"},
        "solution": {"name": "Synthetic Assistant", "vendor": "Synthetic Vendor"},
    }
    data.update(overrides)
    return data


@pytest.fixture
def engagement_dict() -> dict[str, Any]:
    return make_engagement()
