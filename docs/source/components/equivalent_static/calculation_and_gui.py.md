# calculation_and_gui.py — source documentation

**Python source:** [components/equivalent_static/calculation_and_gui.py](../../../../components/equivalent_static/calculation_and_gui.py)
**Git baseline content SHA:** 13bafcf41eeb52944a564cb9f1b248f269a7a2a5
**Subsystem:** NBC 105 equivalent-static analysis
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the equivalent_static implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-04 missing-value diagnosis

The ESM initialization previously referenced an undefined `rayleigh_state`; now validates and uses the actual GUI state. The `_show_empirical` display must tolerate unavailable Aw and leave periods pending rather than aborting the whole project input load. `recommended_story_weight_input` prefers a populated assembled ledger only when current diaphragm IDs match the model. Existing manually reviewed CSV choices remain supported. [Full ESM blank-input diagnosis and tests](../../../00_ESM_INPUT_IMPORT_BLANK_FIX.md).


## Period adoption and GUI contract (2026-11-05)

The preliminary Rayleigh child process uses the assembled seismic preload even after a full-gravity verification session. For a combined X/Y calculation, the automatic review archive starts after both directions finish writing every requested state. A failed direction disables the combined runner list. Single-direction calculations publish their own review archive.

- `resolve_esm_state_periods(height_m,aw_by_axis,factor,states,rayleigh_by_state)`: selects the *matching limit-state* X and Y periods as min(calculated Rayleigh period, amplified `0.075H^.75/sqrt(Aw)`). Strict units: H [m], Aw [m²], period [s]. A `Both` state request fails if separate SLS Rayleigh evidence is absent, rather than silently reusing ULS stiffness-period values.
- `ESMGui._adopted_axis_period`: workbook adopted-period reference is now *opt-in* and is never labelled a native Rayleigh result; verifies selected Aw against the imported workbook Aw and, when available, independent exported geometry. A mismatched workbook value or reference beyond 1.25 empirical is rejected.
- `recommended_story_weight_input`: prefers model-tag-matched assembled story CSV, retaining the historical manual-CSV override. Story weights and effective wall areas are physical inputs requiring ETABS verification: source correctness is not implied by tag equality.
- `ESMGui._calculate`: if Both ULS/SLS, retrieve separate hash-checked state periods and write `result.period_s` into per-case `period_selection`; preserve X/Y, ± sign and eccentricity cases. The ULS ESM for a tall irregular building is diagnostic only where §3.2.1 does not permit static design.
- §6.5 Table 6-1 permits deflection factor 0.85 for 6+ storeys; it does **not** authorize scaling of MRSM drift/displacement by the §7.5 member-force factor.

All automatic calculations must report source model hash, source wall opening interpretation, seismic base and load-path reconciliation. Do not claim native ETABS reproduction until outputs are independently compared. See [parameter manual](../../../review/20261105_PROFESSIONAL_STRUCTURAL_ENGINEERING_PROVENANCE_MANUAL.md).


### 2026-11-05 bounded review — sidecar path and per-state metadata

Source review of `_calculate` identified an unverified/blank `model_script` path previously resolving to current working directory when writing `OpenSees_Initial_PDelta_Input_V124.json`. The new `validated_pdelta_sidecar_path` returns a target **only** for an explicitly selected existing `.py` script, preserving the legacy filename and sidecar location for valid working cases. ESM standalone computations remain usable, but they do not emit a P-Delta model sidecar absent a real model path.

A separate mismatch existed when a combined SLS case used its SLS period `result.period_s` but the output `period_selection.Rayleigh_T1_X_s/Y_s` described the ULS GUI periods. `state_rayleigh_provenance` now attaches the matching SLS imported evidence to SLS outputs and labels the evidence state. These are program integrity corrections, not proof that source modal/period properties are physically correct.

Regressions: `tests/verify_esm_output_safety.py` (seven synthetic tests). No native ETABS comparison is asserted.


## 2026-11-12 complete §6 calculation audit added to every generated direct ESM workbook

`write_outputs` now includes `NBC 5-6 Derivation` with the source-period, Ch, Z, I, C(T), Cs(T), Rmu, Ωu, Ωs, Cd(T1), W, V, k, distribution denominator, full floor force sum and V–ΣFi. It also states force polarity, eccentricity and that P–Delta initial/final physical response remains independently gated. `Storey Formula Audit` lists each source-story `Wi,hi,Wi*hi^k,normalized fraction, Fi, cumulative applied force` and source master node. This is distinct from physical recovered floor shears; original direct ESM JSON and CSV still record individual floor forces.

**This does not recalculate or alter the original ETABS-linked Excel engine.** That historical workbook preserves the older X=1.9582936m² four-6m interpretation. On verified `EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY`, the GUI now creates a **separate** `*_GROUPED_WALL_REVIEW.xlsx` beside the generated ETABS-linked workbook, recording historical X and verified two-12m X (2.0731745m²), respective Y, the discrepancy and actual source SHA. The original ETABS-linked generated workbook is unchanged (its registered hash remains meaningful); the grouped review is **research source-matched, not NBC structural acceptance**. If source verification fails, no new alternative wall area is silently created. This helper runs in Windows with existing OpenPyXL dependency; do not commit project-owned XLSX to the public repository.

Synthetic arithmetic regressions: `tests/test_esm_section6_arithmetic.py` (ULS/SLS Ch, C, Cd, W, V, k, floor sum). Physical native EDB tests still outstanding.


## 2026-11-12 source-period labels and export status

Historical workbook adopted periods are now explicitly labelled **reference only**, distinct from the current computed §5.1.1 OpenSees Rayleigh period and §5.1.3 minimum adopted design period. Importing the original workbook no longer automatically checks the advanced `use_workbook_periods` fallback. User opt-in remains possible for explicitly labelled historical research when current Rayleigh evidence is absent; source state/matching constraints are unchanged. For the 2026-11-12 run: historical workbook X≈2.0385674s differs from current adopted X≈1.9812809s, and historical Y≈1.9219798s matches coincidentally.

The GUI button names now explicitly show `Complete ESM export ZIP (all evidence)` and verified comparison action. The pre-existing status bar now reports ZIP **EXPORTING / EXPORTED / FAILED** distinctly, rather than the only proof being a log line. Packaging status is not native solver acceptance.

## 12 November 2026 — Compact ESM workflow and exact process status

**What/where:** Four primary Calculate, Run, Stop and Combined Excel+ZIP actions replace an 18-action grid in components/equivalent_static/calculation_and_gui.py. Three purpose tabs preserve the original action callbacks and navigate ETABS comparison, wall/period sources and reports. The shared Run Log has vertical/horizontal scrollbars, Start and Latest actions, and mouse-wheel isolation from the outer form.

**Why/when:** Users could not locate existing ZIP exports and progress bar overlapped the status text. The selected module now disables a stale OpenSees Run action in ETABS-linked mode. On cancellation, incomplete scripts appear in CASE_STATUS.json as SKIPPED_CANCELLED rather than treated as solved, and a completed ZIP export no longer turns an incomplete run into green success.

**Who/how:** CI uses the static tests in tests/test_esm_organized_export_gui.py; native Windows UI and ETABS/COM cancellation behavior remain to be checked. Green means only the indicated computation/export process finished, not the code/ETABS equivalence or design acceptability. The in-process ETABS linked workflow does not have a safe cancellation contract; Stop refers only to spawned OpenSees analysis batches.

**Review:** ../../../../REVIEW_MAIN/02_ESM/20261112_ESM_GUI_EXPORT_CASE_MAPPING_AND_JOINT_GATES.md


## ESM route identity and reviewed wall basis

Successful direct solver batches and linked workbook completion both request the route comparison. New direct runner names start with OpenSees_Direct_NBC105_ESM. Saved runner validation accepts both naming schemes.

## 2026-11-21 clause 5 routing

The empirical `0.075H^.75/sqrt(Aw)` and the 1.25 amplification are evaluated by `empirical_period_s` / `amplified_period_s` in the [clause 5 module](../nbc105/clause_05_dynamic_characteristics.py.md) at four sites (`resolve_esm_state_periods`, `_show_empirical`, `_adopted_axis_period`, `_update_periods`). The amplification factor is fixed at 1.25 by NBC 105:2025 §5.1.3: any other `period_factor` is rejected, and `_show_empirical` shows the DEVIATION message and leaves the adopted period unset. The earlier "free factor" wording above is superseded.


## 2026-11-22 — selected CSV geometry and direct Clause 5 routing

`recommended_story_weight_input` used to auto-select an assembled story-weight CSV if the source diaphragm tags were equal, even if its elevations were stale or the model had no stored master XYZ/base. This is an unsafe auto-selection mechanism, now addressed by invoking `components.modal.rayleigh_ledger_audit.verify_storey_elevations`. Tags, all levels, model base and matching floor heights are required for automatic selection; the original source file is not edited and the user can still intentionally supply verified manual data. The confirmation text now says **diaphragm tags AND elevations**, while ETABS mass/weight/components remain independent review gates.

`resolve_esm_state_periods`, `_adopted_axis_period` and `_update_periods` now use `components.nbc105.clause_05_dynamic_characteristics.adopted_period_s` for the §5.1 lesser-of period when a directional Rayleigh value exists. ULS/SLS and X/Y isolation are retained. The permitted advanced workbook research reference remains explicitly non-Rayleigh. No source Vs30, structural irregularity or native ETABS acceptance was claimed.

**Output coverage caveat:** The supplied 2026-11-22 terminal log reports 8 ESM runner scripts (X/Y, ± earthquake polarity, `E+` and `E0` accidental eccentricity). `E−` is absent in that execution. The GUI defaults to Both ±; a user-selected eccentricity subset can legitimately create 8 scripts, but cannot be described as a complete ±5% set until 12 scripts are generated and executed on source-matched models. Script creation is not solver completion.

## 2026-11-22 — exact stage ESM JSON recovery, supports and mass

The ESM combined exporter now finds its numeric `NBC105_ESM_Calculation_*.json` in the **exact** `03_ESM/RUNS/<state>/<same case name>` source path as well as the output root. GUI combined export is permitted to produce a manifest-only Excel+ZIP when no calculation JSON exists, expressly labelled `NO_CALCULATION_JSON`, with no invented base shear, story loads, or engineering approval. Legacy strict API still fails without JSON by default. ESM UI exposes 32 physical supports (default), 76 source restraint points or 97 wall-base idealization (diagnostics), plus an explicit distributed-vs-floor-lumped mass policy. Each script pins those settings and fails if the copied `OpenSees_Runtime_V118` executes a different actual support case. Compare against private native ETABS evidence before design use.

## 2026-11-23 — Exact executed ESM runner process identity

`ESMGui._run_generated` writes the SHA256 of each selected runner file
into the corresponding `CASE_STATUS.json` row as `runner_sha256` with
the original `runner_path`. It rechecks script bytes after the child
process terminates; a changed script is `INCOMPLETE` instead of a
successful recovered response, even if the process exited 0. This source
fingerprint is process evidence only and must not be confused with the
independent `model_sha256` written to ESM response metadata, the original
EDB SHA or original Excel workbook source identity.

Existing `CASE_STATUS` files without a runner hash remain readable but
do not count toward a newly certified `COMPLETE_SOLVER_ONLY` export.
The complete synthetic regression is in
`tests/test_esm_runner_sha_identity.py`. No changes were made to
`calculate_esm`, seismic mass, gravity, support topology, wall Aw,
Rayleigh periods, initial P-Delta or OpenSees solver algorithms.


## 2026-11-23 — ESM actual-support reaction recovery

User-supplied Nov 23 ESM review ZIP showed all twelve `SAVED_RESULT_*.json`
reporting `support_count=76` while solver logs confirmed `PHYSICAL_32`
with 32 assembled actual foundation supports (and 44 source wall-mesh points).
Root cause: ESM generated runner recorded baseline, incremental base shear and
six-component reactions from the original exported source `MODEL_DATA['supports']`
instead of the assembled runtime support set. MRSM already had the canonical
`solver_reaction_support_tags(report, selected_case)` helper. The generated ESM
runner now uses this same fail-closed helper after validating its model runtime
report; it does not change structural fixities, masses, edge transfer or
numerical solver parameters.

Synthetic regression: `tests/test_esm_runtime_support_reaction_source.py`.
The previously uploaded `COMPLETE_SAVED_RESPONSE_ONLY` records claiming 76
remain **historical and uncorrected**; rerun source-matched ESM to regenerate
32-support reaction CSV and saved-evidence summaries. ESM high-rise ULS and
Vs30/native wall auto-edge equivalence remain explicitly unverified.

## 2026-11-23 — exported ESM child-process fast I/O (optional reports)

The default GUI **Run exported OpenSees cases** mode requests fast per-case I/O. It leaves model rebuilding, 32/76/97 support policy, mass operator, signed ± earthquake/eccentricity, P-Delta preflight, OpenSees analysis, convergence, source/runner SHA, support-reaction identity, core story and node JSON/CSV, recorder index and response-force export unchanged. Only the separately generated five-panel PNG and OpenSees response XLSX are deferred within each child run. Select **Detailed PNG/XLSX per case** before starting the batch to retain both; direct manual execution of an individual generated runner without the GUI still defaults to detailed reports. The NBC calculation workbook/force-profile generated by **Calculate** is unaffected.

The GUI captures Python executable, support/mass policy and optional-output choice before launching worker threads (no Tcl variable reads inside child worker). Parent stdout is flushed to disk about once per second instead of for every line, retaining the full log and end-of-process flush. `CASE_STATUS.json` marks `FAST_CORE_JSON_CSV` or `FULL_PNG_XLSX`; successful status still requires the existing saved-response integrity checks.

**Performance scope:** this avoids optional report serialization and some log I/O; it does **not** remove the dominant repeated `runpy.run_path(MODEL_BUILDER_SCRIPT)` model construction, gravity preload and initial P-Delta checks. No elapsed-time reduction has been benchmarked on native Windows/OpenSees, and the observed 114-second model/gravity build per case remains a separate potential cost. Any future shared model-state optimization must be established through exact source hashes and independent X/Y/±/E0, support, mass, initial P-Delta, reaction and drift equivalence checks. Do not pass a reused nonlinear domain as a fresh independent solved case.

Regression: `tests/test_esm_fast_io_option_20261123.py` (synthetic script/GUI contracts only); native Windows timing and complete 12-case batch remain to be verified.

## 2026-11-23 — one source-export-owned ESM output location

A new ESM case previously could be written directly into a folder selected from another module (e.g. `02_MODEL`), and the GUI always wrote `ESM_Runner_Status` beneath its currently selected (often ULS-only) case directory even if the batch included SLS scripts. This split case output, status and combined-export discovery. Source review confirmed the live writer in `_calculate_axis`, GUI selection in `_browse_out`, and batch-status writer in `_run_generated`.

**New canonical in-project layout:**

```text
<selected ETABS export>/
  03_ESM/
    RUNS/
      ULS/<source-matched-model>/{calculation, runner, solver response, timings}
      SLS/<source-matched-model>/{calculation, runner, solver response, timings}
    LOGS_AND_STATUS/
      ESM_Runner_Status/<batch-id>/{CASE_STATUS.json, GUI_Run_*.log}
    REVIEW_SNAPSHOTS/<snapshot-id>/{review copies, Excel, ZIP}
```

`esm_case_output_directory` maps an in-export arbitrary folder to the exact selected state/model under `03_ESM/RUNS`. The GUI preserves an **explicit external custom** directory only; no other internal module can silently receive an ESM case. `esm_batch_status_root` maps all in-export selected cases to the same `03_ESM/LOGS_AND_STATUS/ESM_Runner_Status` (including mixed ULS/SLS). The existing combined reader searches this canonical location **and** historical case-local `ESM_Runner_Status` files without moving or deleting them. The GUI **Open output folder** action opens the one `03_ESM` module folder for in-export outputs.

Each individual generated runner still writes its own exact source-state response directory; this change does not merge ULS and SLS physical runs or change cases, stiffness, supports, gravity, P-Delta or solver equations. A review SNAPSHOT is deliberately separate from original solver data. Project-specific native verification and fully source-matched across-state combined exporting remain open independently.

Regression: `tests/test_esm_single_output_owner_20261123.py`. Existing result paths are left in place.
