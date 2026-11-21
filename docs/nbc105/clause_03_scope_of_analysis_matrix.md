# Clause 3 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 17–21. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 17–21 | `components/nbc105/clause_03_scope_of_analysis.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 17–21 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §3.2 ESM ULS/SLS method eligibility; §3.4 Table 3-1 six components; §3.8 maximum soil-bearing increase.

**Open / do not claim fully implemented:** §3.6/3.7 load combinations need independently verified canonical expression sets; Table 3-1 governs in absence of rational cracked-section assessment. Source incorrectly points irregularity to §5.5; actual §5.4.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 3 gate can pass.
