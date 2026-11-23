# ETABS → OpenSees post-conversion handoff review (23 November 2026)

**Purpose:** source identity, geometry/ID mapping, load and nonlinear mapping review, GUI and archive efficiency **after** an ETABS conversion has returned `elastic_assembled=true`. This is an engineering evidence ledger, not an independent native solver or code-compliance pass.

## Inspected evidence

The user-provided **`OpenSees_Property_Element_Load_Audit_V125(10).xlsx`** and 143-line saved load/warnings text from the current 23 November conversion were inspected **locally**, rather than uploaded to public GitHub. Source EDB path is shown in the user's local artifact but its native EDB bytes/SHA and private project workbook are **UNAVAILABLE in this review**.

| Evidence | Actual parsed value | Interpretation |
| --- | ---: | --- |
| Properties groups | 7 | 2 column sections, 1 assigned beam section, 1 unassigned beam group, 1 steel brace section, 1 wall, 1 slab |
| Source objects (mapping table) | 2092 | 805 beams (including 55 unassigned), 450 columns, 112 braces, 375 shear wall objects, 350 floor objects |
| Source objects with empty solver-tag lists | **55** | ALL `BEAM / UNASSIGNED`, ALL storey 0; their preview tags exist but **no solver element tags exist** |
| Source objects with one or more solver tags | **2037** | 2092 minus 55, not equal to solver element count because frames and shells are refined |
| Assembled solver elements | **14262** | BEAM 3300, COLUMN 450, BRACE 112, WALL 3400, FLOOR 7000; independent solver tag namespace |
| Nodes in node worksheet | **11097** | Original/source plus generated mesh/diaphragm nodes; not all are foundation supports |
| Source frame API load records | **1367** | 617 empty raw distributed-load responses; 750 responses with a source `Wall` distributed load |
| Source area API load records | **729** | 725 empty direct API responses, 4 null; this list alone is NOT a full load-set inventory |
| Assembled gravity ledger | **286419.758231 kN** | Floor Finish 18000; Live 14400; Partition 18000; Wall 26100; Self Weight 209919.758231 |
| Reported active horizontal seismic weight | **284691.556185 kN** | **Different purpose**; not expected to equal 1D+1L without matched source factors and mass attribution |
| Explicit per-frame release warnings | **112** | IDs 1308…1423 in source text. Per-object record kept; UI may group identical explanatory warnings |

**Critical source/solver ID collision confirmed from uploaded workbook:** `FRAME:1` (ETABS object 1, COLUMN C1101) has OpenSees `[100001]`. `AREA:1` (ETABS object 1, wall SW1501) has OpenSees solver tags `[103863, 103864, 103865, 103866, 103867, 103868, 103869, 103870]`. The original `components/model/id_audit.py` constructed separate `assembled` and `assembled_area` maps but serialized the **frame** map into *all* Excel/HTML rows. This could attribute a frame to a wall object when original numeric names coincide. It is a **mapping/output correctness bug**, not proof that the OpenSees model assembled incorrectly.

**Other root causes confirmed in source:**
- `components/sections/mapping_gui.py::reload` called `export_excel` on every window open and reload, and `show_load_audit` called it again unconditionally. Both block Tk unnecessarily on thousands of rows and can multiply locked-workbook timestamped duplicates. The user's desired Excel button was already present; generation must be **on demand**.
- `MappingGUI.populate` performed a linear search of the full solver-element list for every object/segment; `solver_by_tag` indexed lookup avoids repeated scans.
- `MappingGUI` initialized `id_value='1'` and called `highlight_inline_id` upon load, painting `NODE:1` even though no user member was selected; change initial state to an **empty selection**, retaining explicit node-lookup actions.
- `components/sections/mapping_audit.py::collect` labeled *all* unmapped candidates `KEEP_SOURCE_ELASTIC`, including the 55 actual zero-solver-tag source members. The new **additive** `assembly_status` field distinguishes an actual solver element from source topology and prevents attaching a candidate override to a present **source-only** object in an otherwise assembled export.
- The 112 release warnings flooded the load audit popup. The UI now groups identical release messages, but exact source object ID and tag evidence remains untouched in `OpenSees_Complete_Export_Report_V118.json` and no release parameter is modified.

## Revised zero-guess workflow

1. **Import:** open original ETABS EDB via temporary working copy. Capture SHA of source EDB and source Excel/workbook where available. **Do not rewrite EDB or copy private source files to GitHub.**
2. **Assemble:** keep the source output root and SHA-verified categorized mirror. Inspect `OpenSees_Complete_Export_Report_V118.json`: `elastic_assembled=true` and no assembly errors means export/build stage completed, **not native ETABS equivalence**.
3. **Check source counts and ID namespace:** source objects can map to many solver segments. Confirm source type `FRAME` vs `AREA` before interpreting an ETABS numeric name. `OpenSees_ID_Lookup.html`, `Elements and mappings`, and the three 3D Plotly views must display **source ETABS ID, topology preview tag, solver tags and display-only label** independently.
4. **Inspect 55 topology-only/unassigned rows:** do not claim they are structural solver beams, invent source section sizes or automatically delete them. Decide from actual ETABS assignment and source topology whether they are intentional construction/mesh guides or a physically omitted member. They are **not** eligible for a nonlinear solver-material/device mapping until actual assembly creates an element.
5. **Review loads:** compare identical source patterns and dead/live participation to the actual ETABS source run, including local force/moment load paths. The source workbook's raw area `GetLoadUniform` empty results do not rule out separately assigned load sets or assembled gravity assignments. Do not replace full gravity 1.0D+1.0L with NBC 105:2025 `0.3` other-live seismic weight.
6. **Validate the physical model:** 32 real foundations + 44 wall-mesh transfer points, **not 76 fixed physical supports**; verify source joint identity, shell-edge MPC transfer, releases/end offsets, 2×12 m X-direction walls with openings, and solver/ETABS elastic stiffness. Prior pointwise reaction residual max ~768.045 kN in a **different provenance-checked source-elastic run** still remains open. The current 286419.758 kN ledger is **not** that older 311367.314 kN solved load state.
7. **Map nonlinear options only after source review:** preserve current `KEEP_SOURCE_ELASTIC` baseline. PEER 2015/12 literature-based parameters are a separately attributed **research transfer**; installed RC fiber templates do not automatically equal ETABS M45 or approved bar schedules. FVD/BRB candidates must not activate merely by viewing a published demo. For M2/M4/M6 FVD, record literature `C,alpha`, actual kN-mm to kN-m conversion and independently justified Maxwell spring `K`.
8. **Run numerical checks in order:** 32-support source-matched full-gravity comparison first, then source-matched ULS/SLS modal and MRSM, and then a full-duration M0/Kobe/ULS XY/YX native nonlinear run with paired waveform fingerprints and complete accepted-step output. If evidence is missing, label **NOT_VERIFIED** rather than letting clean UI imply PASS.
9. **Export on demand:** opening Mapping/Load Audit windows should be lightweight. `Export / open Excel audit` explicitly creates the workbook with a real timestamped sibling if Excel already locks the old filename; do not regenerate on window reopen. Preserve historical root-level XLSX/HTML reader paths until a separate fully tested path migration is approved.

## Acceptance and regression

**Source-level tests**: `tests/test_postconversion_handoff_20261123.py`: separate frame/area numeric ID map; explicit solver-versus-topology status; no source-only candidate assignment; no automatic workbook creation; no default fake NODE:1 visual highlight; warning digest without deleting raw evidence. Existing `tests/verify_v125.py`, `tests/test_shared_3d_prefix_selector.py`, `tests/test_import01_audit_and_workflow.py` remain compatibility baselines.

**Unverified by this audit:** Windows Tk responsiveness on actual workstation, a regenerated real project's complete ID workbook, native ETABS source object assignment, 44 mesh-node force paths, local reaction equivalence, automated original EDB SHA match, or a full successful 25-storey nonlinear history. No EDB, solver stiffness, load factors, wall openings, seismic mass or device parameters are changed.

**Authoritative contracts:** `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `REVIEW_MAIN/02_MODEL/20261122_NATIVE_ETABS_OPENSEES_CONVERSION_AUDIT.md`, `engineering/rules/ENGINEERING_GATES.md`.
