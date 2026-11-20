# Atom-Format

Ein Atom ist eine einzelne, einzeln belegbare Aussage im Dossier (`atoms` in `engagement.json`, Schema 0.1). Zusätzliche Felder sind nicht erlaubt.

| Feld | Inhalt |
|---|---|
| `id` | `A-` plus drei Ziffern, z. B. `A-007`; fortlaufend, eindeutig |
| `type` | `requirement`, `constraint`, `data_source`, `risk`, `usage_signal`, `decision` |
| `statement` | die Aussage, nicht leer; ein Sachverhalt je Atom |
| `source.kind` | `interview`, `document`, `system`, `analytics`, `regulation`, `workshop` |
| `source.ref` | Verweis auf die Quelle (z. B. `evidence/interview-xy.md`); fehlt er, meldet L001 einen Fehler |
| `source.date` | optional, `YYYY-MM-DD` |
| `source.quote` | optional, wörtliches Zitat |
| `status` | `evidenced`, `assumed`, `refuted` |

## Typen

- `requirement`: was die Lösung erfüllen soll.
- `constraint`: Rahmenbedingung (Technik, Organisation, Ressourcen).
- `data_source`: Daten, die benötigt oder genutzt werden.
- `risk`: benanntes Risiko.
- `usage_signal`: Beobachtung zur heutigen Nutzung oder Nachfrage.
- `decision`: getroffener Entscheid, etwa ein Produktentscheid (Voraussetzung für Neuentwicklung, L004).

## Status

- `evidenced`: die Quelle trägt die Aussage. Nur solche Atome schliessen Gate-Fragen.
- `assumed`: Vermutung oder Ableitung; trotzdem eine `source.ref` angeben (z. B. wer es vermutet hat). Schliesst nie ein Gate. Stützt eine Massnahme sich auf eine angenommene Anforderung, warnt L002.
- `refuted`: eine Quelle widerlegt die Aussage; das Atom bleibt im Dossier.

## Beispiele (synthetisch)

```json
{
  "id": "A-001",
  "type": "requirement",
  "statement": "Standardanfragen sollen innerhalb von fünf Arbeitstagen beantwortet werden.",
  "source": {
    "kind": "interview",
    "ref": "evidence/interview-einwohnerdienste.md",
    "date": "2026-08-25"
  },
  "status": "evidenced"
}
```

```json
{
  "id": "A-009",
  "type": "constraint",
  "statement": "Die Fachapplikation bietet vermutlich eine Schnittstelle für Auszüge.",
  "source": { "kind": "interview", "ref": "evidence/notiz-it-leitung.md" },
  "status": "assumed"
}
```

## Rohmaterial zerlegen

1. Jeden Satz mit Sachaussage einzeln prüfen; Mehrfachaussagen aufteilen.
2. Zuordnen: Typ, Quelle, Status.
3. Fehlt Quelle oder Datum: bei der Person nachfragen, nicht schätzen.
4. Meinungen und Vermutungen als `assumed` erfassen, nie als `evidenced`.
5. Der Person die Liste zeigen, erst dann schreiben; danach `adoptionkit validate` und `adoptionkit lint`.
