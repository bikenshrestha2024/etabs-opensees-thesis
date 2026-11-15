# MESH_04 / 08 / 16 — Excel row ceiling, structured ZIP outputs and area-stage Python location

**Source evidence date:** 15 November 2026, user-supplied local Windows screenshots, three Mesh_Config files, MESH_04/MESH_08 V141 Excel workbooks and matching manifests, and an area inventory JSON. No user's original ETABS EDB or actual source/export run directory is available to this GitHub CI environment.

## Confirmed defect

The active `components/gravity/load_path_formulas.py::add_formula_audit` created one `Loaded node path` Excel worksheet and appended **four per-node path rows** for each source `FLOOR` shell-cell load pattern, without checking Excel's maximum of 1,048,576 rows including header. MESH_04: **7,000** floor cells and **112,001** Loaded node path rows; MESH_08: **28,400** floor cells and **454,401** Loaded node path rows. The MESH_16 screenshot reports `ValueError: Row numbers must be between 1 and 1048576. Row number supplied was 1048577` — direct evidence of an XLSX worksheet row overflow, **not** a proved FE assembly failure.

The published MESH_04 and MESH_08 manifests have `validity=FORMULA_AUDIT_ONLY_NOT_SOLVER_VERIFICATION`. They report total shell cells of **10,400** and **33,100** respectively; no solved gravity reactions or ETABS parity. Both use distinct mesh-specific config SHA256; no model can be substituted into another mesh variant merely by renaming a workbook.

**Engineering consequences:** MESH_16 workbook absence does not establish any mesh convergence. No comparison of floor deflection, shell rotations, beam shear/moment, wall-base reaction, modal period or stability is possible without three actual native solved runs. Do not assume mesh 16 improves a model if geometry, centerline connections, edge restraints or rigid diaphragm compatibility are unverified.

## Corrections

- One active `Loaded node path` page has at most 1,048,576 rows (header included). Additional pages `Loaded node path 02`, `03`, ... preserve **every** record and original `Surface load formulas` formula reference; an index records page data counts. No source ETABS load, material, physical slab bending coefficient or solver boundary condition changed.
- `MESH_04.zip`, `MESH_08.zip`, `MESH_16.zip` are generated individually under `02_MODEL/SLAB_LOAD_PATH/UPLOAD_PACKAGES/`, with original `RUNS/`, `EXCEL/`, `JSON/` paths retained **inside** each archive and a per-entry SHA256 manifest. A ZIP is a diagnostic package, not a complete gravity run by filename alone.
- Mesh-study GUI adds explicit `Current root (hash-checked)` choice and fresh independent 4/8/16 options. `Retry Excel from assembled mesh (no rebuild)` refuses stale original source, mismatched per-case config hash or a missing physical FLOOR mesh. This is important after a successful 16-division FE assembly followed by **XLSX** output failure.
- The area's reviewed-call `.py` Save As defaults to `02_MODEL/AREA_INTEGRATION/PYTHON/`; it never auto-enables nonlinear wall code or invents FSAM/ConcreteCM/SteelMPF calibration.

## Acceptance gates

1. **Software:** focused row-paging test produces multiple pages and rereads XLSX; isolated ZIP tests verify 4/8/16 archive contents and SHA. CI must pass on exact PR SHA.
2. **Native export:** regenerate MESH_16 workbook from the already assembled, SHA-matched model on Windows, if it is saved; otherwise rebuild selected 16 mesh. Confirm all pages and row counts, config identity and no source EDB modifications.
3. **Engineering:** run three independent gravity cases under exactly identical source loads/support and different floor subdivision only; compare ETABS total and per-support reactions plus beam force, slab UZ, vertical interface shear and shell rotations. Interpret *global equilibrium* separately from *per-support equivalence*. No convergence accepted until this evidence exists.
4. **Packaging:** open MESH_04.zip, MESH_08.zip and MESH_16.zip and ensure each contains correct own runs/Excel/config/status; no cross-mesh relabel or vanished legacy folder. **Do not publish private source outputs to a public GitHub repository.**
5. **Area:** confirm generated Python call resides in area-stage PYTHON folder and still begins with `AREA_STAGE_EXECUTION = False`; source-review flags remain unapproved without project materials.

**Status:** CODE_FIX_PENDING_REGRESSION; NATIVE_MESH_16_EXPORT_NOT_RERUN; GRAVITY_MESH_CONVERGENCE_NOT_VERIFIED.

## References

- Microsoft Excel: worksheet limit 1,048,576 rows: https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3
- OpenSees ShellMITC4: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ShellMITC4.html
- OpenSees rigidDiaphragm: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html
- Original project's governing seismic basis: NBC 105:2025; adopted supplementary slab bending factors from IS 16700:2023 Table 5.
