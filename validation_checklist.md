# ETABS ↔ OpenSees Model-Fidelity and NBC 105:2025 Validation Checklist

**Date:** 2026-11-05. **Status:** Engineering protocol only, not verified project compliance.

**Governing source:** [DUDBC NBC 105:2025 second revision](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf).
**Repository evidence:** [Source-state validation](docs/validation/20261105_SINGLE_MODEL_ULS_SLS_COMPARISON.md), [ETABS direct comparison workflow](docs/validation/etabs_direct/README.md), [current parameter provenance](docs/review/20261105_PROFESSIONAL_STRUCTURAL_ENGINEERING_PROVENANCE_MANUAL.md).

## Read this before changing a working structural model

- All private ETABS `.EDB` models and original exports remain **read-only**; no source-model upload or overwrite. Record model SHA256, state ULS/SLS, software/solver versions, source geometry and assigned stiffness. Never change elastic modulus or area merely to force period agreement.
- **One model / one state**: Ultimate EDB → ULS ETABS ↔ ULS OpenSees. Service EDB → SLS ETABS ↔ SLS OpenSees. Use actual mass, gravity preload, damping, output point, response combination, units and model fingerprints.
- **One response basis**: Compare seismic response increments against increments; avoid mixing total gravity-plus-lateral deflection with lateral displacement. Compare identical X/Y directions, model floor and end/centre node coordinates, accidental eccentricity sign, MRSM force scaling and drift-amplification convention.
- Do **not** grant a structural PASS from gravity balance, period proximity, high modal mass participation or a successful solver return code. Any numerical screening tolerance is a project-agreed diagnostic target, **not** an NBC 105 specified cross-program tolerance.
- Preserve experimental-vs-project provenance for `Concrete02`, `ConcreteCM`, `Steel02`, `SteelMPF`, SFI/E-SFI wall, FVD and BRB. Do not replace a documented working material formulation solely because another researcher prefers `Concrete04` or `Steel4`.
- Leave current `components/equivalent_static/calculation_and_gui.py` and `components/response_spectrum/model_analysis.py` physical actions unmodified unless a reproducible formula/provenance fault is established.

## Mandatory stage gates

| Gate | Required comparison | Source evidence | What can be concluded |
|---|---|---|---|
| G0. Geometry and weights | Node coordinates, diaphragm mass/rotational inertia, RC frame/wall geometry/openings, local axes, releases, supports, stiffness modifiers, applied loads | ETABS source tables and OpenSees model export + hashed mapping | If missing: **NOT COMPARABLE** |
| G1. Gravity | Same load combination; applied load, reaction components, axial loads in critical wall/columns, level and roof vertical deflections | ETABS API tables & independent OpenSees nodes/elements | Balanced reactions alone are necessary but insufficient |
| G2. Modal | Correctly paired shape T1/T2/T3 and torsional modes, modal mass in UX/UY/Rz, eigenvectors, MAC at matched nodes, centre of mass | ETABS mode-shape tables, OpenSees modalProperties and eigenvectors | Near periods with different shapes are not equivalent |
| G3. ESM | Current source Aw-X/Aw-Y from real first-story wall piers, distinct directional NBC §5.1.1 Rayleigh and empirical periods, computed V and Fi | Reviewed EDB, workbook cell and model/weight hashes | ULS high-rise ESM is **DIAGNOSTIC** unless §3.2.1 eligibility holds; §3.2.1 permits all SLS ESM |
| G4. MRSM | Same spectrum, direction, mass, damping, adequate modes, CQC/SRSS basis, §7.5 force scaling separately from design drift, top and edge displacements, story drift, base/story shear | Case-by-case source mapping, no spectrum factor double-application | Quantitative comparison only for exactly matched result bases |
| G5. Linear THA | Same elastic model, matched excitation waveform, dt, damping, gravity, integrator, full duration and response time histories | Full record hashes and signed time-aligned response traces | Dynamic implementation screening |
| G6. Nonlinear components | Calibrated RC member cycles; wall axial-shear-flexure and openings; damper Maxwell K/Cd/alpha; BRB core/connection test loops | Actual specimen and constitutive cards/DOI, units, curves, source geometry | Calibration of specimen ≠ proof of whole-building fidelity |
| G7. NLTHA | Same ULS/SLS objective, full accepted XY and YX paired motions, P-Delta, failed-step diagnostics, edge drift, residual, accelerations, element force/stroke/energy | Full-run convergence, model and record hashes | Only accepted full histories enter thesis comparison |
| G8. Design review | ULS/SLS drift, non-ductile force demands, connections, wall boundary, torsion, stability, capacity and ductile detailing | Applicable NBC clauses and actual reinforcement/design evidence | Report any uncovered item as NOT EVALUATED |

**Research-screening example only:** gravity reaction totals around 1% and mode periods around 2%; MRSM response around 5%, after matching response bases. Actual tolerances must reflect nonlinear variability, discretization, model assumptions and software definitions; no universal “5–10% engineering pass” applies to all results.

## NBC-specific torsion and eccentricity

**§5.4.2.1:** compare maximum to minimum *horizontal displacement* at opposite ends of the **same floor**, for a lateral force applied at the centre of mass: torsion irregularity if `Delta_max / Delta_min > 1.5`.

**§5.4.2.2:** extreme torsion if the same ratio `>2.5`; **not permitted**, building configuration must be revised. Ratios exactly 1.5 or 2.5 do not exceed the printed threshold. The Qwen suggestion `max / average` for ordinary torsion is **not the governing 2025 text**. This is a floor-end displacement check, not a ratio to the adjacent storey's displacement or the roof-only center displacement.

**§5.6:** accidental eccentricity may be taken as `±0.05b`. The existing ESM and MRSM code already uses the 5% perpendicular floor breadth; do not introduce another `load_patterns.py` and accidentally double eccentricity.

**Programmatic screen:** `components/validation/torsion_check.py` or standalone `torsion_check.py input.csv review.csv` evaluates paired floor-end records independently. Missing end nodes, zero/minimum displacement, missing centered-CM evidence, unknown limit state or unmatched analysis cases prevent an approval claim. On extreme irregularity, the design acceptance gate becomes blocked, but diagnostic solvers and evidence remain available to examine/reconfigure the plan. This module does **not** replace existing `components/validation/irregularity_review.py` native static-centred response checks and does not itself extract ETABS points.

**§5.5.3:** drift ratios not greater than 0.025 ULS and 0.006 SLS, with §3.4 effective stiffness. Avoid conflating §5.4 floor-end *displacement* torsional screening with §5.5 interstorey *drift* checks.

## Reproducibility and outputs

Store for each comparison row: `model_sha256,limit_state,source_edb,etabs_case,opensees_case,axis,storey,node_or_end,units,basis,value,source_file,reference_clause,evidence_status`. Compare same-floor floor-end response from ETABS and OpenSees independently; do not infer identical geometry from identical response.

For the standalone torsion check, make a local CSV with:
```csv
limit_state,case,axis,storey,end_a_m,end_b_m,centered_cm_load,same_end_basis
ULS,X_E0,X,25,0.009,0.004,true,true
```

Example above is **illustrative**, not your building's analysis. Run `python torsion_check.py <input.csv> <output.csv>`; data are read locally. For comparisons keep your actual geometry/signed-response provenance beside the results and inspect before marking `centered_cm_load=true`.

**Do not** generate fragility curves from one intensity per earthquake and describe them as statistically validated fragility: a justified set of ground-motion intensity levels/damage states and appropriate fragility methodology is necessary.

## Sources and limitations

- Official Government of Nepal, NBC 105:2025 §§3.2.1,3.4,5.4.2.1–5.4.2.2,5.5.3,5.6,7,9.3.
- Source text supplied from Qwen (2026-11-05): useful validation progression, but generalized “exact within 1%”, 2–5% period and 5–10% RSA thresholds are not mandates; `max/average` is not NBC §5.4.2.1. Suggested `validation_checklist.md`, `torsion_check.py` and `load_patterns.py` must not be claimed as previously present without Git verification.
- The present implementation only adds an independently testable torsion screening module and this protocol. It does **not** certify any native ETABS/OpenSees comparison, calibrate all materials, or restructure the physical load-pattern solver.
