# 2026-11-09 | 32-point gravity correction, native ETABS v23 API fix, and consolidated ESM evidence

## Spyder 2026-11-10 — no-argument rebuild procedure

Running the OLD `REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py` with plain
`%runfile ... --wdir` caused `SystemExit: 2`, because the CLI required
`--source-dir`, `--assignment-workbook` and `--dest-dir`.
This was an INPUT-LAUNCHER error, **not** an ETABS or OpenSees solver failure.

The corrected script in the new **`etabs-opensees-thesis`** repository supports
plain Spyder execution **without any arguments**:

```python
%runfile C:/Users/User/Downloads/etabs-opensees-thesis-main/tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py --wdir
```

This path is the user's pictured ZIP-extracted local tree. After downloading
the latest main version, select:
1. Source **folder** holding `OpenSees_Element_Connectivity.json`,
   `OpenSees_Section_Assignment_Audit.json`, `OpenSees_Load_Conversion_Audit.json`,
   `OpenSees_Source_Model_Metadata_V118.json`, and
   `OpenSees_Complete_Model_Config_V118.json`.
2. **Original native ETABS full assignment workbook** with Material List
   by Object Type, Section Property List, Frame Summary, End Offsets,
   Insertion Point and load-pattern tables. The NBC Aw/T1 or gravity
   reaction workbook alone does not satisfy this source requirement.
3. Parent output folder. A timestamped
   `Verified_Clear_Beam_YYYYMMDD_HHMMSS_ffffff` directory is created;
   the original export remains unchanged.

The script checks source files, workbook sheets and source joint-volume
policy *before creating output*. It then applies the native beam
ID/length/offset/self-weight crosswalk in a new export. It does NOT start
ETABS, analyze gravity or rewrite the original EDB. The target contains
`CLEAR_BEAM_REBUILD_STATUS.json`: only
`EXPORT_VERIFIED_NOT_GRAVITY_SOLVED` means the source is ready for the
NEXT analysis step. `BLOCKED` keeps original inputs unchanged.

If you run an older **gravity GUI** from a saved runtime, it previously
searched incorrectly under `C:/Users/User/tools/`. The updated GUI
now offers a file picker to select the actual
`.../etabs-opensees-thesis/tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py`.
Directly running the updated rebuild file in Spyder also bypasses the
old GUI's script-location problem.

**Next:** in the gravity GUI choose the NEW
`OpenSees_Complete_Gravity_Model.py`, reload the original 32 support
selection, verify the new applied load, solve and independently compare
every foundation reaction with original ETABS native tables. The historic
8,652.444-kN global discrepancy remains **PENDING native rerun**.

---

## Why the Nov 9 21:58 solver still reported excess

The uploaded `Gravity_ETABS_OpenSees_Evidence_V04(5).zip` is internally consistent
but describes the PRE-CORRECTION source export, not the reviewed native-beam
correction. Verified in source JSON and run log:

| Evidence | Value |
|---|---|
| Original beam policy | `GROSS_SECTION_LENGTH` |
| Native beam proof in exported source | `NOT_CONFIGURED` |
| Original 32 reaction-bearing supports | 32 |
| Gross source beam weight | 53,984.054880 kN |
| Original ETABS Material List beam weight (separately verified) | 45,331.6105 kN |
| Beam clear-length candidate reduction | 8,652.4443516 kN |
| Old OpenSees total gravity | 320,019.758231 kN |
| Native ETABS original gravity | 311,367.313600–311,367.313880 kN (source table/precision dependent) |
| Gross model's signed global load difference | ~8,652.444 kN |
| Solver residual (old model only) | ~1.82e-14% |
| Corrected source actual gravity run | **NOT YET PERFORMED** |

The old solver PASS is equilibrium only, NOT ETABS equivalence.
The 32-point reaction mismatch and largest node error remain open until a
new corrected model is built and solved. Retain the 76 / 97 support
comparisons as boundary sensitivity checks, not replacement primary cases.

## Actual fix: code changes alone do NOT edit an old generated model

Use an **original native ETABS assignment workbook**, the SAME source export
and a NEW target folder. The latest repository includes
`tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py`:

```powershell
git pull origin main
conda activate etabs_env312
cd C:\path\to\etabs-opensees-thesis
python tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py ^
  --source-dir "D:\Thesis Opensees\ETABS  3 - BELT TRUSS, OUTRIGGER CAP TRUSS 11-9-2026\7" ^
  --assignment-workbook "C:\Users\User\Downloads\<YOUR ORIGINAL ETABS ASSIGNMENT WORKBOOK>.xlsx" ^
  --dest-dir "D:\Thesis Opensees\Verified_Clear_Beam_20261109"
```

The placeholder workbook filename above is NOT a generated file.
Use the real original ETABS assignment workbook containing
`Material List by Object Type` and frame end-offset assignments.

The rebuild checks all 750 beam source IDs, original lengths, both end
offsets, ETABS material weight, self-weight multiplier and workbook SHA256.
It preserves original geometry, frame stiffness, section properties, joint
volume `AUDIT_ONLY`, and source seismic mass conventions except that
the corrected beam self-weight feeds its consistent source load/mass ledger.
It writes `CLEAR_BEAM_REBUILD_STATUS.json`. Only status
`EXPORT_VERIFIED_NOT_GRAVITY_SOLVED` can move to the next solver step;
failed crosswalks are `BLOCKED`. The old source folder is unchanged.

Then select NEW `OpenSees_Complete_Gravity_Model.py` in the gravity GUI,
click `Read BOTH support lists and gravity load`, and rerun the 32-node
full 1.0D+1.0L gravity. Do NOT use the old V04 ZIP or old result registry as
evidence of the corrected model. Re-compare all 32 ETABS joints. The
calculated global new total should be close to 311,367.314 kN if all
other source loads are unchanged; this is a PREDICTION, not a solved result.

The updated gravity GUI now blocks a new ETABS-validation run from an
unchanged gross-beam source and offers a button to rebuild a verified
source in a new folder when launched from the CURRENT updated repository.
The GUI indicates `RUNNING`, `FINISHED`, `BLOCKED`, or `MISMATCH`
separately from the analysis log and PDF export progress. Solved
OpenSees equilibrium is NOT displayed as ETABS equivalence.

## Native ETABS v23 API issue discovered from the user's 22:10 API log

The previous `components/validation/etabs_native_quantity_tables.py`
wrongly required an 8-element GetTableForDisplayArray result and read
fields/count/data at indices 4/5/6. The live ETABS v23 COM output is the
SIX-element OUT tuple:

```text
(FieldKeyList_or_GroupName, TableVersion,
 FieldsKeysIncluded, NumberRecords, TableData, retcode)
```

Thus **fields = result[2]**, **row count = result[3]**, **flattened
table data = result[4]**, and **CSI code = result[5]**.

That false API schema caused thousands of valid native table entries
to be marked `UNAVAILABLE_OR_API_ERROR` even though ETABS returned
hundreds of rows. The new adapter accepts this actual six-field schema,
validates the table shapes, and preserves the wrapper's eight-field
variant only with explicit validation. Its regression tests now use the
actual v23 six-field return. Re-run native ETABS extraction after pulling
the new code to collect the material list and EQX/EQY results.

The seismic extractor also snapshots independent
`DatabaseTables` load-case selection, selects each case for table
display, checks a native output-case column where required, and restores
the original selection. It does not change the ETABS model, analyze any
case, or silently interpret a drift envelope as a signed static response.
Unsupported or ambiguous case results remain blocked.

## ESM Aw/T1 original source authority

Two uploaded ETABS-linked Excel methods use original NBC source Excel
values. Both recorded the same original Excel coefficients:

| Input | Original source reference |
|---|---|
| X Aw | 1.9582936288088642 m² |
| Y Aw | 2.2030803324099724 m² |
| X adopted T1 | 2.03856740011866 s |
| Y adopted T1 | 1.9219797767063125 s |
| X ultimate Cd | 0.08759652970693452 |
| Y ultimate Cd | 0.09291014983861766 |
| X k | 1.76928370005933 |
| Y k | 1.7109898883531562 |

These are the **original model-linked Excel research reference**,
not a substitute accepted NBC calculation. Exact original Excel
source file name, source workbook SHA256, EDB source identity, adopted
Aw/T1 cells and output provenance are preserved separately. The
working-copy EDB path match alone is NOT proof of file-byte equality.

The OpenSees-first geometric synchronization proposed
`Aw-X=1.9306371 m²` and `Aw-Y=2.2030803 m²` and explicitly labeled
them provisional continuous-pier geometry, NOT NBC accepted. Earlier
GUI code could overwrite a more authoritative original Excel Aw/T
reference when the user clicked `Sync from OpenSees model`.
The new GUI preserves the original model-matched Excel Aw/T, lists
the provisional geometry in the status message and keeps it in
separate geometry-audit evidence. It never silently changes the
original workbook or ETABS RS scaling.

If a SERVICE LOAD workbook points to a different EDB, the source import
must continue blocking that workbook for the current ULS model until
explicit identity is confirmed. No Aw substitution between ULS and SLS.

## One-folder ESM validation

The ESM GUI now includes `Bundle ALL ESM validation evidence ZIP`:
1. Choose model/current ESM output directory.
2. Optionally select a SAVED native ETABS EQX/EQY/PDelta evidence folder
   produced by `tools/ETABS_EQX_EQY_PDELTA_EXPORT.py`.
3. Collect original source metadata, model config/weight, story mass
   and ESM forces, ETABS-linked Excel outputs/provenance, Rayleigh
   records, OpenSees ESM response/plots and all available native
   ETABS static story/base/section-cut tables.
4. Produce `ESM_Validation_Evidence_<timestamp>/` and
   `ESM_Validation_Evidence_<timestamp>_UPLOAD.zip`, including
   `ESM_Evidence_Manifest.json`,
   `ETABS_Linked_Original_Excel_Aw_T1_Audit.json` and
   `READ_FIRST_ESM_VALIDATION.txt`.
5. Missing files, oversize exclusions, conflicting linked Excel
   coefficient sources and incomplete native response evidence are
   reported. No silent fabricated numbers.

See `components/equivalent_static/evidence_bundle.py`, and synthetic
`tests/verify_esm_validation_bundle.py` for the exact file contracts.

No standalone four-case equivalence is claimed until real saved
EQX/EQY, initial PDelta and tangent linear EQ cases are matched by
source EDB, mass, stiffness, eccentricity, response step and structure.
Applied floor-force sums are NOT substitutes for internal section-cut
story shears. Comparison of raw versus NBC design-amplified drifts
must remain separate.

## Documentation and independently checked API references
- CSI frame end length offsets:
  https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm
- CSI API 2016 StoryDrifts includes `StepType`, `StepNum`, `Direction`, coordinate and `Label`:
  https://docs.csiamerica.com/help-files/etabs-api-2016/html/e55e16e2-b7b0-2864-f3dc-b781f4062325.htm
- CSI ETABS API 2016 analysis status 1/2/3/4:
  https://docs.csiamerica.com/help-files/etabs-api-2016/html/a24b2f43-be87-e0ff-587b-068339d9a350.htm
- OpenSees PDelta transformation:
  https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/PDelta.html
- OpenSees loadConst:
  https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html
- OpenSees Linear current-tangent algorithm:
  https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/algorithm/LinearAlgorithm.html

## Validation gates (NOT automatically passed)

- Verified native beam material-list crosswalk: **CONFIRMED in earlier
  source evidence; must re-verify for each new model**.
- Fresh corrected source assembled: **PENDING USER EXECUTION**.
- Fresh corrected 32-support gravity solution: **PENDING**.
- ETABS per-node/support reaction comparison: **PENDING**.
- Native CSI v23 six-field API corrected in code: **COMMITTED,
  NATIVE RETEST PENDING**.
- Original Excel workbook coefficients/source provenance:
  **RECORDED; physical NBC wall pier qualification still required**.
- EQX/EQY base/story shear, raw roof/drift, PDelta tangent stiffness
  and ULS/SLS 3D ESM equivalence: **PENDING NATIVE EVIDENCE**.
- Actual GitHub Actions checks and Windows ETABS/OpenSeesPy solver
  tests: **NOT VERIFIED IN THIS CHAT**.
