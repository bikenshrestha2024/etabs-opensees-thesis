# Repository architecture — canonical folder ownership

| Location | Owns | When to add/edit | Why it stays here | Who checks |
|---|---|---|---|---|
| Root numbered launchers | Supported Spyder/Windows entry points | Only when canonical registry/guide and callers are audited | Compatibility contract | Software maintainer |
| `components/model/` | Source-neutral structural assembly, readiness evidence | Geometry/assembly/readiness changes | Prevents confusing model source with UI | Structural + code reviewer |
| `components/gravity/` | Gravity load path, reactions and source comparison | Gravity workstream | Keeps unit/system reconciliation isolated | Structural reviewer |
| `components/modal/` | Eigen and modal evidence | Modal workstream | Separate from seismic acceptance | Earthquake engineer |
| `components/response_spectrum/` | Elastic spectrum analysis | RSA workstream | Distinct from time-history | Earthquake engineer |
| `components/linear_time_history/` | Elastic transient + GUI | LTH workstream | Separate native response from NLTHA | Numerical/software reviewer |
| `components/nonlinear_time_history/` | Wall physics, records, NLTHA, variant comparisons | NLTHA and first-step diagnosis | Preserves nonlinear reproducibility | Numerical + structural reviewer |
| `components/shared/` | Used by multiple modules (recorders, helpers) | Only when a common abstraction already exists | Avoids divergent record conventions | All affected modules' maintainers |
| `Material_Catalog/` | Parameter source cards | New verified literature source or benchmark | Reference values are not production project data | Materials researcher |
| `LITERATURE/` | DOI, article index, source citation and license | Every sourced claim/parameter | Paper and PDF access provenance | Researcher |
| `tests/` | Deterministic engineering/software regressions | With every code change | Guard existing sign conventions/imports | Code maintainer |
| `docs/source/` | Detailed guide per Python module | New/changed module | Trace command behavior | Code author + engineer |
| `KNOWLEDGE_BASE/` | Cross-disciplinary 5W1H discovery and navigation | New module responsibility or method | No duplicated executable implementations | Documentation maintainer |
| `engineering/registry/` | Canonical module ownership and migration contracts | Before moving/renaming canonical code | Traceable ownership | Architecture reviewer |
| `REVIEW_MAIN/` | Missing evidence, discrepancies and decisions | Every unresolved physics/results discrepancy | Avoids hiding failed cases | Engineering reviewer |
| `archive/`, `Saved_Project_V156/` | Historical context | Reproduction only | Immutable compatibility evidence | Repository maintainer |

**Physical relocation policy:** DO NOT move/delete active files merely to improve aesthetics. First map imports, launcher consumers, output readers, tests, legacy Windows shortcuts and citation links; freeze hashes; propose migration in a PR; run full regression/native checks; only then migrate. A new README/index in the correct folder is safer than changing an established Python import path.

## Naming for new contributions

- Canonical source `components/<domain>/<function>.py`; no `*_fixed.py` or `*_latest.py` proliferations.
- Tests `tests/test_<behavior>.py`; matching `docs/source/.../<module>.py.md`.
- Evidence `REVIEW_MAIN/<domain>/<YYYYMMDD>_<scope>.md`; model-bound output kept outside public repo.
- Bibliography stays in `LITERATURE/<engineering_use>/README.md` with stable master IDs and DOI.
- Change log includes WHEN (date/commit), WHY (issue), HOW (diff/tests), WHERE (paths), WHICH (inputs/outputs), WHO (editor + accountable reviewer role).
