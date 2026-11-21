# etabs_comparison_ablation.py: stepwise ETABS comparison ablation and period runs

**Implementation:** [etabs_comparison_ablation.py](../../../tools/etabs_comparison_ablation.py).

**Status:** run driver and comparison only. Results are `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.

## What it does

For each step (name plus top-level config updates; `null` deletes a key):

1. copies a verified clear-beam export (`tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py` output), applies the updates and reassembles with `components.model.assembly.prepare_complete_export`;
2. writes the gravity runner with `components.gravity.gui_and_reports._runner_source` (read with `ast`, so tkinter is not needed) and runs it in a child process with `GRAVITY_1.0D_1.0L` and `ETABS_NONZERO_REACTION_DIAGNOSTIC` (the 32 primary supports), exactly as the gravity GUI does;
3. compares OpenSees `nodeReaction(n, 3)` with the matched ETABS reactions (`Gravity_All_Support_Nodes.csv`, `MATCHED_GLOBAL_Z` rows): per support OpenSees − ETABS, max |diff|, RMS, Σ|diff|, and core (plan box 6 ≤ x ≤ 18, 6 ≤ y ≤ 12 m) and perimeter sums.

Steps run one after another, never in parallel. Output: `ABLATION_SUMMARY.json`, `<step>_reactions.csv`, and per-step `Gravity_Ablation_Run/REACTION_COMPARISON.json`.

`run_rayleigh` runs `components.modal.rayleigh.run` and `run_eigen` runs the modal GUI runner (`components.modal.gui_and_reports._runner_source`, linear model with the seismic gravity preload), each in a child process. `first_translational_modes` picks the lowest mode whose UX (or UY) participation is at least 10 % and larger than the other two directions; it is a candidate, and the mode shape still needs review.

## CLI

```
python tools/etabs_comparison_ablation.py --base-export <verified clear-beam export> ^
    --etabs-support-csv <Gravity_All_Support_Nodes.csv> ^
    --etabs-reaction-table <Joint Reactions csv/xlsx with case "1. DL + LL"> ^
    --out-dir <run>\02_RESULTS\ablation [--steps steps.json] [--only S0,S1]
```

Without `--steps`, `DEFAULT_STEPS` runs the final sequence of the [run finding §8](../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md):

- S0: legacy;
- S1: native wall and frame modifiers, beam J gross;
- X2: plus beam J 0.01;
- X3: plus rigid end zones;
- X8: plus wall-base edge kinematics with lumping.

A step may set:

- `"support_strategy"`: a gravity GUI strategy (default `ETABS_NONZERO_REACTION_DIAGNOSTIC`);
- `"lump_to_reference": true`, which calls `lump_to_reference_supports`. Each extra support reaction is split (1 − t, t) onto the two reference supports bounding the shortest collinear edge that contains it. This is the consistent load of a linear shell edge. A node that lies on no such edge raises an error.

Tests: `tests/test_etabs_comparison_ablation.py` (comparison statistics and runner-source loading only).
