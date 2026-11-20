# deploykit – Bauplan

Stand: 20.11.2026 · Arbeitstitel «deploykit» · Lizenz MIT · Copyright Hayal Özkan
Ablageort im Repo: `docs/BAUPLAN.md`

## 1. Zweck

deploykit strukturiert die Einführung einer KI-Lösung in einer Organisation als prüfbare Pipeline: von Discovery über Prototyp und Wertnachweis bis zur Härtung und Übergabe. Jede Aussage ist mit Evidenz belegt, jeder Phasenwechsel hängt an einem Gate.

Das Kit ist

- **produktunabhängig:** Die einzuführende Lösung ist ein Parameter (Eigenprodukt, Fremdprodukt, Open-Source-Stack).
- **rollenneutral:** Dasselbe Dossier dient der Auftragnehmerin (führt ein) und der Auftraggeberin (prüft, nimmt ab).
- **KI-in-der-Schleife:** Das Python-Paket ruft kein Sprachmodell auf und geht nicht ins Netz. Die KI-Unterstützung läuft über den Claude-Skill, der das Paket bedient.

Muster: journeykit, personakit, dealkit, sentimentkit (Python-Paket + CLI, JSON-Schema mit Evidenz-Atomen, Lints, Single-File-HTML-Viewer, Claude-Skill, synthetischer Beispielfall).

### Nicht-Ziele

- Kein Projektmanagement-Tool, kein Ticket-System, keine Zeiterfassung.
- Keine Rechtsberatung. Gates erzeugen «Klärungsbedarf» mit Verweis auf die Quelle, nie ein rechtliches Urteil.
- Kein Preis-, Angebots- oder Kapazitätsmodell.
- Kein Werkzeug für Software-Deployment im Sinn von CI/CD.
- Der Begriff «Forward Deployed Engineer» erscheint nur in `docs/SOURCES.md` als Herkunft, nicht in README, CLI oder Skill.

## 2. Offene Entscheide (zu Beginn der ersten Session klären)

| # | Frage | Vorschlag |
|---|---|---|
| E1 | Name. «deploykit» kann mit CI/CD verwechselt werden. | Verfügbarkeit auf GitHub und PyPI prüfen; Alternativen `rolloutkit`, `adoptkit`. Bis zum Entscheid überall die Variable `{{name}}` als «deploykit» behandeln. |
| E2 | Name des Claude-Skills | `ai-rollout` |
| E3 | Synthetischer Beispielfall | «Anfragen-Assistent für die Einwohnerdienste einer fiktiven Gemeinde», eingeführt wird ein fiktives Fremdprodukt |
| E4 | Sprache der Bezeichner | Englisch in Code und Schema, Deutsch in Checklisten-Texten und Doku, README zweisprachig (EN/DE) |

## 3. Datenmodell

Ein Einsatz ist eine JSON-Datei `engagement.json`, validiert gegen `engagement.schema.json`.

```
Engagement
├─ meta            id, title, created, updated, schema_version, profile
├─ parties         client, contractor, conflict_of_interest
├─ solution        name, vendor, hosting_model, data_location, config_limits
├─ atoms[]         Evidenz-Atome
├─ phases[]        discovery | prototype | value_proof | hardening | handover
├─ gates[]         G0 … G4
├─ measures[]      geplante oder umgesetzte Anpassungen
├─ evals           eval_set_ref, thresholds, runs[]
├─ artefacts[]     Rückfluss-Register
└─ handover        operators[], training_done, runbook_ref
```

### Evidenz-Atom

| Feld | Werte |
|---|---|
| `id` | `A-001` … |
| `type` | `requirement` · `constraint` · `data_source` · `risk` · `usage_signal` · `decision` |
| `statement` | ein Satz, eine Aussage |
| `source` | `kind` (interview, document, system, analytics, regulation, workshop), `ref`, `date`, optional `quote` |
| `status` | `evidenced` · `assumed` · `refuted` |

Regel: Kein Atom ohne `source.ref`. Ein Atom mit Status `assumed` darf kein Gate schliessen.

### Phase

`id`, `budget_days`, `start`, `end`, `status` (planned, running, done, aborted), `abort_criterion` (Pflicht ab `prototype`).

### Measure

`id`, `description`, `change_type` (`configuration` · `template` · `new_development`), `atom_refs[]`, `product_decision_ref` (Pflicht bei `new_development`: Verweis auf ein `decision`-Atom der Produktverantwortung).

### Artefact (Rückfluss-Register)

`id`, `description`, `origin_measure`, `fate` (`open` · `generalised` · `dropped`), `reviewed_on`.

## 4. Gates

Gates sind Checklisten, die als YAML-**Profile** geladen werden. Das Paket kennt die Gate-Mechanik, die Fragen stehen im Profil. So bleibt das Kit unabhängig von Produkt und Rechtsraum.

- `profiles/generic.yaml` – Gates G0, G3, G4 ohne rechtsraumspezifische Fragen.
- `profiles/ch-zh-public.yaml` – zusätzlich G1 und G2 für öffentliche Organe im Kanton Zürich.

Jede Checkfrage hat: `id`, `question`, `answer` (yes, no, unclear, n/a), `atom_refs[]`, `source_ref` (Verweis auf `docs/SOURCES.md`). Ein Gate ist `passed`, wenn keine Frage `unclear` ist und jede `yes`/`no`-Antwort mindestens ein belegtes Atom referenziert. Ergebniswerte: `passed` · `open` · `stopped`.

| Gate | Zeitpunkt | Inhalt |
|---|---|---|
| **G0 Eignung** | vor Discovery | Ist das Problem geschäftskritisch? Gleicht der Ablauf bekannten Fällen? Rechtfertigt die Integrations- und Auflagenlast den Aufwand? Erfüllt die gewählte Lösung die Auflagen (Datenstandort, Auftragsbearbeitung)? Wo liegt ihre Konfigurationsgrenze? Ergebnis zusätzlich: `guided_rollout` · `standard_rollout` · `decline`. |
| **G1 Vertragsform** | vor Prototyp | Fünf Abgrenzungspunkte zwischen Auftrag und Personalverleih: Weisungsrecht, Eingliederung und Arbeitsort, Arbeitsmittel, wirtschaftliches Risiko und Haftung, Projektbezug. |
| **G2 Verwaltung** | vor Prototyp | Sicherheit, ethische Vertretbarkeit, Einstufung als algorithmisches Entscheidsystem, Transparenz über Einsatz und Technik, Auftragsbearbeitung nach kantonalem Datenschutzrecht. |
| **G3 Evaluation** | vor Wertnachweis | Eval-Set aus echten Fällen vorhanden? Schwellenwerte vereinbart? Letzter Lauf über Schwelle? |
| **G4 Übergabe** | vor Abschluss | Betriebsverantwortliche benannt und geschult? Betriebshandbuch vorhanden? Rückfluss-Register leer von `open`? |

Jede Checkliste trägt den Hinweis: «Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.»

## 5. Lints

| ID | Regel |
|---|---|
| L001 | Atom ohne `source.ref` |
| L002 | `requirement` mit Status `assumed`, auf das eine Measure verweist |
| L003 | Measure ohne `atom_refs` |
| L004 | Measure `new_development` ohne `product_decision_ref` |
| L005 | Phase ab `prototype` ohne `abort_criterion` |
| L006 | Phase `running` über `budget_days` |
| L007 | Phase gestartet, obwohl das vorgelagerte Gate nicht `passed` ist |
| L008 | Gate-Antwort ohne belegtes Atom |
| L009 | `value_proof` ohne mindestens ein `usage_signal` |
| L010 | Artefact `open` und `reviewed_on` älter als 90 Tage |
| L011 | `handover` ohne `operators` |
| L012 | `conflict_of_interest` leer, obwohl `contractor` und `solution.vendor` übereinstimmen |

Schweregrade: `error` (blockiert `gate`), `warning`. Ausgabe als Text und mit `--json`.

## 6. CLI

```
deploykit init <ordner> --profile ch-zh-public   # leeres Dossier mit Profil
deploykit validate <engagement.json>             # Schema-Prüfung
deploykit lint <engagement.json> [--json]        # Lints L001–L012
deploykit gate <engagement.json> G0              # Gate auswerten, Ergebnis schreiben
deploykit status <engagement.json>               # Phasen, Gates, Kennzahlen
deploykit view <engagement.json> -o dossier.html # Single-File-Viewer
deploykit export <engagement.json> --md          # Markdown-Bericht
```

## 7. Viewer

- Eine HTML-Datei, alles eingebettet, keine externen Skripte, Schriften oder CDNs. Funktioniert offline.
- Zwei Ansichten per Umschalter: «Auftraggeberin» (Gates, offene Punkte, Abnahme) und «Auftragnehmerin» (Phasen, Zeitbudget, Measures, Rückfluss).
- Kennzahlen: Anteil belegter Atome, Anteil `configuration` an allen Measures, Anzahl abgelehnter Anpassungen, offene Artefakte.
- Bei gesetztem `conflict_of_interest` ein sichtbarer Hinweis im Kopf.
- Jede Aussage ist auf ihr Atom und dessen Quelle klickbar.

## 8. Claude-Skill

Ablage: `skills/<skill-name>/SKILL.md`. Der Skill

1. führt durch die Phasen und ruft dafür die CLI auf,
2. zerlegt Rohmaterial (Interviewnotizen, Prozessdokumente) in Atome und fragt bei fehlender Quelle nach, statt zu ergänzen,
3. schreibt nichts ins Dossier, was nicht belegt ist, und markiert Annahmen als `assumed`,
4. beantwortet Gate-Fragen nie selbst mit `yes` oder `no`, sondern schlägt vor und lässt bestätigen,
5. gibt keine rechtlichen Urteile ab.

Scaffold mit `skill-creator`, Wirksamkeitstest (Baseline ohne Skill, dann mit) nach `writing-skills`.

## 9. Repo-Struktur

```
deploykit/
├─ src/deploykit/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ models.py
│  ├─ io.py
│  ├─ lints.py
│  ├─ gates.py
│  ├─ viewer.py
│  ├─ schema/engagement.schema.json
│  ├─ profiles/generic.yaml
│  ├─ profiles/ch-zh-public.yaml
│  └─ templates/viewer.html
├─ examples/synthetic-municipality/
│  ├─ engagement.json
│  ├─ evidence/            # synthetische Notizen, klar gekennzeichnet
│  └─ README.md
├─ skills/<skill-name>/SKILL.md
├─ tests/
├─ docs/
│  ├─ BAUPLAN.md
│  ├─ ROADMAP.md           # Stufen, Gates, je ein Start-Prompt pro Stufe
│  ├─ DECISIONS.md
│  └─ SOURCES.md
├─ .github/workflows/ci.yml
├─ CLAUDE.md
├─ README.md  README.de.md
├─ LICENSE  CHANGELOG.md  SECURITY.md  CONTRIBUTING.md
├─ pyproject.toml  .gitignore
```

## 10. Technik und Konventionen

- Python ≥ 3.11, `src`-Layout, `pydantic` v2, `typer`, `pyyaml`, `jsonschema`; Tests mit `pytest`; `ruff` und `pyright` in der CI.
- JSON-Schema wird aus den pydantic-Modellen erzeugt und eingecheckt; ein Test prüft, dass beide übereinstimmen.
- Keine Netzwerkzugriffe, keine Modellaufrufe, keine Telemetrie im Paket.
- Testgetrieben: zuerst der Test je Lint und je Gate-Regel, dann die Umsetzung.
- Umgebung: Windows, PowerShell. Lokaler Ordner `~\deploykit` neben `~\journeykit`, `~\personakit`, `~\dealkit`, `~\sentimentkit`.
- Commits mit der Adresse `8864492+malkreide@users.noreply.github.com`.
- **Kein Push, kein `gh repo create`.** Das GitHub-Repo legt Hayal selbst an und setzt die Topics.
- Beispiel- und Testdaten sind synthetisch und so beschriftet. Keine realen Personen, Organisationen oder internen Abläufe.
- Schweizer Rechtschreibung in deutschen Texten (ss statt ß).

## 11. Quellen und Umgang damit

Alle Quellen stehen in `docs/SOURCES.md` mit dem Vermerk «gelesen» oder «ungeprüft». Es werden **Ideen und Strukturen** übernommen, keine Textpassagen. Checkfragen sind eigene Formulierungen mit Quellenverweis.

Gelesen (Stand 20.11.2026):

- McKinsey Explainer «What is a forward-deployed engineer?» – https://www.mckinsey.com/featured-insights/mckinsey-explainers/what-is-a-forward-deployed-engineer
- Forward Deployed Engineer Roadmap (Apache-2.0; nur die Idee des Einsatzzyklus) – https://github.com/amitshekhariitbhu/forward-deployed-engineer-roadmap
- a16z «The Palantirization of Everything» (Eignungsfragen, Zeitbudget, Rückfluss) – https://a16z.com/the-palantirization-of-everything/
- CIO «There are two completely different roles called FDE» (Konfiguration vor Neubau, Evals) – https://www.cio.com/article/4206312/there-are-two-completely-different-roles-called-fde.html
- First Round Review «So You Want to Hire a Forward Deployed Engineer» (Abbruchkriterium, Nutzung als Wertnachweis) – https://review.firstround.com/so-you-want-to-hire-a-forward-deployed-engineer/
- Kanton Zürich «Künstliche Intelligenz» (G2) – https://www.zh.ch/de/politik-staat/kanton/kantonale-verwaltung/digitale-verwaltung/kuenstliche-intelligenz.html
- BBL/KBB Merkblatt «Abgrenzung Personalverleih / Aufträge» (G1) – https://www.perimap.admin.ch/goto_bbl01_file_37290_download.html

Noch einzuarbeiten (ungeprüft, in Stufe 1 lesen):

- AlgorithmWatch, Impact-Assessment-Tool für die öffentliche Verwaltung (Triage-Checkliste für G2) – https://algorithmwatch.org/de/wp-content/uploads/2022/09/ADM-Folgenabschätzung_AlgorithmWatch_2022.pdf
- Kanton Zürich, Bericht zur KI-Pilot-Anwendung – https://www.zh.ch/content/dam/zhweb/bilder-dokumente/organisation/direktion-der-justiz-und-des-innern/statistisches-amt/KI%20Pilot%20Bericht_V2.0.pdf
- Datenschutzbeauftragte Kanton Zürich, Leitfaden «Bearbeiten im Auftrag» – https://docs.datenschutz.ch/u/d/publikationen/leitfaeden/leitfaden_bearbeiten_im_auftrag.pdf
- Kanton Zürich, Private Arbeitsvermittlung und Personalverleih – https://www.zh.ch/de/wirtschaft-arbeit/gewerbe-betriebsbewilligungen/private-arbeitsvermittlung-und-personalverleih.html
- Bundeskanzlei, Strategie «Einsatz von KI-Systemen in der Bundesverwaltung» – https://www.bk.admin.ch/dam/bk/de/dokumente/dti/Vorgaben/StrategienundTeilstrategien/ki-teilstrategie.pdf.download.pdf/Strategie%20Einsatz%20von%20KI-Systemen%20in%20der%20Bundesverwaltung.pdf

## 12. Stufenplan

Jede Stufe endet mit einem Gate. Ohne bestandenes Gate keine nächste Stufe. `docs/ROADMAP.md` enthält pro Stufe einen Start-Prompt für eine frische Session.

### Stufe 0 – Skelett (erste Session)

Umfang:

- Repo-Struktur, `pyproject.toml`, CI, Standarddateien, `CLAUDE.md`
- Modelle und Schema vollständig
- `init`, `validate`, `lint` (L001–L005, L007), `gate` für G0 mit `generic.yaml`
- synthetischer Beispielfall, der `validate` besteht und genau zwei beabsichtigte Lint-Befunde enthält
- Viewer minimal: Phasen, Gates, Atome, ohne Umschalter
- Skill v0 (Scaffold, noch ohne Wirksamkeitstest)
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/SOURCES.md`

Gate 0:

```
pytest                     # grün
ruff check .               # sauber
pyright                    # sauber
deploykit validate examples/synthetic-municipality/engagement.json   # ok
deploykit lint examples/synthetic-municipality/engagement.json       # genau 2 Befunde
deploykit view examples/synthetic-municipality/engagement.json -o out.html   # Datei öffnet offline
```

### Stufe 1 – Gates und Lints vollständig

Profil `ch-zh-public.yaml` mit G1 und G2, ungeprüfte Quellen lesen und einarbeiten, L006 und L008–L012, `status`, `export --md`.
Gate 1: Jede Checkfrage hat einen `source_ref`; der Beispielfall durchläuft G0 bis G4; eine zweite Fixture endet bei G0 mit `decline`.

### Stufe 2 – Viewer

Zwei Ansichten, Kennzahlen, Hinweis zur Interessenbindung, Klickpfad Aussage → Atom → Quelle.
Gate 2: Eine aussenstehende Person findet in unter zwei Minuten alle offenen Punkte eines Dossiers.

### Stufe 3 – Skill

Skill ausbauen, Wirksamkeitstest nach `writing-skills` mit drei Szenarien (fehlende Quelle, Wunsch nach Neuentwicklung, Bitte um rechtliches Urteil).
Gate 3: In allen drei Szenarien verhält sich die Session mit Skill messbar anders als die Baseline.

### Stufe 4 – Praxistest

Ein realer Fall, rückwirkend erfasst; mindestens ein Fall mit einem Fremdprodukt. Daten bleiben lokal und kommen nicht ins Repo.
Gate 4: Schema-Änderungen aus dem Praxistest sind eingearbeitet; Version 0.1.0 getaggt.

### Stufe 5 – Anschluss

Import von journeykit-Journeys und personakit-Personas als Evidenzquellen. MCP-Server erst, wenn ein konkreter Bedarf vorliegt.
