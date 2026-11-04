# NBC 105:2025: bidirectional horizontal NLTHA, vertical acceleration scope and OpenSees command mapping

**Direct government code:** https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf (NBC 105:2025 Second Revision). The relevant PDF printed page numbers are **27, 45–48**; document pages 49 and 67–70.

## 1. Three-dimensional model DOES NOT automatically mean three acceleration components

- §9.3.1.1, p45: use a **three-dimensional structural model** for NLTHA, including postelastic hysteresis, degradation/pinching where significant, at least bilinear element response.
- §9.3.2.1, p46: for a **torsionally sensitive 3D structure**, use **at least three pairs of orthogonal motions**. The user's asymmetric plan remains a 3D torsional model regardless of no cantilever projection.
- §9.3.2.3(a–c), p47: apply the scaled motions at the model supports in orthogonal principal structural axes; for each pair run BOTH simultaneous horizontal component orientations XY and YX.
- **Neither clause requires a third vertical accelerogram simply because the mathematical model has 3D translation/rotation DOFs.** A 3D model can receive two simultaneous horizontal accelerations.
- Diagnostic ZERO, X-only or Y-only tests are not a replacement for a complete XY and YX pair. Those probes isolate the currently unresolved X-only wall first-step instability.

## 2. Vertical acceleration applicability: §4.3, p27

The following physical building features trigger consideration of the NBC vertical elastic site spectrum Cv(Tv) = 2Z/3:

| Official criterion | Explicit source check | Record status from user text |
|---|---|---|
| §4.3(a) horizontal/nearly horizontal structural **span >=20 m** | Independently examine actual beam/slab spans; bay spacing is not a global unsupported span | UNKNOWN until drawing check |
| §4.3(b) horizontal/nearly horizontal **cantilever >5 m** | Inspect longest actual unsupported cantilever component | Stated absent; requires source verification |
| §4.3(c) **prestressed** horizontal component | Verify member/material schedule | UNKNOWN |
| §4.3(d) **beam supporting column** | Verify transfer beam/column support connectivity | UNKNOWN |
| §4.3(e) **base-isolated** structure | Verify foundation/isolation bearings/scheme | UNKNOWN |

**Therefore:** “no cantilever projection” is insufficient, by itself, to exempt all vertical checks. If all 5 are verified false from drawings and structural model, document the absence of these enumerated triggers, with reviewer and source fingerprints. The audit still avoids converting that to an automatic code certificate; unusual engineering cases need separate assessment.

Use the committed input template `docs/examples/NBC105_Vertical_Feature_Check_Template.json`, save an approved version in your PRIVATE project results (do not publish sensitive drawings), and run:

```powershell
python 33_NBC105_VERTICAL_APPLICABILITY_REVIEW.py "D:/Thesis/NBC105_Vertical_Features.json" --output "D:/Thesis/Checks/NBC105_Vertical_Applicability.json"
```

Absent keys or `null` mean UNKNOWN, not false.

## 3. Exact adopted scale and unit-conversion chain: §9.3.2.2, p46–47

For an original unscaled horizontal acceleration record pair A and B:

1. Independently develop 5%-damped acceleration spectra from genuine A and B records. The ULS target is the **elastic site spectrum** `C(T)/Omega_u` from §4.1.1 divided by the ULS overstrength factor, **not** an ESM reduced-strength demand spectrum.
2. §9.3.2.2(b) matching interval: `Tn <= T <= sqrt(R_mu) * T1` (review first translational period T1 and Tn for 90% effective translational participating mass in each principal direction).
3. Obtain independently fitted **dimensionless** component scale candidates `f_A` and `f_B`. Per §9.3.2.2(c) **each** must be in the range **0.33–3.0**; reject any pair with an out-of-range component rather than clipping.
4. Per §9.3.2.2(d): `f_pair = min(f_A, f_B)`; apply the SAME `f_pair` to **both** A and B in the XY and YX analyses. A and B are not fitted independently in the final excitation.
5. Convert the raw source **acceleration units** into model acceleration in m/s² exactly once:

   - Original source acceleration in `g`: `OpenSees -factor = 9.80665 * f_pair`.
   - Original source acceleration in `m/s2`: `OpenSees -factor = f_pair`.
   - Original source acceleration in `cm/s2`: currently UNSUPPORTED by this strict runner; convert the actual record with a documented traceable transform first.
   - Original record already scaled/matched: DO NOT multiply by the spectral factor a second time; supply independently confirmed original values or a separately reviewed provenance-aware workflow.

**EXAMPLE (NOT the user's Kobe scales):** f_A=1.80, f_B=1.45, hence f_pair=1.45. If the file data contain acceleration values in g, the Path factor is 14.2196425 m/s² per stored 1 g sample. If the file is already in m/s², Path factor is 1.45. Do NOT also set `-fact 1.45` in UniformExcitation; keep that implicit factor at 1.

**Existing spectrum estimator limitation:** `components/response_spectrum/site_spectrum_and_scaling.py` computes a candidate factor from mean target/mean record spectral ordinates, not a code-prescribed fitting tolerance or independently approved spectrum match. `32_NBC105_PAIR_SPECTRUM_AUDIT.py` reuses that method, preserves the original record SHA256 and chooses the smaller candidate when in range. All spectrum selections remain subject to engineering review.

## 4. EXACT OpenSeesPy commands for a 3D kN-m-s model

Assumptions for this example only: raw A/B source ordinates are in g; A and B share a sample interval dt=0.005 s; the separately verified scale f_pair=1.45; horizontal principal axes coincide with global X/Y. Other orientation/units require explicit updated model transformations.

```python
import openseespy.opensees as ops

# Structure created separately with:
# ops.model("basic", "-ndm", 3, "-ndf", 6)
# ... actual nonlinear wall/frame elements, mass, constraints, gravity, P-Delta
dt_record = 0.005
sf_pair = 1.45  # ILLUSTRATIVE; not your record's fitted scale
accel_factor = 9.80665 * sf_pair

# XY CASE: A -> global X (DOF1), B -> global Y (DOF2).
ops.timeSeries("Path", 900001, "-dt", dt_record,
               "-values", *record_A_raw_g, "-factor", accel_factor)
ops.timeSeries("Path", 900002, "-dt", dt_record,
               "-values", *record_B_raw_g, "-factor", accel_factor)
ops.pattern("UniformExcitation", 900001, 1, "-accel", 900001)
ops.pattern("UniformExcitation", 900002, 2, "-accel", 900002)

# YX CASE must build a NEW isolated model/domain:
# A -> global Y (DOF2), B -> global X (DOF1).
ops.timeSeries("Path", 900001, "-dt", dt_record,
               "-values", *record_B_raw_g, "-factor", accel_factor)
ops.timeSeries("Path", 900002, "-dt", dt_record,
               "-values", *record_A_raw_g, "-factor", accel_factor)
ops.pattern("UniformExcitation", 900001, 1, "-accel", 900001)
ops.pattern("UniformExcitation", 900002, 2, "-accel", 900002)

# No pattern is defined for DOF3; no vertical acceleration input.
# Relative nodal displacement from UniformExcitation != absolute floor displacement.
# ops.analyze(1, selected_analysis_dt) is separate from record digitization dt.
```

Do not execute these XY and YX snippets sequentially in the SAME domain as written: the YX case requires a fresh, independently constructed instance, gravity state and time-series/pattern tags. Existing `building_exploratory.py` runs isolated XY and YX after model reconstruction.

Official OpenSees docs: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html; https://openseespydoc.readthedocs.io/en/stable/src/pathTs.html. Relative displacements, support conditions, mass and DOF directions require actual native verification. The program writes `OpenSees_Bidirectional_Input_Commands.json` in each case to preserve the exact applied mapping, source units and numbers.

## 5. Detailed NBC 105 NLTHA clause register

| Clause | Explicit engineering requirement | Current research-code status |
|---|---|---|
| §4.3 | Assess vertical action for 5 listed structural features | Auditable feature questionnaire, unknown != false; no automatic Z excitation |
| §9.3.1.1 | 3D structural model, significant nonlinear hysteresis, strength/stiffness degradation/pinching | 3D OpenSees frame+wall models exist; experiment-specific cyclic wall/source validation NOT COMPLETE |
| §9.3.1.2 | Gravity loads §5.2 | Separate source gravity/reaction audit; complete agreement still requires actual project outputs |
| §9.3.1.3 | P-Delta effect | Separate gravity and P-Delta numerical check; does not follow merely from a linear modal pass |
| §9.3.1.4 | Inherent torsion | Asymmetric core and COM/rigidity eccentricity explicitly checked; no cantilever exemption |
| §9.3.1.5 | Hysteretic energy dissipation | Requires calibrated member, FSAM and FVD/BRB energy analysis; unqualified native smoke test != approval |
| §9.3.1.6 | Below-grade model extends to foundation when basements present | Check source if basement present |
| §9.3.2.1 | At least 3 appropriate orthogonal pairs in torsion-sensitive 3D analysis | M0–M6 manifest checks >=3 per limit state, XY/YX |
| §9.3.2.2(a) | ULS target `C(T)/Omega_u` | Explicit target category, actual spectral evidence still reviewed |
| §9.3.2.2(b) | Match `Tn` to `sqrt(R_mu)*T1` | Audit checks period window in each plan axis |
| §9.3.2.2(c) | Both independent candidate factors 0.33–3 | Pair rejected outside allowed interval |
| §9.3.2.2(d) | Lower factor applied to both horizontal motions | Same scalar used for X and Y |
| §9.3.2.3(a) | Apply motion to supports | UniformExcitation model-support approximation; verify constraints/SSI |
| §9.3.2.3(b) | Two orthogonal components along structural principal axes | DOF1 X and DOF2 Y, with principal-axis review |
| §9.3.2.3(c) | Two analyses per pair with swapped input directions | XY and YX; diagnostic ZERO/X/Y are not substitutes |
| §9.3.2.4 | Numerical integration `dt <= min(record_dt, T1/100, Tn, 0.01s)` in relevant directions | Pure NBC function; Tn from actual 90% participation not last arbitrary eigenmode |
| §9.3.3 | Use max if fewer than 7, average if more than 7 | Exactly seven is NOT specified literally; reviewer determination needed |
| §9.3.3.1 | Drift limit reference within 2025 edition has a cross-reference issue | Actual limit is §5.5.3 (ULS .025, SLS .006) and §9.3.3.1 mentions §5.6; document, do not silently fix |
| §9.3.3.2 | Inelastic member deformation demands satisfy applicable material limits | Require source-calibrated component-specific acceptance, not invented IO/LS/CP limits |

## 6. How to use this in the thesis

1. Verify the five §4.3 feature conditions from ETABS, drawings and engineer judgment. Do not equate re-entrant corner, plan asymmetry or a slab notch with a >5 m horizontal cantilever.
2. Set the dynamic model to **3D**, with both **simultaneous horizontal** X and Y support accelerations. Run the two rotated orientations XY and YX for every compatible pair, limit state and M0–M6 configuration. Nonlinear mass/torsion remain 3D.
3. Determine actual site `C(T)`, ULS `R_mu`, `Omega_u`, `T1` and `Tn90`. These are not all known from a nominal material grade.
4. Determine candidate f_A and f_B from the genuine recorded motions and period interval, check 0.33–3 for each, adopt minimum. Preserve source SHA, unit conversion, separate spectrum matching evidence and exact OpenSees commands.
5. Verify actual gravity, mode participation, P-Delta and first nonlinear step; then complete all motion pairs with accepted-state numerical evidence. Explicitly do not call a numerical-only run experimentally calibrated.
6. Review time-step mesh refinement, displacement/drift/roof twist, wall/column demand, BRB fatigue and damper stroke/force/energy; evaluate NBC limits separately for ULS and SLS.
