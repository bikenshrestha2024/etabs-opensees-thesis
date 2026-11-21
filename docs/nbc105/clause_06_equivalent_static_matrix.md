# Clause 6 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 38–39. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 38–39 | `components/nbc105/clause_06_equivalent_static.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 38–39 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §6.1 ULS/SLS coefficient, §6.2 V=CdW, §6.3 Fi distribution and k exponent, §6.5 six-row deflection factor Table 6-1.

**Open / do not claim fully implemented:** §6.4 load application/eccentricity and production Excel/GUI/ETABS adapter parity remain native-run dependent.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 6 gate can pass.
