# 2026-11-19 Rayleigh independent mass/stiffness second opinion

## Verified source-level discovery

NBC 105:2025 §5.1.1 demands storey weight Wi and elastic floor centre-of-mass translation di with torsional effects ignored. The equation and units in `components/modal/rayleigh.py` are consistent with that formula. However the full building uses **distributed nodal masses on a 3D frame-and-shell mesh** while `components/model/assembly.py` builds `NBC105_ESM_Story_Weights_Assembled_V118.csv` by assigning a mass at intermediate elevation `z` to the **first diaphragm above** it.

This is NOT an algebra error: the story ledger's total mass can reconcile exactly to the nodal mass and still shift the first vertical moment and modal kinetic-energy representation. The accepted eigen period and the NBC storey-lumped Rayleigh estimate cannot be declared physically equivalent just because their resulting values are close.

## Implemented diagnostic (no change to engineering mass, stiffness or model)

`components/modal/rayleigh_mass_audit.py::audit_rayleigh_mass_elevations` is an independent, pure-Python accounting check invoked by the Rayleigh runner. It:

- verifies each source nodal-mass allocation against its matching source storey ledger (node-by-node mapped to first upper diaphragm)
- reports the weight of intermediate-elevation nodes relocated upward, maximum lift, and the first-moment shift (kN·m)
- exposes horizontally partially restrained nodes as a separate axis-specific mass-check concern
- rejects missing/nonfinite nodal mass, malformed geometry, out-of-roof nodal masses, and floor-weight mismatches
- preserves status `SOURCE_MASS_TOTAL_RECONCILED_VERTICAL_LUMPING_NOT_EIGEN_EQUIVALENCE`.

This report **does not calculate** the full consistent 3D mass matrix, the mass-dependent Rayleigh quotient from all physical node displacements, or a certified ETABS eigenperiod. It does not modify the NBC quotient, alter nodal masses or change floor assignments. Private ETABS files and ground motions are not committed.

## Mandatory engineering follow-up

1. Read full existing 3D solver eigen-period and mass-participation outputs *from the same state*, including ULS/SLS, shell modifiers and boundary restraints. Ensure first mode in each direction corresponds to translation, not the torsional mode.
2. Obtain displacement of each active physical mass node under the torsion-suppressed reference force: evaluate a **continuous nodal kinetic-energy comparison** versus the NBC story-lumped `ΣWi di²`, preserving interpolated wall/slab kinematics. Do not replace NBC `Wi` by the continuous variant without the approved standard interpretation.
3. Compare floor centre-of-mass location and diaphragm-membership topology from native ETABS export, including support and boundary mesh nodes that may not be tied to any diaphragm; verify MPC and fixed-DOF transformation behavior.
4. Establish whether the gravity-preloaded `PDelta` tangent is the intended elastic stiffness for NBC §5.1.1; compare with ETABS P-Delta setup on exact source model. Review shell property and member end offsets.
5. Re-run identical native ETABS versus OpenSees source hash and all support reaction components for 32 / 76 / 97 diagnostic topologies before design acceptance.
6. Keep full active-source semantic review, X-wall element 110280 convergence, and all 224 M0–M6 histories explicitly OPEN until actual native evidence exists.

## Acceptance status

- Source mass-ledger arithmetic check: **implemented with synthetic tests, CI required**.
- Distributed-versus-lumped mass physical equivalence: **not verified**.
- Rayleigh formula numerical construction: **previously source-inspected, independent benchmark in CI**.
- Full ETABS versus OpenSees fundamental modes, COM and constraint equivalence: **not verified**.
- Full active code symbol-level semantic review: **not complete**.
- Native gravity nodal reactions, nonlinear wall, complete M0–M6 matrix: **open**.

Related: `REVIEW_MAIN/02_ESM/20261119_RAYLEIGH_SECOND_OPINION_AND_SOURCE_EVIDENCE_GATES.md`; `docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md`; `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261119_STRICT_ACCEPTANCE_CHECKPOINT.md`.
