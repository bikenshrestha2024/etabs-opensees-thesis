# 00 — Nonlinear thesis acceptance and evidence gates

Study: asymmetric high-rise RC frame/core with seven baseline/outrigger variants M0–M6; levels 3,5,7,9,11 are candidate investigation positions, not verified geometry. Reproduce fixed-base source before optional SSI studies.

| Gate | Requirement | Block / invalid result |
|---|---|
| G00 provenance | ETABS export checksum; code commit; solver package version; source file locations | V156/current runtime mixing or missing model SHA |
| G01 input geometry | Story grid and heights; wall openings/edge regions, reinforcement schedule; column/beam and slab sections | Nominal/template reinforcement not source-verified |
| G02 gravity and mass | DL/LL load pattern; gravity reactions and P-Delta, mass source, rigid-diaphragm compatibility | Force imbalance, support/diaphragm conflict, double-counted mass |
| G03 modal | Eigen residual, positive modes, mass participation, ETABS period comparison, model stability | Hung eigen solver or inconsistent effective stiffness |
| G04 materials | Concrete01/02/CM, Steel02/MPF and FSAM tests with actual specimen protocols | Cited formulation mistaken for a calibrated building input |
| G05 walls | Independent panel cyclic test, 3D core openings, coupling beams, confinement and wall orientation | First-step X-only nonfinite wall response unresolved |
| G06 devices | FVD force-velocity-stroke and energy; BRB axial, overstrength and fatigue; explicit connection stiffness | Generic core/truss without actual device qualification |
| G07 transient | Complete record, clean accepted states, step convergence, XY/YX, orientations and ULS/SLS excitation | 0.005 s trial, partial record or native process crash |
| G08 performance | Edge/center drift, torsion, roof displacement, base shear, accelerations, residuals, frame/wall strains, device energy | Missing responses or invented member criteria |
| G09 variants | M0–M6 same source masses/geometry/seismic input with documented controlled outrigger changes | Comparison confounded by changing other variables |
| G10 approval | Independently reviewed member/performance acceptance limits and numerical validity | Case status upgraded by a string transformation |

## Do not equate different completion statuses

COMPLETED_TRUNCATED_TRIAL means short numerical investigation only; COMPLETED_EXPLORATORY_RECORD means the exploratory runtime reports the full duration but is not benchmark validation; COMPLETED_FULL_RECORD is an assessment evidence schema and must not be assigned automatically without matching traceable inputs and quality gates.

## Current critical failure

V168 diagnostics indicate a zero-motion first step succeeded but Kobe X-only failed at t=0.005 s. Post-failure nonfinite wall outputs appeared at solver tags 110280 / 112778 (AREA:354 / AREA:482). Because observed after solve failure, treat as localization clues, not known initiation points. Run independent wall cycles and fresh ZERO/X/Y/XY probes with consistent material and solver configuration.

## Acceptance references

Use R10 for NBC code interpretation, R01–R04/R12/R13 for wall/model experimental methods, R05–R06 for FVD hypotheses, and R07–R09 for brace investigations. See [source register](00_RESEARCH_REFERENCES.md).
