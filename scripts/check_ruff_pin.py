"""Prüft, ob die installierte ruff-Version dem Pin in requirements-lint.txt entspricht."""

import re
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN_FILE = ROOT / "requirements-lint.txt"
INSTALL_CMD = 'uv pip install --python .venv -e ".[dev]"'


def read_pin() -> str:
    text = PIN_FILE.read_text(encoding="utf-8")
    match = re.search(r"^ruff==(\S+)\s*$", text, flags=re.MULTILINE)
    if match is None:
        raise SystemExit(f"Kein Pin 'ruff==<version>' in {PIN_FILE.name} gefunden.")
    return match.group(1)


def main() -> int:
    expected = read_pin()
    try:
        installed = metadata.version("ruff")
    except metadata.PackageNotFoundError:
        print(f"ruff nicht installiert. Soll: {expected}")
        print(f"Befehl: {INSTALL_CMD}")
        return 1
    if installed != expected:
        print(f"ruff-Version weicht vom Pin ab. Soll: {expected}, Ist: {installed}")
        print(f"Befehl: {INSTALL_CMD}")
        return 1
    print(f"ruff pin ok: {expected}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
