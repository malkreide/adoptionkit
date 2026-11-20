# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach
[Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

Stufe 0 (Skelett), Stand 2026-11-20.

### Added

- Python-Paket `adoptionkit` (`src`-Layout) mit CLI: `init`, `validate`, `lint`, `gate`, `view`.
- Datenmodell mit Evidenz-Atomen, Phasen, Gates, Massnahmen, Evaluation, Artefakten und Übergabe;
  JSON-Schema aus den Modellen erzeugt und eingecheckt.
- Lints L001–L005 und L007.
- Gate-Mechanik mit YAML-Profilen; Profil `generic` mit G0, G3 und G4; Hinweis «Arbeitshilfe,
  keine Rechtsberatung».
- Synthetischer Beispielfall «AskDesk in Seewil» (`examples/synthetic-municipality/`) mit zwei
  beabsichtigten Lint-Befunden.
- Minimaler Einzeldatei-Viewer (Phasen, Gates, Atome), offline lauffähig.
- Claude-Skill `ai-rollout` (v0) mit Referenz zum Atom-Format.
- Dokumentation: `docs/BAUPLAN.md`, `docs/DECISIONS.md`, `docs/SOURCES.md`, `docs/ROADMAP.md`.
- Zweisprachiges README (`README.md`, `README.de.md`), `CONTRIBUTING.md`, `SECURITY.md`.
- CI (GitHub Actions), Dependabot und Repo-Metadaten.
- Repo-Regeltests: keine Eszett-Schreibung, keine Rollenbezeichnung aus den Quellen ausserhalb der
  Quellenliste, keine Netzwerk-Importe in `src/`, Lizenzhalterin in `LICENSE`.

### Fixed

- `gate` kann die Datei nicht mehr leeren: atomares Speichern (Temporärdatei und `os.replace`);
  `validate` meldet nicht als UTF-8 kodierbare Texte; `view` meldet Kodierfehler mit Exit-Code 1.
- Hinweistext der Gates im Schema fixiert (abweichende Werte sind ungültig); der Viewer setzt die
  Konstante ein und liest den Text nicht aus der Datei.
- L007 wertet Gates frisch aus statt dem gespeicherten Ergebnis zu trauen; `Finding.gate_id`
  ersetzt den Textvergleich im R9-Filter.
- Check-ID-Präfix muss zum Gate passen; Standard-ID von `init` wandelt Umlaute um
  («Ärger» wird «aerger»); Hinweis auf `--profile <pfad>` bei unbekanntem Profil; «1 Befund»
  im Singular; Viewer zeigt Anbieter ohne doppelte Klammern.
- README-Schnellstart kopiert das Beispiel vor `gate`.
- CI: Wheel-Job prüft, dass Schema, Profile und Vorlagen im Paket enthalten sind;
  Netzwerk-Import-Regeltest arbeitet über den AST.
