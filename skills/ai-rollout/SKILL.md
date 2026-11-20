---
name: ai-rollout
description: Führt durch die belegbasierte Einführung einer KI-Lösung in einer Organisation (Discovery, Prototyp, Wertnachweis, Härtung, Übergabe) und steuert dafür die lokale CLI adoptionkit (init, validate, lint, gate, view). Zerlegt Rohmaterial in Evidenz-Atome, markiert Annahmen als assumed und schlägt Gate-Antworten nur vor. Verwenden bei «KI-Einführung planen», «Rollout», «Gate G0 prüfen», «Interviewnotizen auswerten», «Dossier anlegen», «Eignungsprüfung», «Übergabe vorbereiten», oder auf Englisch "AI rollout", "adoption dossier", "evidence atoms", "gate check", "go/no-go for an AI solution". Auch verwenden, wenn eine engagement.json vorliegt. v0, Wirksamkeitstest folgt in Stufe 3.
---

# ai-rollout (v0 – Wirksamkeitstest folgt in Stufe 3)

Dieser Skill begleitet die Einführung einer KI-Lösung als nachvollziehbare Abfolge: Rohmaterial wird zu belegten Atomen, Atome stützen Gate-Antworten, Gates steuern die Phasen. Die einzuführende Lösung ist ein Parameter (`solution.name` im Dossier), der Skill ist produktneutral.

Das Paket `adoptionkit` arbeitet lokal: keine Netzwerkzugriffe, keine Modellaufrufe. Der Skill steuert nur die CLI und bearbeitet die Dossier-Datei `engagement.json`. Das Atom-Format steht in `references/atom-format.md`.

## Verbindliche Regeln

Diese Regeln gelten immer. Sie schützen davor, dass ein Dossier mehr behauptet, als belegt ist.

1. **Fehlende Quelle: nachfragen, nicht ergänzen.** Fehlt zu einer Aussage Quelle, Datum oder Urheber, frage die Person danach. Erfinde nichts und fülle nichts aus Allgemeinwissen auf.
2. **Nichts Unbelegtes ins Dossier.** Jede Aussage wird ein Atom mit `source.ref`. Ist die Aussage nur eine Vermutung, setze `status: assumed`. Eine Annahme schliesst nie ein Gate (siehe unten); sie zeigt, was noch zu belegen ist.
3. **Gate-Fragen nie selbst mit `yes` oder `no` beantworten.** Schlage eine Antwort vor, nenne die Atom-IDs, die sie stützen, und lass die Person bestätigen. Erst nach der Bestätigung trägst du `answer` und `atom_refs` ein. Ohne Beleg bleibt die Antwort `unclear`.
4. **Keine rechtlichen Urteile.** Äussere nie, ob etwas rechtskonform, zulässig oder bewilligungsfähig ist. Verweise stattdessen auf den Hinweis: «Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.»
5. **Beschlüsse und Zahlen gehören der Person.** Budgets, Abbruchkriterien und Produktentscheide trägst du nur ein, wenn die Person sie genannt hat.

## Ablauf

### 1. Dossier anlegen

```
adoptionkit init <ordner> --profile generic --title "<Titel>" --id <kennung>
```

Legt `engagement.json` und `evidence/` an. Profil `generic` ist gebündelt; `--profile` nimmt auch einen Dateipfad. Fülle `parties` und `solution` aus den Angaben der Person, leere Felder bleiben leer, bis sie belegt sind. Rohmaterial (Notizen, Dokumente) gehört nach `evidence/`; `source.ref` zeigt auf diese Dateien.

### 2. Rohmaterial in Atome zerlegen

Lies das Material und zerlege es in einzelne, einzeln belegbare Aussagen (ein Atom je Aussage):

- Wähle den Typ: `requirement`, `constraint`, `data_source`, `risk`, `usage_signal`, `decision`.
- Setze die Quelle: `kind`, `ref` (Datei oder System), wenn bekannt `date` und `quote` (wörtliches Zitat).
- Setze `status`: `evidenced`, wenn das Material die Aussage trägt; `assumed`, wenn sie nur vermutet oder abgeleitet ist; `refuted`, wenn eine Quelle sie widerlegt.
- Vergib die nächste freie ID `A-001`, `A-002` usw.

Zeige der Person die vorgeschlagenen Atome als Liste, bevor du sie in die Datei schreibst, und frage bei jeder fehlenden Quelle nach (Regel 1). Details und Beispiele: `references/atom-format.md`.

### 3. Prüfen

```
adoptionkit validate <datei>
adoptionkit lint <datei> [--json] [--profile <name|pfad>]
```

`validate` prüft Schema und Verweise. `lint` meldet Lücken (Exit-Code 1 bei Fehlern):

| Code | Stufe | Bedeutung |
|---|---|---|
| L001 | error | Atom ohne Quellenverweis |
| L002 | warning | Measure stützt sich auf eine Anforderung mit Status `assumed` |
| L003 | warning | Measure ohne Atom-Verweise |
| L004 | error | Neuentwicklung ohne Produktentscheid (Atom vom Typ `decision`) |
| L005 | error | Gestartete Phase ab `prototype` ohne Abbruchkriterium |
| L007 | error | Phase gestartet oder abgeschlossen, ohne dass das geforderte Gate bestanden ist |

Behebe Befunde nicht durch Erfinden: bei L001 nach der Quelle fragen, bei L004 und L005 die Person entscheiden lassen. Weitere Lint-Regeln gibt es in Stufe 0 nicht.

### 4. Gates auswerten

Phasen: `discovery`, `prototype`, `value_proof`, `hardening`, `handover`. Gates: G0 bis G4 (das Profil `generic` definiert G0, G3, G4). Jedes Gate ist eine Checkliste; jede Check-Frage hat `answer` (`yes`, `no`, `unclear`, `n/a`) und `atom_refs`.

Vorgehen je Gate:

1. Gehe die offenen Check-Fragen mit der Person durch. Schlage je Frage eine Antwort vor und nenne die Atome dazu (Regel 3). Fehlt ein Beleg, stelle den Beleg-Auftrag, nicht die Antwort.
2. Nach Bestätigung trage `answer` und `atom_refs` in der Gate-Checkliste ein.
3. Führe aus:
   ```
   adoptionkit gate <datei> G0 [--profile <name|pfad>] [--today YYYY-MM-DD]
   ```
   Der Befehl schreibt das Ergebnis in die Datei, nennt Gründe und gibt den Hinweis aus.

Regeln der Auswertung (der Code ist massgeblich, nicht deine Einschätzung):

- Ergebnis `passed`, `open` oder `stopped`.
- `yes` oder `no` zählt nur mit mindestens einem Atom im Status `evidenced` in `atom_refs`; sonst bleibt die Frage offen («nicht belegt»).
- Atome mit Status `assumed` schliessen kein Gate.
- `unclear` hält das Gate offen, `n/a` wird übersprungen.
- Lint-Fehler blockieren `gate`: die Datei bleibt unverändert, behebe zuerst die Befunde.
- G0 liefert zusätzlich eine Empfehlung (`guided_rollout`, `standard_rollout`, `decline`).

Gib das Ergebnis wieder, ohne es rechtlich zu deuten. Bei `open` nennst du, welche Belege fehlen; bei `stopped` nennst du die Abbruchbedingung und überlässt die Entscheidung der Person.

### 5. Phasen führen

Jede Phase ab `prototype` braucht ein `abort_criterion` und ein bestandenes Gate, bevor sie gestartet wird (L005, L007). Frage nach Budget (`budget_days`) und Abbruchkriterium, statt Werte vorzuschlagen, die niemand genannt hat. Setze `status` erst auf `running` oder `done`, wenn die Person es bestätigt, und führe danach `lint` aus. Massnahmen (`measures`) verweisen mit `atom_refs` auf ihre Belege; Neuentwicklungen brauchen einen Produktentscheid als Atom.

### 6. Dossier ansehen

```
adoptionkit view <datei> [-o dossier.html]
```

Erzeugt eine eigenständige HTML-Datei zum Lesen und Weitergeben. Verweise beim Weitergeben auf den Hinweis (Regel 4).

## Beispiel

`examples/synthetic-municipality/` enthält ein vollständig synthetisches Dossier (fiktive Gemeinde, fiktive Lösung) mit Notizen unter `evidence/`. Es dient als Vorlage für Form und Detailgrad.

## Abgrenzung

- Der Skill ersetzt weder Rechts-, Datenschutz- noch Sicherheitsprüfung.
- Der Wirksamkeitsnachweis (Baseline ohne Skill gegen mit Skill) folgt in Stufe 3. Bis dahin ist der Skill v0.
