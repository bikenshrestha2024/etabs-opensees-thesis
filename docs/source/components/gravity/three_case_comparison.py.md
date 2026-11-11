# Three-case gravity response comparison

Source: [three_case_comparison.py](../../../../components/gravity/three_case_comparison.py)

Uses registered, SHA256-checked, separately completed native OpenSees gravity runs for the 32-node primary research comparison, the 76-node ETABS source restraint case, and the 97-node continuous wall-base sensitivity case.

The **applied gravity load must agree** across the cases. The routine does not change restraints, load factors or model properties, and does not imply ETABS equivalence from balanced reactions.

Outputs: `Gravity_Case_Comparison/Case_Comparison.json`, an Excel workbook, two CSV tables, PNG and PDF comparison figures. Missing cases are explicitly listed. Common-node displacements are only compared at tags shared by the available model cases; matching ETABS coordinates and physical restraint conditions need independent proof.

Tests: `tests/test_gravity_three_case_comparison.py`.
