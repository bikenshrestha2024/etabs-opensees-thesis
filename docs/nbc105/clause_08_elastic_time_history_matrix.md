# Clause 8 compliance and integration matrix — NBC 105:2025

Source: user-uploaded official Second Revision, printed pp. 42–43. Scope: canonical Python reference functions, no building acceptance certificate.

| Requirement | Source | Implemented reference helper | Verification status |
|---|---|---|---|
| Numerical / machine-checkable requirements | Printed pp. 42–43 | `components/nbc105/clause_08_elastic_time_history.py` | SOURCE_GROUNDED_REFERENCE_TEST_PENDING_FULL_CI |
| Qualitative and modeling requirements | Printed pp. 42–43 | explicit prerequisite / status or documentation | NATIVE_ENGINEERING_EVIDENCE_OPEN |
| Source-to-production caller parity | Previous ETABS/OpenSees workflows | adapter migration and before/after dataset | NOT_VERIFIED |

**Covered:** §8.1.1 3D, gravity, P-Delta, torsion and damping<=5%; §8.1.3 aggregation for <7 (max) and >7 (average), project set N_GM = 8 USER_DECLARED (`project_record_set_evaluation`, tests/test_nbc105_followup_ground_motions.py); §8.1.3.2 member action reduction.

**Open / do not claim fully implemented:** Source is silent on exactly seven records in §8.1.3; return a BLOCKED error instead of inventing an averaging rule. §8.1.2 defers all ground-motion rules to §9.3.2. Actual case duration/convergence need native proof.

This matrix must be extended with one row per subclause, exact table footnotes, ETABS native evidence, explicit test identifiers and source hash before the overall Clause 8 gate can pass.
