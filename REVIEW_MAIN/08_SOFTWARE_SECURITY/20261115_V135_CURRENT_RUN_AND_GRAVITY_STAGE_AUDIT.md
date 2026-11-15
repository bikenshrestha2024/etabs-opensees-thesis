# 2026-11-15 — V135 design checks: stale CSV risk and run-scoped output integrity

**Source evidence:** 2026-11-15 local user-provided `Design_Check_Report_V135.json`, `Design_Check_Output_Index_V135.json`, CSV tables, log, Excel and screenshot. Private model/data are not committed. Exact report model SHA256: `97def708661a10c165b6e0072b045ca7a0a82e13f021649bdb07c3a522a25f72`.

## Source-level verified results

- Report `overall=INCOMPLETE`, `evidence_status=SOURCE_IDENTITIES_REQUIRE_REVIEW`. Elapsed 8.2096 s; not a structural load-case run.
- 56 defined combination rows all `NOT EVALUATED`; zero signed action-basis rows in `Action_Basis_V135.csv`.
- 11,586 `Section_checks.csv` rows all `CAPACITY REQUIRED`, **not** strength-capacity verifications.
- 2,037 `Section_inventory.csv` rows all `NOT EVALUATED`; 153 `Project_deflection.csv` rows all `LIMIT REQUIRED` (total nodal UZ, not member chord-relative/long-term deflection).
- 14 open issues, including no ULS/SLS drift, nonlinear member/calibration/reinforcement, gravity-vs-seismic-mass, wall cracked EI and slab EI implementation.
- Zero current `Seismic_drift.csv`, `Combined_actions.csv`, `Missing_action_basis.csv`, and `Nonlinear_performance.csv` rows.
- Source `components/validation/design_checks.py::write_rows` intentionally retained same-name flat historical CSV when a table returned no rows. The V135 index accurately said `NO_CURRENT_ROWS_PRIOR_CSV_NOT_REPLACED`, but an operator browsing the directory could still open an older CSV and misread stale data. A current index is necessary but a file-level current-run folder is safer.

## Implementation and output contract

Keep the legacy V135 flat CSVs for compatibility. **New** `RUNS/<UTC_microseconds>_<unique-id>/TABLES/` contains every current derived table, including header-only CSV for zero-row results. Each run has its own manifest with the exact selected model SHA and counts. The existing stable `Design_Check_Output_Index_V135.json` now explicitly points to `current_csv` and `current_run_manifest` for the latest completed publication. Prior run CSVs and manifests remain immutable. The previous `status` field and stable report names remain available for backwards compatibility. No source EDB/Excel, physical analysis or adopted design capacities are changed. Synthetic regression tests verify stale historical file preservation, correct current empty tables, all count equality, and repeated-run immutability.

**Scope limitation:** this fixes evidence selection **within** `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135`. It does not solve the still unverified native 32/76/97 ETABS base support mapping, rigid-end-zone stiffness, wall/slab load path or complete root-level legacy file migration. The export root is still intentionally a legacy compatibility facade for numerous live readers; do **not** remove root files until every caller is redirected and tested.

## NBC design check evidence

- Official NBC 105:2025 §3.6.1 (pp. 19–20) provides combinations including `1.2DL+1.5LL`, `DL+lambda LL±E` and `0.9DL±E`; the V135 template labels are *definitions*, not completed member force actions.
- Table 3-1 (p. 19): wall cracked EI ULS 0.50 EcIg / SLS 0.70 EcIg; columns 0.70/0.90; beams 0.35/0.70; flat slabs 0.25/0.50. These are **modeling assumptions** that must be inspected in native ETABS/OpenSees element and stiffness data, not approved by a config value alone.
- NBC §§9.3.1–9.3.3 nonlinear acceptance requires constitutive and ground-motion evidence; cannot be established by section inventory and gravity equilibrium.
- Official source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf

**Status:** SOFTWARE_OUTPUT_CURRENT_RUN_EVIDENCE_FIXED_PENDING_CI; ENGINEERING_ACCEPTANCE_NOT_VERIFIED. Continue separate native case study under `REVIEW_MAIN/01_GRAVITY/20261115_FULL_76_SUPPORT_REACTIONS_AND_NATIVE_DISCREPANCY.md`.
