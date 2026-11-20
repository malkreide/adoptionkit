from typer.testing import CliRunner

import adoptionkit
from adoptionkit.cli import app


def test_version_is_set() -> None:
    assert adoptionkit.__version__ == "0.0.1.dev0"


def test_cli_version_flag() -> None:
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.0.1.dev0"
