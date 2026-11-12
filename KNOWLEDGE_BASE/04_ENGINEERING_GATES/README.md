# Engineering status and acceptance logic

Every conclusion must explicitly distinguish:
- `SOURCE_CHECKED`: EDB/workbook/motion identity and source data confirmed.
- `NUMERICALLY_CONVERGED`: accepted finite solver history for specified state/record/duration.
- `ETABS_OPENSEES_MATCHED`: like-for-like gravity, mass/stiffness/response comparison met declared criteria.
- `EXPERIMENT_VALIDATED`: applicable material/element/device behavior reproduced with documented error metrics.
- `CODE_ACCEPTED`: governing NBC and adopted supplemental checks, scale/dt, motion pairing, torsion/drift and loads reviewed.

**Why:** the repository may pass CI, a single wall element, or one XY record without meeting thesis-grade nonlinear acceptance.

**Which unresolved P0 gates:** frame bar layouts and wall FSAM tag mapping; X-only first-step wall failure (tag mapping and physical cause not yet established); verified ETABS gravity/mass and supports; source provenance for some earthquake records, exact site evidence and device qualification.

**When can M0–M6 be run as production?** After required preflight/validation and matched sources, execute 7 variants × ULS/SLS × eight pairs × XY/YX. Total 224 intended runs—not 224 completed results. Preserve failed/truncated cases and report exclusions.

**Who validates:** researcher constructs and documents the models; a competent structural/earthquake engineer independently reviews physical interpretation and code applicability; numerical/software reviewer verifies solver and recorded evidence. Code alone does not establish human endorsement.

Sources: [engineering acceptance gates](../../engineering/rules/ENGINEERING_GATES.md), [NBC 105 research rules](../../docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md), [thesis workboard](../../docs/review/20261112_THESIS_DELIVERY_WORKBOARD.md).
