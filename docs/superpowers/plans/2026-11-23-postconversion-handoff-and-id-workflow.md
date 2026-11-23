# 2026-11-23 Post-conversion ID integrity and responsive model-audit GUI

**Using Superpowers:** systematic-debugging to trace current ETABS/solver/GUI identity, TDD RED→GREEN to prove source bugfixes, writing-plans for review, verification-before-completion before merging.

**Source base SHA:** `b98410a0feab7527d5c5e52dec59a5d7f11893ae`. **Branch:** `fix/postconversion-id-audit-and-on-demand-workbook-20261123`. **Source files:** `components/model/id_audit.py`, `components/sections/mapping_audit.py`, `components/sections/mapping_gui.py`; source guides, audited fixture tests.

## Owner/reader boundaries

- `id_audit.export_id_audit` owns `OpenSees_ID_Lookup.html`, `OpenSees_ID_and_Support_Audit.xlsx`, and the injected Plotly element selector. Frame and area ETABS ID namespaces may overlap; never infer one from numeric ID alone.
- `mapping_audit.collect` owns source-to-solver element lookup and user mapping candidates; `save_assignment` writes only the exact model's `OpenSees_Element_Overrides_V125.json`. `export_excel` preserves historical filenames and compatibility. It does not convert source EDB.
- `mapping_gui.MappingGUI` is a Tk viewer/controller, not a model solver. It reads source artifacts on open, exports XLSX **only on explicit button action**, and sends dimensional ID queries to Plotly without touching solver tags.
- The original ETABS source EDB, existing 32-support physics, 44 mesh transfer points, 2×12 m X walls, gravity 1D+1L and NBC seismic mass calculations remain **untouched**.

## TDD implementation records

1. **RED** — `tests/test_postconversion_handoff_20261123.py` constructed a synthetic `FRAME:1` + `AREA:1` collision with independent assembled tags 100001 and 100002. Assert exact columns in ID XLSX. Source failure: row always retrieved frame dictionary. **GREEN:** dimension-specific selection of frame/area maps.
2. **RED** — same synthetic export has `FRAME:55` source-only `UNASSIGNED` geometry; test requires explicit `assembly_status`, unchanged source target, and rejection when an actual successful assembly has no solver instance for proposed nonlinear mapping. **GREEN:** additive status, guard and XLSX scope summary; no automatic geometry/stiffness mutation.
3. **RED** — opening Mapping GUI with export call patched to throw must leave XLSX absent, clear any default highlighted node and report on-demand export. Opening the load popup similarly must not create XLSX. **GREEN:** replace unconditional Excel export with explicit user callback; default node ID blank.
4. **RED** — repetitive release-warning digest compresses 2 frame-specific My/Mz messages into one line, retaining unrelated mesh warning and source raw messages. **GREEN:** exact-pattern digest, no release parameter changes or skipped warning history.
5. **RED** — pure `plotly_query_for_key` demands explicit `category=area` for a wall and `category=frame` for a beam with same ETABS number. `inline_source_keys` rejects numeric collisions in unqualified picker. **GREEN:** type-preserving URL query and distinct typed options.

## Verification and native scope

Required CI: `Headless pytest suite`, `ETABS export staging and display ID regressions`, repository compilation/navigation, integrated tracked-tree/dependency audit, source-discovery queue, public-model disclosure boundary. Inspect every workflow on final head and exact pytest pass count. Native Windows Tk/Plotly click interaction remains **NOT_EXECUTED** by GitHub CI.

**Acceptance remaining:** the 55 unassigned storey-0 objects require ETABS object-source checking; original EDB SHA is not available in uploaded XLSX; 32-support joint reaction residual (up to 768.045 kN in a separate archived elastic run) unresolved; 44 mesh-edge native transfer unresolved; first complete M0 Kobe XY/YX NLTHA not demonstrated. These must not be relabeled PASS because an audit GUI loads.

**Working source-review reference:** `REVIEW_MAIN/01_ETABS_IMPORT/20261123_POSTCONVERSION_ID_MAPPING_WORKFLOW_AUDIT.md`.
