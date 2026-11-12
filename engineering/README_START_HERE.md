# START HERE — ETABS–OpenSees Thesis
**New beginner-facing navigation for an existing research codebase. No solver code was changed by this guide.**
Thesis: *Time History Analysis of Damped Outrigger System in High Rise Building with Asymmetric Plan*. Research variants M0 through M6 compare conventional/damped outriggers, belt and cap trusses in an asymmetric RC high-rise.

## Choose your topic

**Thesis discrepancy and independent verification:** [07 — Review backbone](../07_REVIEW_MAIN/README.md) (numbered entry), with all authoritative cases retained in [REVIEW_MAIN](../REVIEW_MAIN/README.md).

| Area | Start with | Implementation currently located in |
| --- | --- | --- |
| ETABS | [Source and native result extraction](topics/ETABS.md) | Existing root exporters, `components/validation/` |
| OpenSees | [Models, analysis, materials](topics/OPENSEES.md) | `components/model/`, `components/sections/`, `components/modal/`, `components/nonlinear_time_history/` |
| Integration | [ETABS↔OpenSees comparison](topics/INTEGRATION.md) | `components/gravity/`, `components/validation/`, `components/inputs/` |
| Python | [Windows, Spyder, conda](topics/PYTHON.md) | `tools/`, `tests/`, root launchers |
| AI and tokens | [All assistants](topics/AI_AGENTS.md) | `AGENTS.md`, `.agents/`, `.claude/`, `engineering/rules/` |
| Thesis evidence | [Engineering references and validation](topics/RESEARCH.md) | `Research_Components/`, `docs/`, `engineering/migration/` |

## Safe run order
Verify actual current source EDB and workbook -> export/assemble -> compare 32-support gravity -> modal -> NBC ESM / RSA / PDelta -> component calibration and dedicated ZERO/X/Y/XY nonlinear diagnosis -> full XY/YX Soil C matrix only when its acceptance gates pass.
[Current launcher index](../docs/programs/00_PROGRAM_INDEX.md) and [historical run order](../00_READ_FIRST_RUN_ORDER.md) are the executable entry references. Avoid old saved runtime folders unless reproducing an explicitly dated result.

## How to interpret results
A working solver, passed Python unit test or created evidence ZIP does **not** establish ETABS equivalence, experimental validation or NBC code acceptance. Read [engineering gates](rules/ENGINEERING_GATES.md) and [known source migration status](migration/README.md).

## Architecture goal
ETABS integrated model today, independent OpenSees model later, and benchmark specimens should ultimately use a single canonical OpenSees numerical core. See [boundaries](rules/MODULE_BOUNDARIES.md). This is a planned migration, not a claim that standalone building analysis already works.
