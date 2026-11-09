# gravity_etabs_latest.py — current offline gravity comparison

**Python source:** [components/validation/gravity_etabs_latest.py](../../../../components/validation/gravity_etabs_latest.py)
**Subsystem:** Independent ETABS-to-OpenSees gravity validation

## Scope and inputs

This module reads previously completed, native ETABS `Joint Reactions`
results for the exact `1. DL + LL` combination, the preserved
`OpenSees_Element_Connectivity.json` unique-name mapping, and
`Gravity_Case_Reaction_Index.json` with the three independently solved
`GRAVITY_1.0D_1.0L` scenarios:

- `ETABS_NONZERO_REACTION_DIAGNOSTIC` (32 supports);
- `ETABS_SOURCE_SUPPORTS` (76 supports);
- `CONTINUOUS_WALL_BASE_FIXED` (97 supports).

The registry's paths, support tag sets, source model fingerprint and source
input hashes are checked before comparison. Absent files, stale source files,
mismatched strategies, uncompleted runs and an unmatched export fail closed.
The original EDB identity and the XLSX-to-EDB correspondence must still be
independently established; hashing a workbook alone does not prove its
provenance.

## Outputs and limitations

Output folders `PRIMARY_32` and `ETABS_NODE_POSITION_76` contain
comparison Excel, JSON and CSV. The 97-support case is retained as a
sensitivity comparison and must not be presented as ETABS support
equivalence. Files `OFFLINE_GRAVITY_32_76_97_INDEX.json` and
`README_FIRST.txt` record the cases, hashes and limitations.

The GUI can place this output inside the latest wall-base comparison folder
under `ETABS_Full_Table_Offline_Comparison`, where the existing evidence
ZIP collector recognizes it. The standalone Spyder entry point is
`Run_Offline_ETABS_Latest_Gravity.py`.

A zero ETABS reaction is not proof a node is unrestrained. A mapped ETABS
joint without an OpenSees reaction remains missing rather than being
fabricated as zero. Differences at wall mesh joints must also be assessed
by foundation regions and connected wall forces.

This script does not launch ETABS, re-run OpenSees, change support
constraints, adjust force totals or certify structural equivalence.
Physical member self-weight, beam end-offset volume conventions, section
and object modifiers, shell mesh connectivity, loads and foundation
conditions require independent source audits.

[REF docs/review/GRAVITY_ETABS_COMPARISON.md]
[REF components/validation/gravity_etabs_offline.py]
[REF components/gravity/comparison_bundle.py]
