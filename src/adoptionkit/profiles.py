"""Profiles: checklists per gate, loaded from YAML (offline)."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from adoptionkit.errors import AdoptionkitError
from adoptionkit.models import DISCLAIMER, Check, Gate, GateId, PhaseId


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CheckDef(_Base):
    id: str
    question: str
    source_ref: str
    stop_if: Literal["yes", "no"] | None = None
    guided_if: Literal["yes", "no"] | None = None


class GateDef(_Base):
    title: str
    required_before: PhaseId | None = None
    required_to_complete: PhaseId | None = None
    checks: list[CheckDef]


class Profile(_Base):
    name: str
    version: int
    title: str
    disclaimer: str
    gates: dict[GateId, GateDef]

    @field_validator("disclaimer")
    @classmethod
    def _disclaimer_exact(cls, v: str) -> str:
        if v != DISCLAIMER:
            raise ValueError("muss exakt dem vorgeschriebenen Hinweis entsprechen")
        return v


def _available() -> list[str]:
    root = resources.files("adoptionkit") / "profiles"
    return sorted(Path(str(p.name)).stem for p in root.iterdir() if p.name.endswith(".yaml"))


def _parse(text: str, origin: str) -> Profile:
    try:
        return Profile.model_validate(yaml.safe_load(text))
    except (yaml.YAMLError, ValidationError) as exc:
        raise AdoptionkitError(f"Profil {origin} ungültig: {exc}") from exc


def load_profile(name_or_path: str) -> Profile:
    path = Path(name_or_path)
    if path.is_file():
        try:
            return _parse(path.read_text(encoding="utf-8"), str(path))
        except (OSError, UnicodeDecodeError) as exc:
            raise AdoptionkitError(f"Profil {path} nicht lesbar: {exc}") from exc
    resource = resources.files("adoptionkit") / "profiles" / f"{name_or_path}.yaml"
    if resource.is_file():
        return _parse(resource.read_text(encoding="utf-8"), name_or_path)
    raise AdoptionkitError(
        f"Profil «{name_or_path}» nicht gefunden. Verfügbar: {', '.join(_available())}"
    )


def gate_from_profile(profile: Profile, gate_id: GateId) -> Gate:
    gdef = profile.gates[gate_id]
    return Gate(
        id=gate_id,
        title=gdef.title,
        checks=[
            Check(id=c.id, question=c.question, answer="unclear", source_ref=c.source_ref)
            for c in gdef.checks
        ],
    )
