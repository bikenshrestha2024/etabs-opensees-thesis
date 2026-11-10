# 2026-11-10 — Native assignment workbook, gravity source and ESM audit

## Current source and naming
The `V118` filenames (`OpenSees_Complete_Export_Report_V118.json`, `OpenSees_Complete_Model_Config_V118.json`, `OpenSees_Complete_Model_Data_V118.json`) are a **legacy export contract and filename schema**, not the version number of the current GitHub commit or the live V161 GUI. Other current modules (V123, V130, V161, etc.) deliberately refer to those exact paths. Renaming these files now would break saved exports, ESM/Gravity readers, runtime import references and evidence pipelines. Until a versioned migration with compatibility tests exists, retain V118 filenames and record the actual Git SHA/source EDB SHA and output provenance separately. Re-exporting from the main window does NOT, by itself, activate clear-beam self-weight.

## Corrected clear-beam workflow
1. In **Gravity** select the existing generated `OpenSees_Complete_Gravity_Model.py`.
2. Use the newly added **Original ETABS frame/material assignment XLSX (BEAM WEIGHT SOURCE)** row. This is **NOT** the completed Joint Reactions spreadsheet. It must provide native ETABS material list, frame summary, section material list and beam end offsets. The independent source crosswalk is required.
3. Choose **REBUILD verified beam weight in NEW folder**. If you pick the original source or one of its children as output parent, the GUI offers a *new sibling folder*, subject to user confirmation. The CLI still refuses nested targets: no automatic destructive overwrite.
4. The rebuild writes `CLEAR_BEAM_REBUILD_STATUS.json`; only `EXPORT_VERIFIED_NOT_GRAVITY_SOLVED` qualifies for a follow-up gravity run. `BLOCKED` means no corrected source accepted. Old source and EDB are unchanged.
5. In the Gravity GUI point to the **NEW** `OpenSees_Complete_Gravity_Model.py`, read both support lists, keep the original **32 source reaction-bearing nodes** as primary, solve exact 1.0D+1.0L and compare signed ETABS/OpenSees support reactions, load ledger and beam quantities. The 76/97 support alternatives are sensitivity analyses.
6. Do **not** silently subtract both clear-beam end offsets and single-owner joint volume; the current correction is clear-beam-source only, with volume audit separate. Native ETABS weight, source frame IDs and thickness/offset consistency remain mandatory.

## Uploaded original Excel workbook and provenance
A supplied `ETABS_LINKED_ESM.xlsx` and `.provenance.json` were inspected; **do not commit them to this public repository**. The audit records original model `ULTIMATE LOAD ... Copy.EDB`, source EDB SHA256 `8d09a2367fcdf17f969c77226d17a8668ab7989122aea59f6328aabbca9434bc` and original calculation source workbook SHA256 `5166139e7496e6433d2cf20be4be8990a6a2ba47cacde1685032f245854c2bef`. This is *research reference only, not NBC acceptance*; wall-thickness source check matched 600 mm but the mapping of four 2-m opening/spandrel positions to actual wall solid/void geometry has not been established from native openings.

For this ULS EDB, the adopted original calculation references are:
- X: Aw = **1.9582936288088642 m²**, adopted T1 = **2.03856740011866 s**, Cd(U)=**0.08759652970693452**, k = **1.76928370005933**.
- Y: Aw = **2.2030803324099724 m²**, adopted T1 = **1.9219797767063125 s**, Cd(U)=**0.09291014983861766**, k = **1.7109898883531562**.
- Source wall rows are NBC Calculator 24–27 and 32–34, with original values retained (not recalculated from provisional OpenSees wall geometry). EDB path identity by itself does not certify SHA equality if workbooks are separately produced.

A **different SERVICE LOAD EDB** was named in the scanned `NBC105_RS_Scaling_2.xlsx` source register and correctly rejected as the current ULS model's verified Aw/T1 input. Keep the ULS and SLS sources, versions and model identities separate. No fresh dynamic Rayleigh result was included in the uploaded evidence.

## ESM evidence ZIP — actual content and omissions
The supplied `ESM_Validation_Evidence_20261110_094617_411274_UPLOAD.zip` reported `INCOMPLETE_MISSING_EVIDENCE`: **629 collected files**, **2 missing required** items:
1. Original source policy still `GROSS_SECTION_LENGTH` (corrected source **not generated/validated**);
2. No saved OpenSees X/Y ESM structural response profile.

Its generated applied storey forces, calculation XLSX/JSON, plots and scripts are not automatically recovered OpenSees reactions/drifts. The ZIP omitted generated runner .py scripts under the previous extension filter, now corrected with an exact allowlisted filename pattern. Runners are archived but **do not** satisfy the structural response gate.

Calculated ULS research comparison base shears in supplied log: X **24,937.992 kN**, Y **26,450.735 kN**. They are force-distribution calculation results, not independently recovered native ETABS/OpenSees base shear. The GUI itself flags NBC 105:2025 §3.2.1 ESM eligibility not met for the present high-rise; therefore ULS ESM remains **COMPARISON ONLY**, not accepted seismic design, and site class evidence is not verified (Vs30 missing).

The pre-solver "story shear" plotted as cumulative sum of imposed floor actions was relabeled in the code as **cumulative applied floor force**; this is not element-section or floor-cut shear from a solved structure. Full design review still requires signed native EQX/EQY/PDelta responses, modal/RSA methods, input mass, first-order/second-order stiffness and calibrated nonlinear trials. No existing solver algorithm was changed in this patch.

## Reproducibility before declaring validation complete
- Run the clear-beam rebuild to a **new sibling** and confirm the native assignment crosswalk (original frame IDs, lengths, offsets, material-list weight, workbook SHA).
- Run 32-primary gravity after correcting source; save case-specific applied load and 32 native ETABS comparison pairs.
- Run OpenSees ESM X/Y models only after checking NBC applicability, boundary conditions, gravity preload and original-model provenance; export roof displacement, drift, reactions, recovered storey shear and source-local action vectors for each case.
- Rebundle ESM evidence after the response files exist; missing items must remain explicit, not fabricated.

### Changes here
Only GUI file selection/output path handling, safe evidence packaging, and truthful plot labeling were modified; no structural material, self-weight factor, beam offset formula, seismic coefficient, wall properties, or dynamic solver parameters were changed.
