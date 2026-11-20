# Entscheide

Festgehalten in der ersten Session (Stufe 0), 20.11.2026. Grundlage: `docs/BAUPLAN.md`, Abschnitt 2.

## E1 – Name: `adoptionkit`

Geprüft am 20.11.2026:

| Name | PyPI | GitHub (Suche im Repo-Namen) | Befund |
|---|---|---|---|
| deploykit | belegt (`0.0.1a1`, Deployment von Deep-Learning-Modellen) | 104 Treffer, u. a. `docker-archive/deploykit` (Infrastruktur, über 2000 Sterne) | nicht frei, Verwechslung mit CI/CD und Infrastruktur |
| rolloutkit | belegt (Messung von Container-Start und -Stopp) | Feature-Flag-Engine in JavaScript | nicht frei, Verwechslung mit Feature-Rollouts |
| adoptkit | frei | ein Repo mit fast gleichem Zweck («adoption pack») | verwechselbar |
| **adoptionkit** | frei | 0 Treffer | **gewählt** |
| pilotkit | frei | 10 kleine Repos | deckt nur die Prototyp-Phase ab |

Folgen:

- Paket `adoptionkit`, Import `adoptionkit`, CLI `adoptionkit`.
- Wo der Bauplan `deploykit` schreibt (CLI-Befehle, Gate 0), gilt `adoptionkit`.
- Der lokale Ordner heisst vorläufig weiter `~\deploykit`. Den Ordner umbenennen und das GitHub-Repo anlegen macht Hayal.
- `docs/BAUPLAN.md` bleibt unverändert als historisches Dokument.

## E2 – Skill-Name: `ai-rollout`

Ablage `skills/ai-rollout/SKILL.md`. Der Name beschreibt die Tätigkeit und ist unabhängig vom Paketnamen.

## E3 – Synthetischer Beispielfall

«Anfragen-Assistent für die Einwohnerdienste der fiktiven Gemeinde Seewil». Eingeführt wird das fiktive Fremdprodukt «AskDesk» der fiktiven Firma «Beispiel Software AG». Ablage `examples/synthetic-municipality/`. Alle Personen, Organisationen und Abläufe sind erfunden und als synthetisch gekennzeichnet.

## E4 – Sprache

- Bezeichner in Code und Schema: Englisch.
- Checklisten-Texte und Doku: Deutsch, Schweizer Rechtschreibung (ss statt ß).
- README zweisprachig: `README.md` (EN), `README.de.md` (DE).

## Weitere Entscheide in Stufe 0

- **Build-Backend und Ruff-Regeln wie bei journeykit:** setuptools, `src`-Layout, ruff mit `E,F,W,I,UP`. Abweichend vom Bauplan nicht, nur ergänzend.
- **Schema aus den Modellen:** `engagement.schema.json` wird mit `python -m adoptionkit.schema_gen` erzeugt und eingecheckt; ein Test vergleicht beide.
- **Gate-Ergebnis `stopped`:** Ein Gate gilt als `stopped`, wenn eine Frage mit `stop_if` im Profil der gegebenen Antwort entspricht (`yes` oder `no`) und die Antwort belegt ist. G0 liefert dann die Empfehlung `decline`.
- **L005 nur für gestartete Phasen:** Das Abbruchkriterium ist ab `prototype` Pflicht, sobald die Phase nicht mehr `planned` ist. Sonst wäre jedes frisch mit `init` angelegte Dossier sofort blockiert.
- **Profilname aus der Datei nur als mitgeliefertes Profil:** `meta.profile` löst nur auf Profile im Paket auf (Muster `a-z`, `0-9`, `-`). Dateipfade gelten nur über `--profile`. Grund: keine Netz- oder UNC-Zugriffe aus fremden Dossiers.
- **R9 ignoriert L007-Befunde zum ausgewerteten Gate:** Sonst blockiert L007 genau die Auswertung, die den Befund auflösen würde (Selbstblockade). Andere Fehler blockieren weiterhin.
