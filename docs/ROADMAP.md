# Roadmap

Grundlage: `docs/BAUPLAN.md`, Abschnitt 12. Jede Stufe endet mit einem Gate. Ohne bestandenes Gate keine nächste Stufe. Pro Stufe steht ein Start-Prompt bereit, den du in eine frische Claude-Code-Session einfügst.

| Stufe | Thema | Stand |
|---|---|---|
| 0 | Skelett | erledigt (2026-11-20) |
| 1 | Gates und Lints vollständig | offen |
| 2 | Viewer | offen |
| 3 | Skill | offen |
| 4 | Praxistest | offen |
| 5 | Anschluss | offen |

Gemeinsame Regeln für alle Stufen: Paket `adoptionkit`, Bezeichner Englisch, deutsche Texte in Schweizer Rechtschreibung (nie das Eszett, immer «ss»), keine Netzwerkzugriffe und keine Modellaufrufe im Paket, Beispiel- und Testdaten synthetisch, Gates als Arbeitshilfe ohne rechtliches Urteil, Checkfragen als eigene Formulierungen mit `source_ref`.

## Stufe 0: Skelett (erledigt, 2026-11-20)

**Umfang:** Repo-Struktur, `pyproject.toml`, CI, Standarddateien; Modelle und Schema; `init`, `validate`, `lint` (L001–L005, L007), `gate` für G0 mit `generic.yaml`; synthetischer Beispielfall mit genau zwei beabsichtigten Lint-Befunden; minimaler Viewer; Skill v0; `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/SOURCES.md`.

**Gate 0:**

```
pytest                     # grün
ruff check .               # sauber
pyright                    # sauber
adoptionkit validate examples/synthetic-municipality/engagement.json   # ok
adoptionkit lint examples/synthetic-municipality/engagement.json       # genau 2 Befunde
adoptionkit view examples/synthetic-municipality/engagement.json -o out.html   # Datei öffnet offline
```

Kein Start-Prompt nötig.

## Stufe 1: Gates und Lints vollständig

**Umfang:**

- Die fünf ungeprüften Quellen (U01–U05) lesen und in `docs/SOURCES.md` mit «gelesen» vermerken.
- Profil `ch-zh-public.yaml` mit G1 (Vertragsform) und G2 (Verwaltung), eigene Formulierungen, je Frage ein `source_ref`, Hinweis «Arbeitshilfe, keine Rechtsberatung».
- Lints L006 und L008–L012 (L006 und L010 brauchen `today`).
- CLI `status` und `export --md`.

**Gate 1:** Jede Checkfrage hat einen `source_ref`; der Beispielfall durchläuft G0 bis G4; eine zweite Fixture endet bei G0 mit `decline`.

**Start-Prompt:**

```
Arbeite im Repo ~\deploykit (Python-Paket `adoptionkit`, neuer Branch; kurzer Pfad). Wir setzen Stufe 1 um.

Lies zuerst: docs/BAUPLAN.md (Abschnitte 4, 5, 6, 11, 12), docs/DECISIONS.md, docs/ROADMAP.md, docs/SOURCES.md, CLAUDE.md und die globale CLAUDE.md. Halte dich an deren Konventionen: testgetrieben (je Lint und je Gate-Regel zuerst ein fehlschlagender Test), Verifikation vor jeder Erfolgsmeldung (Befehle frisch ausführen, Output lesen), Schweizer Rechtschreibung (nie das Eszett), kein `git push`, kein `gh repo create`. Umgebung: `.venv` im Repo, nie globales ruff, nie ins System-Python installieren.

Umfang Stufe 1:
1. Lies die fünf ungeprüften Quellen U01–U05 aus docs/SOURCES.md und trage in SOURCES.md den Vermerk «gelesen» ein. Übernimm Ideen und Strukturen, keine Textpassagen.
2. Lege src/adoptionkit/profiles/ch-zh-public.yaml an: G1 (Vertragsform: Abgrenzung Auftrag und Personalverleih, fünf Punkte) und G2 (Verwaltung: Sicherheit, ethische Vertretbarkeit, Einstufung als algorithmisches Entscheidsystem, Transparenz, Auftragsbearbeitung). Eigene Formulierungen, jede Frage mit `source_ref` auf eine ID in SOURCES.md, Hinweis «Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.» Das Profil enthält zusätzlich die Gates G0, G3 und G4 des generischen Profils.
3. Implementiere die Lints L006 und L008–L012 gemäss BAUPLAN Abschnitt 5 in src/adoptionkit/lints.py (L006 und L010 brauchen `today`), je mit zuerst fehlschlagendem Test.
4. Ergänze die CLI um `status <datei>` (Phasen, Gates, Kennzahlen) und `export <datei> --md` (Markdown-Bericht), mit Tests.
5. Zweite Fixture (synthetisch), die bei G0 mit `decline` endet; Test, dass der Beispielfall G0 bis G4 durchläuft.
6. Aktualisiere README.md und README.de.md (Lints-Tabelle, Befehle, Profile), CHANGELOG.md und docs/ROADMAP.md (Stufe 1 als erledigt).

Gate 1 (am Ende ausführen und Output lesen):
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
.venv/Scripts/adoptionkit.exe validate examples/synthetic-municipality/engagement.json
.venv/Scripts/adoptionkit.exe lint examples/synthetic-municipality/engagement.json
Gate 1 gilt als bestanden, wenn jede Checkfrage einen source_ref hat, der Beispielfall G0 bis G4 durchläuft und die zweite Fixture bei G0 mit `decline` endet.

Commits klein und sprechend, jede Message endet mit der Co-Authored-By-Zeile gemäss Konvention. Schliesse mit einem kurzen Abschlussbericht: Status, Commits, Testzusammenfassung, offene Punkte.
```

## Stufe 2: Viewer

**Umfang:** Zwei Ansichten per Umschalter (Auftraggeberin, Auftragnehmerin), Kennzahlen (Anteil belegter Atome, Anteil `configuration` an allen Measures, Anzahl abgelehnter Anpassungen, offene Artefakte), sichtbarer Hinweis bei gesetzter Interessenbindung, Klickpfad Aussage → Atom → Quelle. Weiterhin eine HTML-Datei, alles eingebettet, offline.

**Gate 2:** Eine aussenstehende Person findet in unter zwei Minuten alle offenen Punkte eines Dossiers.

**Start-Prompt:**

```
Arbeite im Repo ~\deploykit (Python-Paket `adoptionkit`; kurzer Pfad). Wir setzen Stufe 2 (Viewer) um.

Lies zuerst: docs/BAUPLAN.md (Abschnitt 7 und 12), docs/DECISIONS.md, docs/ROADMAP.md, CLAUDE.md und die globale CLAUDE.md. Halte dich an deren Konventionen: testgetrieben, Verifikation vor jeder Erfolgsmeldung, Schweizer Rechtschreibung (nie das Eszett), kein `git push`, kein `gh repo create`. Umgebung: `.venv` im Repo, nie globales ruff, nie ins System-Python installieren.

Ausgangslage: src/adoptionkit/viewer.py und src/adoptionkit/templates/viewer.html liefern einen minimalen Einzeldatei-Viewer (Phasen, Gates, Atome). Ergänze:
1. Zwei Ansichten mit Umschalter: «Auftraggeberin» (Gates, offene Punkte, Abnahme) und «Auftragnehmerin» (Phasen, Zeitbudget, Measures, Rückfluss).
2. Kennzahlen: Anteil belegter Atome, Anteil `configuration` an allen Measures, Anzahl abgelehnter Anpassungen, offene Artefakte.
3. Sichtbarer Hinweis im Kopf, wenn `conflict_of_interest` gesetzt ist.
4. Klickpfad: Jede Aussage ist auf ihr Atom und dessen Quelle klickbar.
5. Weiterhin eine HTML-Datei, alles eingebettet, keine externen Skripte, Schriften oder CDNs, funktioniert offline. Tests für jede Eigenschaft (z. B. keine externen URLs im Output).

Gate 2 (am Ende ausführen):
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
.venv/Scripts/adoptionkit.exe view examples/synthetic-municipality/engagement.json -o out.html
Gate 2 gilt als bestanden, wenn eine aussenstehende Person in unter zwei Minuten alle offenen Punkte eines Dossiers findet. Das kannst du nicht selbst messen: Bereite den Test vor (Aufgabenblatt für eine Testperson, Stoppuhr) und halte fest, dass er mit Hayal durchzuführen ist.

Commits klein und sprechend, jede Message endet mit der Co-Authored-By-Zeile gemäss Konvention. Schliesse mit einem kurzen Abschlussbericht: Status, Commits, Testzusammenfassung, offene Punkte.
```

## Stufe 3: Skill

**Umfang:** Skill `ai-rollout` ausbauen und nach `superpowers:writing-skills` auf Wirksamkeit testen, mit drei Szenarien: fehlende Quelle, Wunsch nach Neuentwicklung, Bitte um rechtliches Urteil. Baseline ohne Skill, dann mit Skill, dann erneuter Test.

**Gate 3:** In allen drei Szenarien verhält sich die Session mit Skill messbar anders als die Baseline.

**Start-Prompt:**

```
Arbeite im Repo ~\deploykit (Python-Paket `adoptionkit`; kurzer Pfad). Wir setzen Stufe 3 (Skill) um.

Lies zuerst: docs/BAUPLAN.md (Abschnitte 8 und 12), docs/DECISIONS.md, docs/ROADMAP.md, skills/ai-rollout/SKILL.md, skills/ai-rollout/references/atom-format.md, CLAUDE.md und die globale CLAUDE.md. Halte dich an deren Konventionen: Verifikation vor jeder Erfolgsmeldung, Schweizer Rechtschreibung (nie das Eszett), kein `git push`, kein `gh repo create`. Der Skill ist ein bestehender Skill: nutze `superpowers:writing-skills` (Baseline ohne Skill, dann mit Skill, dann Re-Test); `skill-creator` ist nicht nötig.

Umfang Stufe 3:
1. Drei Testszenarien als Dateien unter tests/ oder skills/ai-rollout/evals/ festhalten (synthetisches Rohmaterial): (a) fehlende Quelle zu einer Aussage, (b) Wunsch nach Neuentwicklung ohne Produktentscheid, (c) Bitte um ein rechtliches Urteil.
2. Baseline: Szenarien ohne Skill ausführen, Verhalten wörtlich festhalten (Unterlagen unter docs/ oder skills/ai-rollout/evals/).
3. Skill überarbeiten, mit Skill erneut ausführen, Unterschied pro Szenario belegen; Lücken schliessen und erneut testen.
4. Der Skill muss die Regeln halten: nachfragen statt ergänzen, `answer` nie selbst setzen, kein rechtliches Urteil (Hinweis «Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.»), Beschlüsse und Zahlen gehören der Person.
5. Nach Stufe 3 trägt der Skill keinen v0-Vermerk mehr; Strukturtest (tests/test_skill.py) anpassen.

Gate 3 (am Ende ausführen):
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
Gate 3 gilt als bestanden, wenn sich in allen drei Szenarien die Session mit Skill messbar von der Baseline unterscheidet; belege das mit den festgehaltenen Läufen.

Commits klein und sprechend, jede Message endet mit der Co-Authored-By-Zeile gemäss Konvention. Schliesse mit einem kurzen Abschlussbericht: Status, Commits, Testzusammenfassung, offene Punkte.
```

## Stufe 4: Praxistest

**Umfang:** Ein realer Fall, rückwirkend erfasst; mindestens ein Fall mit einem Fremdprodukt. Die Daten bleiben lokal und kommen nicht ins Repo. Schema-Änderungen, die der Praxistest zeigt, werden eingearbeitet; Version 0.1.0 wird getaggt.

**Gate 4:** Schema-Änderungen aus dem Praxistest sind eingearbeitet; Version 0.1.0 getaggt.

**Start-Prompt:**

```
Arbeite im Repo ~\deploykit (Python-Paket `adoptionkit`; kurzer Pfad). Wir setzen Stufe 4 (Praxistest) um.

Lies zuerst: docs/BAUPLAN.md (Abschnitt 12), docs/DECISIONS.md, docs/ROADMAP.md, CLAUDE.md und die globale CLAUDE.md. Halte dich an deren Konventionen: testgetrieben, Verifikation vor jeder Erfolgsmeldung, Schweizer Rechtschreibung (nie das Eszett), kein `git push`, kein `gh repo create`. Die Release-Abschlusskette der globalen CLAUDE.md gilt (verification-before-completion, github-repo-Prüfung, finishing-a-development-branch).

Wichtig: Reale Daten bleiben lokal und kommen NICHT ins Repo (auch nicht in Tests, Beispiele, Commit-Messages oder Issues). Lege den realen Fall ausserhalb des Repos oder in einem .gitignore-Ordner ab. Frage Hayal, welcher Fall rückwirkend erfasst wird und wo die Rohdaten liegen, bevor du beginnst.

Umfang Stufe 4:
1. Den realen Fall rückwirkend mit dem Skill `ai-rollout` und der CLI erfassen (init, Atome, Gates, lint, view). Mindestens ein Fall mit einem Fremdprodukt.
2. Reibungspunkte und Schema-Lücken protokollieren (nur abstrakt, ohne reale Inhalte) und die nötigen Schema- und Profiländerungen testgetrieben einarbeiten; schema_version und Schema-Datei neu erzeugen (`python -m adoptionkit.schema_gen`).
3. Version auf 0.1.0 anheben (pyproject, CHANGELOG-Datum) und taggen, erst nach bestandener Abschlusskette. Kein Push.

Gate 4 (am Ende ausführen):
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
git tag --list v0.1.0
Gate 4 gilt als bestanden, wenn die Schema-Änderungen aus dem Praxistest eingearbeitet sind und Version 0.1.0 getaggt ist.

Commits klein und sprechend, jede Message endet mit der Co-Authored-By-Zeile gemäss Konvention. Schliesse mit einem kurzen Abschlussbericht: Status, Commits, Testzusammenfassung, offene Punkte.
```

## Stufe 5: Anschluss

**Umfang:** Import von journeykit-Journeys und personakit-Personas als Evidenzquellen. Ein MCP-Server erst, wenn ein konkreter Bedarf vorliegt.

**Gate 5 (Vorschlag, im Bauplan nicht festgelegt):** Importierte Journeys und Personas erscheinen als Atome mit `source.ref` auf die Ursprungsdatei; Validierung und Lints laufen darüber; Tests mit synthetischen Fixtures sind grün.

**Start-Prompt:**

```
Arbeite im Repo ~\deploykit (Python-Paket `adoptionkit`; kurzer Pfad). Wir setzen Stufe 5 (Anschluss) um.

Lies zuerst: docs/BAUPLAN.md (Abschnitt 12), docs/DECISIONS.md, docs/ROADMAP.md, CLAUDE.md und die globale CLAUDE.md. Halte dich an deren Konventionen: testgetrieben, Verifikation vor jeder Erfolgsmeldung, Schweizer Rechtschreibung (nie das Eszett), kein `git push`, kein `gh repo create`. Das Paket bleibt offline: keine Netzwerkzugriffe, keine Modellaufrufe.

Umfang Stufe 5:
1. Schau dir die Formate der Schwester-Repos journeykit (journey.json) und personakit (Personas) read-only an (lokale Kopie oder `gh api`, nichts auf GitHub ändern). Halte in docs/DECISIONS.md fest, welche Felder auf welche Atom-Typen abgebildet werden.
2. Implementiere einen Import (z. B. `adoptionkit import <quelle> --into <engagement.json>`), der Journeys und Personas als Evidenz-Atome übernimmt: je Aussage ein Atom mit `source.ref` auf die Ursprungsdatei, Status nach Evidenzklasse der Quelle (nie stillschweigend `evidenced` für Angenommenes). Mit synthetischen Fixtures und zuerst fehlschlagenden Tests.
3. Einen MCP-Server NICHT bauen, ausser Hayal nennt einen konkreten Bedarf; frage am Anfang nach.
4. README, CHANGELOG und ROADMAP aktualisieren.

Gate 5 (am Ende ausführen):
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pyright
.venv/Scripts/adoptionkit.exe validate <Importergebnis aus der Fixture>
Gate 5 gilt als bestanden, wenn importierte Journeys und Personas als Atome mit `source.ref` erscheinen und Validierung und Lints darüber laufen.

Commits klein und sprechend, jede Message endet mit der Co-Authored-By-Zeile gemäss Konvention. Schliesse mit einem kurzen Abschlussbericht: Status, Commits, Testzusammenfassung, offene Punkte.
```
