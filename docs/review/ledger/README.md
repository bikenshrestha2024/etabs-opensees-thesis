# File-by-file review ledger — frozen Git baseline

**Baseline reviewed:** [66c5c971ea297dc9d7fb0499b871a6204297913d](https://github.com/bikenshrestha2024/opensees-nbc105-research/commit/66c5c971ea297dc9d7fb0499b871a6204297913d) at 2026-11-04 12:59 UTC. The ledger is a **snapshot**, not a certification of current head or native solver correctness.

**PR overlap check:** [draft PR #5](https://github.com/bikenshrestha2024/opensees-nbc105-research/pull/5) remains **open and unmerged**. It changes `full_record_gate.py`, `tests/verify_full_record_gate.py`, the README and `03_THESIS_REVIEW_2026_11_04.md`. This branch deliberately does **not** duplicate its time-step numeric string and case-identity changes.

## Coverage and evidence tiers

- [CSV ledger](REVIEW_LEDGER_BASELINE_20261104.csv): **275 Python files** at frozen revision (115 root launchers/compatibility files, 103 component files, 53 tests, 4 tools).
- **10** files have explicitly documented source inspection sections on this review pass; **265** are `NOT_REVIEWED` and have **no** inferred findings. Inspection is only within declared lines/functions unless marked full source.
- `PARTIAL_SEMANTIC_REVIEW` means only named lines/functions were read, not the entire module; `REVIEWED_SOURCE_FULL` means the source text was inspected, **not** experimentally or physically validated.
- `git_blob_sha` is the Git blob object ID from the baseline tree; it is **not** a source file SHA-256 and should not be used as if it were a PEER/SeismoMatch record fingerprint.
- No ETABS/OpenSeesPy native 25-storey analyses were run as part of this ledger creation. The listed earlier CI outcome is historical and cannot be upgraded to current native test evidence.

## Directly inspected modules — source findings

| Exact source | Lines/functions examined | Evidence and open issue |
|---|---|---|
| `components/nonlinear_time_history/full_record_gate.py` | 1-131; verify_numeric_accepted_row; verify_accepted_history; compare_time_step_results | SW-03: compares same record/model hashes, but no XY/YX or ULS/SLS case identity gate (PR #5 separately addresses this); numeric text step comparison also in PR #5 |
| `components/nonlinear_time_history/building_exploratory.py` | 203-280; 300-375; 510-590 | Transient runner, wall source preflight, source files and paired OpenSees Path/UniformExcitation mapping inspected; native first-step wall failure unresolved |
| `components/nonlinear_time_history/soil_c_physics_preflight.py` | 1-160; audit_soil_c_analysis_config; assess_modal_damping_and_time_step | Soil C scaling/units and mode-evidence gates inspected; actual Tn90 and period-fit coverage require project evidence |
| `components/nonlinear_time_history/wall_diagnostics.py` | 1-118; inspect_wall_geometry; write_wall_audit | Geometry checks do not certify 3D wall/FSAM constitutive stability; source AREA:354/482 are failure suspects only |
| `components/model/assembly.py` | 1-100; 190-270; 620-695 | Reviewed wall node ordering, area mesh and build entry; actual ETABS mass, loads, reinforcement, openings and connectivity not reconciled |
| `components/nonlinear_time_history/research_building_materials.py` | 165-270; check_project_material_qualification; define_building_materials | Literature/nominal concrete and steel sensitivity profiles explicitly not transferable as project-calibrated core materials |
| `components/nonlinear_time_history/soil_c_run_matrix.py` | 40-167; create_configs; main | 8 pair and M0-M6 planning inspected; configuration generation is not evidence of 224 completed runs |
| `tests/verify_full_record_gate.py` | 1-65; GateTests | Existing accepted history tests examined; draft PR #5 adds further timestep identity regressions; tests not executed in this ledger-only review |
| `tools/audit_active_repository.py` | 1-105; inventory; inspect_one_python | AST inventory is not semantic review; existing tool indexes modules but lacks per-file inspected-line evidence |
| `components/nonlinear_time_history/variant_comparison.py` | 1-120; validate_variant_manifest; compare_completed_cases | Source equality gate inspected; output metrics not independent project physical acceptance and no optimum established |

## Review queue — evidence order, not alphabetic renaming

1. **P0:** `components/model/assembly.py`, loads/diaphragms and ETABS source reconciliation: mass, stiffness, boundary conditions and rebar; more line-by-line batches.
2. **P0:** `components/nonlinear_time_history/building_exploratory.py`, `wall_topology.py`, `wall_diagnostics.py`, `research_building_materials.py`: node ordering, source mesh, real RC core openings and wall material region/axial modeling.
3. **P0:** Native ZERO/X/Y/XY fresh-domain reproduction, failed wall tag to original ETABS area mapping and last accepted-state evidence.
4. **P1:** `soil_c_nltha_suite.py`, motion matching evidence, real T1/Tn90 interval, Gorkha/Loma anomalies and separate XY/YX output status.
5. **P1:** `device_recording.py` / FVD and BRB material/element recorders, sign conventions and energy; independent laboratory specimen calibration.
6. **P1:** `full_record_gate.py` and `variant_comparison.py` cross-case comparison identities, case status and 8-pair M0–M6 fair comparison. Avoid overlapping draft PR #5.

## How to validate the frozen ledger

```powershell
git fetch origin
python tools/validate_review_ledger.py
python tests/verify_review_ledger.py
```

The validator compares the **exact baseline Git tree** against each ledger path, Git blob and byte size, rejects duplicates, rejects invented findings for unreviewed rows, and checks review-status evidence. A clone containing the frozen commit is necessary. The CI workflow fetches full history.

To advance this ledger: branch from the current latest revision, select a small group of `NOT_REVIEWED` files, inspect exact source lines/functions, write a new dated **snapshot** for that revision and add actual failing/passing tests with input hashes. **Never overwrite this historical ledger or convert automated AST scan coverage into semantic review.** This first snapshot excludes the new ledger validator and test modules introduced on the review branch; they enter the next snapshot after commit.

## Engineering evidence status

| Criterion | Status |
|---|---|
| Frozen Git inventory/blob provenance | PASS after CI verification |
| Per-file semantic review across all active code | NOT EVALUATED — 265 files unreviewed |
| Software tests for this ledger | NOT RUN until PR CI executes |
| Native E-SFI-MVLEM-3D X-wall failure reproduction | REQUIRES PROJECT EVIDENCE |
| ETABS-to-OpenSees mass/load/rebar validation | REQUIRES PROJECT EVIDENCE |
| 8 Soil C records and full M0–M6 XY/YX NLTHA | NOT RUN |
| NBC 105:2025 project design compliance | NOT EVALUATED |
| Experimentally validated core/FVD/BRB material models | REQUIRES PROJECT EVIDENCE |
