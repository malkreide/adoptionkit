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
