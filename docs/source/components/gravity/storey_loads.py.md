# storey_loads.py — source documentation

**Python source:** [components/gravity/storey_loads.py](../../../../components/gravity/storey_loads.py)
**Git baseline content SHA:** 51a6cbc1fba7bcca4afb1b83edbbbb9606b9239b
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


## 2026-11-17 — 28-minute import bottleneck: deferred Excel formula expansion

The user-supplied ETABS conversion worker log dated 2026-11-16 measured `Storey gravity load classification and workbook` at **1614.536 seconds** of `1628.883 seconds` in model assembly; source ETABS connection/extraction and Plotly export were seconds. This stage previously ran `OpenSees_Load_Path_V141.add_formula_audit` synchronously inside `prepare_complete_export`, creating per-cell surface formula rows and four per-node rows, duplicating the surface sheet for seismic preload and serializing a large openpyxl workbook. The log times the combined method, not individual spreadsheet operations.

**New production behavior:** `prepare_complete_export` calls `export_storey_gravity(...,generate_workbook=False)` by default. Reconciled numerical storey totals, every source detail, and the CSV/JSON exports are unchanged. `Gravity_Storey_Workbook_Status_V131.json` marks `DEFERRED_FORMULA_WORKBOOK_NOT_A_MODEL_FAILURE`, source model-config SHA256 and gravity total. If an older XLSX exists in the same output root, it is preserved under `09_SOFTWARE_DIAGNOSTICS/DEFERRED_GRAVITY_WORKBOOKS/` to avoid suggesting it represents the new model. No existing FE mesh/analysis data or previous workbook bytes are silently discarded.

**Optional full Excel:** From the Gravity & NBC tab choose **Generate detailed storey-gravity Excel from saved model (no ETABS)**, or:

```powershell
python -m components.gravity.storey_loads --workbook "D:\Thesis Opensees\ETABS 11-16-2026\4"
```

The generator requires a complete error-free `OpenSees_Complete_Export_Report_V118.json`, model JSON, matching exact config SHA256, original load audit, and retains native ETABS load-pattern classifications from `OpenSees_Source_Model_Metadata_V118.json`. The detailed formula XLSX is generated **only on explicit request**. This is separate from the `Slab_Load_Path_Formulas_V141.xlsx` mesh study export; the two must not be conflated. A full formula spreadsheet can still take substantial CPU/memory/disk and is deliberately outside mandatory conversion.

**Compatibility:** Existing direct callers of `export_storey_gravity` still default to `generate_workbook=True`; the assembler explicitly selects the deferred mode unless `export_gravity_formula_workbook_on_import=true` is recorded in the source config. Only an actual Boolean is permitted. This prevents silently rewriting other callers' semantics. The loaded-model results and gravity mass/classifications remain computed identically.

**Performance validation:** Compare `[TIMING] Storey gravity load classification and workbook`, `[ASSEMBLY PHASE]` and final worker duration before/after under the same source SHA, four mesh divisions and a fresh output. No claim about the new Windows wall clock is made without a measured native run.

**Automated acceptance:** `tests/test_deferred_storey_workbook.py` verifies numerical source detail/level reconciliation, archive of an obsolete XLSX, and refusal to generate a workbook from a stale or failed assembled model. No numerical results are replaced with generic approximations.


## 2026-11-17 — actual semantic review of optional Excel publication

The previous on-demand exporter saved directly to the original Gravity_Storey_Load_Breakdown_V131.xlsx and computed SHA256 via xlsx.read_bytes(). Both were reproduced in regression tests as interrupted-save overwrite of previously valid evidence and avoidable whole-file RAM allocation. A third regression showed an apparently successful writer could produce invalid XLSX bytes and still be marked READY.

The gravity source reconciliation and source-detail CSV/JSON are **unchanged**. Formula construction remains in OpenSees_Load_Path_V141. The full workbook now uses the shared components.gravity.workbook_publishing.publish_workbook helper to write an exclusive same-directory temporary XLSX, validate ZIP container, stream SHA256, then atomically commit. The status manifest transitions GENERATING -> READY or EXPORT_FAILED. If save, ZIP validation, hashing or replace fails, the prior workbook stays intact and the status does not report success.

Excel's formula recalculation is a separate verification step (openpyxl does not evaluate formulas). The detailed workbook supports source-load-path comparison but does not directly solve ETABS/OpenSees 32/76/97 support reactions. No changes were made to structural loads, mass, finite-element mesh or boundary conditions.
