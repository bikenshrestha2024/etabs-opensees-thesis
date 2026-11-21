# Six-DOF mapped gravity reaction and common-origin audit

Canonical module: `components/validation/reaction_common_cut.py`

## Ownership and workflow

This independent pure-Python diagnostic compares **solved** globally mapped ETABS analysis/object joint reactions and OpenSees reactions with a shared physical origin, as a controlled alternative to judging only FZ total. This module does not own any OpenSees model assembly or CSI API queries, and it never changes model restraints or boundary stiffness. Existing source mapping remains with `components/gravity/etabs_reaction_support_filter.py`.

The source model must be documented by exact SHA256, explicit case `1. DL + LL`, global axes, verified/native provenance, and the precise `PRIMARY_32`/ `WALL_TRANSFER_44`/ `EXTRA_21` partition. Every mapped point requires a complete six-DOF solved reaction, coordinates and unique source mapping. Missing data fail closed; ETABS object-joint zeros are **not** imputed as free analytical joints.

## Equations and output

For each joint, the common-origin moment is `M_origin = M_joint + (xyz-origin) x F_joint`. Signed six-DOF results are summed with `math.fsum`, and separate pointwise absolute errors prevent cancellation from masquerading as agreement. `compare_ablation` explicitly compares four controlled saved solver configurations with the same source EDB, ETABS reference, origin and node mappings but different model hashes. A configuration with the smallest discrepancy is not automatically valid.

## Test / engineering gates

`tests/test_reaction_common_cut.py` tests six-DOF transformations, changed origin, duplicate mappings, incomplete sources, hashes, saved CSV and forced-mismatch scenarios. The CI job is `.github/workflows/six-dof-common-cut.yml`.

**Not verified:** original native EDB and internal ETABS analysis shell edge/MPC forces; source-identical shell formulation, offsets, restraint topology, true physical wall-base cut and structural engineering tolerance. See `REVIEW_MAIN/01_GRAVITY/20261121_REACTION_RAYLEIGH_INDEPENDENT_EVIDENCE_GATE.md`.

[REF source: native ETABS `JointReact` and six-DOF support work; no new NBC equation introduced.]
