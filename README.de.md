# adoptionkit

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-pre--alpha%20(Stufe%200)-orange)

> Evidenz-basierte Einführung einer KI-Lösung in einer Organisation: Evidenz-Atome, Phasen, Gates als YAML-Checklisten, Lints, ein Einzeldatei-Viewer und ein Claude-Skill.

🇬🇧 [English version](README.md)

> **Arbeitshilfe, keine Rechtsberatung.** Die Gates sind Checklisten, die offene Punkte sichtbar machen. Sie fällen nie ein rechtliches Urteil. Offene Punkte mit der zuständigen Fachstelle klären.

## Zweck

adoptionkit strukturiert die Einführung einer KI-Lösung in einer Organisation als prüfbare Pipeline: von Discovery über Prototyp und Wertnachweis bis zur Härtung und Übergabe. Jede Aussage ist mit Evidenz belegt, jeder Phasenwechsel hängt an einem Gate.

- **Produktunabhängig:** Die einzuführende Lösung ist ein Parameter (Eigenprodukt, Fremdprodukt, Open-Source-Stack).
- **Rollenneutral:** Dasselbe Dossier dient der Seite, die einführt, und der Seite, die prüft und abnimmt.
- **KI in der Schleife, nicht im Paket:** Das Python-Paket ruft kein Sprachmodell auf und geht nicht ins Netz. Die KI-Unterstützung läuft über den Claude-Skill `ai-rollout`, der das Paket bedient.

Stand: **Pre-Alpha, Stufe 0** (Skelett). Siehe `docs/ROADMAP.md`.

## Nicht-Ziele

- Kein Projektmanagement-Tool, kein Ticket-System, keine Zeiterfassung.
- Keine Rechtsberatung. Gates erzeugen «Klärungsbedarf» mit Verweis auf die Quelle, nie ein rechtliches Urteil.
- Kein Preis-, Angebots- oder Kapazitätsmodell.
- Kein Werkzeug für Software-Deployment im Sinn von CI/CD.

## Installation

Nicht auf PyPI veröffentlicht. Installation aus dem Quellcode (Python 3.11 oder neuer):

```bash
git clone https://github.com/malkreide/adoptionkit.git
cd adoptionkit
uv venv .venv
uv pip install --python .venv -e ".[dev]"
```

Oder mit pip: `pip install -e ".[dev]"`. Der Befehl heisst danach `adoptionkit` (unter Windows `.venv/Scripts/adoptionkit.exe`).

## Schnellstart

Das Repository enthält einen synthetischen Beispielfall: ein Anfragen-Assistent für die Einwohnerdienste der fiktiven Gemeinde Seewil (`examples/synthetic-municipality/`). Alle Daten darin sind erfunden.

```bash
adoptionkit validate examples/synthetic-municipality/engagement.json
```
```
ok: examples/synthetic-municipality/engagement.json
```

```bash
adoptionkit lint examples/synthetic-municipality/engagement.json
```
```
L002 warning measures/M-002: Anforderung A-006 ist nur angenommen (assumed), nicht belegt.
L003 warning measures/M-004: Measure M-004 verweist auf kein Atom.
2 Befunde (0 error, 2 warning)
```

Die beiden Warnungen sind beabsichtigt: Sie zeigen, was die Lints melden.

`gate` schreibt das Ergebnis in die Datei, also zuerst das Beispiel ins Arbeitsverzeichnis kopieren (bash, oder `Copy-Item` in PowerShell):

```bash
cp examples/synthetic-municipality/engagement.json .
# PowerShell: Copy-Item examples/synthetic-municipality/engagement.json .
adoptionkit gate engagement.json G0 --today 2026-09-07
```
```
G0: passed
Empfehlung: guided_rollout
Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.
```

Zum Schluss eine einzelne HTML-Datei erzeugen, die offline öffnet:

```bash
adoptionkit view examples/synthetic-municipality/engagement.json -o dossier.html
```

Ein eigenes Dossier startet mit `adoptionkit init mein-dossier --profile generic --title "..."`. Ein nicht gebündeltes Profil muss ausdrücklich mit `--profile <pfad>` übergeben werden (auch bei `lint` und `gate`); `meta.profile` löst nur gebündelte Namen auf.

## CLI-Befehle

| Befehl | Zweck | Stand |
|---|---|---|
| `adoptionkit init <ordner> [--profile] [--title] [--id]` | Leeres Dossier mit Gates und Phasen des Profils anlegen | vorhanden |
| `adoptionkit validate <datei>` | Gegen JSON-Schema und Integritätsregeln prüfen | vorhanden |
| `adoptionkit lint <datei> [--json] [--profile]` | Lints L001–L005, L007 | vorhanden |
| `adoptionkit gate <datei> <GATE_ID> [--profile] [--today]` | Gate auswerten und Ergebnis in die Datei schreiben | vorhanden |
| `adoptionkit view <datei> [-o dossier.html]` | Minimaler Einzeldatei-Viewer (Phasen, Gates, Atome) | vorhanden |
| `adoptionkit status <datei>` | Phasen, Gates, Kennzahlen | geplant (Stufe 1) |
| `adoptionkit export <datei> --md` | Markdown-Bericht | geplant (Stufe 1) |

Exit-Codes: 0 = ok, 1 = Befund, ungültige Eingabe oder Fehler.

## Datenmodell in Kürze

Ein Einsatz ist eine JSON-Datei `engagement.json`, validiert gegen `engagement.schema.json` (aus den Modellen erzeugt und eingecheckt).

- `meta`, `parties`, `solution`: Kennung, Beteiligte, die einzuführende Lösung.
- `atoms[]`: **Evidenz-Atome**. Eine Aussage je Atom, mit Typ (`requirement`, `constraint`, `data_source`, `risk`, `usage_signal`, `decision`), Quelle (`kind`, `ref`, `date`, optional `quote`) und Status (`evidenced`, `assumed`, `refuted`). Kein Atom ohne `source.ref`; ein Atom mit Status `assumed` schliesst nie ein Gate.
- `phases[]`: `discovery`, `prototype`, `value_proof`, `hardening`, `handover`, je mit Budget in Tagen, Status und ab `prototype` einem Abbruchkriterium.
- `gates[]`: Checklisten mit Antworten (`yes`, `no`, `unclear`, `n/a`), referenzierten Atomen und Ergebnis (`passed`, `open`, `stopped`).
- `measures[]`, `evals`, `artefacts[]`, `handover`: Anpassungen, Evaluationsläufe, Rückfluss-Register, Betriebsverantwortliche.

## Lints

| ID | Regel | Stand |
|---|---|---|
| L001 | Atom ohne `source.ref` | umgesetzt |
| L002 | Measure stützt sich auf eine nur angenommene (`assumed`) Anforderung | umgesetzt |
| L003 | Measure ohne Atom-Verweise | umgesetzt |
| L004 | Neuentwicklung ohne Produktentscheid | umgesetzt |
| L005 | Gestartete Phase ab `prototype` ohne Abbruchkriterium | umgesetzt |
| L006 | Laufende Phase über `budget_days` | geplant (Stufe 1) |
| L007 | Phase gestartet, obwohl das geforderte Gate nicht bestanden ist | umgesetzt |
| L008 | Gate-Antwort ohne belegtes Atom | geplant (Stufe 1) |
| L009 | `value_proof` ohne mindestens ein `usage_signal` | geplant (Stufe 1) |
| L010 | Offenes Artefakt, letzte Prüfung älter als 90 Tage | geplant (Stufe 1) |
| L011 | `handover` ohne Betriebsverantwortliche | geplant (Stufe 1) |
| L012 | Interessenbindung leer, obwohl Auftragnehmerin und Hersteller übereinstimmen | geplant (Stufe 1) |

Schweregrade: `error` (blockiert `gate`) und `warning`. Ausgabe als Text oder mit `--json`.

## Gates

Gates sind YAML-Profile. Das Paket kennt die Gate-Mechanik, die Fragen stehen im Profil. So bleibt das Kit unabhängig von Produkt und Rechtsraum. Jede Frage ist eine eigene Formulierung und trägt ein `source_ref`, das auf eine ID in `docs/SOURCES.md` zeigt.

| Profil | Gates | Stand |
|---|---|---|
| `generic` | G0 Eignung, G3 Evaluation, G4 Übergabe | vorhanden |
| `ch-zh-public` | zusätzlich G1 Vertragsform, G2 Verwaltung | geplant (Stufe 1) |

Ein Gate ist `passed`, wenn keine Frage `unclear` ist und jede `yes`/`no`-Antwort mindestens ein belegtes Atom referenziert. G0 liefert zusätzlich eine Empfehlung (`guided_rollout`, `standard_rollout`, `decline`).

## Claude-Skill

`skills/ai-rollout/SKILL.md` (v0) führt eine Session durch das Dossier: Er zerlegt Rohmaterial in Evidenz-Atome, markiert Annahmen als `assumed` und schlägt Gate-Antworten nur vor. Der Wirksamkeitstest folgt in Stufe 3.

## Grenzen

- Offline: keine Netzwerkzugriffe, keine Modellaufrufe, keine Telemetrie. Ein Test prüft, dass `src/` keine Netzwerk-Bibliothek importiert.
- Beispieldaten sind synthetisch. Keine echten personenbezogenen Daten oder internen Dokumente committen.
- Pre-Alpha: Schema und Profile können sich noch ändern.

## Mitwirken

Beiträge sind willkommen – siehe [CONTRIBUTING.md](CONTRIBUTING.md). Hintergrund: `docs/BAUPLAN.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`, [CHANGELOG.md](CHANGELOG.md).

## Sicherheit

Schwachstellen bitte wie in [SECURITY.md](SECURITY.md) beschrieben melden. Dossiers können interne Informationen enthalten: reale Fälle lokal halten und nicht ins Repo legen.

## Lizenz

MIT, siehe [LICENSE](LICENSE). Copyright (c) 2026 Hayal Özkan.

## Autor

Hayal Özkan · [malkreide](https://github.com/malkreide)
