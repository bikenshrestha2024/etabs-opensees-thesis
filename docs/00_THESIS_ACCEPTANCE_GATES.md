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


## 2026-11-15 conditional outrigger diagonal model decision (not a passed gate)

**Researcher-adopted working assumption:** retain ETABS pin-ended steel *diagonal* members for the comparative steel outrigger truss configurations, as a **provisional two-force idealization**. This preserves the current model but does not physically establish the connections are pinned. Do not hinge all chords, RC frame members, shear-wall connections, belt/cap transfer components or FVD/BRB links by inference. Detailed basis and CTBUH guide/book-paper citations: [DB-OUT-2026-11-15-01](../REVIEW_MAIN/00_MODEL/20261115_PROVISIONAL_HINGED_OUTRIGGER_BRACE_DESIGN_BASIS.md).

- **G01** still requires exact source `GetReleases`/member-role and truss geometry, real top/bottom chord path, and connection/drawing evidence.
- **G03** still requires source-matched frequencies and elimination of mechanisms/rotational zero-energy modes under the released elastic beam idealization.
- **G04/G06** still require cyclic buckling/fracture and BRB/FVD calibration and connection-stiffness sensitivity; an exploratory `corotTruss + Steel01` is NOT certified nonlinear behavior.
- **G09/G10** still require comparable M0–M6 controlled variants and defined acceptance criteria. The reviewed nonlinear hinged-brace gate **must remain fail-closed** until a physically justified formulation is tested.

**Status:** `PROVISIONAL_DESIGN_BASIS`, not `VERIFIED_MEMBER_CONNECTION`, `NLTHA_READY` or `CODE_ACCEPTED`. No legacy outputs have been retroactively promoted.


## 2026-11-15 full 76-point gravity reaction reconciliation blocker

The 2026-11-15 1.0D+1.0L exported ETABS global `FZ=311367.313600 kN` matches OpenSees solved `Rz=311367.31387955 kN` only in **global arithmetic**. The native 76-source support ledger has **44 fully source-restrained points with ETABS FZ=0**. The primary32 diagnostic releases those restraints; the 76-support OpenSees solver carries approximately **104463.014 kN** at them. Aggregate absolute node mismatches are **37297.027 kN (32 model)** and **208926.027 kN (76 model)**. The native preflight flags 1367 rigid-end-zone metadata records. Therefore no case may be tagged ETABS support/reaction **physically equivalent** without source restraint/analysis-element mapping and stiffness/load-path tests. New full-76 source mapping output is implemented in `components/gravity/three_case_comparison.py`. See [full native discrepancy review](../REVIEW_MAIN/01_GRAVITY/20261115_FULL_76_SUPPORT_REACTIONS_AND_NATIVE_DISCREPANCY.md).

**G02/G03 remain OPEN**. The 32-support case is a sensitivity case; don't remove 44 fixed DOFs from the original source model or rewrite reactions to force agreement.

## 2026-11-16 independent verification Studio evidence

The standalone B01–B12 OpenSeesPy Studio (separate from the production thesis model) has user-submitted results of **B01–B11 native PASS** plus **B12 ANALYTICAL_PASS**, 58/58 recorded metrics passed. This is useful `INDEPENDENT_COMPONENT_BENCHMARK` evidence only. B06 proves 54 kN slab-patch gravity equilibrium across MESH_04/08/16; it does not prove ETABS matched load path or deflection mesh convergence. B12 verifies a constitutive equation only, not a native viscous device.

A local private evidence importer validates JSON reports and exports a sanitized `EVIDENCE_CONSISTENT` status; **this does not promote G00–G10 thesis qualification**, the 32 physical support-equivalence gate, wall calibration or X-wall NLTHA convergence.

See [12-case review](../REVIEW_MAIN/00_MODEL/20261116_B01_B12_STUDIO_RESULTS_AND_ACCEPTANCE.md) and [verification matrix](../tools/verification_studio/THESIS_VALIDATION_MATRIX.md).
