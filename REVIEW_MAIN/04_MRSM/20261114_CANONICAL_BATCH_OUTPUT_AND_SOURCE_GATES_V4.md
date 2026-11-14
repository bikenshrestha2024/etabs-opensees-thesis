# MRSM canonical output and evidence-integrity review V4

**Scope:** Source-code-level production-output fix in `components/response_spectrum/model_analysis.py` and `components/response_spectrum/reports.py`. No NBC 105:2025 spectrum coefficient, eigen solution, CQC mathematical expression, source shell stiffness, ETABS EDB, gravity restraints or original Excel workbook is modified.

## Verified source defects

- Earlier MRSM GUI batches emitted files under `OpenSees_Analysis_Results/<state_and_source>/MRSM_<state>`, rather than the shared `05_MRSM` stage.
- The native `run_model_spectrum` wrote a separate modal reference *cache* into a legacy results folder. This was an invisible second writer that complicated UI result discovery and source provenance.
- `reports.saved_cases` looked for legacy folders and used first encountered case per state/key/model signature. The stage-level viewer could silently combine same-direction results from multiple differently fingerprinted models or select an earlier run based on enumeration order.
- A process exit code of zero was not itself proof that every one of the six expected `X_E0/X_Eplus/X_Eminus/Y_E0/Y_Eplus/Y_Eminus` result records had been exported.

## Current code-stage changes

Automatic MRSM runs now create a unique path in `05_MRSM/RUNS/<state>/MRSM_<gravity-profile>/<run-id>`, with `00_INPUT_SOURCE/MRSM_Config_V132.json`, `01_LOGS/MRSM_Run_V132.log`, unchanged native numerical output under `02_RESULTS`, a saved-case completeness report under `06_REVIEW`, and copies of workbook/figure evidence in `03_EXCEL`/`04_FIGURES`. Each new run records the SHA256 of the exact serialized `OpenSees_Complete_Model_Data_V118.json`. The model hash is a file fingerprint, **not** independent ETABS equivalent-source certification.

The MRSM modal reference is retained within its originating `02_RESULTS/Modal_Reference/<state>/<gravity-profile>` instead of being written into a different stage. Reader compatibility of formerly cached modal references remains a native Windows follow-up; original older reference caches are **not deleted**. A saved-results gate checks the six expected cases, each state, axis, populated stories and one model digest before setting **COMPLETED_SOLVER_ONLY**. If the saved file is incomplete or inconsistent, the run and ledger are marked incomplete/failed for review. This is not NBC compliance or member design adequacy.

`saved_cases()` now searches saved canonical and historical MRSM files, ignores review/ZIP copies, selects the latest identical-model case and blocks combined reports for the same state/case with conflicting model SHA. Select the exact `02_RESULTS` folder to inspect a historical run with a different source model; do not relabel different ULS/SLS stiffness states as identical.

## Native Windows checks not performed in GitHub CI

1. Run the current third-floor ULS model with the *same* immutable ETABS source identity, source state, 32/76/97 restraint mapping and reviewed mass source. Confirm six cases and actual modal-force/drift workbook data. Check CQC, force-scale-only vs displacement, modal mass and geometry.
2. Reopen the same result from the MRSM GUI, generated Excel, figures, ZIP and displacement viewer. No blank figure should count as zero deformation; no result from a different EDB SHA should be accepted.
3. Fail one disposable trial and compare `MRSM_Batch_Status_V151.json`, `CASE_MANIFEST.json` and saved-case gate. Confirm no run is silently marked complete.
4. Confirm historical result/Excel in `OpenSees_Analysis_Results` can still be read and that a new run does not recreate legacy cache folders.
5. Native structural gates remain open: wall–slab–beam gravity load path, shell MESH_04/08/16 and foundation reactions, source-matched RC slab in-plane/plate modifiers, pinned-outrigger/brace equivalence, and full nonlinear material calibration.

## Regression tests

`python -m unittest discover -s tests -p "test_mrsm_canonical_output_v4.py" -v`

This unit suite uses synthetic JSON records. A passing suite verifies source/file safeguards but does not mean the user's native Windows analyses have passed.
