# 2026-11-16 consolidated gravity discrepancy and beam-force audit

Status: GLOBAL EQUILIBRIUM PASS; LOCAL REACTION EQUIVALENCE FAIL; native ETABS internal mesh/constraints unverified.

## Preserved evidence from previous source-linked review

| Quantity | kN |
| --- | ---: |
| ETABS total FZ 1. DL + LL | 311367.313600 |
| OpenSees 32/76/97 total Rz | 311367.31387955 |
| 32-node sum of absolute point differences | 37297.02723154 |
| 76-node sum of absolute point differences | 208926.02678841 |
| OS76 reactions at 44 ETABS-object zero-FZ wall-only nodes | 104463.01353398 |

Prior evidence classified all 44 additional restrained points as connected to two OpenSees wall shell cells and zero frame elements. Source line objects connecting those points lack assigned structural beam sections. ETABS point-object reaction FZ is zero at those 44 names, but all 44 are directly fixed in OS76. This proves a model representation mismatch and a large distribution difference; it does **not** prove the internal ETABS analysis-joint restraints or master-node condensation mechanism.

Previously corrected source beam gross-to-clear self weight (approximately 8652.444 kN) resolved the prior total-load excess, not the separate rigid-end-zone stiffness. ETABS source offset records have rigid factor 1, whereas earlier OpenSees elastic frames were reported as centroid-line transforms without matching rigid offsets. Do not mix historical gravity totals (~320047.789 kN) or seismic preload (~286419.758 kN) with the corrected 1D+1L solve.

## Root-cause candidates in evidence order

1. H1: ETABS native object-versus-analysis-element reporting, wall auto-mesh edge constraints and 44 shell-only base nodes (highest priority).
2. H2: Missing or mismatched frame/column rigid-end-zone bending/shear stiffness and force-transfer points, although self-weight lengths were corrected.
3. H3: Floor mesh and ShellMITC4 load distribution, compatibility and shell-to-frame coupling; a rigid diaphragm is in-plane and does not enforce UZ.

## Minimum discriminating experiment

1. From original exact EDB and gravity combo, capture authored six-DOF restraints, wall-auto-mesh and auto-edge settings, ETABS internal analysis element/point IDs, and both Object and Element level JointReact F1/F2/F3/M1/M2/M3.
2. Compare ETABS and OpenSees **integrated force and moment** resultants on the same wall-base physical cut, including directly applied base-level loads and common origin.
3. Join split ETABS Element Forces - Beams by Story, Unique Name, Output Case, Station and relevant step fields. Align matched OpenSees segmented frame actions via source connectivity IDs, offsets and local directions; compare end shears and moments, not just base reactions.
4. If wall-base resultants match but node reactions do not, analyze ETABS reaction attribution/MPC topology. If regional resultants diverge, isolate load path, wall mesh and rigid-zone transformation one at a time in ETABS/OpenSees equivalent subassemblies.
5. Retain 32 as user-preferred primary comparison, 76 as source-restraint candidate, 97 as sensitivity. No production fixity/stiffness changes until ETABS native source-equivalence tests pass.

## Tool added for split-beam worksheets

Run: python -m components.validation.etabs_split_beam_forces OUTPUT_FOLDER PART1.xlsx PART2.xlsx PART3.xlsx

The stream reader verifies duplicate overlaps and writes CSV (no 1,048,576-row worksheet limit) plus per-source SHA256 manifests. It fails closed if overlap forces conflict and never silently treats unseen workbook data as complete. Regressions: tests/test_etabs_split_beam_forces.py, tests/test_gravity_partial_source_comparison.py. The 531 MB original full export must be inventoried independently. This branch has no native ETABS/OpenSees analysis execution.

Related existing records: REVIEW_MAIN/01_GRAVITY/20261115_FULL_76_SUPPORT_REACTIONS_AND_NATIVE_DISCREPANCY.md and docs/review/PRIMARY_GRAVITY_SEISMIC_INPUT_INVESTIGATION.md.

Public repository must not contain the original EDB, source workbooks, complete geometry, private source paths, user secrets or source result ZIPs.