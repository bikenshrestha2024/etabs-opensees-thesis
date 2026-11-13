# Q&A 02.01 — Why ±1.5EL from an initial IS P-Delta case is not automatically the earthquake time-history starting force

**Reviewed:** 2026-11-13 | **Question raised by:** structural researcher | **Engineering status:** justified analytical distinction; project-specific native verification OPEN. This is a source-based explanation, **not** a completed 25-storey NLTHA.

## Q1. What exactly is the apparent contradiction?

**Short answer:** There is no contradiction. The IS 16700 initial analysis is a **COMPULSORY separate project prerequisite**, while the NBC 105 ground-motion analysis needs a **physically compatible initial state**. Both can be required without their load histories being identical.

- IS 16700:2023 §7.2(d) (base text; 2025 amendment pending) supplies `1.2DL + 0.5IL ±1.5EL/WL` for an *initial P-Delta analysis*. In this thesis, `EL` uses **NBC 105:2025 seismic-coefficient actions**, not IS 1893 spectra. Run separate signed X+, X−, Y+, Y− initial cases, retaining all convergence, sign, identity and equilibrium evidence. An EQ load defined for reference from NBC ESM does not itself make ULS ESM a code-eligible **design method** for a tall building.
- NBC 105:2025 §§8.1.1.2–8.1.1.3 and 9.3.1.2–9.3.1.3 require seismic-weight-consistent gravity and P-Delta in elastic and nonlinear time histories. They do **not** state “hold ±1.5EL as a permanent lateral bias while superposing the complete earthquake record”.
- The full-ground-motion case applies a **time-varying inertial action** through the excited support, not an incremental static `EL` in the same sense as an ETABS static EQ case. The selected initial state must satisfy equilibrium at the beginning of the new history.

## Q2. Why is holding signed ±1.5EL a problem?

**Mechanics:** Write the nonlinear dynamic equilibrium schematically as

```text
M*u_ddot + C*u_dot + f_int(u, z, P_gravity) =
    p_gravity + p_static_EL - M*Gamma*a_ground(t).
```

Here `z` contains internal material/constitutive state; `p_static_EL` is the held **lateral static EQ** pattern if left active, and `-M Gamma a_ground(t)` is the time-varying support acceleration excitation. A conventional gravity-initialized transient has `p_static_EL = 0` while retaining `p_gravity` and internal stress/displacement equilibrium at `t=0`.

If `p_static_EL = ±1.5EL` is deliberately retained, the model is experiencing a *biased initial lateral deformation* plus the earthquake record. This is not an algebraic “double multiplication” of a single vector; the two actions differ in time and shape. It is, however, an **additional seismic lateral action** that can double-count the intended earthquake demand or bias hysteretic forces, P-Delta stability, FVD forces and residual drift unless the scenario and load history are independently justified. For example a record starts with zero acceleration but the model may already have a substantial ±EL-induced first-storey drift and damaged wall state.

**Do not** assume that the static elastic force profile equals the signed instantaneous support excitation or that applying both reproduces the same earthquake. The difference is physical, not merely a software naming convention.

## Q3. Then why run the signed initial cases at all?

Because the researcher has explicitly adopted the IS §7.2(d) rule as the **compulsory initial P-Delta verification procedure**: separate signed lateral static states test second-order effects under specified initial combinations and provide a reproducible baseline to investigate stiffness sensitivity, stability, torsional effects and ETABS case dependency. A case can pass signed static equilibrium without qualifying the *entire nonlinear transient initial state*; both checkpoints remain.

### Conditional admissible study types
- **Compulsory signed initial checks:** X±/Y±, `1.2D + 0.5IL ±1.5EL`, source-identified NBC EL; output `INITIAL_PDELTA_STATIC_CHECK`.
- **NBC gravity-equilibrium NLTHA (recommended production branch):** perform source-correct §5.2 gravity, preserve gravity stresses and displacements, include geometric nonlinearity, freeze those gravity patterns and introduce ground acceleration without held static ±EL; output `GRAVITY_INITIALIZED_DYNAMIC`.
- **Signed-EL-bias sensitivity (optional independent research branch):** only after documenting target physical scenario, load holding/unloading, initial state, stress damage, record relationship and double-demand check; output `SIGNED_EL_BIASED_DIAGNOSTIC`. Never merge its response with the governing NBC record ensemble without explicit approved rationale.
- **No P-Delta control:** the `ZERO_LATERAL_REFERENCE_NO_PD` baseline is comparison-only, not NBC-compliant time-history analysis. **Zero initial** must never be misconstrued as removing required NBC §5.2 gravity.

## Q4. Why does ETABS look different from OpenSees?

**Two different numerical operations:**

1. **Tangent-stiffness linear case**: after a nonlinear-static P-Delta case, ETABS can use the *stiffness at the end* of the initial case for a new **linear** analysis. According to CSI's *Stiffness to Use* guidance, initial-case **loads are not included in the dependent linear-case response**, and the fixed tangent does not continually update when new EQ forces grow.
2. **Full nonlinear-state continuation**: ETABS nonlinear-direct-integration time histories may continue from a preceding nonlinear static state, carrying the displacement, internal force, material history and loads. CSI *Initial Conditions* notes that loads in the subsequent nonlinear case are **incremental on top of those already active**. Thus a signed static EQ state retained here is not just an invisible stiffness correction.
3. **OpenSees**: `ops.loadConst('-time',0.0)` makes every currently existing LoadPattern constant, including **any static ±EL pattern mistakenly left present**. It does not automatically strip EL, roll back displacements or remove nonlinear state. New Path/UniformExcitation load patterns created afterward are not frozen. `ops.wipeAnalysis()` changes analysis objects while preserving model state; `ops.wipe()` destroys the domain and is unsuitable for state continuation.

Consequently **no direct 1:1 ETABS “initial stiffness” toggle exists for general full 3D OpenSees nonlinear histories** without explicit implementation/verification. Rebuilding and solving gravity equilibrium is generally more defensible than pretending a matrix or JSON captures a nonlinear wall's hysteretic internal state. If the study requires an independent *linearized* OpenSees tangent approximation, develop and benchmark it separately; do not pass it off as full NLTHA.

## Q5. What precisely is `loadConst` doing?

After successful gravity convergence, `ops.loadConst("-time",0.0)` (a) freezes load patterns **already in the domain** and (b) resets pseudo-time to zero. It does not itself:
- prove gravity equilibrium or verify the NBC §5.2 load-pattern ledger;
- introduce geometric nonlinearity into elements previously built without it;
- transform a signed `1.2DL+0.5IL±1.5EL` case into a correct NBC §5.2 gravity preload;
- remove a static `EL` load or clear earthquake material-history bias;
- constitute a complete time-history setup.

`ops.wipeAnalysis()` removes the old **analysis configuration**, not the model/elements, gravity displacements, or previously frozen loads. New XY/YX Path and UniformExcitation patterns are configured after the freeze; their magnitudes, units and scale factors still must be audited.

## Q6. Is the initial gravity load exactly `1D+1L`?

**No.** Three load states must remain separate:

| Purpose | Source | Load interpretation |
|---|---|---|
| Independent full-gravity load path | Original ETABS 1.0D+1.0L (including roof load as applicable) | Used to check vertical reaction sum/member transfer; not the seismic mass definition |
| NBC seismic weight / TH gravity | NBC §5.2 & Table 5-1 as cross-referenced by §§8.1.1.2/9.3.1.2 | D including self-weight and permanent loads + 0.6 storage live + 0.3 other live + 0 roof live, per actual classified source patterns; verify specific floor and occupancy |
| Compulsory initial static P-Delta | Project-adopted IS §7.2(d) | 1.2DL + 0.5IL ±1.5EL (or wind variant when justified), using independently derived NBC EL |

*Warning:* An actual ETABS mass source factor of `0.3` or `0.6` does **not** establish whether a pattern is dead or imposed load. The current `components/model/initial_pdelta.py` has an open classification risk; do not claim its native four cases are source-validated until corrected against actual ETABS load pattern types.

## Q7. What should happen before the nonlinear first step?

**Minimum acceptance sequence:**

1. Freeze EDB, ETABS source loads, assembled 3D model, ULS/SLS stiffness, material assignments, support mapping and record SHA.
2. Run four independent signed project-required static initial cases and verify lateral/vertical reaction equilibrium; archive signs, source EL coefficient, factor basis, convergence and full source identity.
3. In a **fresh native domain per record/orientation**, rebuild the nonlinear structure with verified P-Delta geometric formulations for frames and physically correct walls; apply **NBC §5.2 gravity only** incrementally; converge and inspect stress/vertical reactions/lateral displacements.
4. Check that no signed static EL pattern is inadvertently active before `loadConst`. Record original/current pattern tags, gravity state, time and support resultant; **fail closed** if source provenance missing.
5. `ops.loadConst('-time',0.0)`, then `ops.wipeAnalysis()` (only the analysis objects). Create proper damping, integrator, test, system and recorder; apply new calibrated XY/YX Path/UniformExcitation patterns.
6. Run **zero-motion**, X-only, Y-only and both bidirectional orientations for controlled diagnostic isolation; complete full histories only after numerical failures are resolved. Compare gravity-reference and dynamic-incremental displacements, forces, energy and period basis.
7. Keep numerical completion, ETABS-equivalence, physical material calibration and NBC acceptance as four separate outcomes.

## Q8. What evidence would make a signed-EL-starting-history defensible?

A physical research reason for signed lateral bias, the original and held load patterns, complete verified nonlinear constitutive state, signed initial deformation/axial/shear results, a reproducible unloading/hold procedure, a baseline gravity-only history using identical record and integration settings, a quantitative sensitivity study of peak/residual drifts/energy, and independent reviewer acceptance. It remains a **research scenario**, not the automatic starting condition for all NBC-compliant histories.

## Q9. How should the GUI and result folder label these branches?

Use distinct, source-verified flags: `IS16700_PD_INIT_STATIC_{X+|X-|Y+|Y-}`; `NBC105_TH_GRAVITY_INITIALIZED_{XY|YX}`; `DIAGNOSTIC_NO_PDELTA`; and, if explicitly approved, `RESEARCH_SIGNED_EL_BIAS`. Save initial static case and NLTHA outputs separately, including `source_code`, `load_case_purpose`, `active_pattern_tags_at_t0`, `physical_initial_state_policy`, `solver`, `accepted_time_s`, `record_sha256`, `model_sha256`, `status`, `validation_gate` and an engineering reviewer. Do not silently change saved legacy path conventions without checking callers.

## Source and citation register

| ID | Document / publication | Source location | What it supports | What it does NOT establish |
|---|---|---|---|---|
| NBC105-2025 | Government of Nepal/DUDBC, *NBC 105:2025 Seismic Design of Buildings in Nepal*, 2025 | §§5.2, 8.1.1.2–.3 and 9.3.1.2–.3; https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf | Nepal seismic gravity and required P-Delta | Does not prescribe that ±1.5EL must remain active throughout all records |
| IS16700-2023 | BIS, *Criteria for Structural Safety of Tall Concrete Buildings*, 1st revision, 2023 | §7.2(d); base user study text, BIS catalogue amendment no. 1 (2025) | Adopted compulsory signed initial static combination | Does not itself prove dynamic initial state or the transfer method; amended clauses pending review |
| CSI-IC | CSI ETABS *Initial Conditions* | https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Cases/Initial_Conditions.htm | Nonlinear-state continuation carries prior loads/history; subsequent loads incremental | Not a substitute for source-specific model verification |
| CSI-STIFF | CSI *Stiffness to Use* | https://docs.csiamerica.com/help-files/sap/Menus/Define/Load_Cases/Stiffness_to_Use.htm | Linear cases can use final nonlinear tangent without previous loads in linear response | Does not imply an NLTHA can freely discard material state |
| OPS-LC | OpenSees *loadConst* | https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html | Fixes current load patterns, resets pseudo-time if requested | Does not classify or remove EL/convert ETABS states |
| OPS-WA | OpenSees *wipeAnalysis* | https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/wipeAnalysis.html | Clears analysis objects, preserves domain | Does not validate gravity |
| OPS-PD | OpenSees *PDelta transformation* | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/PDelta.html | Geometric P-Delta in suitable frame elements | Does not verify 3D shell/core wall second-order behavior |
| PEER-TBI-2017 | PEER, *Guidelines for Performance-Based Seismic Design of Tall Buildings*, 2017 | §4.2.6; https://peer.berkeley.edu/sites/default/files/publications/tbi-working-group-led-by-co-chairs-ron-hamburger-and-jack-moehle_10.9.2017.pdf | Nonlinear gravity/lateral state and non-superposition reasoning | Non-governing supplementary guideline, not NBC substitution |

**Crosslinks:** [P0 NBC/IS initial state issue](../../00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md), [adopted gravity handoff](../../07_TIME_HISTORY/20261113_NBC_GRAVITY_PRELOAD_TO_EQ_TRANSIENT_DECISION.md), [code hierarchy](../../../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md).

**Open items:** source-categorized D/IL patterns; actual native four-case convergence and source hash; high-rise EL derivation/ESM eligibility; 2025 IS amendment; all wall/fiber and P-Delta formulation tests; no-static-EL source pattern audit; ZERO/X/Y/XY and full NLTHA completion.
