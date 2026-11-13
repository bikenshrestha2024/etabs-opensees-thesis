# Governing code matrix — NBC 105:2025 FIRST; IS 16700 only for declared exceptions

**Decision recorded:** 2026-11-13; thesis-specific source hierarchy. **Status:** documented engineering design basis for implementation; **not** a certificate of compliance or evidence that all code modules currently implement every rule.

> **MANDATORY:** Nepal **NBC 105:2025** governs *all seismic analysis methods, input hazard and spectral definitions, seismic loads and combinations, seismic weight, directions, structural response, design checks and interpretation*. **IS 16700:2023 (base text subject to 2025 Amendment No. 1 verification)** is explicitly selected for **(1) the COMPULSORY initial EQ P-Delta native cases required by the adopted project workflow** and **(2) conventional RC slab flexural stiffness multipliers only**, and may be used as separately labelled *supplementary research checks* when NBC does not specify an issue. Never use IS 16700 to silently override a directly applicable NBC requirement.

## Specific, noninterchangeable roles

| Case / module | Governing authority | IS 16700 treatment | Required implementation / evidence |
|---|---|---|---|
| Research scope, location, seismic hazard | **NBC §4** (seismic spectra, zoning, importance and site classification), project verified geotechnical data | Optional supplementary guidance, never a replacement for Nepal zoning or site spectrum | Official Nepal hazard basis; soil Vs30 gate; traceable hazard/record files |
| **Seismic weight and mass** | **NBC §5.2, Table 5-1** | **Not used** to derive seismic mass | 100% dead including verified permanent actions; 60% storage live, 30% other live, roof live 0% as categorized; independently classify source load patterns and count weight once |
| **Seismic design combinations** | **NBC §3.6** (including applicable nonparallel/vertical rules); NBC limit state selections | **Not used** to replace NBC combinations | Exact NBC code combinations, factor provenance, applicability and sign; distinct from initial IS P-Delta prerequisite |
| **INITIAL P-Delta prerequisite (special project adoption)** | **IS 16700:2023 §7.2(d)** explicitly adopted as a **COMPULSORY initial EQ P-Delta gate**, with applicability and 2025 amendment review | **YES, compulsory project method:** `1.2 DL + 0.5 IL ± 1.5 EL/WL` for all applicable X±/Y± earthquake initial cases (EL calculated from NBC seismic coefficient); wind variants only where applicable | Record source clause, case IDs `IS16700_PD_INIT_{X|Y}_{PLUS|MINUS}`, exact imported EL/WL definitions, geometric nonlinearity setting, iteration/convergence, displacements and member forces. Do not substitute for NBC §3.6 design load cases, NBC-required P-Delta behavior, or gravity preload in TH |
| **Conventional RC slab effective flexural stiffness (special project adoption)** | IS 16700:2023 **Table 5** because project's beam-supported conventional slab needs a separate rational basis | **YES, required conventional-slab source:** strength `0.25 Ig`, serviceability `0.35 Ig`; source `Ag=1.0 Ag` | Apply to actual slab **bending** behavior only; document elastic plate section axes and numerical representation; preserve geometry/thickness, physical weight and in-plane diaphragm membrane behavior unless separately justified; no hidden multiplication/double-reduction. IS table's other member factors do not displace NBC wall/beam/column rules |
| Beam/column/wall effective elastic stiffness | **NBC Table 3-1** | Cross-check only, **not used for adopted member stiffness** | Source ETABS and OpenSees effective EI, wall in-plane (not merely slab plate bending), limit state ULS/SLS, shell/membrane assumptions |
| ESM / equivalent static | **NBC §§3.2.1, 5, 6** (eligibility, empirical/Rayleigh period, Aw, seismic force, torsion, drift/deflection) | Not used for calculation | For tall building, ULS ESM only if eligible by NBC §3.2.1; otherwise `COMPARISON_ONLY`; show full section 6 input/result ledger |
| MRSM / modal response spectrum | **NBC §§3.2.2, 4, 5, 7** | Supplementary checks clearly separated, never source of response spectrum or scaling | NBC spectrum, mode combination, minimum shear and force scaling per NBC, drift independently unscaled when required, ULS/SLS state |
| Linear (elastic) time history | **NBC §§3.2.3, 4, 5, 8**, applicable other NBC clauses | Supplementary numerical/stability checks only | Gravity as NBC §5.2 where specified, P-Delta, torsion, damping, paired records, integration and response checks according to NBC; require audited initial EQ P-Delta cases and a physically verified state-transfer method; NBC §5.2 gravity remains required; never double-count a held static ±EL and the full support ground motion |
| Nonlinear time history | **NBC §§3.2, 4, 5, 9.3** including 9.3.1–9.3.3 | Supplementary element/detailing/checking only | 3D nonlinear material/geometry, NBC seismic gravity and mass, hysteresis, bidirectional XY/YX, spectral scaling/integration/response limits and all complete histories; independent component calibration remains mandatory |
| Drift, torsion, performance and design acceptance | **NBC §§5.4–5.6 (applicability), 5.5, 8/9 and relevant material provisions** | Additional `IS16700_SUPPLEMENTARY` result panel if requested; never sets NBC PASS | Each criterion must carry `source_code`, `edition`, `clause`, `limit_state`, `approval_status`. Never replace NBC drift with IS drift |
| Additional tall-building checks not explicitly defined by NBC | NBC first; project-specific approved basis and other applicable Nepal provisions | Optional source-labelled **supplementary** diagnostics: tall-building stability indicator, rigid offsets, collector/backstay only when physical configuration applies, floor dynamics, differential shortening | Explicit `SUPPLEMENTARY_NOT_NBC`, actual IS clause and 2025 amendment status; no implicit code-compliance stamp |

## Time-history initial-condition branching — compulsory engineering review

**NBC §§8.1.1.3 and 9.3.1.3 require P-Delta**; §8.1.1.2 and §9.3.1.2 refer to §5.2 gravity. Thus the compulsory IS §7.2(d) initial signed earthquake cases supply a project *method for initialization*, not the underlying NBC hazard, mass or load combinations. Compute EL from NBC seismic coefficient, then solve X+ X− Y+ Y− with convergence and source verification **before** P-Delta-enabled time histories. A P-Delta-disabled history with zero perturbation is **diagnostic/noncompliant control only**. In both branches NBC gravity must be applied for any claim of NBC seismic analysis; `zero initial` is not permission to omit the gravity equilibrium. A P-Delta enabled run must begin from an explicitly verified state; holding ±1.5 EL during a full ground-acceleration time series risks *double-counting seismic lateral load*. Require source-documented transfer/unloading procedure, reactions, and fresh-domain replay; do not blindly transfer the signed static EL. See [P0 review](../../REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md).

## Load-case firewall

```text
GRAVITY_FULL_1D_1L          = actual full gravity-source comparison; includes roof LL if applicable
NBC105_SEISMIC_WEIGHT       = D + 0.60 L_storage + 0.30 L_other + 0.00 L_roof
IS16700_PD_INIT_{axis,sign} = 1.2 D + 0.5 IL ± 1.5 EL/WL (compulsory project initial EQ P-Delta analysis)
NBC105_ULS_SLS_DESIGN       = exact NBC 105:2025 §3.6 factors & applicable signs
NBC105_LTH_GRAVITY_PRELOAD  = NBC §8.1.1.2 / §5.2 gravity, separate from signed EQ static initialization
NBC105_NLTH_GRAVITY_PRELOAD = NBC §9.3.1.2 / §5.2 gravity, separate from signed EQ static initialization
```

These are **different purposes**, even if a source pattern is reused. Apply each physical load once. No equation on this page authorizes assigning *NBC seismic-mass weights* as a generic factored gravity combination, or replacing NBC sustained preload requirements with the IS initial case.

## Programmatic provenance fields (proposed schema, not proof of current code implementation)

```json
{
  "governing_code": "NBC 105:2025",
  "analysis_method": "NBC105_NLTHA",
  "code_clause": "NBC 105:2025 §9.3",
  "load_case_purpose": "NBC105_NLTH_GRAVITY_PRELOAD",
  "supplemental_source_exceptions": [
    {"topic": "initial_pdelta_gate", "code": "IS 16700:2023", "clause": "7.2(d)", "approval": "PROJECT_ADOPTED", "amendment_2025": "PENDING_RECONCILIATION"},
    {"topic": "conventional_slab_bending", "code": "IS 16700:2023", "clause": "Table 5", "strength_Ig": 0.25, "serviceability_Ig": 0.35, "amendment_2025": "PENDING_RECONCILIATION"}
  ],
  "engineering_validation": "NOT_VERIFIED"
}
```

**Before implementation:** review actual parsed NBC text and latest official amendments; map every existing calculation/GUI button to a single primary `NBC105_` method, and keep the 2 adopted IS checks in clearly named special-use classes. Before claiming the IS factors are currently amended, obtain the authenticated 2025 amendment and establish whether §7.2(d) and Table 5 are affected.

## Quality assurance requirements

1. **Static policy test:** every ESM/MRSM/LTH/NLTHA and code combination generator references NBC as `governing_code`; only exact declared IS exceptions may supply adopted values.
2. **Numerical regression:** old vs new source-equivalent models; report if parameters, masses, offsets, shell stiffness or load-case definitions changed.
3. **Review:** sign source editions, amendments, precise scope, ULS/SLS and all physical acceptance limits. A documentation policy change does not itself modify or validate model solver execution.
4. **User interface:** always display **NBC Governing** in main module headings; display the two IS exceptional items with distinct labels **IS 16700 — COMPULSORY initial EQ P-Delta** and **IS 16700 — REQUIRED conventional slab bending**. Output sheets/JSON must carry this designation and avoid merged code-status indicators.

### Primary references
- [NBC 105:2025, DUDBC official source](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)
- [IS 16700:2023 §7.2(d), Table 5, base standard (BIS)](https://www.services.bis.gov.in/tmp/CED20920094_14092023_1.pdf)
- [IS 16700:2023 amendment listing (BIS)](https://standards.bis.gov.in/website/standard-details)
- [IS 16700 amendment source verification and transfer rules](../../LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md)
