# OpenSeesPy seismic research — V167

**[00 — Ordered launchers](00_READ_FIRST_RUN_ORDER.md)** · **[Per-program manuals](docs/programs/00_PROGRAM_INDEX.md)** · **[All 20 old/new filenames](docs/00_WORK_ORDER_RENAME_MAP.md)** · **[Baseline handoff](START_HERE_V167.md)**

The 20 primary executable entry points now use work-order numbers 01–20. The previous filename for each remains a compatibility alias. This ordering prioritizes input reconciliation and material/component validation before whole-building nonlinear analysis. Internal Python modules, earthquake records, research results and historical exports retain their existing names.

**Open blocker:** The full-building nonlinear time history still has an unresolved first-step transient failure; no complete validated NLTHA or certified optimum is claimed. The rename itself has not been validated by a native solver run.

[Research modeling basis](Research_Components/02_MODELLING_BASIS.md) · [Organization policy](docs/00_REPOSITORY_ORGANIZATION.md)


**V169 nonlinear diagnostic enhancement:** [21 — NLTHA triage](docs/programs/21_NLTHA_TRIAGE.md) generates isolated ZERO/X/Y/XY probes, validates accelerogram quality and records explicit full-record evidence gates. Existing first-step failure is not resolved.

## Research source documentation

- [Guides for all 84 active Python modules](docs/source/00_SOURCE_GUIDE_INDEX.md)
- [Scientific reference and citation register](docs/00_RESEARCH_REFERENCES.md)
- [Thesis NLTHA acceptance gates](docs/00_THESIS_ACCEPTANCE_GATES.md)
- [Contributor / ChatGPT / Codex instructions](AGENTS.md)

This documentation does not certify native solver convergence or project-specific material calibration.

## Stage 01–06 NLTHA implementation (Nov 2026)

The exploratory runner now includes physical wall geometry preflight (stage 01), opt-in source-approved frame reinforcement mapping (02), declared wall opening occupancy checks (03), accepted-step FVD/BRB recorder demand channels (04), chronological full-duration evidence gates (05), and a fail-closed M0–M6 research comparison executable (06). See docs/programs/22_WALL_FAILURE_AUDIT.md through 27_M0_M6_OUTRIGGER_COMPARISON.md. These are engineering validation capabilities **not** a claim that the first-step X wall solver failure is resolved or that all seismic records and variants converged.


[Six-stage NLTHA implementation and validation guide](docs/00_NLTHA_SIX_STAGE_EXECUTION_GUIDE.md) covers executed code changes, source inputs and unsolved physical validation tasks.

## Historical version organization

Superseded root versioned reports, manifests and logs are stored under [archive/previous_versions](archive/previous_versions/README.md), grouped by filename family. Only the latest version in each family stays at root, except two older Python compatibility facades still consumed by the GUI. The archive manifest documents those exceptions and exact original hashes.


The [expanded visual material workbench](docs/programs/06_MATERIAL_DEVICE_VALIDATION_EXPANDED.md) retains V149 Concrete01/Steel02/FVD/BRB plots and adds Concrete02/ConcreteCM/SteelMPF/E-SFI panels plus full research catalog and calibration tools.

## Evidence-based nonlinear model readiness

The main ETABS workflow **OpenSees nonlinear readiness / calibration status** button opens the [model-bound readiness dashboard](docs/programs/02_NONLINEAR_READINESS_EVIDENCE_DASHBOARD.md) instead of a static nine-item warning. Evidence presence, reviewer sign-off and numerical validation are different categories; no automatic analysis approval is granted.


**2026-11 research update:** [Verified NBC 105:2025 NLTHA clauses, OpenSees implementation and recent research evidence](docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md). The new optional strict metadata precheck does not approve real model behavior or a completed earthquake analysis.
