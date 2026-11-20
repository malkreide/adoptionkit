"""Command-line entry point for adoptionkit."""

import sys
from pathlib import Path

import typer

from adoptionkit import __version__
from adoptionkit.errors import AdoptionkitError
from adoptionkit.io import load_json, validate_data

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


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    app()
