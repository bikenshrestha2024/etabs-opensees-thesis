# V21 active-source audit and unresolved engineering gates — 15 November 2026

**Status: TARGETED_CODE_DEFECTS_COMMITTED; NOT A COMPLETE LINE-BY-LINE REVIEW.**
**Source head before this review:** `e0000eaaa9977befa41d574440687fb47843b15a`.
**Primary authority:** `AGENTS.md`, `docs/review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md`, `docs/review/ledger/`, `REVIEW_MAIN/` and the central folder contract.

## What was actually inspected

The full GitHub tree was enumerated (2,971 tracked blobs at the start of this round), with focused semantic inspection of the ETABS point-reaction extractor, the two gravity reaction comparators and bundle tests, wall quad geometry/first-storey selector, NLTHA failure-evidence capture, material qualification gate, active source inventory and output-stage migration audit. That is **not** a per-line review of every file or a physical/numerical equivalence assessment. Existing frozen review ledgers must not be upgraded from `NOT_REVIEWED` by automated AST/source inventory alone.

## Confirmed corrections

| ID | Priority | Source | Confirmed flaw | Correction and test |
|---|---|---|---|---|
| V21-01 | P0 evidence integrity | `components/validation/gravity_node_comparison.py` | Numerical `rz_global_kN` was accepted as comparable even if `global_z_basis` was absent, rotated or unknown. Point-local ETABS F3 is not global OpenSees Z. | Require exact `GLOBAL_Z_VERIFIED_DEFAULT_AXES` in coordinate matching, else mark `MATCHED_AXES_UNVERIFIED`; reject nonfinite ETABS global reactions. Tests: `tests/verify_gravity_node_comparison.py`. |
| V21-02 | P0 evidence integrity | Same source, original-support export and all-node inventory | The 76-source-support exporter could rank unverified-axis reactions as matched; all-node inventory silently replaced duplicate ETABS point reactions and displacements. | Apply axis guard to the 76-node workbook and aggregate ETABS total; leave unsupported global-Z comparisons empty; reject duplicate point evidence. Tests added in `tests/verify_gravity_node_comparison.py`. |
| V21-03 | P0 output regression | `tests/verify_gravity_comparison_bundle.py` | Synthetic test used `GLOBAL_Z_VERIFIED` instead of exact native extractor value `GLOBAL_Z_VERIFIED_DEFAULT_AXES`; new proper axis guard caused its expected 76 matches to become zero. | Correct **synthetic fixture**, not physical-code guard. Preserve tests for 44 zero-ETABS vs nonzero-OpenSees support discrepancies. GitHub CI failure analyzed and fixture corrected. |
| V21-04 | P1 nonlinear probe | `components/nonlinear_time_history/one_storey_wall_probe.py` | Selection of an isolated wall quad did not explicitly reject NaN/Infinity source coordinates before sorting floor elevations. | Exclude invalid coordinate quadruples; deterministic regression for NaN/+Inf/-Inf in `tests/verify_one_storey_wall_probe.py`. This does not execute or certify the native E-SFI element. |

## Five separate unresolved acceptance gates

### G1. Full source review — OPEN

- **Goal:** Every active source file and then historical/archive file has a tracked exact revision, actual inspected line range/functions, source/units/runtime side effects, caller/reader/GUI implications, defect severity and test evidence.
- **Existing infrastructure:** `tools/audit_active_repository.py`, `tools/audit_live_output_writers.py`, `tools/validate_review_ledger.py`, frozen `docs/review/ledger/REVIEW_LEDGER_BASELINE_20261104.csv`.
- **Missing:** A contemporary, independently reviewed line ledger for every one of the 2,971 tracked files. File counts and AST parsing are NOT semantic inspection.
- **Gate:** A dated per-file inspected-lines ledger at exact Git SHA, explicit `NOT_REVIEWED` for untouched files, deterministic tests, native check when numerical behavior changes. Historical files must not be mistaken for active runtime.

### G2. Complete legacy writer/reader migration — OPEN

- **Target:** One selected export-case root: `01_ETABS_EXPORT`, `02_MODEL`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES` and `REVIEW_MAIN`.
- Every newly migrated solver run must use `<stage>/RUNS/<state>/<case>/<run-id>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`.
- **Missing:** Stage-by-stage proof that every producing function, historical reader, GUI chooser, ZIP publisher, index/pointer and plot loader uses the matching canonical/legacy paths. Never move outputs or remove legacy folders solely for tidiness.
- **Commands:** `python tools/audit_live_output_writers.py --repo .` and `python tools/audit_stage_output_migration.py "<selected-export-case>" --write`. Keep local reports **local** (they include private absolute paths).
- **Gate:** Tested producer/consumer compatibility and reopen of real old output for each stage, source identity and no overwrite.

### G3. Native Windows GUI regression — OPEN

- **Required environment:** User's Windows/Spyder Python 3.12 + conda-forge, native ETABS OAPI and source model, OpenSees/XARA as configured.
- **Missing:** Real end-to-end button, scroll, copy, folder picker, responsive logs, process cancellation, run-summary, export ZIP, and restart/reopen tests for gravity, ESM, modal, MRSM, LTHA, NLTHA.
- **Gate:** Actual timestamped Windows GUI action log and screenshot/produced manifest per stage. Headless GitHub Actions do NOT satisfy this.

### G4. Nonlinear X-wall first-step failure — OPEN / P0

- **Known symptom:** Historical first X transient step ~0.005 s, nonfinite localForce associated with wall-element tag 110280. Post-failure nonfinite response does **not** prove the initiating element.
- **Source modules:** `components/nonlinear_time_history/wall_diagnostics.py`, `wall_topology.py`, `one_storey_wall_probe.py`, `failure_evidence.py`, `research_building_materials.py`, `components/model/assembly.py`.
- **Missing physical evidence:** Actual project web/boundary rebar/confinement and fiber geometry, source wall openings, local node order, constitutive transition and units, isolated native ZERO/X/Y runs on a fresh domain, gravity prestate, last committed snapshot, failing response trace, dt convergence, mass and constraint checks.
- **Critical production block:** `check_project_material_qualification()` intentionally prevents `THESIS_NLTHA` with uncalibrated literature/sensitivity material cards. A one-wall-quad smoke test is NOT a full-storey model or full NLTHA.
- **Gate:** Native source-hashed wall/device/structural subassembly verification followed by complete bidirectional full-record analyses. Do not change material or restraints simply to force convergence.

### G5. ETABS/OpenSees 32/76/97 support equivalence — OPEN / P0

- **Source:** `components/validation/gravity_etabs_direct.py` reports ETABS point-local `JointReact`; `compare_support_nodes` and `export_fixed_source_support_reactions` compare coordinate-matched reactions.
- **Distinguish:** The 32 reaction-bearing locations and 76 exported restraints are not automatically the same physical boundary-condition model. A 97-node continuous wall base is a sensitivity alternative.
- **Required comparison:** Exact EDB and model hashes, all six restraint DOFs, global reaction forces/moments and source local axes, actual supported joint tags, wall/beam/slab mesh and load paths, source mass/gravity profile, MESH_04/08/16 mesh-convergence results, base reactions and individual foundation-force distribution.
- **Gate:** Source-identical ETABS/OpenSees results with explicit discrepancy tolerances and attribution; a coincident global `sum Rz` alone is insufficient. Preserve 32/76/97 outputs independently; never force extra mesh nodes to fixed just to match totals.

## Verified source and runtime boundary

No ETABS EDB, source Excel, source accelerogram, native original gravity record or user data was modified in this review. The code changes are data-integrity safeguards and source selection guards, not nonlinear model calibration. Passing Python CI is a **software regression result** only. Run the following on a checked-out current revision:

```powershell
python tests/verify_gravity_node_comparison.py
python tests/verify_gravity_comparison_bundle.py
python tests/verify_one_storey_wall_probe.py
python tests/verify_wall_geometry_preflight.py
python -m unittest tests.test_stage_output_migration_audit tests.test_unified_output_contract -v
python tools/audit_active_repository.py --output audit/active_inventory.json --fail-on-missing-canonical
```

Native Windows validation requires the private original ETABS source and full run output; do not upload private EDB/workbooks to public CI. Explicit status remains `NATIVE_ETABS_OPENSEES_EQUIVALENCE_NOT_VERIFIED`.
