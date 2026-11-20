"""Command-line entry point for adoptionkit."""

import json
import sys
from pathlib import Path

import typer

from adoptionkit import __version__
from adoptionkit.errors import AdoptionkitError
from adoptionkit.io import load_json, validate_data
from adoptionkit.lints import lint as run_lint
from adoptionkit.models import Engagement

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
) -> None:
    """Engagement-Datei auf Lücken prüfen (Lints L001-L005)."""
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
    findings = run_lint(Engagement.model_validate(data))
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


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    app()
