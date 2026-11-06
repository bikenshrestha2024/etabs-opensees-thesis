# OpenSees-first NBC 105:2025 inputs, with read-only ETABS fallback

**Application:** `22_NBC105_INPUT_SYNC.py` (single Python launcher, Spyder-compatible),
`components/inputs/opensees_nbc_sync.py`, and ESM GUI buttons.

## Why the previous ETABS script filled the workbook automatically

The user's uploaded `ETABS_NBC105_Integrated_RS_Scaling_Direct_BATCH_STATUS_STABLE (2)(1).py` makes ETABS the master. It reads story and wall objects, thickness, piers, openings and spacing, groups physical bays, writes a new NBC Calculator workbook, evaluates the NBC effective first-storey wall index and writes `SCALING SUMMARY`. **That script then modifies the ETABS EQX/EQY user coefficients and RSX/RSY scale factors, runs structural analyses and saves a changed EDB. Those write steps are expressly excluded from the new sync workflow.**

Actual sample user-uploaded completed scaling workbook:
- `SCALING SUMMARY!B4`: older Ultimate EDB under `D:\Thesis\Etabs\NBC Ultimate\...`
- X: `B14=1.958293628808864 m²`, `C14=2.03856740011866 s`
- Y: `B15=2.203080332409972 m²`, `C15=1.921979776706312 s`.
These numbers are **historical source-workbook values**, not automatically the current `ETABS  3 - BELT TRUSS, OUTRIGGER CAP TRUSS 11-6-2026` export values. The other uploaded `NBC105_2025_Seismic_Calculator_ETABS_Direct Interaction - Copy.xlsx` is a template with blank detailed wall records. Mixing these silently is unacceptable.

## New master and fallback sequence

1. **OpenSees first (mandatory):** find matching ULS or SLS `OpenSees_Complete_Model_Data_V118.json`, `OpenSees_Element_Connectivity.json`, `OpenSees_Section_Assignment_Audit.json`, and `NBC105_ESM_Story_Weights_Assembled_V118.csv`. Existing ESM import/geometry code reconstructs first-storey X/Y wall patch slices and contributions `Aw_i = t_i L_i [0.2+min(L_i/H,0.9)^2]`. The current `OpenSees_Analysis_Results` Rayleigh JSON is imported only if the existing model SHA256, seismic-weight SHA256, limit state and directional wall-area matching checks pass.
2. **Uniform verified geometry** produces source-labelled `OPEN_SEES_GEOMETRY_CANDIDATE_REVIEW_REQUIRED` numbers which the new ESM `Sync from OpenSees model` button can prefill for manual review. The geometry calculation is not the same as independently qualified NBC effective wall piers. A mismatch with the source-matched workbook is marked `CONFLICT_GEOMETRY_VS_WORKBOOK` and cannot automatically overwrite the GUI.
3. **Nonuniform/partially open first storey:** the synchronizer enumerates all height slices, X/Y candidate Aw, segments and per-segment contributions but returns NO automatically adopted Aw. The original integrated ETABS program used pier/spandrel grouping and opening width/count to reconstruct physical bays; OpenSees shell slices alone do not prove the equivalent group of perforated wall piers. Reconcile original pier geometry, opening width/height and first-storey effective lengths before adopting an input. The source workbook is also preserved as a *candidate*, not silently approved.
4. **Workbook fallback:** the existing import routine accepts `SCALING SUMMARY!B14/B15` only when its `B4` EDB identity matches the current export (or both EDB files are byte-identical SHA256) and values are finite positive numbers. `C14/C15` are **adopted-period workbook references**, not OpenSees Rayleigh proof. Invalid labels, including `Aw (m²)`, cannot become numeric inputs.
5. **Direct ETABS API fallback (opt-in):** the `Check live ETABS geometry (read-only)` button or CLI `--etabs-fallback` attaches to the existing ETABS instance and verifies the currently open EDB path before reading wall panel nodes and thicknesses. Uses `AreaObj.GetNameList/GetPoints/GetProperty`, `PointObj.GetCoordCartesian` and `PropArea.GetWall`; temporarily sets kN-m-C and restores units. **Never opens, saves, unlocks, runs analyses or changes EQ/RS scale factors.** This is an independent geometry cross-check, not an automatic complete pier/spandrel interpretation; errors and skipped nonorthogonal panels are reported.
6. **New Excel output:** produces `NBC105_OpenSees_Input_Sync.xlsx` and `NBC105_OpenSees_Input_Sync.json` in a new model/state-specific folder. Excel preserves the original template, adds `OpenSees Source Sync` wall-slice/segment sheet and `Source Review Notes`; original `NBC Calculator` bay formulas and `SCALING SUMMARY` source values remain untouched. The GUI can prefill candidate fields only where one valid uniform cross-section has been reconstructed. Do not treat a newly created audit workbook as a certified / recalculated NBC design sheet.

## Command lines (Windows Spyder, conda-forge)

From a GitHub checkout updated to current main:

```powershell
git pull --ff-only origin main
conda install -c conda-forge openpyxl comtypes

python 22_NBC105_INPUT_SYNC.py --export "D:\Thesis Opensees\ETABS  3 - BELT TRUSS, OUTRIGGER CAP TRUSS 11-6-2026" --state ULS --template "D:\YourFiles\NBC105_2025_Seismic_Calculator_ETABS_Direct Interaction - Copy.xlsx"
```

To use currently OPEN and matching ETABS v23 as an optional **read-only** check:

```powershell
python 22_NBC105_INPUT_SYNC.py --export "D:\Thesis Opensees\ETABS  3 - BELT TRUSS, OUTRIGGER CAP TRUSS 11-6-2026" --state ULS --etabs-fallback --output "D:\Thesis Opensees\ESM_Sync_Review_2"
```

If using the ESM application directly, click `Sync from OpenSees model` first; it uses the same export directory and ULS selection, saves evidence and only prepopulates uniform-geometry candidate inputs. Use the explicit `Check live ETABS geometry (read-only)` button for cross-checks.

**Separate applications:** `TOP_DISPLACEMENT_DASHBOARD_BUILDER_V20(1).py` consolidates *ETABS displacement results*. It does not provide pier geometry, NBC Aw or source-consistent Rayleigh periods and is not an input source for the new synchronizer.

## Acceptance limits

- SHA256-matched OpenSees results are internally source-traceable, not automatically equivalent to physical ETABS sections and masses.
- The current user's model first-storey wall footprint reportedly **changes with elevation**. The synchronizer will therefore intentionally leave Aw unapproved rather than silently substitute values from the older completed workbook.
- There is no validated project-specific numerical Aw, wall-pier grouping, ETABS native API test or physical modal equivalence included in this repository change.
- A numerically converged gravity preload with 286447.790 kN applied and 286447.788933 kN reactions does not validate Aw, mass participation, Rayleigh periods or NBC §3.2.1 ESM eligibility.

## Tests

`python tests/verify_opensees_first_nbc_sync.py`: synthetic uniform and nonuniform OpenSees import, source evidence hashes, preservation of an existing template, non-overwrite, read-only mocked ETABS API with restored units and wrong-EDB rejection.

A real Windows ETABS 23 COM session must be used to verify the fallback against the exact current Ultimate EDB. No native ETABS tests run in GitHub Linux CI.
