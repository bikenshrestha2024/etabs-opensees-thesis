# LTHA / NLTHA automatic output routing — controlled migration V3

Date: 2026-11-14. Source: NBC 105:2025 review context, but no seismic design clause is changed by this filesystem update. **Status: Python/CI verification only; native Windows solver and physics acceptance open.**

## Implemented

Both `components/linear_time_history/runner_and_gui.py` and `components/nonlinear_time_history/runner_and_gui.py` direct **automatically selected** cases to the source export owner's canonical `06_LINEAR_TIME_HISTORY` or `07_NONLINEAR_TIME_HISTORY`. `prepare_history_run` creates a new unique run per invocation. Explicitly browsing to a custom output folder preserves the previous user-selected output behavior.

```text
<selected ETABS export>/
  06_LINEAR_TIME_HISTORY/                    [or 07_NONLINEAR_TIME_HISTORY]
    RUNS/ULS/<source-script_case>/RUN_<UTC...>/
      00_INPUT_SOURCE/
        CASE_MANIFEST.json
        HISTORY_INPUT_PROVENANCE.json
        NBC105_*_Time_History_RunConfig_V*.json
      01_LOGS/
        NBC105_*_Time_History_Run_V*.log
      02_RESULTS/
        <original solver-native files and run status>
        NBC105_*_Time_History_Run_V*.log [compatibility copy]
      03_EXCEL/<copies of generated XLSX ≤25 MB>
      04_FIGURES/<copies of generated PNG/PDF ≤25 MB>
      05_COMPARISONS/
      06_REVIEW/
      07_EXPORT_ZIP/
```

The result runner continues to write all physical numerical output files into one `02_RESULTS` folder. Its Python algorithms, transient step size, mass, material, constraints, Newton solution, Rayleigh damping and ground-motion scaling have **not** been changed. The GUI's last-run readers, plot/Excel viewer, ZIP exporter and log viewer follow that exact native output; the open-folder button opens the complete run root. No original EDB, Excel source or pre-existing legacy run is moved or overwritten.

The manifest records the model **script SHA** and the selected analysis basis (`kN-m-s` for metres or `kN-mm-s` for millimetres), but does not invent an assembled OpenSees model/EDB hash. `COMPLETED_SOLVER_ONLY` means the process exited with code zero; it is **not** NLTHA completion, full record validation, code compliance or ETABS foundation-reaction equivalence. Trial durations and failed partial records remain non-certified. `FAILED` marks a failing child process; logs persist with the run.

The native output structure and status are tested without invoking OpenSees through `tests/test_history_run_output_contract.py`. Existing history GUI, security and numeric regression suites run in GitHub CI. The actual engineering solver must still be executed on the user's Windows machine.

## Mandatory Windows smoke test for each source model/state

1. Update the checkout and back up/verify your source EDB and original ETABS Excel hash, then inspect the complete model script and source identity.
2. Open the LTHA GUI for the 3rd-storey ULS test. Keep automatic destination, choose one paired XY/YX short *diagnostic* run and inspect `06_LINEAR_TIME_HISTORY/RUNS/ULS`. Confirm JSON provenance, timestamps, run log, plot workbook and child process status. Re-run to confirm a second unique run instead of overwrite.
3. Repeat the diagnostic under the NLTHA GUI only after it clears material, wall and device readiness. A two-step smoke trial does **not** qualify as accepted NLTHA or physics validation.
4. Verify `Completed run graphs / Excel / unit audit`, `Inspect all saved input records...`, `Open output folder` and `Export review ZIP` from each GUI open the **same latest run**; no stale legacy folder or case should be selected.
5. For a source model in millimetres verify `kN-mm-s` in the run manifest and inspect motion input acceleration/dt and exported `m` displacements. Never infer unit correctness from the folder alone.
6. Test a deliberate disposable missing-record failure; verify it is marked FAILED, partial files retained, source assets unchanged. Test Cancel or interrupted process separately.
7. Verify full run duration/accepted states, modal participation, P-Delta preload, floor displacements, reactions and ETABS source agreement separately. Mark native checks OPEN until evidence is recorded.

## Remaining writer migrations

Production ESM multi-case solver, MRSM CQC batch and any residual legacy gravity/comparison exporters continue to require writer+reader native validation. No file-system wrapper resolves the foundation reaction disagreement (32/76/97 support selections), ShellMITC4 vertical transfer, brace hinge equivalence, FVD/BRB calibration, RC wall nonlinearity or missing ULS/SLS response data. Keep each issue in its existing `REVIEW_MAIN` subfolder.

**No original EDB/Excel/ground-motion file is committed by this change.**
