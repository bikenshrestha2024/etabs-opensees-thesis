# 21 November 2026 — ESM results misrouting and flat export audit

## Screenshot observations

For selected `D:\Thesis Opensees\ETABS 11-21-2026\1`, `03_ESM` is empty while ESM `NBC105_ESM_Calculation_*.json` and `.xlsx` files appear in `OpenSees_Analysis_Results\ULS_Floor_3_...`. Root files include model JSON, complete export audit/workbooks, conversion files and other generated artifacts. The structure already contains `01_ETABS_EXPORT`, `02_GRAVITY`, `02_MODEL`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`, plus historical `OpenSees_Analysis_Results` and `OpenSees_Runtime_V118`.

These screenshot observations do not prove file validity, content completeness, or the physical correctness of ETABS/OpenSees calculations. The selected Windows directory was not mounted into the GitHub editing environment.

## Confirmed code defect

`components/inputs/project_workbooks.py::analysis_output_folder` built `<export>/OpenSees_Analysis_Results/<state>_Floor_<n>_<slug>` for *all* callers, including ESM and Rayleigh. The project layout created `03_ESM` as a directory, but the ESM GUI and Rayleigh producer still used the old shared root.

## Implemented changes

1. Add an **explicit** `stage='ESM'` argument to the shared output resolver; it now maps to `<export>/03_ESM/RUNS/<same-case-id>`. Calls without the stage keep the legacy path so gravity/modal/MRSM consumers are not accidentally redirected.
2. Update ESM GUI default output/auto-state/change, ESM generated cases, Rayleigh default writer, ESM input synchronization and ETABS-linked Excel audit lookup to the stage-owned path. Historical lookup remains active, and saved Rayleigh input import still applies existing hashes/method/limit-state checks before accepting any archived period.
3. Add `tools/repair_project_output_layout.py` with dry-run default. `--apply` uses the existing categorized root copy mirror and creates explicitly identified, hash-verified `03_ESM/REVIEW_SNAPSHOTS/HISTORICAL_<case>` copies for *already generated* ESM and Rayleigh files. Original byte content and locations remain unchanged.
4. Add synthetic filesystem tests for exact canonical paths and non-destructive, repeated migration.

## Acceptance gates still open

- Confirm Windows GUI uses `03_ESM/RUNS` for every ULS/SLS case, runner and Rayleigh output (and that linked validation/audit readers can reload them).
- Re-run native ETABS 23 + OpenSees/XARA source-matched cases and validate EDB/mass ledger SHA checks and actual result profiles.
- Use `tools/audit_live_output_writers.py` and `components.inputs.folder_audit` to resolve remaining root writers stage by stage, without guessing from file names.
- **Do not delete** root JSON/CSV/XLSX/PY files or historical analysis results until every source consumer and saved-run manifest reference is resolved.
- Do not merge as a fully validated comprehensive cleanup while native Windows acceptance remains missing. Directory routing fixes cannot certify NBC 105 physical compliance.
