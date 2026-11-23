# id_audit.py — source documentation

**Python source:** [components/model/id_audit.py](../../../../components/model/id_audit.py)
**Git baseline content SHA:** 8ecacd10fbd4cff624a9ea95b793697039e85ba4
**Subsystem:** ETABS geometry/mass/constraint and model assembly
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the model implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R10 R12. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-15 new source-linked element role columns

`export_id_audit` uses `components.model.display_ids.member_identity` to write additive `Main family`, `Brace role` and `Display prefix` columns to the original `Elements` worksheet and the exact-ID HTML lookup. Existing column indexes 0–9 are unchanged: original ETABS object, original category, story, source property, topology and solver tags remain available. An additional `OpenSees_Brace_Role_Review.csv` lists each source frame with BR-family membership, its current source/proposed role and evidence-review state.

To assign an **explicit source-verified role**, add to the *working copied* `OpenSees_Complete_Model_Config_V118.json`:

```json
{"display_member_roles": {
  "REVIEWED_ETABS_UNIQUE_ID": "CO",
  "ANOTHER_REVIEWED_ETABS_UNIQUE_ID": "BT"
}}
```

These are illustrative keys; do not paste them as real IDs. Only the source unique ID namespace is allowed, **never** OpenSees preview/assembled tags. For CT, first verify the member belongs to the cap-truss assembly at the 25th storey. A chosen role changes labels/lookup only and is not constitutive-model evidence. Unknown IDs, invalid roles and contradictory explicitly typed categories fail before writing an output. Source drawings/ETABS group proof and independent FVD/BRB assignments remain separate gates. Existing source EDB is never touched.


## 2026-11-15 — unified compact 3D element inspector (V162)

The exported Plotly HTML for **structural elements by storey**, **frame/area connectivity** and **load-assignment 3D** uses one source-driven toolbar injected by `export_id_audit`. The toolbar's primary **Prefix → Storey → Element number** flow populates from the saved, verified `OpenSees_Element_Connectivity.json` `display_category`, `storey_number`, `display_label`, and original `etabs_object`; a user must explicitly select a member before highlighting. Prefix choices: B (beam), C (column), BR (normal brace), CO (core-wall-to-perimeter outrigger), BT (belt/perimeter truss), CT (cap-truss), FVD, BRB, SW (wall) and FL (slab/floor). If a source role/device was **not explicitly mapped**, the selector reports `no source-verified members` and does **not invent** CT, CO, BT, FVD or BRB tags. FVD/BRB appear only for exact source-typed device categories. A generic SHS brace cannot be silently relabeled a BRB or damper.

The member dropdown shows `display_label · ETABS original ID`. `Highlight` uses the established source-object-to-Plotly geometry selection pathway; `Focus` zooms the Plotly scene to finite endpoint/corner XYZ coordinates in metres. Neither changes the camera's data geometry, analysis connectivity, original ETABS EDB, saved load cases, OpenSees source node tags, solver tags or numeric results. For area objects the original four-or-more corner geometry is used. The original ID/nodal namespaces remain available under the accessible expandable `Exact source IDs · Node selection · Advanced` section; zoom/preset controls remain visible. Responsive CSS gives a compact multi-row toolbar, accessible labels, keyboard focus states and clear unavailable feedback; no extra modal.

The injector targets all root-level exported Plotly HTML views, retains existing non-Plotly HTML, and replaces the old injected selector/style by ID on regeneration (no repeated toolbars or CSS). It does **not** automatically apply to the separately implemented Matplotlib/Tk V126 panel; its existing source-label viewer remains independent.

**Important distinction:** `display_label` (e.g. `CT2501`) is a **UI alias**; `etabs_object` and `element_tag` refer to source namespaces; `assembled[object]` carries actual OpenSees solver segment tags only when assembly succeeded. Highlighting an alias in this visualization is not proof a calibrated FVD/BRB or nonlinear connection exists.

**Validation:** `tests/test_shared_3d_prefix_selector.py` builds synthetic source-typed cases and verifies all three generated Plotly HTML views, preserved Excel ID namespaces, distinct role labels, responsive controls, optional Node JS syntax check, and idempotent regeneration. In CI `.github/workflows/export-staging-regressions.yml` installs `openpyxl` and executes the integration tests. Windows Chrome interaction on the real project remains a user-side acceptance gate.

## 2026-11-23 — post-conversion source-ID and on-demand audit fixes

The uploaded V125 workbook contains 2,092 source objects, of which 55 `BEAM / UNASSIGNED` storey-0 records have **empty solver tags**, alongside 14,262 actual assembled solver elements. These source-only objects are not automatically missing beams nor OpenSees solver elements; retain the topology until original ETABS assignments are checked. The additive `assembly_status` in the mapping/Excel sheet explicitly distinguishes `ASSEMBLED_SOLVER_ELEMENT`, `SOURCE_TOPOLOGY_ONLY_NO_SOLVER_ELEMENT` and unverified assembly. A source-only object in an otherwise completed assembly cannot be assigned a nonexistent nonlinear solver mapping. Repetitive frame-release messages are summarized only in the GUI; original full per-ID warnings remain in the untouched export report.

**ID bug fixed:** `export_id_audit` previously calculated `assembled_area` but never read it when generating the Excel/HTML table's solver-tag column. ETABS frame 1 and area 1 may coexist with distinct OpenSees tags. The exporter now selects the correct dimension-specific map for frame or area; existing columns retain their positions and the header accurately says assembled solver element tags. No source ID or real element tag is renumbered.

**Performance:** `MappingGUI.reload()` and `show_load_audit()` no longer automatically generate the large workbook. `Export / open Excel audit` remains an explicit user-requested action, keeping the locked-workbook timestamped fallback. `MappingGUI.populate()` uses indexed solver-tag/property lookup. The inline node picker starts blank, so opening the inspector no longer falsely highlights `NODE:1`. Exact Plotly source IDs and separate solver tags remain available.

Reference: [23 November source-grounded handoff report](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/REVIEW_MAIN/01_ETABS_IMPORT/20261123_POSTCONVERSION_ID_MAPPING_WORKFLOW_AUDIT.md). Tests: `tests/test_postconversion_handoff_20261123.py`, `tests/verify_v125.py`, `tests/test_shared_3d_prefix_selector.py`. These checks are not a new native ETABS–OpenSees equivalence or NLTHA run.
