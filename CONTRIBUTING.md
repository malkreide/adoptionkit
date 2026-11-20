# Mitwirken / Contributing

*English note:* Contributions are welcome. The short version: set up with `uv`, write the failing
test first, use synthetic data only, cite a source for every checklist question, and write German
text in Swiss spelling. Details below (in German).

## Setup

```
uv venv .venv
uv pip install --python .venv -e ".[dev]"
```

Prüfen (alles muss grün sein):

```
.venv/Scripts/python.exe scripts/check_ruff_pin.py
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
.venv/Scripts/python.exe -m pytest
```

Unter Linux und macOS liegt der Interpreter unter `.venv/bin/python`. Nie globales ruff
verwenden, nie ins System-Python installieren.

## Regeln

- **Testgetrieben:** Zuerst ein fehlschlagender Test, dann die Umsetzung. Das gilt für jeden Lint
  und jede Gate-Regel.
- **Schweizer Rechtschreibung:** Deutsche Texte nie mit Eszett, immer mit «ss». Bezeichner in Code
  und Schema sind Englisch. Ein Test prüft die Eszett-Regel.
- **Synthetische Daten:** Beispiel- und Testdaten sind erfunden und als synthetisch beschriftet.
  Keine realen Personen, Organisationen oder internen Abläufe.
- **Quellen-Regel:** Checkfragen sind eigene Formulierungen. Jede trägt ein `source_ref`, das auf
  eine ID in `docs/SOURCES.md` zeigt. Aus Quellen werden Ideen übernommen, keine Textpassagen.
- **Keine Rechtsberatung:** Gates sind Arbeitshilfen und tragen den Hinweis «Arbeitshilfe, keine
  Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.»
- **Offline:** Keine Netzwerkzugriffe, keine Modellaufrufe, keine Telemetrie in `src/`.
- **ruff:** `line-length = 100`, Regeln `E, F, W, I, UP`; die Version ist gepinnt
  (`requirements-lint.txt`).
- **Commits:** klein und sprechend (`feat:`, `fix:`, `docs:`, `test:`, `ci:`).

## Weiterführend

`docs/BAUPLAN.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`.
