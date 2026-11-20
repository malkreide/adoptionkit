# Synthetischer Beispielfall: AskDesk in Seewil

**Synthetisch.** Alle Angaben in diesem Ordner sind erfunden und dienen nur zur Demonstration von adoptionkit. Es gibt keine realen Personen, Organisationen oder internen Abläufe.

## Der Fall

- Auftraggeberin: fiktive Gemeinde **Seewil**, Einwohnerdienste.
- Fremdprodukt: fiktives **AskDesk** der fiktiven **Beispiel Software AG** (Auskunftsassistent für Standardanfragen).
- Auftragnehmerin: fiktive **Beispiel Beratung GmbH**.
- Stand: Gate G0 ist bestanden (Empfehlung: begleiteter Rollout), die Phase `discovery` ist abgeschlossen, `prototype` läuft. G3 und G4 sind noch nicht beantwortet.

## Inhalt

- `engagement.json`: das Engagement mit Atomen, Phasen, Gates und Massnahmen.
- `evidence/`: erfundene Notizen (Interview, Workshop, Dokumente, Auswertung), auf die die Atome verweisen.

## Befehle

```bash
adoptionkit validate examples/synthetic-municipality/engagement.json
adoptionkit lint examples/synthetic-municipality/engagement.json
```

## Die zwei beabsichtigten Lint-Befunde

Der Fall enthält absichtlich genau zwei Warnungen, damit sichtbar wird, was die Lints melden. Beide blockieren `adoptionkit gate` nicht.

- **L002** bei `M-002`: Die Massnahme (englische Antwortvorlagen) stützt sich auf die Anforderung `A-006`, die nur angenommen (`assumed`) und nicht belegt ist.
- **L003** bei `M-004`: Die Massnahme (Eskalationsregel) verweist auf kein Atom.

Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.
