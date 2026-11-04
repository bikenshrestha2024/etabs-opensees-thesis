# AGENTS.md — Nonlinear ETABS-to-OpenSeesPy thesis coding contract

## Environment
Windows; Spyder IDE; Python 3.12; conda-forge only. Keep source modules import-compatible and the 01–21 launchers usable. No external upload of sensitive ETABS exports or internal model datasets without permission.

## Physical correctness
Model: nonlinear RCC beams, columns and RC core walls with openings, ordinary steel braces, possible BRBs and fluid viscous dampers, seven M0–M6 outrigger configurations, bidirectional motions and ULS/SLS.
Do not invent project reinforcement, axial load, cylinder strengths, damper parameters, seismic record pairing or material-test figures.
Record adopted kN–m–s model units, stress kN/m² and SI time step; 1 MPa = 1000 kN/m² only once. FVD Cd has fractional-exponent dimensions, not universally kN*s/m.
Distinguish nominal, experiment-reproduced and transferred values. Do not relabel smoke tests as calibration or short trials as completed NLTHA.

## Edit requirements
Read docs/00_RESEARCH_REFERENCES.md, docs/00_THESIS_ACCEPTANCE_GATES.md and the individual docs/source guide. Cross-check imports and runtime-generated path references before moving files.
Make the smallest reversible physical-code edit. Include a failing deterministic test, then report executed test evidence and known missing native checks. Never claim unseen tests passed.
Write module/function documentation on units, source DOI/paper section, assumptions, side effects, inputs and outputs only where the source actually supports them.
Catch native solver failure at case boundary, keep original traceback/failed time/stage, identify post-failure contaminated data and use a fresh domain for retries.
Keep ETABS source read-only; write analysis to isolated output folders. Never use stale preserved V156 runtime as if it were matching active V170 code.
Ensure GUI remains responsive and native modal analysis is cancellable at process level, not just Python flag.

## Priority
P0 resolve X-only wall step failure; verify core region reinforcement/confinement, wall openings, trace, FVD/BRB qualification, and case statuses.
P1 update source geometry/section/mass mapping, tests for dt, drift/torsion, energy and full-record outputs.
P2 clean package archive, replace silent exceptions, split oversized UI components, preserve historical results as immutable evidence.

## References
Use source IDs R01–R13 in docs/00_RESEARCH_REFERENCES.md and include original DOI/source in documentation. Do not cite a 2026 paper as if it was already calibrated in an older release.

## NBC 105:2025 research implementation contract (2026-11)

Before changing seismic analysis code read docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md and the official NBC 105:2025 document (DUDBC). Main governing clauses are 9.3.1 (nonlinear 3D, gravity, P-Delta, torsion and hysteresis), 9.3.2 (motion pairs, C(T)/Omega_u target, lower of two component factors, 0.33–3, XY/YX swap, integration dt bound) and 9.3.3 (response evaluation), with interstory limits in 5.5.3. Clause 9.3.3.1 erroneously cites 5.6, which is accidental eccentricity. The published 9.3.3 response-aggregation text does not specify EXACTLY seven records: require documented professional code interpretation instead of assuming a rule.

Use components/nonlinear_time_history/nbc105_2025_audit.py and components/response_spectrum/nbc_pair_spectrum_audit.py for shared conditions; do not hard-code different limits in a launcher/GUI. Existing candidate_scale_factor calculates a mean spectral-ordinate scaling estimate; this is a diagnostic, not proof of compliant spectral matching. Never auto-approve an FVD, wall specimen or project rebar from a literature card. Preserve source hashes and native failed states, and run GitHub Actions on every relevant code change.
