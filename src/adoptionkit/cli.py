"""Command-line entry point for adoptionkit."""

import typer

from adoptionkit import __version__

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


def main() -> None:
    app()
