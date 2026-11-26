# tools/gravity_reaction_attribution.py: source guide

**What:** a read-only post-processor for a saved ETABS-vs-OpenSees gravity comparison. For each support it reports the OpenSees − ETABS reaction delta and a tributary-statics benchmark, in which each applied nodal load goes to the nearest reaction-bearing support in plan and ties are split equally. It also reports the residual after scaling each support group (core box vs perimeter) by its own OpenSees/ETABS total ratio, and a `consistent_with` tag: `GROUP_AXIAL_STIFFNESS_SPLIT`, `SUPPORT_TOPOLOGY`, `LOCAL_REDISTRIBUTION`, `WITHIN_TOLERANCE` or `UNMATCHED`. Summary outputs: group totals and ratios, the explained fraction, the maximum mirror asymmetry, and optionally the per-group axial-stiffness indicator EA_os/EA_etabs ≈ (ΣN_os/ΣN_etabs)/(mean Uz_os/mean Uz_etabs) at one elevation.

**When:** after `Gravity_ETABS_OpenSees_Direct` has written its CSV files, whenever individual support reactions disagree while the totals match.

**Why:** a symmetric, zero-sum redistribution between groups points to a relative-stiffness assumption, for example ETABS wall in-plane modifiers against `LEGACY_GROSS_SHELL`. That is a different cause from a load or mapping error, and the tool separates the two before anyone changes the model. Finding: [GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md](../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md).

**How:** Python standard library plus `components.inputs.output_contract` (`create_case_run`, `atomic_json`, `write_table`). Units are kN and m. Classification rules (`classify`): zero ETABS reaction with a nonzero OpenSees reaction gives `SUPPORT_TOPOLOGY`; |delta| ≤ tolerance (default 50 kN) gives `WITHIN_TOLERANCE`; a group-scaling residual ≤ 0.5·|delta| gives `GROUP_AXIAL_STIFFNESS_SPLIT`; anything else is `LOCAL_REDISTRIBUTION`. The tool supplies no default core box; the caller passes it.

**Where:** source `tools/gravity_reaction_attribution.py`; tests `tests/test_gravity_reaction_attribution.py`. CLI:

```
python tools/gravity_reaction_attribution.py --supports Gravity_All_Support_Nodes.csv \
  --applied OpenSees_Applied_Nodal_Gravity_By_Pattern.csv --core-box 6 18 6 12 \
  [--mirror-x 12 --mirror-y 9] [--model-nodes Gravity_All_Model_Nodes.csv \
  --etabs-joint-displacements <ETABS Joint Displacements table>.csv --z-ref 95] \
  [--tolerance-kN 50] [--export-dir <ETABS export case root> --case-id NAME --state AS_CONFIGURED]
```

With `--export-dir` the tool creates `<export>/02_GRAVITY/RUNS/<state>/<case>/<run id>/` following the [output-folder standard](../../OUTPUT_FOLDER_STANDARD.md). The JSON and CSV go to `05_COMPARISONS` and the input SHA256 values to `00_INPUT_SOURCE`. The manifest keeps `solver_status = CREATED` and `structural_acceptance = NOT_VERIFIED`. Without `--export-dir` it only prints the summary.

**Which:** it reads CSV files only. It opens no EDB, imports no solver and changes no load, mass or stiffness. Status is always `DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE`.

**Limits:** the tributary benchmark is plan-nearest statics with no continuity and no vertical transfer. Group scaling identifies a pattern but does not prove a cause. The axial-stiffness indicator uses base reactions as a proxy for the axial-force profile up the height. `LOCAL_REDISTRIBUTION` rows need native ETABS element forces.

**Who:** the software maintainer owns the tool; the thesis author owns any engineering reading of its output.
