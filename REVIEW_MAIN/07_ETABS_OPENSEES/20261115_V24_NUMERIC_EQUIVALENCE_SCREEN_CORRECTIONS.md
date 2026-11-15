# V24 — ETABS ↔ OpenSees normalized comparison evidence and safety
**Date:** 2026-11-15
**Initial main SHA:** `68f9b5a959965d4b761a525781a0e694b77d2623`
**Classification:** targeted source semantic inspection, code+regression correction; **NOT NATIVE ETABS EQUIVALENCE**

## Concrete defects found

`components/validation/etabs_equivalence_report.py::evaluate()` checked that ETABS reference scalars were finite but did not validate the OpenSees scalar before computing a difference or exporting the record. A `NaN`, `Inf` or malformed OpenSees scalar could therefore produce an invalid numerical discrepancy row. Arithmetic on otherwise individually finite extreme values could overflow to an infinite difference/percentage. The tolerance policy accepted unknown metric names, booleans and nonnumeric values that might produce unexpected exceptions or deceptive interpretation. The comparison method assumes **exactly eight semantic key fields**, but did not explicitly enforce that schema.

## V24 corrections and test evidence

- Validate exactly eight distinct normalized key fields: method, limit state, case, axis, location, metric, unit and response basis.
- Require a dictionary policy; reject nonboolean `assumptions_verified`, malformed tolerance overrides, unknown metric names, boolean/negative/nonfinite thresholds.
- Validate every ETABS and OpenSees scalar before matching; an unmatched OpenSees NaN remains a **data-integrity error**, never a harmless missing-reference case.
- Detect arithmetic overflow in difference and percent deviation, including huge opposite-signed but individually finite results.
- Maintain the existing explicit `NOT_COMPARABLE` state when engineering source comparability has not been independently approved; a numerical screening PASS is not a structural design certificate.
- Regression tests added in `tests/verify_etabs_direct_equivalence.py`, run in existing `NLTHA Python quality checks` CI.

## Remaining physical equivalence requirements

No real native ETABS OAPI or independent OpenSees solve was run during this targeted review. Obtain original source EDB SHA, authoritative Aw/T1 workbook provenance, actual model export SHA, six-component signed reactions, correct 32/76/97 restraint interpretation, complete geometry and opening mapping, calibrated effective stiffness, mass and floor load path, modal period/mass/eigenvectors, ESM/MRSM ULS/SLS force and displacement scaling, torsion, P-Delta and drift at the *same* basis and location. Record tolerance source, independent reviewer and case matching. `REVIEW_MAIN/07_ETABS_OPENSEES` is the canonical location for discrepancy and acceptance evidence.

**Acceptance:** `SOFTWARE_NUMERIC_GATE_CORRECTED_NATIVE_EQUIVALENCE_UNVERIFIED`.
