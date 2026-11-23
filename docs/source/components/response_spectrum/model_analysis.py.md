# model_analysis.py — source documentation

**Python source:** [components/response_spectrum/model_analysis.py](../../../../components/response_spectrum/model_analysis.py)
**Git baseline content SHA:** 03da0dd6173126200f166bfaf2d7023a25bd556f
**Subsystem:** Modal response spectrum and NBC scaling
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the response_spectrum implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 visible run and export workflow

The existing per-case `CaseLedger` remains authoritative. A top-level status field and indeterminate bar now report **READY / RUNNING / EXPORTING / EXPORTED / COMPLETED / FAILED / REVIEW REQUIRED** and on reopen show the stored `MRSM_Batch_Status_V151.json` completion count. Each stage status is written through the Tk UI thread. Numerical completion is not NBC design acceptance. Preserve model source state, six-case X/Y E0/Eplus/Eminus output, 76-source-supported production baseline pending original six-DOF restraint review, and full selected-model hash in ZIP.



## 2026-11-15 MRSM root-source consistency

`OpenSees_Model_Response_Spectrum_V132.py` is an exec-loaded compatibility facade. When this module computed `Path(__file__).parents[2]`, it could point outside the active checkout or exported runtime instead of the folder containing the authoritative project-input code. `_runtime_repo_root()` now derives the project root from `_component_source` under the facade, or from this component source's own `__file__` when imported normally. The existing current-EDB/workbook, ULS/SLS and spectrum checks remain in force; this patch changes only folder context, not seismic coefficients, modes or solver loads. Native UI/ETABS equivalence remains unverified.

## 2026-11-22 — MRSM source foundation and seismic mass case selection

The MRSM GUI now offers `PHYSICAL_32` primary and explicitly diagnostic `SOURCE_76` / `WALL_BASE_97`, as well as `SOURCE_DISTRIBUTED` (default) / `STORY_LUMPED_NBC` (opt-in dynamic mass modification). Both choices are recorded in case configuration, passed to the **same shared** `components/model/assembly.py::build_complete_model` owner, and the returned actual source support tags and profile are independently checked with `components.model.support_case_contract.require_runtime_support_case` before modes and response spectra. Native EDB, source analytical MPC mapping, ETABS elastic stiffness and original end-zone equivalence remain independently NOT_VERIFIED; a high-rise MRSM code-design PASS additionally needs §7.4 CQC/SRSS combination, §7.5 scaling and accepted geology/site evidence.

## 2026-11-22: executed MRSM support/mass identity attached to results

Each new MRSM case result now records actual `support_case`, `seismic_mass_policy`, and `support_case_evidence` obtained after the model builder's runtime verification. The assembled *geometry* model SHA alone does not encode the selected 32-versus-76-versus-97 physical restraints or modified dynamic mass operator. Existing six-case ULS review packages created before the change are preserved, but marked incomplete execution provenance when compared with the primary 32-support reference. Reanalyze from the refreshed exact same source EDB/runtime to obtain genuinely identical model-basis ETABS/OpenSees comparisons.


## 2026-11-23 — MRSM reopen identity and numerical-evidence gate

The original `launch()` counted `COMPLETED` rows in
`05_MRSM/MRSM_Batch_Status_V151.json` on reopening without matching
the current `OpenSees_Complete_Model_Data_V118.json`, selected ULS/SLS,
32/76/97 support profile, source-distributed/floor-lumped mass, periods,
hazard configuration or stored per-run numeric outputs.

New `mrsm_input_signature(fields)` hashes the exact UI input selection,
including selected gravity profile, seismic mass/support policy, ULS/SLS,
soil, hazard, spectral/period parameters and modes. It is **not** an EDB
or workbook fingerprint. `review_saved_mrsm_batch(...)` checks the
latest stage ledger's model SHA, state and input digest, requires an exact
canonical `05_MRSM/RUNS/<state>/<case>/<run-id>` directory and valid
`CASE_MANIFEST.json` with `COMPLETED_SOLVER_ONLY`, then reopens the
six X/Y E0/Eplus/Eminus actual `MRSM_Results_V132.json` cases using
the existing `validate_mrsm_case_output()`. Missing or mismatched
evidence reports `LEGACY_UNVERIFIED`, `SOURCE_OR_INPUT_MISMATCH`
or `NUMERIC_EVIDENCE_INCOMPLETE`, with zero verified saved numeric
cases; the older process-row count remains visible.

The GUI saves provenance into its stage ledger and copies a snapshot to the
unique run's `06_REVIEW` folder. The worker captures source SHA before
launch and rejects a model JSON changed during processing. A runtime
model/SHA/period/analysis result match is still **not** native ETABS
equivalence, actual Vs30 geotechnical verification or NBC design approval.

**Remaining:** exact EDB and workbook source hashes, original mass,
constraints and wall-edge force transfer; independent 32-support cut
comparison, modal CQC/scaling/drift and nonlinearity. This software
change does not alter spectrum equations, stiffening, damping, mass,
support selection, gravity/P-Delta preload or calculated responses.


### Nonblocking saved-run readback

`launch()` now performs only an inexpensive existence check before showing
the MRSM window. It reviews large saved JSON response files on a background
thread and schedules the status label update through `win.after` on the
Tk UI thread. The initial label is `CHECKING SAVED RUN`. If an analysis
input changes while this runs, or a new analysis starts, the earlier
saved numeric-review message cannot overwrite the new state. Any later
edit to a currently displayed saved-review selection invalidates that
label. Synthetic AST regression:
`tests/test_mrsm_reopen_source_gate.py::test_saved_numeric_readback_does_not_block_tk_launch_thread`.
The user does not need to wait for a large historical result to open the GUI.
