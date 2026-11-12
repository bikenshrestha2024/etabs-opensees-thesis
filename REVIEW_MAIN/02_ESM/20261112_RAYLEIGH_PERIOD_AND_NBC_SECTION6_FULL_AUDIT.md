# 2026-11-12 NBC 105:2025 §5.1.1 Rayleigh and §6 ESM arithmetic — source/run/code audit

**Engineering status: METHOD_AND_FORMULA_VERIFIED / SCREENSHOT_PERIODS_RECORDED / PER-STORY_NUMERICAL_RECONSTRUCTION_PENDING / HIGH-RISE_ULS_ESM_COMPARISON_ONLY / NATIVE_ETABS_EQUIVALENCE_OPEN.**

## Source identity and authoritative references
- Original Nepal National Building Code: [NBC 105:2025 official DUDBC government PDF](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). Clauses: 3.2.1, 3.4, 3.6.1–3.6.3, 4.1.1–4.1.5, 4.2, 5.1.1–5.1.3, 5.2, 5.5, 5.6, 6.1–6.5.
- Tall concrete building review: [IS 16700:2023 (BIS full text, distributed by RMCMA)](https://www.rmcmaindia.org/adminpanel/admin/server/upload/1762423704_IS%2016700%20-%202023.pdf), §§6.3.4, 7.2(a–d), 7.3.9–7.3.10. Its initial geometric-nonlinearity load combination is **1.2DL+0.5IL±1.5EL/WL**; separate from the final NBC ULS/SLS ESM action. IS 16700 is a supplementary modeling benchmark; NBC 105 governs Nepal seismic actions.
- Source: user screenshots and `Pasted text (2)(20261112-093435).txt` from the 2026-11-12 ULS OpenSees comparison. **Crucial limitation:** the source Rayleigh JSON, its X/Y 25-storey Excel sheet and the full individual ESM calculation JSON/CSV were *not attached*; exact 25-storey numerators and denominators, corresponding native source stiffness and support modes cannot be independently recomputed from a screenshot alone.

## Source-verified equations; all units

NBC §5.1.1 (printed page 28):
`T_R = 2 π sqrt( sum_i Wi di² / [g sum_i Fi di] )`, Wi kN, Fi kN, elastic **center-of-mass incremental** di metres, g=9.81m/s², torsion excluded. **Do not confuse this period estimate with Rayleigh damping coefficients.**

NBC §5.1.2–§5.1.3: `Aw= Σ Awi[0.2 + (Lwi/H)²]`, wall system `T_emp = 0.075 H^(3/4) / sqrt(Aw)`; `T_emp,amp=1.25 T_emp`; `T_design=min(T_R,T_emp,amp)`.

NBC §4.1.1: `C(T)=Ch(T)*Z*I`. §4.2: `Cs(T)=0.20*C(T)`. Soil C ESM has alpha=2.5, Tc=1.0s, Td=4.0s; for chosen periods here (1 < T < 4), `Ch=2.5*1/T`.

NBC §6.1(1) ULS: `Cd(T)=C(T)/(Rmu*Omega_u)`. §6.1(2) SLS: `Cd(T)=Cs(T)/Omega_s`. Rmu/Omega_u/Omega_s must be **selected from the actual NBC Table 5-2 lateral system in the model**, no assumptions that RC frame, RC wall or RC dual system are equivalent. §6.2: `V=Cd*W` where `W=sum_i [D_i+0.6*StorageLL_i+0.3*OtherLL_i]`; roof live participation 0 by Table 5-1. **The solved gravity 1.0D+1.0L = 311,367.31388kN is NOT automatically the seismic W.**

NBC §6.3: `k=1 (T<=0.5); k=2 (T>=2.5); otherwise 1+(T-0.5)/2`. `Fi=V*Wi*hi^k/[Σ Wi hi^k]`. The denominator, source Wi and hi for **every** floor, Fi and cumulative *applied* force must be reported; `ΣFi=V` is the independent arithmetic check, not a physical base-reaction/shear recovery.

## Values reconstructed from visible ULS screenshots (not independently re-solved)

| Quantity | X ULS | Y ULS | Evidence / gate |
|---|---:|---:|---|
| Source-assessed wall grouping | Two 12m X walls, each 2 door openings | Three solid 6m Y walls | Node/shell export review; independent native ETABS geometry and EDB identity gate still open |
| Adopted Aw, m² | 2.07317451524 | 2.20308033241 | Exported geometry interpretation |
| H, m | 95 | 95 | Review basement/base-height interpretation |
| T empirical, s | 1.5850247080 | 1.5375838214 | NBC §5.1.2 calculation |
| 1.25 empirical, s | 1.9812808850 | 1.9219797767 | NBC §5.1.3 |
| Preliminary T Rayleigh, s | 3.8985139079 | 5.5904409801 | Screenshot, not independently reconstructed from Wi/Fi/di |
| **Adopted T for ESM, s** | **1.9812808850** | **1.9219797767** | Minimum of two methods |
| Soil C Ch(T) | 1.2618099831 | 1.3007420943 | alpha Tc / T |
| Z | 0.35 | 0.35 | Screenshot Kirtipur interpolated Z; independently verify actual site |
| C(T) | 0.4416334941 × I | 0.4552597330 × I | Importance factor I missing from supplied screenshot |
| Period exponent k | 1.7406404425 | 1.7109898884 | NBC §6.3 |
| Reported ULS V, kN | 25,659.046 | 26,450.735 | Pasted ESM log, NOT independently verified without actual W, Rmu and Omega_u |
| Site Vs30 | NOT VERIFIED | NOT VERIFIED | H > 40m; NBC §4.1.3.1 gate |
| ULS ESM design eligibility | NOT PERMITTED for given tall model | NOT PERMITTED for given tall model | §3.2.1; retain only comparison/reference, use qualifying dynamic method |

## Read and review of live Rayleigh program

File `components/modal/rayleigh.py`:
- Reads `NBC105_ESM_Story_Weights_Assembled_V118.csv`, checks diaphragm masters against the source JSON, computes Wi with Table 5-1. Outputs model and weight-ledger SHA256.
- Uses `k_ref=1+(T_emp-0.5)/2` (bounds at 1 and 2) to form reference shape `Wi hi^k_ref`, scales **total Fi_ref=0.01 ΣWi**. For elastic fixed-stiffness response its *amplitude* cancels the quotient, but the force *shape* does not cancel. Here `k_ref≈1.54251235 X`, `k_ref≈1.51879191 Y`; adopted period ESM exponents are **1.74064044 X** and **1.71098989 Y**. That difference must be documented and its influence tested, rather than treating Rayleigh Fi_ref as the final NBC §6.3 Fi design force.
- Builds a fresh elastic model with gravity preload, adds SP rotational constraint at the diaphragm master in each floor, equilibrates the constrained gravity state, freezes it, applies X/Y reference Fi, and uses **incremental** center-of-mass displacements.
- Calculates two independent sums and checks against a separate helper `components/modal/rayleigh_ledger_audit.py`; prior workbook exported hard-coded Python terms. Current `rayleigh.py` now writes **live Excel formulas**, sum rows and an independent Excel reconstruction alongside Python period, reference exponent, reference-force magnitude, model SHA, weight-ledger SHA and state. This is a **formula audit**, not a recalculation of the latest unseen Windows case.
- Suspect 5.59s Y mode: investigate source 76 vs 32 mesh restraints (the GUI 32 default is a **diagnostic**, production still retains 76 exported source restraints), shell/wall stiffness, master DOF constraint and source period comparison, model gravity tangent; test another reference force shape and 0.5%, 1%, 2% amplitudes to verify amplitude independence *in the actual solver*. Do not silently replace with eigenperiod.

## ESM module formula/output audit

`components/equivalent_static/code_basis.py` implements correct branch-specific formulas for C, Cs, Cd, W, k, V and Fi. Every new direct ESM Excel now includes **NBC 5-6 Derivation** and **Storey Formula Audit** showing underlying factors, spectra, and each force/distribution term, plus case status. The full JSON already includes these source parameters. The original ETABS-linked Excel is a separate historical engine, not the same current grouped-wall source method. In `components/equivalent_static/etabs_linked_excel.py` the original calculation still calls `eng.calculate_direction` on the copied source workbook. Its **Aw-X 1.9582936288m² = four 6m panels** is genuine historical method output, not the user's newer selected **two 12m walls = 2.073174515m²**. Do **not** silently overwrite the original source Excel formulas or relabel 1.958 as adopted. The GUI's `_apply_reviewed_wall_policy()` switches the active grouped-wall source-verified inputs back where available. Keep an explicit difference report until the ETABS-linked source calculation adopts a separate fully verified two-12m wall grouping in its research report. EDB **path equality is not SHA equality**; workbook registered SHA and model SHA must be checked independently.

### EQ force signs and torsion

At each storey `Fi >= 0` is a *magnitude*. For X+: Fx=+Fi; X−: Fx=−Fi. For Y+: Fy=+Fi; Y−: Fy=−Fi; each has its own run. Accidentally shifted load application is equivalent to an applied floor Mz, with **e=±0.05b** along the plan axis perpendicular to force: X load acting at +y yields `Mz=−Fx*e_y`; Y load acting at +x yields `Mz=+Fy*e_x`. These signed moments change with both seismic force and eccentricity sign. Centered E0 suppresses accidental torsion only, not the actual inherent mass/stiffness eccentricity. Combination of perpendicular loads is governed separately by NBC §3.6.2 only when non-parallel systems criteria apply; do not mistake X/Y polarity cases for simultaneous 100/30 action. Default 12 signed X/Y plus centered eccentricity cases cover ± forces and ± accidental signs.

### P-Delta / initial versus main earthquake

`components/model/initial_pdelta.py` is a **separate runner**: builds a fresh elastic model, applies classified `1.2D+0.5IL`, then applies **±1.5 diagnostic EL** in each X and Y, four `PD_INIT_EL_{X,Y}_{PLUS,MINUS}` cases, checks convergence and lateral equilibrium. It uses the exported source restraints and is **not** evidence of a separately completed SLS series or a final high-rise ULS design. Compare each case input fingerprint, load pattern classification and geometric transformation with the source EDB. The full model's regular `GRAVITY_1.0D_1.0L` result is a separate load case and **cannot be relabeled 1.2DL+0.5IL±1.5EL**. A success in the `PDelta initial` runner must not be read as proof of all `G+EQ` final second-order cases. NBC §3.6.1 includes `DL+λLL±E` and `0.9DL±E`; NBC §3.6.2 adds 100%+30% orthogonal when systems are not oriented mutually orthogonally. The actual combined, geometric-nonlinear structural response must be reported per ULS/SLS state if used for acceptance.

**Important modeling limit:** IS 16700:2023 §6.3.4 also discusses the rigorously analyzed period for buildings ≥50m; it is a supplemental independent tall-building criterion and is not substituted for Nepal NBC §5.1 period selection. IS §7.3.10 includes a drift stability coefficient; a P-Delta convergence result alone cannot establish its acceptance.

## Required native evidence to close the numerical gate

1. Current exact `NBC105_Rayleigh_Preliminary_V123.json` and `.xlsx` for ULS, and `_SLS` for SLS if run; `NBC105_ESM_Story_Weights_Assembled_V118.csv` with source hash; `OpenSees_Complete_Model_Config_V118.json` and source metadata hash; `NBC105_ESM_Calculation_ULS_{X,Y}+_E0_V111.json`, all source-matched.
2. All 25 rows `Wi,Fi_ref,di`; recompute `Σ Wi di²`, `gΣ Fi di` and T per direction with independent spreadsheet formulas. Compare periods for 0.5%,1%,2% reference force fractions and two physically reasonable lateral-force distributions. Any variation indicates nonlinear-tangent, state or boundary-condition sensitivity requiring investigation.
3. Same-model native ETABS stiffness, effective walls, diaphragm constraints, gravity reference, six-DOF base supports, response spectrum/mode periods, equilibrium, CM displacement profiles.
4. Explicit selected structural system for Rmu, Ωu, Ωs; importance I, verified site Z/Vs30, actual seismic W. Trace `Ch,C,Cs,Cd,W,V,k,ΣWi hi^k,Fi` each state. Until source W is provided, reported V cannot be independently replicated.
5. File fingerprints and completed `OpenSees_IS16700_Initial_PDelta_Results.json` with actual convergence/reactions and all four initial polarities; separate ULS/SLS final G±E response, drift/θ PDelta, main response comparisons.

### Authoring / physical safety

Research audit, not certified code compliance. No source EDB/XLSX rewritten, not changing MRSM/TH scale factors, raw 32/76/97 sensitivity runs retained. New program report sheets are **derived** evidence and need Windows OpenSees + ETABS validation.
