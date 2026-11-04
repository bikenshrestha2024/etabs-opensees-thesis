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

## Soil C primary NLTHA data invariants (2026-11-04)

The study has exactly 8 matched Soil-C horizontal earthquake pairs: 6 research-classified near-field (Gorkha, Landers, Northridge, Kobe, Kocaeli, Chi-Chi) and 2 far-field (Hector Mine, Loma Prieta), all input `Acc(g)`; do not relabel as Soil D. Read the Stage 35 and Stage 36 guides. The matched record's extra spectral multiplier in OpenSees is 1.0; Path acceleration units conversion 9.80665. Use original A/B source hashes to select the event, both XY/YX simultaneous orientations and full history. Do not infer original SeismoMatch scale from PGA ratio, use its session logs to review NBC 9.3.2.2. Enforce Gorkha 322.94s vs original 120s provenance and the one-sample Loma Prieta mismatch; no hidden trimming, zero padding, rematching or unlogged corrections. For eight pairs report NBC §9.3.3 average of complete accepted responses; failed/nonconverged data cannot enter accepted comparison. Current modal `T1/Tn90` verification is required; a selected 20th eigenperiod cannot be assumed to be Tn90. Use only correct project ETABS reinforcement, mass and actual core-wall geometry. Do not label elastic-wall exploratory output as full nonlinear wall verification. When changing UniformExcitation recorder logic, preserve BOTH relative and absolute acceleration fields and unit tests. Every new Python module must have an individual `docs/source/.../*.py.md` guide.


## RTFC task briefing (new AI changes)

Use [docs/rtfc/README.md](docs/rtfc/README.md) for concise **ROLE → TASK → FORMAT → CONSTRAINTS** prompts. Select a numbered prompt for the exact engineering task instead of pasting the entire repository or unrelated project memories. Preserve the hard invariants in this AGENTS file and the tested NBC/Soil C data rules. No RTFC prompt can waive source-validation or native solver checks.
