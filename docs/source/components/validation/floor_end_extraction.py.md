# components/validation/floor_end_extraction.py — engineering source guide

**Role:** Fail-closed review of physical perimeter node geometry and paired signed directional displacements for official NBC 105:2025 §§5.4.2.1–5.4.2.2. This is a data-review tool and does **not** run or modify ETABS or OpenSees.

**Input provenance:** separate model-specific CSV for geometry `node_id,storey,x_m,y_m,z_m,is_perimeter` and response `node_id,storey,limit_state,case,axis,step,ux_m,uy_m,centered_cm_load,response_basis`. Requires reviewed actual physical perimeter and center-of-mass force application, one ULS or SLS state only. Node IDs need only be consistent *within* each model's own data, not numerically identical between ETABS and OpenSees.

**Units and calculations:** x/y/z, ux/uy [m]. X loading compares Ux at opposite Y extremes with approximately matched X; Y loading compares Uy at opposite X extremes with approximately matched Y. Alignment (default 0.10 m) and extremity (default 0.05 m) are **research geometry-matching tolerances**, not NBC acceptance values. The downstream floor-end check uses `max(abs(Uend1),abs(Uend2))/min(abs(Uend1),abs(Uend2))`; triggers >1.5 and >2.5 respectively. Signed response is preserved for audit. No displacement resultant or cross-step peak picking.

**Output:** per-candidate floor-end pair CSV; per-floor/case governing max-ratio CSV; provenance JSON with SHA256 of source geometry and response CSV and assumptions. Missing/unaligned edges → NOT EVALUATED and blocked design acceptance; no measured project quantities are fabricated. For L-shaped floor with re-entrant cutout, candidates are taken from explicitly labelled physical perimeter nodes, with similar along-building coordinate.

**Limitations:** Not a native ETABS v23 joint-extraction connector, automatic EDB geometry parser, robust polygon edge detector, continuum max search or proof that ETABS/OpenSees mesh and load cases correspond. Real Windows-model integration and physical comparison are unverified. A `centered_cm_load=true` marker documents the user's evidence claim; it cannot independently prove that loading geometry or stiffness matches.

**Source:** [official NBC 105:2025 printed page 34](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) and [workflow guide](../../../validation/floor_end_extraction/README.md). Tests: `tests/verify_floor_end_extraction.py`, plus `tests/verify_nbc105_torsion_check.py`.
