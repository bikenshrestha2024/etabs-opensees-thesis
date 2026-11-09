# Gravity joint-overlap integration (2026-11-09)

**Source code:** `components/gravity/source_load_reconciliation.py`,
`components/gravity/joint_overlap_review.py`,
`components/model/joint_volume_ownership.py`.

The ETABS converter already builds a geometric RCC volume ledger at export time.
The gravity GUI now runs the overlap review again for the exact source ledger
used by each 32-, 76-, or 97-support gravity case. This produces, alongside
`Gravity_Source_Components_Audit.xlsx`:

- `Gravity_Joint_Type_Overlap_Review.json`
- `Gravity_Joint_Type_Overlap_Review.csv`
- `Gravity_Joint_Type_Overlap_Review.xlsx`
- `Gravity_Joint_Type_Overlap_Solids.csv`

`Gravity_Source_Components_Audit.json` now contains
`joint_overlap_run_evidence` with the source ledger path, SHA256, weight
hypothesis and explicit no-automatic-deduction status. Its Excel report includes
the `Joint overlap source audit` sheet. Gravity GUI logs
`GRAVITY_JOINT_OVERLAP_GATE` and `GRAVITY_JOINT_OVERLAP_FILE` even if a
subsequent independent source-acceptance gate is blocked.

## Engineering safety

This diagnostic does **not** change OpenSees loads, mass, stiffness,
constraints, the seismic preload, or existing ETABS input. The geometric
union is only valid to the extent that original axis-aligned centered
rectangular solids have been verified; it cannot automatically prove ETABS
self-weight convention. The beam end-offset candidate and the geometric joint
union cannot be added as independent deductions without a disjoint-volume,
source-verified ETABS reconciliation.

The default `AUDIT_ONLY` mode reports `applied_gravity_correction_kN=0`.
An explicit pre-existing `VERIFIED_SINGLE_OWNER` exported model is marked
as already source-corrected, with an *unknown* applied amount in this separate
audit, rather than misleadingly claiming a zero applied correction. Policy
mismatches fail closed. A missing source ledger is reported explicitly and
never invented as a zero geometric overlap.

## Verification

Run from the repository root:

```powershell
python -m unittest tests.verify_gravity_joint_overlap_integration
python -m unittest tests.verify_joint_overlap_review
python -m unittest tests.verify_joint_volume_ownership
```

These are regression tests, not certification of ETABS model equivalence.
Rerun the converter and gravity analysis from the same verified original
source model before using regenerated outputs for research conclusions.
