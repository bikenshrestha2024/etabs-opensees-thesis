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
