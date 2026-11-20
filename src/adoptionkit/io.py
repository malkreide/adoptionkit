"""Loading, validating and saving engagement files."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from adoptionkit.errors import AdoptionkitError
from adoptionkit.models import Engagement


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def load_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise AdoptionkitError(f"{p}: Datei ist nicht UTF-8-kodiert: {exc.reason}") from exc
    except OSError as exc:
        raise AdoptionkitError(f"{p}: Datei nicht lesbar: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AdoptionkitError(
            f"{p}: ungültiges JSON (Zeile {exc.lineno}, Spalte {exc.colno}): {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise AdoptionkitError(f"{p}: JSON-Wurzel muss ein Objekt sein")
    return data


def load_schema() -> dict[str, Any]:
    text = (
        resources.files("adoptionkit")
        .joinpath("schema", "engagement.schema.json")
        .read_text(encoding="utf-8")
    )
    return json.loads(text)


def _fmt_path(parts: Any) -> str:
    items = [str(p) for p in parts]
    return "/".join(items) if items else "(root)"


def _encoding_issues(node: Any, path: tuple[str, ...] = ()) -> list[ValidationIssue]:
    """Report strings (values and keys) that cannot be written as UTF-8, e.g. lone surrogates."""
    out: list[ValidationIssue] = []
    message = "Text ist nicht als UTF-8 kodierbar (z. B. einzelnes Surrogat-Zeichen)"

    def bad(text: str) -> bool:
        try:
            text.encode("utf-8")
        except UnicodeEncodeError:
            return True
        return False

    if isinstance(node, str):
        if bad(node):
            out.append(ValidationIssue(_fmt_path(path), message))
    elif isinstance(node, dict):
        for key, value in node.items():
            if bad(str(key)):
                out.append(ValidationIssue(_fmt_path(path + (str(key),)), message + " (Schlüssel)"))
            out += _encoding_issues(value, path + (str(key),))
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            out += _encoding_issues(value, path + (str(idx),))
    return out


def validate_data(data: dict[str, Any]) -> list[ValidationIssue]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    issues = _encoding_issues(data) + [
        ValidationIssue(_fmt_path(e.absolute_path), e.message) for e in validator.iter_errors(data)
    ]
    if not issues:
        try:
            eng = Engagement.model_validate(data)
        except ValidationError as exc:
            issues = [ValidationIssue(_fmt_path(e["loc"]), e["msg"]) for e in exc.errors()]
        else:
            issues = _integrity_issues(eng)
    issues.sort(key=lambda i: (i.path, i.message))
    return issues


def _duplicates(ids: list[str], prefix: str) -> list[ValidationIssue]:
    seen: set[str] = set()
    out: list[ValidationIssue] = []
    for idx, id_ in enumerate(ids):
        if id_ in seen:
            out.append(ValidationIssue(f"{prefix}/{idx}/id", f"doppelte ID {id_}"))
        seen.add(id_)
    return out


def _integrity_issues(eng: Engagement) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues += _duplicates([a.id for a in eng.atoms], "atoms")
    issues += _duplicates([p.id for p in eng.phases], "phases")
    issues += _duplicates([g.id for g in eng.gates], "gates")
    issues += _duplicates([m.id for m in eng.measures], "measures")
    issues += _duplicates([x.id for x in eng.artefacts], "artefacts")
    issues += _duplicates([r.id for r in eng.evals.runs], "evals/runs")
    atom_ids = {a.id for a in eng.atoms}
    measure_ids = {m.id for m in eng.measures}
    for gi, gate in enumerate(eng.gates):
        issues += _duplicates([c.id for c in gate.checks], f"gates/{gi}/checks")
        for ci, chk in enumerate(gate.checks):
            for ri, ref in enumerate(chk.atom_refs):
                if ref not in atom_ids:
                    path = f"gates/{gi}/checks/{ci}/atom_refs/{ri}"
                    issues.append(ValidationIssue(path, f"Atom {ref} existiert nicht"))
    for mi, meas in enumerate(eng.measures):
        for ri, ref in enumerate(meas.atom_refs):
            if ref not in atom_ids:
                issues.append(
                    ValidationIssue(f"measures/{mi}/atom_refs/{ri}", f"Atom {ref} existiert nicht")
                )
        pdr = meas.product_decision_ref
        if pdr is not None and pdr not in atom_ids:
            issues.append(
                ValidationIssue(
                    f"measures/{mi}/product_decision_ref", f"Atom {pdr} existiert nicht"
                )
            )
    for xi, art in enumerate(eng.artefacts):
        if art.origin_measure not in measure_ids:
            issues.append(
                ValidationIssue(
                    f"artefacts/{xi}/origin_measure",
                    f"Measure {art.origin_measure} existiert nicht",
                )
            )
    return issues


def load_engagement(path: str | Path) -> Engagement:
    data = load_json(path)
    issues = validate_data(data)
    if issues:
        detail = "\n".join(f"{i.path}: {i.message}" for i in issues)
        raise AdoptionkitError(f"{path}: ungültig\n{detail}")
    return Engagement.model_validate(data)


def save_engagement(eng: Engagement, path: str | Path) -> None:
    """Write atomically: serialise and encode first, then temp file and os.replace.

    On any failure the original file stays untouched and the temp file is removed.
    """
    text = json.dumps(eng.model_dump(mode="json", exclude_none=True), indent=2, ensure_ascii=False)
    payload = (text + chr(10)).encode("utf-8")
    target = Path(path)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
