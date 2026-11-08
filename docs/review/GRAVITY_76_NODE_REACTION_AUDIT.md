# Original 76-node ETABS/OpenSees gravity reaction audit (V161)

**Engineering scope:** fixed-node reactions for `1.0DL+1.0LL` with the ETABS ULS elastic stiffness properties. This is NOT a 1.5(DL+LL) load combination and NOT the 0.3LL seismic preload.

The correct numerical baseline for ETABS matching is the original `ETABS_SOURCE_SUPPORTS` model with **OpenSees node tags 1–76**, not a comparison against the 97 fixed nodes in `CONTINUOUS_WALL_BASE_FIXED`. The latter model is a foundation sensitivity study only.

## How to obtain the complete audit from the gravity GUI

1. Pull current `main`, restart the Python app and rebuild the source export. The new 3D HTML control `Zoom to Node` is created by `components/model/id_audit.py`. Existing saved HTML files on disk are **static**; changing Python does not retrofit files previously generated.
2. Run the original 76-support gravity model with the desired unchanged load case. Run ETABS `1. DL + LL` from the original verified source EDB or supply the previously extracted `etabs_gravity.json`. Preserve source hashes and model identity.
3. In `10_GRAVITY.py`, use the existing direct ETABS comparison with 1.0DL+1.0LL and then `Bundle gravity evidence ZIP`. The exporter reads `OpenSees_Element_Connectivity.json`, the source gravity `Gravity_Result_V110.json`, and ETABS `joint_reactions`.
4. Open the new `node_audit_76/Gravity_76_Source_Support_Reactions.xlsx` from the ZIP or extracted bundle:
   - `Nodes 1-76`: original OpenSees tag, ETABS unique point ID, global coordinates and the two independently extracted vertical reactions.
   - `Critical nodes ranked`: every valid matched pair sorted by |OpenSees Rz – ETABS Rz|, with a chart for the 20 largest mismatches.
   - `Review summary`: expected count, valid matched count, missing/ambiguous entries and source reaction sums.
   - CSV and JSON equivalents preserve data without Excel.
5. Open `source/OpenSees_ID_and_Support_Audit.xlsx` to inspect precise source mapping, and the Plotly structural HTML view if included. Choose Node selection → OpenSees node tag → enter `41` → Select to highlight → Zoom to Node to focus at its exact source XYZ. The button requires a newly generated HTML file.
6. Check regions only after reviewing explicit geometric membership of all core/side wall and column support groups. A zero at an ETABS mesh joint is not necessarily an absent wall or zero wall force. Do not infer ETABS support reactions for missing source points.
7. For every major discrepancy inspect support restraint, source position, wall/column family, wall shell/column axial stiffness and connectivity, slab load transfer, offsets, actual applied gravity (and total balance) in that order.

## Output locations and mandatory evidence

`<gravity_root>/Gravity_Evidence_Upload/Gravity_ETABS_OpenSees_Evidence_VNN.zip`
contains:
- `node_audit_76/Gravity_76_Source_Support_Reactions.xlsx`, `.csv`, `.json`
- `node_audit_76/Gravity_76_Critical_Reaction_Nodes.csv`
- `source/OpenSees_Element_Connectivity.json` and source ETABS node-to-OpenSees mapping
- `source/OpenSees_ID_and_Support_Audit.xlsx`, plus generated HTML views when present
- `opensees/Gravity_Result_V110.json` and response CSVs, and both wall-base runs when supplied
- `etabs/etabs_gravity.json` and `direct_comparison/` tables where available
- `EVIDENCE_MANIFEST.json`, `EVIDENCE_FILE_PATHS.txt`, the validation scorecard, and `REVIEW_76_NODES_FIRST.txt`.

If native ETABS extraction is missing, **the node audit still lists tags 1–76**, but ETABS values remain blank, every row has an explicit missing status, and the comparison is **not verified**. A ZIP is not proof of model equivalence.

**Do not label numerical solver equilibrium as ETABS node-by-node acceptance.**

This workflow changes only evidence exports and HTML visualization, not structural stiffness, loading, restraints or solver reactions.

[REF components/validation/gravity_node_comparison.py] for verified coordinate/point mapping.
[REF components/model/id_audit.py] for HTML node selection and exact XYZ zoom.
