# NBC 105:2025 independent numerical checks — 2026-11-21

## Exact source editions inspected

Two separately uploaded versions of the official **NBC 105:2025 Second Revision** were reopened as independent PDF sources:

| Source file | Pages | Printed p.1 | Printed p.28 | Printed p.49 | Printed p.50 |
|---|---:|---:|---:|---:|---:|
| `NBC105_2025_SeismicDesignofBuildingsinNepal.pdf` | 137 | PDF 21 | PDF 50 | PDF 71 | PDF 72 |
| `NBC_105_2025_Seismic Design of Buildings in Nepal_lqqvx6a_2.pdf` | 138 | PDF 22 | PDF 51 | PDF 72 | PDF 73 |

**Consequences:** The source files have a different leading page count, plus repeated/un-numbered Figure 4-3/26 pages in the code. The repository's `PRINTED_PAGE_OFFSET=21` is for its previously indexed **138-page** PDF; do not apply it to the separate 137-page upload. For legal and engineering citation, use the **printed page and clause**, not an assumed constant PDF offset. The existing `clause_01_scope_definitions.pdf_page_for_printed` helper is deliberately restricted to Clause 1 printed pp.1–9 and its previously indexed PDF variant.

## Independently checked clauses and code paths

| Clause | Source benchmark | Production path | Verification finding |
|---|---|---|---|
| §5.1, printed p.28 | Adopt `min(TR,1.25 T_empirical)` | `clause_05_dynamic_characteristics.adopted_period_s` | Reference function enforces lesser-of; latest V10.7 ETABS JSON **does not supply a validated Rayleigh period**. **PROJECT ACCEPTANCE OPEN** |
| §5.1.1, printed p.28 | `TR=2π sqrt(Σ Wi di²/(g Σ Fi di))`, torsion excluded from elastic COM displacement | `clause_05_dynamic_characteristics.rayleigh_period_s` | Correct units/form, and now rejects nonfinite/negative physical inputs. Correct COM displacement and gravity/P-Delta tangent on native 25-storey model **not yet proven** |
| §5.2, printed p.30 | Seismic LL: storage 0.60, other 0.30, roof nil | `clause_05_dynamic_characteristics.seismic_weight_kN` | Constants verified against printed Table 5-1; rejects nonfinite/negative contributors |
| §5.3, printed p.32 | Table 5-2, 21 structural systems | `table_5_2_system_factors` | Source values present and previously focused-tested; system/ductility qualification **not native verified** |
| §5.4, printed pp.33–35 | Weak story **<80%**, soft story **<70%** or **<80%**, torsion **>1.5** extreme **>2.5** | `weak_story`, `soft_story`, `torsion_irregularity` | Previously `math.isclose` weakened strict limits; fixed to literal strict comparisons with smallest-representable exceedance tests |
| §5.5.3, printed p.37 | Design drift ≤0.025 ULS, ≤0.006 SLS | `interstory_drift_check` via `components/validation/response_checks.py` | Former `or isclose` accepted above-limit values; removed. Source-level tests and production caller gate added |
| §6.1–6.5, printed pp.38–39 | Cd, V, k, Fi, kd | `clause_06_equivalent_static` via active ESM `code_basis` | Previously implemented and parity tested; actual ETABS ESM/PDelta assignment still requires matched model evidence |
| §7.3, printed pp.40–41 | At least 90% directional mass; only <33Hz modes combined, higher frequency missing-mass correction | Clause 7 readiness + MRSM preflight | Code blocks unsupported missing-mass; physical mass participation of newest EDB not independently validated |
| §7.4, printed p.41 | SRSS or CQC established combination | `clause_07_modal_response_spectrum.cqc_correlation_matrix` now called by `components/response_spectrum/model_analysis.cqc_matrix` | CQC **method permitted by NBC**; numeric correlation formula is accepted structural-dynamics practice **not printed in NBC**. Preserves previous production formula with input checks and numerical parity tests |
| §7.5, printed p.41 | MRS shear/forces/reactions scaling only, **drifts/displacements unscaled** | Clause 7 and MRSM force-scaling production path | Prior code already routes factor and leaves drifts unscaled; complete native data comparison open |
| §8.1.3, printed pp.42–43 | <7 maximum, >7 average; exactly seven unspecified | Clause 8 and LTH preflight | Exactly-seven input is explicitly review-required, not silently treated as a valid average |
| §9.3.2, printed pp.46–47 | Scale 0.33–3; 3D paired XY/YX; time step ≤digitization,T1/100,Tn,0.01s | Clause 9 through NLTHA metadata preflight | Source rules available; actual hysteresis model/wall first step and all 224 histories not demonstrated |
| §10.3, printed pp.49–50 | `Fp=Z(1+hp/H)(ap/μp)IpWp`; Table 10-1 ap from 2.5 to 1.0 | Clause 10 + settings calculator | Verified against the uploaded **page image**. Equality at 0.5 s is implicit; continuous endpoint ap=1.0. Actual nonstructural inventory and connection capacities missing |

## Software changes and evidence

- RED regression: `tests/test_nbc105_source_numerical_integrity_v2.py` initially failed on overly permissive near-boundary comparisons, invalid Rayleigh weights and the absence of canonical CQC.
- GREEN branch: `components/nbc105/clause_05_dynamic_characteristics.py` hardens strict code boundaries and source weights; `components/nbc105/clause_07_modal_response_spectrum.py` owns the established CQC correlation formula; `components/response_spectrum/model_analysis.py` delegates the active modal method to Clause 7.
- Contradictory historical assertion `torsion_irregularity(1.5,0.999999999999)==REGULAR` was corrected because the *actual ratio exceeds 1.5* under the code's strict condition. Synthetic tolerance must not silently weaken NBC design limits.

## Native engineering acceptance

**NOT CERTIFIED.** The V10.7 report self-describes `AMPLIFIED_EMPIRICAL_ONLY__NO_ANALYTICAL_PERIOD_CHECK` and `NOT_TESTED__REQUIRES_REACTION_MASS_MODAL_DRIFT_TORSION_COMPARISON`. Additional project-specific evidence is needed for source model hash, actual measured Vs30, CM vs diaphragm displacement, cracked stiffness and coupled 12 m walls, support base reactions, eigenmode mass, P-Delta state, drift/edge torsion, nonlinear wall convergence and all full-duration history cases. Source-level software verification can neither replace nor infer those numerical model outcomes.

**No private EDB, analysis workbooks or accelerograms were uploaded to public GitHub.**
