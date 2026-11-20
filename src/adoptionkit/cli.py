"""Command-line entry point for adoptionkit."""

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import cast, get_args

import typer

from adoptionkit import __version__
from adoptionkit.errors import AdoptionkitError
from adoptionkit.gates import GateBlocked, run_gate
from adoptionkit.io import load_engagement, load_json, save_engagement, validate_data
from adoptionkit.lints import lint as run_lint
from adoptionkit.models import (
    DISCLAIMER,
    PHASE_ORDER,
    SCHEMA_VERSION,
    Engagement,
    GateId,
)
from adoptionkit.profiles import Profile, gate_from_profile, load_profile, load_profile_file
from adoptionkit.viewer import render_html

app = typer.Typer(
    no_args_is_help=True,
    help="adoptionkit: Evidenz-basierte Einführung einer KI-Lösung in einer Organisation.",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        help="Version anzeigen und beenden.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """adoptionkit CLI."""


def _resolve_profile(explicit: str | None, from_file: str) -> Profile:
    """Explicit --profile may be a bundled name or a file; meta.profile only a bundled name."""
    if explicit is None:
        return load_profile(from_file)
    if Path(explicit).is_file():
        return load_profile_file(explicit)
    return load_profile(explicit)


@app.command()
def validate(file: Path = typer.Argument(..., help="Engagement-Datei (JSON).")) -> None:
    """Engagement-Datei gegen Schema und Integritätsregeln prüfen."""
    try:
        issues = validate_data(load_json(file))
    except AdoptionkitError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1) from exc
    if issues:
        for issue in issues:
            typer.echo(f"{issue.path}: {issue.message}")
        raise typer.Exit(1)
    typer.echo(f"ok: {file}")


@app.command()
def lint(
    file: Path = typer.Argument(..., help="Engagement-Datei (JSON)."),
    as_json: bool = typer.Option(False, "--json", help="Ausgabe als JSON."),
    profile: str | None = typer.Option(
        None, "--profile", help="Profil (Name oder Pfad); Standard: meta.profile."
    ),
) -> None:
    """Engagement-Datei auf Lücken prüfen (Lints L001-L005, L007)."""
    try:
        data = load_json(file)
    except AdoptionkitError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1) from exc
    issues = validate_data(data)
    if issues:
        for issue in issues:
            typer.echo(f"{issue.path}: {issue.message}")
        raise typer.Exit(1)
    eng = Engagement.model_validate(data)
    try:
        loaded = _resolve_profile(profile, eng.meta.profile)
    except AdoptionkitError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1) from exc
    findings = run_lint(eng, loaded)
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors
    if as_json:
        payload = {
            "findings": [f.to_dict() for f in findings],
            "summary": {"error": errors, "warning": warnings},
        }
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            typer.echo(f"{f.code} {f.severity} {f.path}: {f.message}")
        typer.echo(f"{len(findings)} Befunde ({errors} error, {warnings} warning)")
    if errors:
        raise typer.Exit(1)


def _fail(message: str) -> typer.Exit:
    typer.echo(message)
    return typer.Exit(1)


@app.command()
def gate(
    file: Path = typer.Argument(..., help="Engagement-Datei (JSON)."),
    gate_id: str = typer.Argument(..., metavar="GATE_ID", help="Gate, z. B. G0."),
    profile: str | None = typer.Option(
        None, "--profile", help="Profil (Name oder Pfad); Standard: meta.profile."
    ),
    today: str | None = typer.Option(None, "--today", help="Datum (YYYY-MM-DD); Standard: heute."),
) -> None:
    """Ein Gate auswerten und das Ergebnis in die Datei schreiben."""
    if gate_id not in get_args(GateId):
        raise _fail(f"Unbekannte Gate-ID «{gate_id}». Erlaubt: {', '.join(get_args(GateId))}.")
    try:
        day = date.fromisoformat(today) if today else date.today()
    except ValueError:
        raise _fail(f"Ungültiges Datum «{today}». Erwartet: YYYY-MM-DD.") from None
    try:
        eng = load_engagement(file)
        loaded = _resolve_profile(profile, eng.meta.profile)
        gid = cast(GateId, gate_id)
        if gid not in loaded.gates:
            raise AdoptionkitError(
                f"Gate {gid} ist im Profil «{loaded.name}» nicht definiert."
            )
        new, evaluation = run_gate(eng, loaded, gid, day)
    except GateBlocked as exc:
        typer.echo("Gate blockiert, die Datei bleibt unverändert:")
        for f in exc.findings:
            typer.echo(f"{f.code} {f.severity} {f.path}: {f.message}")
        raise typer.Exit(1) from exc
    except AdoptionkitError as exc:
        raise _fail(str(exc)) from exc
    try:
        save_engagement(new, file)
    except OSError as exc:
        raise _fail(f"{file}: nicht schreibbar: {exc}") from exc
    typer.echo(f"{evaluation.gate_id}: {evaluation.result}")
    if evaluation.recommendation is not None:
        typer.echo(f"Empfehlung: {evaluation.recommendation}")
    for reason in evaluation.reasons:
        typer.echo(f"- {reason}")
    typer.echo(DISCLAIMER)


def _default_id(folder: Path) -> str:
    slug = re.sub(r"[^a-z0-9-]", "-", folder.resolve().name.lower()).strip("-")
    return slug or "engagement"


@app.command()
def init(
    folder: Path = typer.Argument(..., help="Zielordner."),
    profile: str = typer.Option("generic", "--profile", help="Profil (Name oder Pfad)."),
    title: str = typer.Option("", "--title", help="Titel des Engagements."),
    id_: str | None = typer.Option(None, "--id", help="Kennung (a-z, 0-9, Bindestrich)."),
) -> None:
    """Neues Engagement mit Profil-Gates und Phasen anlegen."""
    target = folder / "engagement.json"
    if target.exists():
        raise _fail(f"{target} existiert bereits.")
    try:
        loaded = _resolve_profile(profile, profile)
    except AdoptionkitError as exc:
        raise _fail(str(exc)) from exc
    today = date.today().isoformat()
    slug = id_ if id_ is not None else _default_id(folder)
    data = {
        "meta": {
            "id": slug,
            "title": title,
            "created": today,
            "updated": today,
            "schema_version": SCHEMA_VERSION,
            "profile": loaded.name,
            "synthetic": False,
        },
        "parties": {"client": "", "contractor": ""},
        "solution": {"name": "", "vendor": ""},
        "phases": [{"id": p, "budget_days": 0, "status": "planned"} for p in PHASE_ORDER],
        "gates": [
            gate_from_profile(loaded, gid).model_dump(mode="json", exclude_none=True)
            for gid in loaded.gates
        ],
    }
    issues = validate_data(data)
    if issues:
        raise _fail("\n".join(f"{i.path}: {i.message}" for i in issues))
    try:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "evidence").mkdir(exist_ok=True)
        save_engagement(Engagement.model_validate(data), target)
    except OSError as exc:
        raise _fail(f"{folder}: nicht anlegbar: {exc}") from exc
    typer.echo(f"angelegt: {target}")


@app.command()
def view(
    file: Path = typer.Argument(..., help="Engagement-Datei (JSON)."),
    output: Path = typer.Option(Path("dossier.html"), "-o", "--output", help="Ausgabedatei (HTML)."),
) -> None:
    """Engagement als eigenständige HTML-Datei ausgeben."""
    try:
        eng = load_engagement(file)
    except AdoptionkitError as exc:
        raise _fail(str(exc)) from exc
    try:
        output.write_text(render_html(eng), encoding="utf-8")
    except OSError as exc:
        raise _fail(f"{output}: nicht schreibbar: {exc}") from exc
    typer.echo(str(output))


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    app()
