# 2026-11-23 — ETABS → OpenSees workflow continuation across modules

**Review scope:** current `main@b042f1583504c4f66bc54312232e5cf04013b077` and source-controlled change in draft PR #163. Reuses `20261123_ALL_MODULE_ETABS_OPENSEES_HANDOFF_AUDIT.md`, rather than replacing or claiming to repeat a whole-repository line-by-line semantic review. No private EDB, current full Excel, Windows native OpenSees solve, native ETABS database or 2026-11-23 solver-output ZIP was directly available.

## What changed in this iteration

The old MRSM `launch()` reopening behavior counted `COMPLETED` strings in `05_MRSM/MRSM_Batch_Status_V151.json` and displayed six numerical cases as complete without checking the active model JSON SHA, input parameters, ULS/SLS selection or actual saved `MRSM_Results_V132.json`.

A new saved-evidence gate uses the existing `CaseLedger`, `inspect_case_manifest`, and `validate_mrsm_case_output` instead of a second output scanner. New ledger fields preserve source-model SHA256, configuration SHA256, source limit state and exact created run path. Upon reopening, the GUI reports current numerical completion only when:

1. Existing stage ledger describes exactly the six X/Y E0/Eplus/Eminus cases, with no missing/duplicate/non-completed cases;
2. Original input state, site/spectrum/period settings, support and mass selection, gravity profile, mode count, and model JSON SHA agree with selected fields/source;
3. The saved run belongs **exactly** beneath current `05_MRSM/RUNS/<state>/<case>/<run-id>`, is not a linked path, and its `CASE_MANIFEST.json` is valid and `COMPLETED_SOLVER_ONLY`;
4. `06_REVIEW/SAVED_CASE_COMPLETENESS.json` agrees with six actual cases and current model SHA;
5. The current exact saved `02_RESULTS/MRSM_Results_V132.json` passes the existing per-case numeric completeness validator.

Otherwise the UI reports `LEGACY_UNVERIFIED`, `SOURCE_OR_INPUT_MISMATCH`, `SAVED_PROCESS_INCOMPLETE` or `NUMERIC_EVIDENCE_INCOMPLETE`, and shows **0 verified current numeric cases**, even when a historical ledger still reports six process completions. Old files remain unmodified; a new case's process ledger is copied to its unique run review folder after execution.

This is an **application source-integrity fix only**. A matching SHA and six complete saved JSON cases are NOT proof of the correctness of structural stiffness, wall edge transfer, native mode shapes, soil/Vs30, ETABS equivalence or NBC 105 compliance.

## Cross-module acceptance and integration map

| Stage | Canonical current dependency | Source of possible inconsistency | Safe next change / proof required |
| --- | --- | --- | --- |
| ETABS import | `components/inputs/project_workbooks.py`; native EDB, exact source workbooks, beam-force parts and ETABS API export | Source selection can be confused with old V10.6 or unrelated 6m pier workbook; calculated numeric results may use old source | Freeze exact EDB SHA + V10.7 source workbook SHA and cell provenance; require exact-pair reader/writer tests |
| Model conversion | `components/model/assembly.py`, `source_node_identity.py` | ETABS 32 real foundation supports/44 wall mesh points, native wall edge interpolation and frame rigid offsets may not be represented equivalently | Source-node/edge transfer and 1200 native end-zone assignment study; do not modify supports to force reaction agreement |
| Gravity/initial P-Delta | `components/gravity/solver_stack.py`, `comparison_bundle.py`; `components/model/eq_pdelta_initial_tangent.py` | 768.045kN max pointwise full D+L reconstructed-elastic residual (archived *different* from older 3041kN case); selected signed initial states must not double count lateral EQ | Native same-source 32-foundation six-component reaction and slab/wall cuts, separate D/L reconciliation, PDelta tangent/mass source |
| Modal and Rayleigh | `components/modal/analysis.py`, `rayleigh.py` | Physical support/mass constraints and separately selected ULS/SLS stiffness propagate into periods; generic eigen period not a substitute for §5.1 Rayleigh | Directional same-source model/stiffness/mass basis; modal mass/COM parity and actual floor-height ledger |
| ESM | `components/equivalent_static/calculation_and_gui.py` plus last PR #162 executed runner SHA | 12 scripts vs 12 actual solves; external ESM reference-only due to high-rise ULS eligibility and absent Vs30 | Immutable pre/post-run source hashes, complete eccentricity response, separate force-only and solved-evidence ZIP |
| MRSM | `components/response_spectrum/model_analysis.py`; `CaseLedger` | **Fixed in PR #163:** stale saved case reopen without model/config/run match. Remaining source concern: `run_model_spectrum` initializes `support_tags` from raw `data['supports']` despite a separately selected physical 32 vs 76/97 support profile. It also calculates some generalized mass terms from `data['nodal_mass']` when `STORY_LUMPED_NBC` is optional. These are concrete code paths that need source/solver alignment checks; not yet proven wrong numerically. | Report actual `ops` restraint/constraint DOFs and masses vs source lists; compare native six-component support cuts, CQC scale and unscaled drifts. Do not silently replace mass or section force definition |
| LTHA | `components/linear_time_history/runner_and_gui.py`; shared `CaseLedger` | Per-orientation freshly built solver domain is intentional; saved record hashes, full duration and preload identity are distinct from stdout [OK] | Adopt optional shared ledger provenance and strict source motion SHA/units/dt pair manifest; avoid premature caching across unrelated domains |
| NLTHA | `components/nonlinear_time_history/direct_existing_model.py`, `runner_and_gui.py` | X-wall first-step `localForce` nonfinite on wall element 110280 remains unresolved; 224 planned histories not demonstrated solved | ZERO/X/Y/XY isolated failure trace with nonfinite state, PEER specimen-transfer evidence and full-duration XY/YX gates; preserve full record and 3D constitutive behavior |
| NBC / design validation | `components/nbc105/`, `components/validation/` | Compliance modules and scaled force comparisons are not proof of all native requirements | Clause-by-clause source-referenced model evidence; ULS ESM method eligibility, Vs30, torsion, base shear, drift and actual supporting source pages |
| UI & exports | `components/ui/application.py`, stage GUIs, `components/inputs/output_contract.py` | Stage-level legacy JSON/CSV/Excel and plot copies can be picked as if current; dialogs and automatic workbook exports may duplicate work | Per-stage writer+reader migration and reopened manifest test; on-demand Excel/3D, responsive UI, progress/failure badges with proper acceptance tiers |

## Efficiency plan and non-goals

1. **Compute input SHA once per selected run**, propagate immutable provenance into per-stage reports. Hash source model before and after the MRSM subprocess. A saved source marker is not a physics cache key by itself; include source support/mass, ULS/SLS, stiffness, solver version and procedural context.
2. **Defer heavyweight report generation.** The previous converter/GUI benchmark identified a 1,614-second optional Excel construction; retain Generate Excel on demand and use compact CSV/JSON for continuous progress. Time model conversion, gravity, each modal direction, each MRSM eccentric case and report generation separately before claiming performance improvement.
3. **Use bounded caches for read-only input parsing** after exact SHA and physical configuration match. Do not reuse a nonlinear OpenSees global domain between history cases or silently share an axis' residual tangent; preserve independent full XY/YX runs.
4. **Review model assembly cost by source class.** Existing `_mesh_areas` plane indexing reduces repeated geometric searches, but still needs timed same-source benchmark for 4/8/16 meshes and saved conformity/edge-transfer checks before further optimization.
5. **Triage static duplicate functions and path markers.** Existing CI active-AST scan at the prior reviewed main counted 32 cross-file exact-body clone groups and 84 executable legacy path-marker occurrences. Keep them as per-file candidates, not auto-deletion instructions. The current native Windows path migration issue #141 remains open.
6. **One authoritative stage per result.** Never rename or delete old native EDB, geometry, source metadata or actual response files to make the repository look clean. Publish a clear canonical index and immutable per-run manifest, plus a one-click optional combined Excel + evidence ZIP that distinguishes process, numerical, ETABS parity and code acceptance.

## Changes and verification boundaries

- **New software test:** `tests/test_mrsm_reopen_source_gate.py`, five independent synthetic temporary-folder cases; no native EDB, OpenSees model or external data.
- **New shared functionality:** optional `CaseLedger(..., provenance={...})` and `set_provenance`, existing LTHA/NLTHA ledger format unchanged unless caller opts in.
- **MRSM saved evidence:** source/config/ULS/SLS identity, per-run canonical manifest and six numeric-case completeness; no changes to `run_model_spectrum()` mathematical calculations or solver algorithm.
- **Red GitHub CI observation:** at `dc505037`, five new tests failed due to missing gate while 1,775 existing passed; additional CI results must be taken from **latest PR head**, not historic runs.
- **Native status:** NO local EDB/Excel/Windows ETABS v23 analysis, full OpenSees solve, Vs30 test, wall-edge transfer comparison or nonlinear full-record acceptance executed in this review. **Not engineering-approved.**
