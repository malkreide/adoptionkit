"""Pydantic models for the adoptionkit engagement file (schema version 0.1)."""

from __future__ import annotations

import datetime as dt
from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.1"
DisclaimerText = Literal[
    "Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären."
]
# Single source of truth: the Literal above (fixed in the JSON schema); the constant derives from it.
DISCLAIMER: DisclaimerText = get_args(DisclaimerText)[0]
PHASE_ORDER = ("discovery", "prototype", "value_proof", "hardening", "handover")

AtomType = Literal["requirement", "constraint", "data_source", "risk", "usage_signal", "decision"]
SourceKind = Literal["interview", "document", "system", "analytics", "regulation", "workshop"]
AtomStatus = Literal["evidenced", "assumed", "refuted"]
PhaseId = Literal["discovery", "prototype", "value_proof", "hardening", "handover"]
PhaseStatus = Literal["planned", "running", "done", "aborted"]
Answer = Literal["yes", "no", "unclear", "n/a"]
GateId = Literal["G0", "G1", "G2", "G3", "G4"]
GateResult = Literal["passed", "open", "stopped"]
Recommendation = Literal["guided_rollout", "standard_rollout", "decline"]
ChangeType = Literal["configuration", "template", "new_development"]
MeasureStatus = Literal["proposed", "accepted", "implemented", "rejected"]
Fate = Literal["open", "generalised", "dropped"]
HostingModel = Literal["saas", "private_cloud", "on_premise", "hybrid", "unknown"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Meta(_Base):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str
    created: dt.date
    updated: dt.date
    schema_version: Literal["0.1"]
    profile: str
    synthetic: bool = False


class Parties(_Base):
    client: str
    contractor: str
    conflict_of_interest: str | None = None


class Solution(_Base):
    name: str
    vendor: str
    hosting_model: HostingModel = "unknown"
    data_location: str = ""
    config_limits: list[str] = Field(default_factory=list)


class Source(_Base):
    kind: SourceKind
    ref: str | None = None
    date: dt.date | None = None
    quote: str | None = None


class Atom(_Base):
    id: str = Field(pattern=r"^A-\d{3}$")
    type: AtomType
    statement: str = Field(min_length=1)
    source: Source
    status: AtomStatus


class Phase(_Base):
    id: PhaseId
    budget_days: int = Field(ge=0)
    start: dt.date | None = None
    end: dt.date | None = None
    status: PhaseStatus = "planned"
    abort_criterion: str | None = None


class Check(_Base):
    id: str = Field(pattern=r"^G[0-4]-\d{2}$")
    question: str
    answer: Answer = "unclear"
    atom_refs: list[str] = Field(default_factory=list)
    source_ref: str


class Gate(_Base):
    id: GateId
    title: str
    checks: list[Check] = Field(default_factory=list)
    result: GateResult | None = None
    recommendation: Recommendation | None = None
    evaluated_on: dt.date | None = None
    disclaimer: DisclaimerText = DISCLAIMER


class Measure(_Base):
    id: str = Field(pattern=r"^M-\d{3}$")
    description: str
    change_type: ChangeType
    status: MeasureStatus = "proposed"
    atom_refs: list[str] = Field(default_factory=list)
    product_decision_ref: str | None = None


class EvalRun(_Base):
    id: str = Field(pattern=r"^R-\d{3}$")
    date: dt.date
    metric: str
    value: float


class Evals(_Base):
    eval_set_ref: str | None = None
    thresholds: dict[str, float] = Field(default_factory=dict)
    runs: list[EvalRun] = Field(default_factory=list)


class Artefact(_Base):
    id: str = Field(pattern=r"^X-\d{3}$")
    description: str
    origin_measure: str
    fate: Fate = "open"
    reviewed_on: dt.date | None = None


class Handover(_Base):
    operators: list[str] = Field(default_factory=list)
    training_done: bool = False
    runbook_ref: str | None = None


class Engagement(_Base):
    meta: Meta
    parties: Parties
    solution: Solution
    atoms: list[Atom] = Field(default_factory=list)
    phases: list[Phase] = Field(default_factory=list)
    gates: list[Gate] = Field(default_factory=list)
    measures: list[Measure] = Field(default_factory=list)
    evals: Evals = Field(default_factory=Evals)
    artefacts: list[Artefact] = Field(default_factory=list)
    handover: Handover = Field(default_factory=Handover)

    def atom(self, id: str) -> Atom | None:
        return next((a for a in self.atoms if a.id == id), None)

    def phase(self, id: str) -> Phase | None:
        return next((p for p in self.phases if p.id == id), None)

    def gate(self, id: str) -> Gate | None:
        return next((g for g in self.gates if g.id == id), None)

    def measure(self, id: str) -> Measure | None:
        return next((m for m in self.measures if m.id == id), None)
