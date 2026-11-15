# Gravity support sensitivity — reported equilibrium percentage consistency

**Review date:** 2026-11-15  
**Baseline:** `248329658b5976c51834e96fe9662b06a955062d` (`main`)  
**Classification:** CONFIRMED SOFTWARE DATA-INTEGRITY DEFECT; NATIVE ENGINEERING NOT VERIFIED  
**Owner:** `components/gravity/support_scenarios.py::compare_wall_support_gravity`

## Actual source inspection

The sensitivity comparison already independently verified both case loads, per-node reaction sums and a force equilibrium residual. It also exported `report.equilibrium_error_percent` without reconciling this cached field to the **same node reaction rows**. A reused or stale percentage could therefore be published as if it represented the accepted calculation.

This is not evidence that ETABS restraints or OpenSees node reactions are physically correct. The function remains a comparison of two prescribed restraint cases, not an ETABS foundation verification.

## Coordinated correction

Compute the percentage magnitude from the independently summed `rz_kN` and `applied_vertical_load_kN`; reject a published percentage if inconsistent. Preserve sign flexibility in historical reporting; allow the same 0.01 kN rounding floor already permitted for scalar equilibrium. Add regression tests for a stale 7% report despite balanced rows and a 0.005 kN rounding residual.

Do **not** change solver physics, boundary conditions, seismic mass, default support policy, source model, or any imported historical result. This change only affects comparison acceptance and exported report integrity.

## Evidence and acceptance

- **Source inspected:** `components/gravity/support_scenarios.py`, `tests/verify_gravity_support_scenarios.py`
- **Regression command:** `python -m unittest -v tests.verify_gravity_support_scenarios`
- **Static integrated workflow:** `.github/workflows/integrated-repository-audit.yml`
- **Software acceptance:** PENDING until CI executes on this exact branch
- **ETABS/OpenSees native equivalence:** NOT_VERIFIED (source 32 vs mesh-derived 76/97 remains separate)
- **Full repository semantic review:** NOT_COMPLETE; this is a bounded manual finding

## Remaining physical checks

Review actual ETABS source six-DOF restraints, 32 original joint positions, associated wall auto-mesh DOF constraints, nodal reaction sign/unit conventions and full gravity load definition. Pair one-to-one model source fingerprints; test signed six-DOF joint/group reactions and mesh transfer. A software PASS is not design approval.
