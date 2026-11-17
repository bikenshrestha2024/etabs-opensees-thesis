# load_path_formulas.py — source documentation

2026-11-10 extension: `recovered_vertical_transfers(payload, elevations_m)`
uses recorded six-DOF global element resisting forces (kN/kN-m). It sums lower
faces of elements crossing a horizontal mesh interface just above a given
elevation. Direct loads at/below that interface are separate. It is not an
arbitrary within-element section-cut interpolation. `vertical_joint_balance`
reports signed element Fz minus applied Fz minus support Rz at every joint.
Free-joint residuals are not foundation reactions. Both require complete frame
and shell vectors and reject incomplete old results. These functions read data
only and never modify the solver. The native isolated primary-case regression
recorded 14262 vectors and closed 11097 vertical joint balances within 4e-10 kN.

**Python source:** [components/gravity/load_path_formulas.py](../../../../components/gravity/load_path_formulas.py)
**Git baseline content SHA:** 245bd43de57522753fe561a705ccd742d75de851
**Subsystem:** Gravity-load and support equilibration
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the gravity implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-08 correction: full gravity vs seismic preload formula tabs

The `Slab_Load_Path_Formulas_V141.xlsx` generator formerly populated
the visible `Surface load formulas` Gravity factor (column G) directly
from `cfg.gravity_factors` (typically Live 0.3), even when the native
gravity GUI used the runtime `GRAVITY_1.0D_1.0L` profile (Live 1.0).
That was an evidence labeling/calculation-view defect, **not** a
confirmed error in the OpenSees gravity solver.

The exported workbook now contains two separate sheets:
- `Surface load formulas`: **FULL GRAVITY 1.0D+1.0L**. All included
  dead and live source patterns, including assigned roof live, use
  gravity factor 1.0. For an area of 2.25 m² with 4 kN/m² live,
  applied load is 9.0 kN, not 2.7 kN.
- `Surface seismic preload`: the model configuration's
  `gravity_factors`, typically 0.3 for Live.
Both retain the independent original `mass_factors` column; seismic
mass is not multiplied by the gravity full-load override. Other
source-detail formulas continue to use unfactored source loads and
their own analysis-context settings.

Workbook sheets are diagnostic arithmetic, not replacement for
independently executed, case-specific solver reactions and
displacements. A previously saved workbook does **not** update itself
from GitHub. Refresh using the existing **Export / open current
load-path formulas** action after updating the application, then
check the full-gravity factor and configured seismic-preload factor.

Regression: `python tests/verify_slab_full_gravity_factors.py`.

## 2026-11-09 project clarification: roof live assignment vs roof live factor

The full-gravity comparison profile `GRAVITY_1.0D_1.0L` uses **1.0** for
every classified, *actually assigned* permanent, floor-live and roof-live
source load. A Roof Live **pattern definition** does not, on its own, mean
an applied roof live force exists. If its source assignment ledger is empty
(or its applied sum is numerically zero after explicitly verified source
extraction), the corresponding full-gravity load contribution is zero even
though the requested factor is 1.0. Do **not** generate a synthetic roof
load, silently discard a nonzero roof load, or infer the absence of load
assignments solely from an ETABS pattern name.

The configured seismic mass source is separate: for this model
`mass_factors['Roof Live'] = 0.0`, while floor live is currently configured
as 0.3 where applicable. A separately defined seismic **preload** likewise
retains its configured factors; it is not the independently requested
`1.0D + 1.0L` full gravity reference. Verify the actual ETABS load
combination components and assigned load patterns before asserting
equivalence.

In the implementation `components/model/assembly.py::apply_gravity_profile`,
the full gravity calculation uses independently stored
`unfactored_patterns`, records
`gravity_by_pattern_kN['Roof Live'] = 0` for an existing but empty Roof
Live pattern, and does not mutate `nodal_mass`. This is an **input and
comparison invariant**, not evidence that the user's entire original ETABS
EDB contains no roof-live assignments. Test:
`tests/verify_gravity_comparison_profile.py` (both empty-pattern and
absent-pattern cases).


## 2026-11-13 — Stage 02 model mesh / area-integration output update

For the full rationale, mesh procedure, distinctions between **source quads** and **assembled meshed ShellMITC4 cells**, evidence requirements and safety warnings, read [the numbered Stage 02 review](../../../../REVIEW_MAIN/00_MODEL/20261113_STAGE02_AREA_INTEGRATION_AND_SLAB_MESH_STUDY.md). Mesh 04/08/16 files are separate case outputs and never a single rebadged baseline. Area inventory is source-only Excel + JSON; it does not instantiate OpenSees elements or validate gravity transfer.


## 2026-11-15 formula workbook and assembled-mesh identity

The 4/8/16 comparative workbook uses the same strict `components.gravity.mesh_cases.validated_mesh_size` as the mesh-run staging helper. Both the `export` preflight and `Mesh identity` sheet refuse fractional or boolean sizes rather than silently truncating them with `int()`. Existing strict config SHA check remains unchanged. Workbook formula values, original ETABS load/mass factors and source geometry are not altered by this validation-only change. Excel generation and native 4/8/16 ShellMITC4 / gravity equivalence remain separate acceptance gates.


## 2026-11-15 — saved force-vector identity validation

The active gravity load-path postprocessor now refuses duplicate/canonical-alias IDs in saved node/element/force tables; a duplicate entry is not silently overwritten by Python dict construction. It checks every complete six-DOF global vector, endpoint membership/order and nonfinite elevation even when no floor cut is selected (the zero-level completeness call used by joint balance). Joint-balance results reject duplicate or nonfinite reaction rows and missing/nonfinite applied loads. This does **not** alter OpenSees forces, ETABS source records or the signed Fz formula. Regression: `tests/test_gravity_loadpath_evidence_integrity.py`; evidence: `REVIEW_MAIN/01_GRAVITY/20261115_LOAD_PATH_EVIDENCE_TAG_COLLISION_AUDIT.md`. Native validation remains NOT_VERIFIED.


## 2026-11-15 — MESH_16 Excel 1,048,576-row failure and recovery

Reported Windows exception `ValueError: Row numbers must be between 1 and 1048576. Row number supplied was 1048577` occurred when MESH_16 node-level slab pressure load vectors exceeded one worksheet's hard Excel row ceiling. The original `add_formula_audit` appended four rows per floor-shell load record to a single `Loaded node path` sheet, even when many subdivisions produced millions of nodal records. **This is an export file format limit, not proof that ShellMITC4 numerical assembly failed**. Previously supplied MESH_04 workbook contains 112,001 node rows and MESH_08 contains 454,401; MESH_16 requires worksheet pagination.

Every new `Loaded node path` sheet is capped at the Excel row limit **including the header**. Additional sheets are named `Loaded node path 02`, `Loaded node path 03`, etc.; `Loaded node path index` records exact data counts, excluding itself. The legacy first sheet remains present, and each nodal formula continues pointing to its original `Surface load formulas!L<row>` row (the source load surface rows do not get repaged). The output remains `FORMULA_AUDIT_ONLY_NOT_SOLVER_VERIFICATION`. No individual node record is silently truncated. `tests/test_slab_mesh_excel_paging.py` forces a 9-row synthetic limit to validate multiple page rollover and XLSX round-trip without building 16x16 native geometry.

The GUI additionally offers **Current root (hash-checked)** (unchanged existing workbook check), separate `4`, `8`, `16` selected new assemblies, **Retry Excel from assembled mesh (no rebuild)** (source manifest + assembled config hash validation), and one-click **ZIP selected mesh** after saving case files. The ZIP includes source run snapshots, workbooks and structured case evidence; SHA256-manifested, no false gravity-solver acceptance. See `docs/source/components/gravity/mesh_cases.py.md`.

**Important:** full MESH_16 workbook with millions of rows may still be computationally expensive in OpenPyXL; this fixes row-limit correctness and avoids unnecessary FE reassembly, but large Windows memory/storage and Excel recalculation behavior require native tests. If no verified saved assembled MESH_16 exists, recovery fails explicitly.

## Single-owner volume policy in the workbook

When the assembled model uses `VERIFIED_SINGLE_OWNER`, the source-detail
worksheet keeps the recorded unfactored floor self-weight from the assembled
ledger. The applied weight uses that recorded value and the source gravity
factor. The surface worksheets and node-path worksheets still reconstruct
gross weights from shell geometry and material density. The vertical-load
path notes identify those rows as diagnostics before volume corrections.
The workbook change does not change assembled loads, seismic mass, or solver
results. `tests.verify_slab_full_gravity_factors` covers both workbook profiles.


## 2026-11-17 — mesh 4/8/16 XLSX evidence publication

The mesh-specific export(folder, output_root=...) writer previously saved XLSX directly to its final timestamped filename and wrote an un-hashed success manifest. An interrupted or corrupt XLSX could be left in the EXCEL directory, and the manifest did not prove the bytes persisted there. The exporter now calls components.gravity.workbook_publishing.publish_workbook and writes an atomic JSON manifest carrying workbook_sha256. Linked EXCEL/JSON output parents are refused.

This is **output integrity only**, not a modification of shell loads, Excel formulas, member weights, 4/8/16 mesh cases, structure stiffness, gravity reaction balance or seismic mass. Separate assembled-model SHA matching remains mandatory. ZIP validation is not formula evaluation or native physical acceptance; compare native ETABS+OpenSees solved reactions, wall-base resultants and beam bending/shear independently.


## 2026-11-17 — constant-time node-path paging

`add_formula_audit` tracks the current node-sheet row locally. Calling
openpyxl `Worksheet.max_row` before every append scanned every accumulated
cell and made node-path generation quadratic. The counter resets to 1 for
each new header, preserving Excel row limits, every node row, formula target
and the page-index counts. No loads or solver inputs change.

A synthetic one-pattern, four-node-per-cell benchmark on this Linux Python
3.12 host measured formula generation only (not XLSX serialization):

| Floor cells | Before (s) | After (s) |
|---|---:|---:|
| 250 | 0.187 | 0.082 |
| 500 | 0.549 | 0.095 |
| 1000 | 2.187 | 0.192 |

These are illustrative host measurements, not a full-building Windows timing
claim. `tests/test_slab_mesh_excel_paging.py` checks bounded dimension scans,
all 28 fixture node rows across four reduced-limit pages, formula references,
index counts and a saved/reopened XLSX. Native gravity and ETABS parity remain
separate checks.


## 2026-11-17 — root workbook GUI freeze and overlapping exports

`current_workbook` formerly invoked the entire `export` operation synchronously
on Tk's main thread. The advanced root-export button was also missing from the
shared disabled-controls list. It could start a second large workbook while an
independent mesh assembly/export was active. Both workbook-only routes now use
`_workbook_job`: a background worker reports progress/result/error through a
queue, polled only by Tk's main loop. No Tk method is called by these workers.
The root button joins the shared controls; busy requests return without starting
another export. Controls restore on success and exception. No model loads or
solver equations change. Synthetic worker scheduling, completion, failure and
busy-click checks are in `tests/test_mesh_workbook_publication.py`. Windows GUI
and peak-memory measurements remain pending.
