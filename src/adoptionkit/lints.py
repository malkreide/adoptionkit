"""Lint rules L001-L005 for engagement files (deterministic, offline)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Literal

from adoptionkit.models import PHASE_ORDER, Engagement

Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


RULES: dict[str, tuple[Severity, str]] = {
    "L001": ("error", "Atom ohne Quellenverweis (source.ref fehlt oder ist leer)."),
    "L002": ("warning", "Measure stützt sich auf eine Anforderung mit Status «assumed»."),
    "L003": ("warning", "Measure ohne Atom-Verweise."),
    "L004": ("error", "Neuentwicklung ohne Produktentscheid (Atom vom Typ «decision»)."),
    "L005": ("error", "Phase ab «prototype» ohne Abbruchkriterium."),
}


def _finding(code: str, path: str, message: str) -> Finding:
    return Finding(code, RULES[code][0], path, message)


def lint(eng: Engagement, today: date | None = None) -> list[Finding]:
    """Run all rules; return findings sorted by (code, path)."""
    findings: list[Finding] = []

    for a in eng.atoms:
        if not (a.source.ref or "").strip():
            findings.append(
                _finding("L001", f"atoms/{a.id}", f"Atom {a.id} hat keinen Quellenverweis.")
            )

    for m in eng.measures:
        path = f"measures/{m.id}"
        for ref in m.atom_refs:
            atom = eng.atom(ref)
            if atom is not None and atom.type == "requirement" and atom.status == "assumed":
                findings.append(
                    _finding(
                        "L002",
                        path,
                        f"Anforderung {atom.id} ist nur angenommen (assumed), nicht belegt.",
                    )
                )
        if not m.atom_refs:
            findings.append(_finding("L003", path, f"Measure {m.id} verweist auf kein Atom."))
        if m.change_type == "new_development":
            decision = eng.atom(m.product_decision_ref) if m.product_decision_ref else None
            if m.product_decision_ref is None:
                findings.append(
                    _finding("L004", path, f"Neuentwicklung {m.id} ohne Produktentscheid.")
                )
            elif decision is not None and decision.type != "decision":
                findings.append(
                    _finding(
                        "L004",
                        path,
                        f"Verweis {decision.id} ist kein Atom vom Typ «decision» "
                        f"(Typ: {decision.type}).",
                    )
                )

    for p in eng.phases:
        if PHASE_ORDER.index(p.id) >= 1 and not (p.abort_criterion or "").strip():
            findings.append(
                _finding("L005", f"phases/{p.id}", f"Phase {p.id} hat kein Abbruchkriterium.")
            )

    findings.sort(key=lambda f: (f.code, f.path))
    return findings
