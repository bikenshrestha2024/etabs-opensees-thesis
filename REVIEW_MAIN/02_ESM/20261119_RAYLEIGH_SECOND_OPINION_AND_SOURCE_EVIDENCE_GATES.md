# Rayleigh V126 second-opinion review — 19 November 2026

## Verdict and boundary

The **NBC 105:2025 §5.1.1 equation is implemented in its declared kN–m–s units**. The saved V126 X/Y periods cannot be certified ETABS-equivalent solely from matching a same-domain eigenperiod. Current data include a full 3D distributed-mass, potentially P-Delta-modified model with intermediate wall/frame mass assigned to the next floor for the NBC storey ledger. This storey-lumped approximation is not guaranteed to equal the 3D modal mass operator and forces. The complete native-model benchmark is an OPEN engineering gate.

The 18 November documented ULS results (source document claims, **not independently rerun**):

| Direction | V126 floor-node Rayleigh | Same-domain eigen | Rayleigh minus eigen |
| --- | ---: | ---: | ---: |
| X | 1.662332 s | 1.663934 s | -0.001602 s |
| Y | 2.383772 s | 2.383914 s | -0.000142 s |

An exact Rayleigh quotient on a common positive-definite mass/stiffness model **gives a period no greater than the longest fundamental eigenperiod**, so the sign of the differences above is not proof of an error. Their small size also does not independently prove the floor mass and constraints agree. The Rayleigh quotient with arbitrary elastic trial displacements is an approximation; the selected empirical-period-based lateral force exponent is a trial load pattern, not automatically the final NBC §6.3 design force distribution.

## Reviewed code and confirmed problem

- `components/modal/rayleigh.py` computes 25-storey physical tied-node UX/UY increments after establishing a torsion-restrained gravity state, then applies one step of reference lateral force. It verifies floor translation spread, reference load factor and reaction equilibrium. This numerically addresses the *retained master SP/MP drift* previously observed in OpenSees 3.8.0.
- `components/model/assembly.py` uses rigid diaphragms, masses at every mesh node, a `PDelta` transform for elastic frames, and model-config-selected shell stiffness. The mass-weight CSV assigns intermediate mesh node seismic weights to the next floor. **Confirm that both eigen and Rayleigh use identical mass, boundary conditions, P-Delta state, section modifiers and support options**.
- `components/inputs/project_workbooks.py` previously imported a matching V126 cache based on its status label, basic period metadata and SHA of assembled model and storey weight CSV, without recomputing saved `Wi*di²`, `Fi*di`, actual force total, reaction balance or diaphragm spread. It also did not bind the cache to the model configuration file. These are confirmed source-level gaps.

## Code correction in this PR

1. `verify_saved_rayleigh_axis()` reconstructs saved all-storey terms and checks one-step load-factor and reaction/translation integrity; bad, missing or inconsistent evidence fails closed.
2. The Rayleigh runner stamps `model_config_sha256`. Import now requires exact current model-config SHA in addition to assembled model and weight-source SHA. Older V126 reports lacking config SHA will be treated as stale and require regeneration; no silent migration or invented substitute.
3. Tests include altered sums, corrupted periods, invalid masters, bad reaction/error, missing physical constrained nodes and skipped/missing one-step proof.

**Not changed:** force-shape selection, `g=9.81`, base supports, ETABS geometry, gravity/elastic stiffness policy, native model results, library material parameters or `1.25T_{emp}` period cap. They are subject to the separate native review below.

## Required additional independent engineering checks

1. **Mass operator**: compare every solver nodal X/Y mass with reconstructed `Wi/g` aggregated by identical floor mapping, including wall nodes between levels, master rotations and rigid-diaphragm transformation. Quantify vertical lumping shifts and compare eigen modal participation.
2. **Stiffness/initial state**: run a matched native eigen, one-step Rayleigh and a second physically independent static method on the **same** stiffness and gravity/P-Delta equilibrium, source configuration and support topology. Do not compare ULS and SLS or different elastic shell policies.
3. **COM**: verify floor-master geometry and every rigid-diaphragm MPC; compute centre-of-mass displacement from consistent kinematics with torsion exactly zero. Check loose/unconnected shell nodes that are not actual diaphragm slaves.
4. **Reference-force shape**: re-run at 0.5%, 1% and 2% *with the same shape*, verify displacement proportionality, then compare a different rational trial pattern. A single 1% result does not establish amplitude independence in the gravity-preloaded model.
5. **OpenSees constraint treatment**: compare one-step Transformation with independently solved Lagrange/SP-MP and, where physically appropriate, eigen modes; rule out retained master drift. A 3-node native passing test does not close the 25-storey benchmark.
6. **ETABS comparison**: independent source EDB/analysis export source hash, 32/76/97 support and wall-edge MPC policy, section modifiers and mass, 25-storey force/reaction/COM displacements, and case-by-case source-to-target results.
7. **NBC design adoption**: confirm §5.1.2 wall area grouping, basement height reference, 1.25 empirical upper bound and §3.2.1 high-rise ESM applicability. Keep Rayleigh period verification separate from ESM design eligibility.

## Other acceptance gates remain open

Active-source symbol-level semantic review is not complete, ETABS–OpenSees individual support reaction discrepancy remains as large as 756.511 kN in best documented probe, the initial X-wall element failure remains unsolved, and no completed validated 224-case M0–M6 full-duration native batch has been produced. This report does not relabel any of them as PASS.

**References:** `docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md`; `docs/validation/20261118_32_SUPPORT_GRAVITY_CONVERSION.md`; NBC 105:2025 §5.1.1–5.1.3; OpenSees 3.8.0 TransformationDOF_Group constraints (upstream issue/PR linked in earlier Rayleigh report).
