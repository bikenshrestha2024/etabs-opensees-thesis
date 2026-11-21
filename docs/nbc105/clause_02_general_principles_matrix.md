# Clause 2 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 10–16. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 10–16 | `components/nbc105/clause_02_general_principles.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 10–16 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §2.1 ULS/SLS declarations; overturning, sliding, foundation and evacuation functional prerequisites. Qualitative §2.2–2.5 require engineering review.

**Open / do not claim fully implemented:** Actual stability capacity, seismic detailing, SSI, performance evidence and capacity design cannot be inferred from booleans.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 2 gate can pass.
