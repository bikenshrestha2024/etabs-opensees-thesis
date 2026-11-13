# 04 — ETABS ↔ OpenSees P-Delta equivalence

**Q. Does “Stiffness at End of Nonlinear Case” equal “Continue from State”?** No. CSI's linear-case tangent-stiffness option can use a preloaded tangent matrix without including preloading as a new dependent-case force response. A nonlinear direct-integration continuation carries actual state and load history; subsequently applied loads are incremental.

**Q. Is OpenSees `loadConst` a tangent-matrix-only transfer?** No; it freezes all currently present patterns. It does not remove a static ±EL pattern, repair model connectivity, copy constitutive state between independent rebuilt domains or validate P-Delta transformations.

**When:** Compare matched source-model ETABS cases and OpenSees results before claiming physical equivalence. **Evidence:** exact initial conditions, explicit active patterns, material internal states, P-Delta geometric formulations, supports and mode/drift/reaction response. **Who:** qualified numerical and structural reviewers.

[Detailed FAQ](../02_PDELTA_INITIAL_STATES/01_SIGNED_EL_VS_GRAVITY_START.md) · [Cross-model review](../../07_ETABS_OPENSEES/REVIEW.md) · [Q&A home](../README.md)

**Status:** not independently demonstrated for the current 25-storey model.
