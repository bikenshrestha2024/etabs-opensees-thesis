# Three-case gravity response comparison

Source: [three_case_comparison.py](../../../../components/gravity/three_case_comparison.py)

Uses registered, SHA256-checked, separately completed native OpenSees gravity runs for the 32-node primary research comparison, the 76-node ETABS source restraint case, and the 97-node continuous wall-base sensitivity case.

The **applied gravity load must agree** across the cases. The routine does not change restraints, load factors or model properties, and does not imply ETABS equivalence from balanced reactions.

Outputs: `Gravity_Case_Comparison/Case_Comparison.json`, an Excel workbook, two CSV tables, PNG and PDF comparison figures. Missing cases are explicitly listed. Common-node displacements are only compared at tags shared by the available model cases; matching ETABS coordinates and physical restraint conditions need independent proof.

The evidence-status worksheet writes the list of solved scenario labels as comma-separated text. The JSON retains the list, and Excel retains numeric counts and reaction quantities as numbers. The workbook is published atomically.

Tests: `tests/test_gravity_three_case_comparison.py`.


## 2026-11-15 exact ETABS native FZ across 32/76/97 independent gravity cases

`join_source_etabs_reactions(available, reaction_rows)` reads `ETABS_Nonzero_Reaction_Support_Audit.json` **only from the currently registered completed primary32 Gravity_Result_V110.json sibling directory**; it never searches an unrelated source model, timestamp or GUI path. Validates exactly 76 source restrained six-DOF point records, 32 matching primary source tags, source ETABS vertical reaction total, finite scalar FZ and unique map. Excludes synthetic 97 support points from fabricated ETABS comparisons. A missing ETABS source audit becomes a visible `SOURCE_ETABS_SUPPORT_AUDIT_NOT_FOUND` report, not a blank claim of validated equivalence.

An exact source audit produces a full **97-node ETABS/OpenSees comparison table** as `ETABS_OpenSees_All_76_Source_Support_Reactions.csv` and the `ETABS vs OpenSees all` worksheet inside the existing `Gravity_32_76_97_Comparison.xlsx`, with `source_dof`, original ETABS FZ and separately solved 32/76/97 Rz plus differences where comparable. The summary includes total absolute per-support difference and the 76-run reaction carried by the 44 source-restrained points with zero ETABS reported FZ. Existing writer/reader file paths remain unchanged. New records retain the explicit source/solver discrimination `SOURCE_NODE_MAPPED_REACTIONS_NOT_STRUCTURAL_EQUIVALENCE`.

Tests: `tests/test_gravity_full_source_reactions.py`, existing `tests/test_gravity_three_case_comparison.py`. Native 3D ETABS point-element auto-mesh transfer, rigid end zones and full six-component reactions remain engineering gates. Review case: `REVIEW_MAIN/01_GRAVITY/20261115_FULL_76_SUPPORT_REACTIONS_AND_NATIVE_DISCREPANCY.md`.
