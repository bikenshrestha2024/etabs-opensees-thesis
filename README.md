# OpenSeesPy seismic research — V167

**[00 — Ordered launchers](00_READ_FIRST_RUN_ORDER.md)** · **[Per-program manuals](docs/programs/00_PROGRAM_INDEX.md)** · **[All 20 old/new filenames](docs/00_WORK_ORDER_RENAME_MAP.md)** · **[Baseline handoff](START_HERE_V167.md)**

The 20 primary executable entry points now use work-order numbers 01–20. The previous filename for each remains a compatibility alias. This ordering prioritizes input reconciliation and material/component validation before whole-building nonlinear analysis. Internal Python modules, earthquake records, research results and historical exports retain their existing names.

**Open blocker:** The full-building nonlinear time history still has an unresolved first-step transient failure; no complete validated NLTHA or certified optimum is claimed. The rename itself has not been validated by a native solver run.

[Research modeling basis](Research_Components/02_MODELLING_BASIS.md) · [Organization policy](docs/00_REPOSITORY_ORGANIZATION.md)


**V169 nonlinear diagnostic enhancement:** [21 — NLTHA triage](docs/programs/21_NLTHA_TRIAGE.md) generates isolated ZERO/X/Y/XY probes, validates accelerogram quality and records explicit full-record evidence gates. Existing first-step failure is not resolved.
