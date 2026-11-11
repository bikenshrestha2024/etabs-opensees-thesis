# Native ETABS ↔ OpenSees equivalence protocol
**RV-EQV-001:** P0 OPEN_BLOCKER — missing independently source-matched comparison results

**Order:** (1) EDB and XLSX provenance; (2) geometry/mesh and support DOFs (32/76/97 sensitivity); (3) load case/self-weight/diaphragm/master mapping; (4) effective stiffness, shear transfer, frame offsets and P-Delta; (5) mass/period/modes; (6) ESM/RSA; (7) LTH; (8) qualified NLTHA.

**Required quantitative outputs by identical case/point/unit:** support joint ID, xyz, FX FY FZ MX MY MZ; sum of reactions; load source ledger; mode number, period, X/Y effective mass participation and physical shape; floor mass/COM; response spectrum base shear; **cut-recovered** storey shear; floor COM displacement and drift; leading/trailing corner displacement and edge drift; torsion and accidental eccentricity. Use signed comparison where physically meaningful; unsigned CQC envelopes must retain envelope label. Separate X/Y, ULS/SLS, E0/E+/E-, gravity combo and stiffness state.

**Comparison errors:** absolute delta, symmetric percent difference when reference ≈0, unpaired/missing IDs, mismatched units, sign convention, net load balance; do not divide by zero or relabel unavailable as 0. Do not compare unloaded ETABS support reaction with a restrained OpenSees auto-mesh node as if identical physics.

**Output:** every row with source_method, limit_state, case, axis, location, metric, unit, basis, ETABS value, OpenSees value, delta, normalized_delta, evidence_source, matching_status. Missing ETABS rows → MISSING_ETABS (not PASS).

**Engineering finding:** Matching global shear alone cannot validate stiffness, diaphragm or load redistribution; require storey curves plus modal shape/period and local reaction comparisons.
