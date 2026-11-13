# 03 — Which gravity case serves which analysis?

**Q. Is NBC §5.2 the full-gravity 1D+1L test?** No. NBC §5.2 prescribes seismic weight, referenced by the 2025 TH gravity subsections; distinguish D+0.60 storage live +0.30 other live +0 roof live (actual source categorization required) from full 1D+1L load-path checking and from IS 1.2D+0.5IL±1.5EL initial P-Delta.

**Q. Can mass fractions classify dead/live patterns automatically?** No; explicit ETABS pattern type/assignment source is mandatory. `components/model/initial_pdelta.py` currently has an open classification risk: its source `mass_factors` should not be treated as verified D/IL categories.

**When:** Before building model gravity or any signed initial P-Delta cases. **Evidence:** full pattern ledger, individual supports, six DOF reactions, case hash, source EDB and independent force-equilibrium proof.

[Gravity review](../../01_GRAVITY/REVIEW.md) · [Source/model review](../../00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md) · [Q&A home](../README.md)

**Status:** not fully reconciled.
