# Clause 9 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 44–48. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 44–48 | `components/nbc105/clause_09_nonlinear_analysis.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 44–48 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §9.2 both-sign pushovers; §9.3 minimum records/pairs, XY/YX, scale factor 0.33–3, target interval [Tn,sqrt(Rmu)T1], timestep cap min(record_dt,T1/100,Tn,0.01).

**Open / do not claim fully implemented:** Actual N2 target calculation, true material hysteresis and wall convergence, completed XY/YX histories, exactly-seven-record aggregation and M0–M6 matrix remain OPEN. Positive test declarations are NOT native simulation proof.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 9 gate can pass.
