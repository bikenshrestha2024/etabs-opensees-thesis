# ESM post-run result integrity gate V5

**Date:** 2026-11-14. **Scope:** Generated ESM child-process saved evidence and GUI completion bookkeeping only. No modifications to NBC 105 spectra, Aw decisions, stiffness, source ETABS EDB, Excel, ground motion or the generated numerical load solver.

## Previously observed inconsistency

The ESM GUI assigned **SUCCESS** to any child with exit code 0 without independently verifying that the result belonged to the selected source model, the requested X/Y case and ULS/SLS state, or that a complete story-response JSON and support-reaction ledger existed. A successful process status and a calculated force workbook were not sufficient evidence of a completed OpenSees static-response analysis.

## Implementation

`verify_generated_esm_result(script_path, export_dir)` checks:

1. Exact generated script case suffix `<ULS|SLS>_<X|Y><+|->_E...`.
2. Nonempty response JSON, META JSON, original calculation JSON, recorder index and support reaction CSV in the generated case folder.
3. The exact current source `OpenSees_Complete_Model_Data_V118.json` SHA256 equals the saved response META source SHA.
4. Response limit state, axis, case, and calculation direction/state agree.
5. Saved response has the same nonzero number of storeys as its force calculation; each row reports the correct case and finite height, displacement and design drift.
6. At least one support reaction row and a valid response recorder manifest.

For an exit-zero child **only**, the GUI writes an explicit `SAVED_RESULT_<runner>.json` alongside the batch `CASE_STATUS.json`. If this independent evidence gate fails, the case is marked **INCOMPLETE**, error details are appended to its persistent log, and batch completion is not reported. The guard asserts **COMPLETE_SAVED_RESPONSE_ONLY** rather than structural compliance.

## What was deliberately not changed

- Existing `OpenSees_Analysis_Results` ESM generation path and its multi-case X/Y stored files; a full canonical 03_ESM writer+reader migration remains OPEN until all force-curve viewers, calculator paths, Rayleigh state-inputs, ETABS-linked inputs and ZIP publishers are verified together.
- `0.3 LL` seismic mass is NOT assumed to be a universal gravity load combination.
- A zero displacement, a passing drift ratio or base-shear arithmetic does NOT qualify physical ETABS/OpenSees equivalence.
- ULS ESM remains COMPARISON ONLY where NBC §3.2.1 high-rise eligibility does not permit it; selecting calculated forces does not waive dynamic method requirements.

## Required native Windows verification

Run one SLS/ULS-comparable ESM case for the exact frozen export. Record source EDB/model SHA, source state, frame support node mapping, source ETABS displacement/drift, source model E and stiffness modifier, basis of initial P-Delta and complete saved child logs. Run a deliberately disposable missing-response test to confirm the new INCOMPLETE status, then verify combined Excel and ZIP distinguish calculated force profiles from solved OpenSees responses.

**Engineering discrepancies remain open:** 32/76/97 physical support reactions, ShellMITC4 slab–beam–wall vertical load path, MESH_04/08/16 gravity recovery, modal/wall stiffness equivalence, pinned truss/brace and nonlinear wall/device calibration. Those require native model evidence, not folder formatting.
