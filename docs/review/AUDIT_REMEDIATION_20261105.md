# High-priority codebase audit remediation — 2026-11-05

**Repository:** `bikenshrestha2024/opensees-nbc105-research`  
**Base:** main `2ef41aa86ccd5f9527f01ba0a5067b4022c32cfc`  
**Branch:** `fix/high-priority-audit-findings-20261105`; PR #16.  
**Assessment:** software corrections and diagnostic safeguards only; **NOT** an ETABS v23/OpenSeesPy numerical equivalence certificate or an NBC design compliance certificate.

The previous review said "26 findings" but labelled **28** (A01–A08, B01–B07, C01–C05, D01–D08). All 28 are inventoried below. The "fixed" label means the specified **source-level behavior was changed** and requires CI/native validation as noted; it does not imply that unrelated implementation paths were line-by-line audited. The existing ETABS export, gravity model, original .EDB and physical constitutive models have **not** been altered.

## 1. Finding-by-finding resolution register

| ID | Classification | Action in this PR or remaining work | Files / verification |
|---|---|---|---|
| A01 | **Code fix** | MRSM now selects the source Ultimate→ULS / Service→SLS instead of defaulting to Both; entry-point checks requested state before solving | `components/response_spectrum/model_analysis.py`; existing source-state tests |
| A02 | **Code fix, evidence outstanding** | MRSM no longer preloads unclassified workbook C14/C15 as design T. `mrsm_period_defaults` uses the model height, source-matched directional wall Aw and verified imported Rayleigh cache; adopted T is `min(Tr,1.25×0.075H^0.75/sqrt(Aw))` for this **concrete shear-wall model**. Missing inputs remain empty with source note, never silently use another workbook period. | `components/response_spectrum/model_analysis.py`, `tests/verify_mrsm_period_source.py` |
| A03 | **Not implemented** | Verified NBC §7.3 missing-mass treatment above the frequency threshold is not yet coded. Existing fail-closed MRSM stop is preserved. Requires a physical benchmark and code-clause treatment, not removal of the safety gate. | `components/response_spectrum/model_analysis.py` |
| A04 | **Physical verification required** | Elastic shell wall in-plane and flexural stiffness must be reconciled to real ETABS wall modifiers and source geometry. Do not tune a factor merely to match an unpaired T1. | `components/model/assembly.py` |
| A05 | **Physical metadata required** | Missing source releases/local axes/insertion offsets can still cause conversion warnings; no automatic guessed replacements applied. Fresh ETABS v23 source export/review needed. | `components/model/assembly.py` |
| A06 | **Physical reconciliation required** | Code-derived seismic mass ledger matches itself, not automatically ETABS assigned mass source. Verify storey mass, floor center of mass, diaphragm polar inertia, loads and base exclusions against EDB. | `components/model/assembly.py` |
| A07 | **Numerical benchmark required** | Generalized accidental torsion influence/eigenvector MRSM formula remains unmodified pending ETABS centred/E± benchmark. No unverified formula adjustment has been made. | `components/response_spectrum/model_analysis.py` |
| A08 | **Existing warning preserved** | Component-wise positive CQC deformation values are not concurrent deformed shapes; such plots remain research envelopes, never physical snapshots. | `components/response_spectrum/model_analysis.py` |
| B01 | **Code fix** | ETABS and OpenSees modal participation now compare individual MX/MY by mode and cumulative MX/MY at ALL in percent and matching semantic keys, instead of per-mode versus cumulative mismatch. | `components/validation/etabs_direct_api.py`, `components/validation/etabs_comparison.py` |
| B02 | **Partial safety fix** | ETABS joint displacement comparison's basis remains unapproved without explicit `same_location_verified=true` on each point and case `point_response_basis_verified=true`. Direct coordinate/node pairing from real EDB is still pending. | `components/validation/etabs_direct_api.py` |
| B03 | **Partial safety fix** | Existing MRSM joint envelope extraction still uses a maximum over ETABS output rows; it cannot be used as synchronous signed response. Its result basis is now explicitly unverified unless exact point and result basis are attested. Native step/combination validation remains pending. | `components/validation/etabs_direct_api.py` |
| B04 | **Code fix** | Saved MRSM results now include assembled-model SHA256, and comparison collector rejects wrong-state, missing-hash and mismatched-hash files. Exclusion evidence written to `Comparison_Source_Exclusions.json`. Legacy un-hashed ESM responses also excluded until provenance is introduced; they remain on disk. | `components/response_spectrum/model_analysis.py`, `components/validation/etabs_comparison.py`, synthetic audit test |
| B05 | **Code fix** | A basis/unit mismatch is not also counted as a missing OpenSees result. | `components/validation/etabs_equivalence_report.py` |
| B06 | **Partial safety fix** | Reject truthy string flags (e.g. `"false"`) for the reviewer approval value; an explicit JSON boolean True still represents human evidence, not a software certificate. Independently verified signed evidence remains necessary. | `components/validation/etabs_equivalence_report.py` |
| B07 | **Native integration pending** | ETABS v23 COM API return signatures and actual .EDB response extraction have not been exercised in Linux CI; requires controlled native Windows validation. | `tests/verify_etabs_direct_equivalence.py`, `tests/verify_etabs_floor_end_api.py` |
| C01 | **Physical geometry pending** | `is_perimeter=true` is not independently reconstructed from slab polygon/void topology; an L-shaped plan requires reviewed polygon and floor-edge node map. | `components/validation/floor_end_extraction.py` |
| C02 | **Code fix** | Each story label now requires consistent node z-elevations within a disclosed 0.1 mm numerical alignment screen; mismatches block torsion extraction. This research geometry tolerance is not an NBC threshold. | `components/validation/floor_end_extraction.py`, synthetic test |
| C03 | **Code fix** | Result step must be consistent across all floors of an axis/case, not merely within each individual floor. | `components/validation/floor_end_extraction.py`, synthetic test |
| C04 | **Evidence still external** | The centered-CM load and same-end basis markers are user-declared, not independently generated from ETABS. Native verification is still necessary before code-compliance attribution. | `components/validation/torsion_check.py` |
| C05 | **Code fix** | Irregularity review GUI defaults to source-model ULS/SLS instead of Both, and the analysis function enforces same state before rebuilding. | `components/validation/irregularity_review.py` |
| D01 | **Code fix, native test pending** | NLTHA accepted-step histories now include X/Y floor-master *relative* acceleration [m/s²]. These are **not absolute floor accelerations**; add matched ground acceleration to derive absolute acceleration after confirming sign, units and time interpolation. | `components/nonlinear_time_history/runner_and_gui.py` |
| D02 | **Code fix, conditional on source mapping** | NLTHA records gravity-subtracted signed X/Y support resultants and base shear [kN] using the same shared recorder as linear TH. When support mapping is absent, it reports NOT_RECORDED rather than fabricating zero. | `components/shared/response_recorders.py`, NLTHA runner |
| D03 | **Code integration, native test pending** | Activated and tagged FVD/BRB devices are sampled at accepted steps and exported as force, relative displacement, relative velocity and signed work. No claim is made about energy sign, fatigue, manufacturer stroke capacity or device calibration. | `components/nonlinear_time_history/device_recording.py`, NLTHA runner |
| D04 | **Code fix, data still required** | Runner now produces comparison-compatible `max_story_drift_X/Y`, `peak_base_shear_X/Y_kN`, and `peak_roof_torsion_rad`. Missing base shear is recorded None and must fail an M0–M6 completed-case manifest gate, not become zero. | `components/nonlinear_time_history/runner_and_gui.py`, `variant_comparison.py` |
| D05 | **Actual OpenSees run required** | Nonfinite element `110280` at `t≈0.005s` is an observed historical solver error, not fixed by these changes. Requires tag-to-ETABS object mapping, support/constraint review, monotonic gravity preload, wall panel/material/unit checks and native trace. | `components/nonlinear_time_history/failure_evidence.py` and native logs |
| D06 | **Material calibration pending** | ConcreteCM/Concrete02/SteelMPF, SFI/E-SFI wall, FVD and BRB calibrations depend on real specimen/manufacturer data and per-material units; source code alone cannot certify. | material/validation subsystems |
| D07 | **Spectrum evidence pending** | Soil C preflight contains a project-specific Z/period spectrum target/hash; verify it matches the chosen EDB, ULS/SLS purpose and original SeismoMatch target. No silent refitting/rescaling. | `components/nonlinear_time_history/soil_c_physics_preflight.py` |
| D08 | **Physical edge validation pending** | NLTHA drift may use rigid-floor reconstructed extreme positions; this is not the full nonlinear frame/wall/local shell deformation field. Verify extreme perimeter nodes and floor-opening edge demands. | `components/validation/response_checks.py` |

## 2. What is held constant

- Original EDB and export source files: **read-only**, no upload.
- Gravity load factors, nodal seismic mass, rigid diaphragm constraints, FVD/BRB material cards, wall/beam/column constitutive models and nonlinear solver integration settings: **unchanged**.
- NBC shear-wall period rule: `T_emp=0.075 H^0.75/sqrt(Aw)`, `T_adopt=min(T_Rayleigh,1.25T_emp)`, current model source only. NBC 105:2025 §5.1; use direction-specific effective wall area and independently verified first-storey geometry.
- Torsion screening: `Delta_max/Delta_min` >1.5 / >2.5 using the same floor, opposite physical ends, centered CM load, directional displacement (§§5.4.2.1–5.4.2.2). This is not the interstorey drift check.
- Accidental plan eccentricity: existing ±0.05b implementation retained; no automatic further change (§5.6).
- Screen thresholds and software PASS/FAIL tolerances are **research comparison targets**, not code-prescribed equivalence tolerances.

## 3. Newly recorded quantities, provenance, units and limits

| Field / output | Data source and extraction time | Units | Meaning and restriction |
|---|---|---|---|
| `*_UX_relative_accel_m_s2`, `*_UY_relative_accel_m_s2` | `ops.nodeAccel(master)` at every **accepted** nonlinear step | m/s² | Relative floor acceleration under UniformExcitation; not absolute floor acceleration |
| `base_shear_X_kN`, `base_shear_Y_kN` | `ops.reactions()` and sum of actual mapped source support nodes, subtract reaction vector after frozen gravity | kN | Signed incremental support resultant; synchronized with roof displacement; only if exact source mapping exists |
| `device_sample`: displacement/velocity/force | Mapped FVD `basicForce`, BRB `axialForce`, projected i-j node response at accepted step | m, m/s, kN | Demands only; deformation relative to postgravity baseline, force sign unqualified |
| `peak_roof_torsion_rad` | Maximum absolute RZ of mapped top diaphragm in accepted-step history | rad | Master rotation demand, not edge translation/torsional irregularity ratio |
| `max_story_drift_X/Y` | Alias for full accepted-step envelope, including independently reconstructed floor edge peak where available | ratio | Compatible field for M0–M6 comparator; not proof of local wall edge kinematics |
| `model_sha256` on MRSM cases | SHA256 of assembled `OpenSees_Complete_Model_Data_V118.json` | hex SHA256 | Reject stale MRSM results; does not establish equivalence to ETABS EDB, which requires separate source fingerprints |

## 4. Test interpretation and next physical verification

**CI**: syntax, existing numerical screens and mock regression tests. A passing green workflow proves the tested software contracts on Linux/Python 3.12, NOT real .EDB COM connections, nonlinear wall stability, FE discretization or full NBC compliance.

**Windows ETABS v23 / OpenSees native steps** (must be done on the private source model):
1. Pick **Ultimate only** or **Service only**. Record original .EDB SHA256 and source export hash; compare floor/story, support and source case identities.
2. Verify gravity reactions, concentrated distributed loads, inter-floor wall/column masses, diaphragm inertia and selected frame/member forces against the actual EDB, not the internal assembled mass ledger only.
3. Verify modal periods, mode shapes/MAC and UX/UY/RZ individual and cumulative participation, current stiffness and support conditions.
4. Validate E0/E± MRSM shear, drift and roof-edge displacement against ETABS matching physical points; review damping, spectrum and force scales independently. Do not compare the old unverified CQC point envelopes as signed simultaneous displacement.
5. Reproduce physical NLTHA first-step element 110280 issue with localForce/material responses and initial tangent/mass/support/constraints. Only once solved, compare linear histories and full nonlinear signed XY/YX records with calibrated component models.
6. Confirm FVD/BRB force/stroke/velocity/dissipated-energy sign with component experiments or calibrated manufacturer data, and the wall openings/axial/shear-flexure behavior with an actual wall specimen.

**NOT CLAIMED:** a literal complete line-by-line independent verification of all archived and active ~515 Python files; all physical or model-related findings remain open until native evidence exists.
