# Opt-in OpenSees initial-PDelta -> current-tangent unit EQ diagnostic

**Experimental structural comparison; not native ETABS equality certification.**
Run only after generating a fresh verified clear-beam-weight OpenSees source
and selecting original ETABS base reaction-bearing 32-source-point table.
The 76/97 support strategies remain separate engineering sensitivity
studies and should NOT be erased from the project.

## What this runner now actually solves

`components/model/eq_pdelta_initial_tangent.py` constructs the complete
ELASTIC OpenSees domain (including existing `geomTransf PDelta`
frames and ShellMITC4 surfaces) and runs:

**Initial nonlinear load state from zero (one simultaneous full combination):**
`1.2 SelfWeight +1.2 FloorFinish +1.2 Partition +1.2 Wall
+0.5 Live +1.5 EQX` (or corresponding signed EQY force CSV).
All components are introduced in the same nonlinear pattern and
ramped with Newton/LoadControl over 20 load steps. The EQ lateral
source comes from the user's existing NBC105 ESM `Storey_Forces`
CSV (with actual signed Fx/Fy and eccentric torque Mz), NOT from an
assumed hardcoded coefficient. A second negative signed source CSV
is required for a negative-direction counterpart.

**Dependent current-tangent analysis:**
After initial convergence, record the initial base reactions and story
master displacements, invoke `ops.loadConst('-time',0.0)`, add
separate `EQX × 1.0` or `EQY × 1.0` lateral pattern and solve one
step with `ops.algorithm('Linear')` (no `-initial` and no
`-factorOnce`). Output the **incremental raw** response relative to
initial state and check signed support force balance. This is conceptually
comparable to the pictured ETABS dependent linear case that selects
nonlinear initial CASE STIFFNESS and excludes initial loads.

**Limitations:**
- ETABS geometric stiffness of wall shells, offsets, diaphragm and
  nonlinear solver tangent is NOT proven identical to OpenSees elastic
  ShellMITC4 / PDelta frame transformation. Compare against actual
  native ETABS results; do not declare equality from solver convergence.
- Only applied floor-force accumulated story shear is exported. A
  truly recovered 3D internal floor section cut incorporating
  `ShellMITC4` wall forces has NOT been implemented; missing true
  shear remains explicit `null`/NOT_IMPLEMENTED.
- Dynamic mass, modal results and NLTHA materials are NOT modified.
  This diagnostic must not be merged into M0–M6 NLTHA production
  until nonlinear material/tangent behavior is separately calibrated.
- Full original ESM Aw, T1, C, k and story weight provenance from
  `NBC105_RS_Scaling.xlsx` must be verified against ETABS before
  using this diagnostic for design result comparison.
- Initial native ETABS PDelta result includes signed ±1.5 lateral
  load and may be influenced by ETABS iterative options; the current
  tangent diagnostic is a research approximation until proven equal.
- Running a structural converter may refresh generated audit files
  inside the source export directory. Keep backed-up original
  source files and use a separate corrected-conversion working copy.
  No ETABS EDB is opened, run, saved or closed by this script.

## Command from repository root (Anaconda Prompt)

```powershell
git pull origin main
conda activate etabs_env312
python tools/OPENSEES_EQ_PDELTA_TANGENT_DIAGNOSTIC.py --source-dir "D:/path/to/VERIFIED_CLEAR_BEAM_Export" --force-csv "D:/path/to/NBC105_ESM_Storey_Forces_ULS_X+_E+_V111.csv" --support-table "C:/Users/User/Downloads/Original_ETABS_Finished_Joint_Reactions.xlsx" --axis X --out-dir "D:/EQ_PDelta_Research"
```

Repeat for `Y` with the corresponding exact ESM source CSV and
`--axis Y`; negative sources must use negative signed floor forces
in their own CSV. The filenames in this example are descriptive
placeholders: use existing locally generated source files, not
invented paths.

Expected outputs (unique timestamped directory):
- `EQ_PDelta_Input_Audit.json` (SHA256 of source files)
- `ETABS_Nonzero_Reaction_Support_Audit.json` (32-node mapping)
- `EQ_PDelta_OpenSees_Tangent_Results.json` (initial and dependent
  incremental signed support force and roof results)
- `EQ_PDelta_OpenSees_Story_Responses.csv` (incremental raw
  diaphragm displacement and drift, applied-force shear explicitly
  separate from missing recovered story shear)
- `EQ_PDelta_Diagnostic_Failure.log` on a blocked/error case

The native ETABS read-only extractor and matrix are documented in
`docs/review/ETABS_EQX_EQY_PDELTA_NATIVE_VALIDATION_RUNBOOK_20261109.md`.

## Independent engineering references

CSI's Linear Static dependent-case description:
https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Cases/Linear_Static.htm

CSI P-Delta nonlinear options:
https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Cases/Static_Nonlinear_Pushover_Cases/Geometric_Nonlinearity_Options.htm

OpenSees `loadConst`:
https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html

OpenSees current-tangent Linear solver:
https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/algorithm/LinearAlgorithm.html

Run synthetic preflight checks:
```powershell
python tests/verify_eq_pdelta_tangent_preflight.py
python tests/verify_eq_pdelta_case_comparison.py
```

The full ETABS v23/native 25-storey solver validation remains
**NOT EXECUTED / NOT ACCEPTED** by these CI tests.
