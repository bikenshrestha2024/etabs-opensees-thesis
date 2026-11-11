# P0 — MRSM completed numerically but no ETABS response comparison exists

Status: OPEN_HIGH.

## Verified uploaded evidence
`MRSM_Review_20261111_192633_103133_UPLOAD.zip` contains `Comparisons/ETABS_Comparison_V148/run.json` with `row_count=0`, `etabs_file=""`, `direct_api=false`, `evidence_verified=false`; `Comparison_Source_Exclusions.json` is empty. UI shows `NO COMPARABLE SAVED RESULTS`.

## MRSM log supplied by user
ULS X: Vraw=22586.58436 kN, S=1.10410639; ULS Y: Vraw=16748.18906 kN, S=1.57931911. Modal UX=91.24498698%, UY=90.77458703%. 40 eigenmodes; residual 1.28e-7. Both X/Y E0/Eplus/Eminus executed; these are OpenSees numerical outputs, not ETABS comparison.

## Engineering interpretation
Compare native ETABS matched ULS response to OpenSees with same EDB, load case, gravity/P-Delta state, mass model, cracked stiffness, damping/spectrum, orientation, eccentricity, and coordinate system. Do not compare CQC response envelopes as signed concurrent forces. Similar base shear among E0/Eplus/Eminus does not establish torsional equivalence: eccentricity effects should be inspected at diaphragm-edge displacement/drift and overturning/torsion.

## Implementation acceptance
- Attempt read-only direct ETABS API extraction after analysis only if ETABS is available, the selected EDB/hash matches and the required analysis cases are truly solved. Otherwise show `NATIVE_ETABS_RESULTS_REQUIRED` with precise missing evidence, not an empty successful comparison.
- Index all OpenSees response artifacts by model hash/state/case; retain original provenance and compare matching normalized metrics only.
- Capture mode shapes/MAC or directional participation, periods, base shear, story shear, drift edges, torsion, support forces and units.
- Export a complete `Comparison_Source_Exclusions.json` explaining each missing file or model/limit-state mismatch.
- Require independent reviewer to close.

No MRSM solver code altered by this issue report.
