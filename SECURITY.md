# Sicherheit / Security

## Sicherheitslücken melden

Bitte melde Sicherheitslücken nicht über öffentliche Issues, sondern über GitHub:
**Security → Report a vulnerability** (GitHub Private Vulnerability Reporting bzw. Security
Advisories) im Repository `malkreide/adoptionkit`.

Beschreibe, was du gefunden hast, wie es sich reproduzieren lässt und welche Version betroffen ist.

*English:* Please report vulnerabilities privately via GitHub (Security → Report a vulnerability),
not through public issues.

## Rahmen

- `adoptionkit` macht keine Netzwerkzugriffe, keine Modellaufrufe und keine Telemetrie. Ein Test
  stellt sicher, dass `src/` keine Netzwerk-Bibliotheken importiert.
- Profile aus der Dossier-Datei (`meta.profile`) lösen nur auf mitgelieferte Profile auf; Dateipfade
  gelten nur über die Option `--profile`.
- Keine echten Daten ins Repo: Beispiel- und Testdaten sind synthetisch. Keine Zugangsdaten,
  keine personenbezogenen Daten, keine internen Dokumente committen.
