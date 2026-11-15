# Source guide: components/model/display_ids.py

**Scope:** A pure-Python human-label adapter. No engineering properties, equations, solver or ETABS state are altered. Source of proposed labels: user specification 2026-11-14; no DOI applies to label presentation.

**Inputs:** iterable of dictionaries with `native_id` (unique within namespace), `category` (NODE, BEAM, COLUMN, CONVENTIONAL OUTRIGGER, BELT TRUSS, CAP TRUSS, SHEAR WALL, FLOOR), and nonnegative integer `storey`. Category is an upstream validated classification, **not inferred from the visual geometry**. The `native_id` key must not conflate a source ETABS ID, preview OpenSees element tag, and actual solver segment tag: invoke the helper separately per namespace.

**Outputs:** string-native-ID -> display label dictionary; 100-based, one-based positions in each category/storey. At positions > 99, labels use a unique overflow form e.g. N-S01-0100. This preserves the requested simple form for the first 99 without risking numerical collisions. Natural examples: N1, N101, N202, B701, C2501, CO701, BT701, CT2501, SW2501, FL2501.

**Effects:** None; does not alter its input, numerical model, EDB, workbook or files. Deterministic under input permutation when native IDs are unique.

**Failure conditions:** Unknown category, invalid floor/position, duplicate native IDs or (defensive) label collision all raise, rather than silently inventing mappings. Native ID sorting is not physical location sorting; a future stable coordinate/order rule must be separately specified and versioned before changing label assignments.

**Unit convention:** dimensionless labels; no engineering conversion. The project's physical unit contract remains kN-m-s.

**Integration contract:** display labels should be added as extra columns to Excel/HTML and Plotly hover tooltips after mapping audit, while retaining existing ETABS unique object, topology tag and actual solver element tag columns. Do not pass label strings to `ops.node`, `ops.element`, `equalDOF`, recorders, or ETABS OAPI. Existing files and algorithms must remain backwards-compatible.

**Test:** `python -m pytest tests/test_display_ids_storey.py -q`. This test command is a prescribed validation, not a claim that tests have executed in the Windows solver environment.

**Engineering review:** [2026-11-14 export review](../../../../REVIEW_MAIN/00_MODEL/20261114_EXPORT_ID_HINGE_MESH_REVIEW.md).


## 2026-11-15 thesis brace hierarchy (user specification)

`member_identity(category, explicit_role=None)` preserves **family BRACE** separately from the thesis role `BR` (ordinary brace), `CO` (conventional outrigger spanning core wall to exterior column), `BT` (belt/perimeter outrigger member), and `CT` (25th-storey cap-truss/outtrigger member). The original source ETABS category is separately retained. **A frame at the roof, or any diagonal, is not automatically CT/CO/BT**: ETABS group membership, source element ID and geometry/drawings must confirm that. An explicitly reviewed ETABS `BEAM` can be assigned a truss role as presentation metadata without changing its OpenSees section or elements. Source `COLUMN`, `FLOOR`, wall and device types cannot be silently converted into brace roles. `FVD` and `BRB` require their own actual element/device source mapping and are not inferred from a SHS section.

The extra classification information does **not** modify ETABS topology, IDs, OpenSees integer tags, material parameters or recorder references. See `tests/test_export_workflow_roles.py` and `tests/test_id_audit_roles.py`.
