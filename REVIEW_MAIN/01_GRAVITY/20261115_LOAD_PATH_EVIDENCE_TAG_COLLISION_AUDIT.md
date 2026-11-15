# 2026-11-15 — Gravity load-path recorded evidence tag collisions

**Baseline:** `248329658b5976c51834e96fe9662b06a955062d`  
**Status:** CONFIRMED SOFTWARE DATA-INTEGRITY DEFECT; NATIVE PHYSICS NOT VERIFIED  
**Scope:** `components/gravity/load_path_formulas.py`, the saved-result reporting functions `recovered_vertical_transfers` and `vertical_joint_balance`.

## Evidence and semantic reasoning

Before the change, `nodes`, `edges`, `forces` and later `reactions` were constructed via dictionary comprehensions keyed by `int(tag)`. Duplicate saved node IDs, element IDs, force-vector IDs or reaction node IDs silently replaced earlier entries. A syntactically complete but ambiguous recorded force set could then produce a floor-cut or joint-balance table with missing, replaced, nonfinite or mismatched data. Furthermore, `recovered_vertical_transfers(payload, [])`, which the joint-balance method calls as a completeness check, did not inspect actual force-vector values unless a cut crossed a member. Nonfinite force vectors could pass that preflight.

This is a proven source-code evidence-checking defect, **not proof that the native solver actually produced duplicate tags**, and is not an ETABS/OpenSees physics fix.

## Coordinated correction

Validate unique canonical integer node, element and global-force IDs before aggregating. Check the full endpoint membership, node order and 6-DOF-per-node vector length for every saved element, even when no cut is requested; reject nonfinite force vectors and node elevations. On joint-balance reporting reject duplicate/unknown/nonfinite support reactions and applied loads. Preserve signed Fz, original solver values and normal output schema for valid input.

## Regression and negative gates

`python -m unittest -v tests.test_gravity_loadpath_evidence_integrity` covers valid transfer and joint balance, duplicate/aliased source IDs, off-cut NaN, missing node, invalid elevations, duplicate support reaction and invalid applied load. Added to the existing integrated GitHub Actions audit, without executing native OpenSees/ETABS or using private case exports.

## Physical acceptance remains separate

- Source-hash-matched gravity run and ETABS source applied loads
- 32 original restraints versus 76/97 mesh/restraint interpretation
- Complete six-DOF joint and support reaction vectors
- ShellMITC4 slab/beam/wall connectivity and mesh convergence 04/08/16
- Signed element end-forces verified in consistent global coordinates
- Model-specific native gravity state, modal properties and seismic design

**Review state:** SOFTWARE SOURCE FIX COMMITTED ON REVIEW BRANCH; CI pending; NATIVE_NOT_VERIFIED. No automatic move, rename or deletion of evidence files.
