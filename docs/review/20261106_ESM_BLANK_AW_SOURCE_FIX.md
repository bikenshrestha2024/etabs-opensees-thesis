# 2026-11-06 — Equivalent Static Method Aw and period boxes were blank

## Reproduced GUI symptom

In the Windows ESM dialog the source weight ledger may be correctly selected while the X-direction effective first-storey wall index is blank and the Y field may contain Excel *text* (e.g. `Aw (m²)`) rather than a numeric value. The status said `missing awx`; an automatic startup ETABS attach then overlaid this with `[WinError -2147221021] Operation unavailable`.

These are **two independent faults**. ETABS COM is **not needed** to read a genuine workbook, calculate an audited wall Aw from an ETABS-derived OpenSees export, or display empirical T. Rayleigh T requires a separate solver calculation, and ETABS eigenperiod is a comparison reference only.

## Changed behavior

- Import only **finite positive** numeric `Aw-X`/`Aw-Y` and directional time periods. Excel labels and formula errors are rejected with their original source sheet/cell and actual value; never render `Aw (m²)` as calculated area.
- Search the selected export, project workbook subfolders and **adjacent export parent** for source workbooks. An explicit selection of just the scaling book does not hide the calculator sheet stored elsewhere.
- Retain source `SCALING SUMMARY!B4` model identity, floor/limit state and existing byte-identical EDB copy controls. No permissive fuzzy-name fallback. An old `- Copy` file without identical source EDB remains **REJECTED**; the workbook source mismatch can be inspected.
- Display a persistent button `Why are Aw/period fields blank?`; it writes a local `ESM_Source_Diagnostics.txt` with expected export/source EDB, candidate scaling workbook paths, B4 source, B14/B15 contents, rejected source and wall geometry exceptions.
- Do not automatically call COM on dialog startup. Click `Open ETABS / refresh X-Y periods` **only** if a live source EDB and analyzed modal case are available in ETABS. The unsupported COM result does not erase a valid workbook import.
- Updating a reviewed manual Aw value recalculates the empirical/amplified period preview; an adopted period remains **pending** until a matching Rayleigh run or explicitly approved, source-compatible reference period.
- If current wall mesh has openings, discontinuities or ambiguous wall grouping, preserve the existing conservative geometry preflight and leave Aw pending rather than fabricate a code-compliance quantity.

## Windows usage

1. Update source checkout with `git pull --ff-only origin main`, restart the ESM GUI using the **real ETABS export directory**. If launched standalone, pass this directory explicitly, e.g. `python 12_EQUIVALENT_STATIC.py "D:\\Thesis Opensees\\Etabs Nodes Export ULS 3 b,o,c"`.
2. Look at **Verified story seismic-weight CSV** and ensure it comes from that very export. A successful ledger selection does not establish wall Aw.
3. If one or both wall indices are missing, click `Why are Aw/period fields blank?` and inspect the local `ESM_Source_Diagnostics.txt` plus `NBC105_Input_Provenance_V123.xlsx` / `Review notes`. The source folder may differ from the hard-coded default `D:\\Thesis Opensees\\Etabs Nodes Export`.
4. Select the actual calculator and scaling workbooks using **Excel sources…**. If the scaling workbook was created for a different EDB or has invalid formula values, no numeric Aw is imported from it. Re-export/recalculate source-compatible wall data, or enter independently verified X/Y effective wall areas manually, documenting calculation and cell references.
5. Once both Aw values are finite positive, run **Preliminary Rayleigh run (X/Y)** for the matching Ultimate→ULS or Service→SLS model. ETABS modal attachment is optional and reference-only.

**Important:** This code repair does not establish the *actual* Aw for the user's private building; no original private EDB or spreadsheets were uploaded into GitHub. Never substitute arbitrary example values (such as 3.6779 or 0.8019) merely to make the boxes nonblank.

## Verification

Unit test `tests/verify_esm_blank_aw_source_20261106.py` checks numeric labels, NaN/formula errors, source mismatch, adjacent workbook discovery and explicit scaling-only selection with calculator fallback. Additional previous ESM tests remain mandatory. The native ETABS COM Windows attachment issue is not considered fixed by this GUI change; ETABS can fail if the server is not running, the model differs or elevation/COM registration is inconsistent.
