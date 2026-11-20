# adoptionkit

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-pre--alpha%20(stage%200)-orange)

> Evidence-based adoption of an AI solution in an organisation: evidence atoms, phases, gates as YAML checklists, lints, a single-file viewer and a Claude skill.

🇩🇪 [Deutsche Version](README.de.md)

> **Working aid, not legal advice.** The gates are checklists that surface open points. They never give a legal verdict. Clarify open points with the responsible specialist unit.
> (Fixed wording in every checklist: «Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.»)

## Purpose

adoptionkit structures the adoption of an AI solution in an organisation as an auditable pipeline: from discovery through prototype and proof of value to hardening and handover. Every statement is backed by evidence, and every phase change hangs on a gate.

- **Product-independent:** the solution being introduced is a parameter (own product, third-party product, open-source stack).
- **Role-neutral:** the same dossier serves the party that introduces the solution and the party that reviews and accepts it.
- **AI in the loop, not in the package:** the Python package calls no language model and makes no network access. AI support runs through the Claude skill `ai-rollout`, which operates the package.

Status: **pre-alpha, Stage 0** (skeleton). See `docs/ROADMAP.md`.

## Non-goals

- No project-management tool, no ticket system, no time tracking.
- No legal advice. Gates produce "needs clarification" with a reference to the source, never a legal verdict.
- No price, offer or capacity model.
- No tool for software deployment in the CI/CD sense.

## Installation

Not published on PyPI. Install from source (Python 3.11 or newer):

```bash
git clone https://github.com/malkreide/adoptionkit.git
cd adoptionkit
uv venv .venv
uv pip install --python .venv -e ".[dev]"
```

Or with plain pip: `pip install -e ".[dev]"`. The command is then `adoptionkit` (on Windows `.venv/Scripts/adoptionkit.exe`).

## Quickstart

The repository ships a synthetic example case: an enquiry assistant for the residents' services of the fictional municipality Seewil (`examples/synthetic-municipality/`). All data in it is invented.

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

The two warnings are intended: they show what the lints report.

```bash
adoptionkit gate engagement.json G0 --today 2026-09-07
```
```
G0: passed
Empfehlung: guided_rollout
Arbeitshilfe, keine Rechtsberatung. Offene Punkte mit der zuständigen Fachstelle klären.
```

`gate` writes the result into the file, so run it on a copy of the example. Finally, render a single HTML file that opens offline:

```bash
adoptionkit view examples/synthetic-municipality/engagement.json -o dossier.html
```

To start your own dossier: `adoptionkit init my-dossier --profile generic --title "..."`.

## CLI commands

| Command | Purpose | Status |
|---|---|---|
| `adoptionkit init <folder> [--profile] [--title] [--id]` | Create an empty dossier with the profile's gates and phases | available |
| `adoptionkit validate <file>` | Check against the JSON schema and integrity rules | available |
| `adoptionkit lint <file> [--json] [--profile]` | Lints L001–L005, L007 | available |
| `adoptionkit gate <file> <GATE_ID> [--profile] [--today]` | Evaluate a gate and write the result to the file | available |
| `adoptionkit view <file> [-o dossier.html]` | Minimal single-file viewer (phases, gates, atoms) | available |
| `adoptionkit status <file>` | Phases, gates, key figures | planned (Stage 1) |
| `adoptionkit export <file> --md` | Markdown report | planned (Stage 1) |

Exit codes: 0 = ok, 1 = finding, invalid input or error.

## Data model in brief

An engagement is one JSON file, `engagement.json`, validated against `engagement.schema.json` (generated from the models and checked in).

- `meta`, `parties`, `solution`: identification, parties, the solution being introduced.
- `atoms[]`: **evidence atoms**. One statement per atom, with a type (`requirement`, `constraint`, `data_source`, `risk`, `usage_signal`, `decision`), a source (`kind`, `ref`, `date`, optional `quote`) and a status (`evidenced`, `assumed`, `refuted`). No atom without `source.ref`; an `assumed` atom never closes a gate.
- `phases[]`: `discovery`, `prototype`, `value_proof`, `hardening`, `handover`, each with a budget in days, a status and, from `prototype` on, an abort criterion.
- `gates[]`: checklists with answers (`yes`, `no`, `unclear`, `n/a`), referenced atoms and a result (`passed`, `open`, `stopped`).
- `measures[]`, `evals`, `artefacts[]`, `handover`: adaptations, evaluation runs, feedback register, operators.

## Lints

| ID | Rule | Status |
|---|---|---|
| L001 | Atom without `source.ref` | implemented |
| L002 | Measure relies on a `requirement` that is only `assumed` | implemented |
| L003 | Measure without atom references | implemented |
| L004 | New development without a product decision | implemented |
| L005 | Started phase from `prototype` without abort criterion | implemented |
| L006 | Running phase over `budget_days` | planned (Stage 1) |
| L007 | Phase started although the required gate has not passed | implemented |
| L008 | Gate answer without an evidenced atom | planned (Stage 1) |
| L009 | `value_proof` without at least one `usage_signal` | planned (Stage 1) |
| L010 | Open artefact, last review older than 90 days | planned (Stage 1) |
| L011 | `handover` without operators | planned (Stage 1) |
| L012 | Conflict of interest empty although contractor and vendor match | planned (Stage 1) |

Severities: `error` (blocks `gate`) and `warning`. Output as text or with `--json`.

## Gates

Gates are YAML profiles. The package knows the gate mechanics; the questions live in the profile, so the kit stays independent of product and jurisdiction. Every question is an own formulation and carries a `source_ref` pointing to an ID in `docs/SOURCES.md`.

| Profile | Gates | Status |
|---|---|---|
| `generic` | G0 suitability, G3 evaluation, G4 handover | available |
| `ch-zh-public` | additionally G1 contract form, G2 public administration | planned (Stage 1) |

A gate is `passed` when no question is `unclear` and every `yes`/`no` answer references at least one evidenced atom. G0 also yields a recommendation (`guided_rollout`, `standard_rollout`, `decline`).

## Claude skill

`skills/ai-rollout/SKILL.md` (v0) guides a session through the dossier: it splits raw material into evidence atoms, marks assumptions as `assumed`, and only proposes gate answers. The effectiveness test follows in Stage 3.

## Limits

- Offline: no network access, no model calls, no telemetry. A test checks that `src/` imports no network library.
- Example data is synthetic. Do not commit real personal data or internal documents.
- Pre-alpha: the schema and the profiles may still change.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md), `docs/BAUPLAN.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`, [CHANGELOG.md](CHANGELOG.md).

## Licence

MIT, see [LICENSE](LICENSE). Copyright (c) 2026 Hayal Özkan.
