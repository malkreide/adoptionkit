"""Gate evaluation (pure) and application to an engagement (deterministic, offline)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from adoptionkit.errors import AdoptionkitError
from adoptionkit.lints import Finding, lint
from adoptionkit.models import DISCLAIMER, Check, Engagement, GateId, GateResult, Recommendation
from adoptionkit.profiles import Profile, gate_from_profile


@dataclass
class GateEvaluation:
    gate_id: GateId
    result: GateResult
    recommendation: Recommendation | None
    reasons: list[str] = field(default_factory=list)


class GateBlocked(AdoptionkitError):
    """Raised when lint errors prevent a gate evaluation."""

    def __init__(self, findings: list[Finding]) -> None:
        super().__init__(f"Gate blockiert durch {len(findings)} Lint-Fehler.")
        self.findings = findings


def _evidenced(eng: Engagement, check: Check) -> bool:
    for ref in check.atom_refs:
        atom = eng.atom(ref)
        if atom is not None and atom.status == "evidenced":
            return True
    return False


def evaluate_gate(eng: Engagement, profile: Profile, gate_id: GateId) -> GateEvaluation:
    gdef = profile.gates.get(gate_id)
    if gdef is None:
        raise AdoptionkitError(f"Gate {gate_id} ist im Profil «{profile.name}» nicht definiert.")
    gate = eng.gate(gate_id)
    existing = {c.id: c for c in gate.checks} if gate is not None else {}

    open_reasons: list[str] = []
    stop_reasons: list[str] = []
    guided = False
    for cdef in gdef.checks:
        check = existing.get(cdef.id)
        if check is None:
            open_reasons.append(f"{cdef.id}: nicht beantwortet")
            continue
        if check.answer == "unclear":
            open_reasons.append(f"{cdef.id}: unklar")
            continue
        if check.answer == "n/a":
            continue
        if not _evidenced(eng, check):
            open_reasons.append(f"{cdef.id}: nicht belegt")
            continue
        if cdef.stop_if == check.answer:
            stop_reasons.append(f"{cdef.id}: Abbruchbedingung erfüllt")
        if cdef.guided_if == check.answer:
            guided = True

    result: GateResult
    recommendation: Recommendation | None = None
    if stop_reasons:
        result, reasons = "stopped", stop_reasons
        if gate_id == "G0":
            recommendation = "decline"
    elif open_reasons:
        result, reasons = "open", open_reasons
    else:
        result, reasons = "passed", []
        if gate_id == "G0":
            recommendation = "guided_rollout" if guided else "standard_rollout"
    return GateEvaluation(gate_id, result, recommendation, reasons)


def run_gate(
    eng: Engagement, profile: Profile, gate_id: GateId, today: date
) -> tuple[Engagement, GateEvaluation]:
    evaluation = evaluate_gate(eng, profile, gate_id)  # R1 before lint
    own = f"Gate {gate_id} "
    errors = [
        f
        for f in lint(eng, profile, today)
        if f.severity == "error" and not (f.code == "L007" and own in f.message)
    ]
    if errors:
        raise GateBlocked(errors)

    new = eng.model_copy(deep=True)
    template = gate_from_profile(profile, gate_id)
    gate = new.gate(gate_id)
    if gate is None:
        gate = template
        new.gates.append(gate)
    else:
        gate.title = template.title
    existing = {c.id: c for c in gate.checks}
    gate.checks = []
    for tcheck in template.checks:
        check = existing.get(tcheck.id, tcheck)
        check.question = tcheck.question
        check.source_ref = tcheck.source_ref
        gate.checks.append(check)
    gate.checks.extend(c for c in existing.values() if c.id not in {t.id for t in template.checks})
    gate.result = evaluation.result
    gate.recommendation = evaluation.recommendation
    gate.evaluated_on = today
    gate.disclaimer = DISCLAIMER
    new.meta.updated = today
    return new, evaluation
