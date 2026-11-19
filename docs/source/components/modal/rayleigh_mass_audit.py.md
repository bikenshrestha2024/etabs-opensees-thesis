# rayleigh_mass_audit.py — independent nodal mass-elevation evidence

**Source:** [components/modal/rayleigh_mass_audit.py](../../../../components/modal/rayleigh_mass_audit.py)

**Owner:** Modal / NBC 105:2025 §5.1.1, pre-adoption evidence.

**Entry point:** `audit_rayleigh_mass_elevations(model,story_rows)` is pure Python. The active Rayleigh runner calls it immediately after loading its matching assembled model and seismic story-weight ledger.

**Inputs:** `OpenSees_Complete_Model_Data_V118.json` provides the exported model's nodes, `nodal_mass` (kN·s²/m), `supports`, diaphragms and seismic base elevation. The matching story ledger provides `dead_load_kN`, `storage_live_load_kN`, `other_live_load_kN` and master tags. It uses `g_mass=9.80665 m/s²`, matching the existing assembly's mass conversion.

**Contract:** It maps every active horizontal mass to the first diaphragm at or above the physical node elevation, exactly as the existing source ledger does. It checks all floor weights and reports total active weight, intermediate-elevation node count, upward-relocated mass fraction, first-moment shift, maximum vertical lift, out-of-roof geometry and mixed-XY-support nodes.

**What it does not establish:** Equivalent 3D eigen mass operator, independently derived kinetic energy, calibrated ETABS mass source, matching P-Delta tangent, RC wall stiffness, torsional equivalence, accepted Rayleigh design period or site/code compliance. A matching total source weight is **not** physical equivalence.

**Tests:** [tests/test_rayleigh_mass_audit.py](../../../../tests/test_rayleigh_mass_audit.py), executed in the integrated CI. Actual building evaluation requires the user's private original EDB / export inputs and native ETABS + OpenSees.

**Engineering review:** [Rayleigh mass-distribution physical gap](../../../../REVIEW_MAIN/02_ESM/20261119_RAYLEIGH_MASS_DISTRIBUTION_PHYSICAL_GAP.md).
