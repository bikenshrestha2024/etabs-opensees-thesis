# Clause 7 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 40–41. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 40–41 | `components/nbc105/clause_07_modal_response_spectrum.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 40–41 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §7.2 modal effective gravity load, signed floor modal forces; §7.3 directional mass coverage; §7.4 SRSS helper; §7.5 force-only scaling.

**Open / do not claim fully implemented:** CQC correlation coefficient/damping, ≤15% close-frequency grouping, >33 Hz missing-mass correction and ETABS/solver 90% coverage are NOT implemented in this reference module. Source wording for close-mode direct summation is retained for engineering review.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 7 gate can pass.
