# rayleigh_mass_audit.py — independent nodal mass-elevation evidence

**Source:** [components/modal/rayleigh_mass_audit.py](../../../../components/modal/rayleigh_mass_audit.py)

**Owner:** Modal / NBC 105:2025 §5.1.1, pre-adoption evidence.

**Entry point:** `audit_rayleigh_mass_elevations(model,story_rows)` is pure Python. The active Rayleigh runner calls it immediately after loading its matching assembled model and seismic story-weight ledger.

**Inputs:** `OpenSees_Complete_Model_Data_V118.json` provides the exported model's nodes, `nodal_mass` (kN·s²/m), `supports`, diaphragms and seismic base elevation. The matching story ledger provides `dead_load_kN`, `storage_live_load_kN`, `other_live_load_kN` and master tags. It uses `g_mass=9.81 m/s²`, matching the existing assembly's mass conversion.

**Contract:** It maps every active horizontal mass to a floor with `components.nbc105.clause_05_dynamic_characteristics.storey_index_for_elevation`, the NBC 105:2025 §5.2 mid-height rule (printed p. 30) that the assembly ledger in `components/model/assembly.py` also uses. A node below the mid-height between two floors goes down, a node above it goes up, and a node at or below the first floor stays with floor 1. It checks all floor weights against the ledger (0.01 kN) and reports total active weight, intermediate-elevation node count, relocated mass fraction, signed first-moment shift, maximum upward and maximum downward lump, and mixed-XY-support nodes. A node above the roof diaphragm raises an error.

**2026-11-21 change:** the earlier version still lumped every node upward while the ledger had moved to the mid-height rule, so any model with mass below a storey mid-height would have stopped the Rayleigh run with a floor-weight mismatch. The function now matches origin/main commit 891843e; see [the run finding](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md). For the November 21 export all intermediate masses sit 2.3 m above a floor (above the 1.9 m mid-height), so both rules give the same floor weights for that model.

**2026-11-21 selectable convention:** the new keyword `convention=None` defaults to the model data key `storey_mass_allocation_convention`. When that key is absent, the historical mid-height rule applies and the floor weights are numerically unchanged. The two ETABS conventions are described in [storey_mass_convention.py](storey_mass_convention.py.md). For them, base-row weight is excluded from the floors and reported as `base_row_excluded_weight_kN`, and floors plus base row still reconcile with the nodal mass. A linear split moves fractions of a node to both adjacent levels. The result also carries `storey_mass_allocation_convention`. Tests: `tests/test_storey_mass_convention.py`.

**What it does not establish:** Equivalent 3D eigen mass operator, independently derived kinetic energy, calibrated ETABS mass source, matching P-Delta tangent, RC wall stiffness, torsional equivalence, accepted Rayleigh design period or site/code compliance. A matching total source weight is **not** physical equivalence.

**Tests:** [tests/test_rayleigh_mass_audit.py](../../../../tests/test_rayleigh_mass_audit.py), executed in the integrated CI. Actual building evaluation requires the user's private original EDB / export inputs and native ETABS + OpenSees.

**Engineering review:** [Rayleigh mass-distribution physical gap](../../../../REVIEW_MAIN/02_ESM/20261119_RAYLEIGH_MASS_DISTRIBUTION_PHYSICAL_GAP.md).
