# Tasks A/B — independent native-evidence gate (2026-11-21)

**Status:** implementation of offline comparison gates, **NOT** recovered Claude branch and **NOT** native ETABS/OpenSees verification. The unpushed local branch `feat/joint-reaction-rayleigh-fix` and reported local SHA `3c63a30` are not accessible through the GitHub remote. This work is on a distinct review branch so source changes cannot silently replace unreviewed shell, end-zone or support settings.

## Purpose and non-goals

This change adds two strict, pure-Python **diagnostic tools**. It does **not** change seismic or gravity loads, support fixities, wall shell formulation, end-zone offsets, mesh density, nonlinear materials, OpenSees model assembly or NBC coefficient calculations.

The tools accept only native-recorded numerical inputs and fail closed for missing point mappings, bad units, unverified source identities, invalid DOFs, incomplete X/Y Rayleigh evidence, changed floor ledgers and non-finite results.

### A. Common-origin six-component gravity reaction diagnostics

Module: `components/validation/reaction_common_cut.py`

Input: private JSON with EDB and model SHA256 values, explicit case `1. DL + LL`, global `kN/m` coordinates, ETABS `OBJECT_JOINT` or `ANALYSIS_JOINT` reaction level, native-restraint review status, origin, mapped ETABS/OpenSees node IDs, 3D coordinates, six global reaction components per node, and group membership `PRIMARY_32`, `WALL_TRANSFER_44`, `EXTRA_21`.

For each node with `r=(x,y,z)-origin`, calculate:

`F_cut = (Fx,Fy,Fz)`, `M_cut = M_joint + r × F_joint`.

The code reports original local reaction differences, six resultant differences and absolute nodal discrepancy sums per group and total. `PRIMARY_32` requires 32 mapped records; `WALL_TRANSFER_44` requires 44. Unmatched nodes are errors: an absent solved reaction may not be manufactured as zero. A blank OS32 reaction on a released node is not a zero in OS76. Compare **each configuration in a separate native result**, not by mixing different support topologies into one common-cut file.

```bash
python -m components.validation.reaction_common_cut PRIVATE_NATIVE_REACTIONS.json OUTPUT/A
```

Emitted: `Reaction_Six_DOF_Common_Cut.json`, `Reaction_Six_DOF_Common_Cut.csv`, in the user-specified local output folder. Keep EDB, actual geometry, raw tables and personal paths **out of public GitHub**.

**Critical limitation:** comparing ETABS point-object reactions to OpenSees nodes does not reproduce ETABS internal analytical mesh edge forces. A six-component sum of object reactions is not a physically complete wall-base cut without separate wall-edge, frame and applied-load contributions.

### B. Source-hashed NBC 105:2025 §5.1.1 Rayleigh arithmetic

Module: `components/modal/rayleigh_xy_evidence.py`

Both X and Y require verified solver result snapshots, identical gravity and torsion conditions, floor-master identities, positive seismic story weights, reference forces and two displacement states: baseline (after gravity) and loaded perturbation. The calculation uses **incremental displacement** `di = loaded - baseline`, never total gravity displacement.

`T = 2π√(Σ Wi di² / (g Σ Fi di))`, where `g=9.81m/s²` from the canonical NBC clause module. Saved reference periods from ETABS are recorded separately without claiming identical period definition or model representation.

When a second independent perturbation solve is available, the checker requires scaled force vectors and compares their displacement scaling and period invariance. **1% shape and 0.1% period checks are diagnostics only**, not NBC 105 tolerances or physical-equivalence acceptance. These do not replace the previously required continuous nodal mass-operator comparison.

```bash
python -m components.modal.rayleigh_xy_evidence PRIVATE_RAYLEIGH_XY.json OUTPUT/B
```

Emitted: `Rayleigh_XY_Independent_Evidence.json`.

## Native work still mandatory before structural acceptance

1. Capture exact private EDB SHA, ETABS frame/shell object settings, *analytical* shell formulation and meshing, six native restraint DOFs, MPC constraints and wall edge transfer; compare shell-thin/thick and 1 m subdivision **one variable at a time**.
2. Verify native ETABS end-offset records on the correct ends and members and distinguish clear-length beam self-weight from end-zone stiffness and section demand recovery.
3. Compare common physical wall-base **forces and moments** and frame/slab corner flows, not merely 32 mapped support reactions.
4. For baseline, wall mesh, rigid end zones, and combined models, retain separate **native** support records and reproduce 32/76/97 sensitivity cases without silently changing original source restraints.
5. Verify source floor mass, diaphragm COM/master mapping, gravity/P-Delta tangent, reference lateral vectors and full X/Y displacement profiles. Execute and publish native Rayleigh values from the selected exact source model.
6. Diagnose first-step X-wall nonlinear convergence before running full-duration eight-ground-motion XY/YX analyses. Do not start Annex A/B member design until NLTHA is functioning.

## Acceptance / merging policy

Synthetic offline tests are automated in `.github/workflows/six-dof-common-cut.yml`. They establish *arithmetic and input-provenance behavior only*. Native ETABS/OpenSees results, analytical mesh verification, physical reaction equivalence, Rayleigh period equivalence and full NLTHA remain **OPEN**.

**Do not merge into `main` as a certified Task A/B solution.** Review the diagnostics separately; recover/compare the missing local Claude branch first, then require native-evidence approval before changing physical solver presets or production defaults.
