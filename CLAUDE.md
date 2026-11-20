# CLAUDE.md

Paketname: `adoptionkit` (der Ordner heisst noch `deploykit`).

## Zweck

Evidenz-basierte Einführung einer KI-Lösung in einer Organisation: Schema, Lints, Gates, Viewer und Skill. Reines Python-Paket mit CLI, `src`-Layout unter `src/adoptionkit/`.

## Befehle

```
uv venv .venv
uv pip install --python .venv -e ".[dev]"
.venv/Scripts/python.exe scripts/check_ruff_pin.py
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
.venv/Scripts/python.exe -m pytest
```

Nie globales ruff verwenden, nie ins System-Python installieren.

## Grenzen

- Keine Netzwerkzugriffe, keine Modellaufrufe, keine Telemetrie in `src/`.
- Bezeichner Englisch. Deutsche Texte in Schweizer Rechtschreibung: nie «ß», immer «ss».
- Gates sind Arbeitshilfen, nie ein rechtliches Urteil.
- Beispiel- und Testdaten sind synthetisch und so beschriftet.

## Weiterführend

- `docs/BAUPLAN.md`
- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
