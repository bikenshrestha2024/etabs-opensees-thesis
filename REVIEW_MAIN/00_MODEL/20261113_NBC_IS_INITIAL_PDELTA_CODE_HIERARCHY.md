# P0 — NBC time-history P-Delta initial-state chain and IS 16700 adopted method

Date: **2026-11-13** | Review type: **mandatory project modeling basis / not a successful structural check** | Evidence: original official NBC 105:2025 and IS 16700:2023 §7.2(d) base text. **No native ETABS/OpenSees solves performed in this review.**

> **Detailed follow-up Q&A:** [Why signed static ±1.5EL is not automatically retained during nonlinear ground-motion records](../09_ENGINEERING_QA/02_PDELTA_INITIAL_STATES/01_SIGNED_EL_VS_GRAVITY_START.md). This page remains the canonical P0 engineering issue; the Q&A explains physics, software semantics and evidence required.

## 1. Source hierarchy (WHEN, WHY, WHICH)

- **NBC 105:2025 §§8.1.1.2–8.1.1.3** (printed p. 42): for *elastic time-history*, apply gravity loads calculated under NBC §5.2 and **include P-Delta effects**; associated torsion/damping/record requirements stay NBC, not IS.
- **NBC 105:2025 §§9.3.1.2–9.3.1.3** (printed p. 45): for *nonlinear time-history*, likewise apply gravity calculated under §5.2 and **include P-Delta effects**; yielding/hysteresis, scaling, bidirectional inputs, step and checks stay NBC.
- **NBC 105:2025 §3.4/Table 3-1:** use NBC effective RC beam, column, and cracked/uncracked wall properties for each ULS/SLS state. Do **not** multiply an NBC shell/section modifier again.
- **IS 16700:2023 §7.2(d)** (base text, printed p. 7): adopted to supply the **COMPULSORY project initial P-Delta analysis combination** that is not numerically prescribed in those two NBC TH subsections: `1.2 DL + 0.5 IL ± 1.5 EL/WL`. For earthquake initial cases, `EL` means an independently calculated **NBC 105 seismic coefficient / equivalent static design-action reference**, not an IS 1893 earthquake coefficient; preserve its derivation, directions, sign and applicability. **IS 16700 is the source of the *initial analysis combination* only; NBC remains the seismic-action source.**
- **IS 16700:2023 Table 5:** project **REQUIRED** for conventional RC slab **bending** modifiers (ULS/strength `0.25 Ig`, SLS/serviceability `0.35 Ig`), because NBC Table 3-1 does not provide a dedicated conventional slab entry. NBC Table 3-1 still controls other listed RC members and walls. The 2025 BIS Amendment No. 1 has been catalogued; amended content must be checked before treating IS passages as amended-current.

## 2. REQUIRED branches — WHAT initial state enters WHICH analysis?

```text
Frozen, source-matched 3D geometry + support/load ledger + NBC ULS/SLS stiffness
                              |
                 NBC105 seismic coefficient / ESM action
                 (source for EL ONLY; use reference calculation
                  even where ESM is not the design method)
                              |
            IS16700 initial P-Delta combination
            1.2 DL + 0.5 IL ± 1.5 EL
              |      |       |       |
             +X     -X      +Y      -Y
            converge and audit 4 native initial cases
                              |
           CHOICE OF DYNAMIC CASE — NOT EQUIVALENT:
             /                                 \
  EQ_NO_PDELTA_CONTROL                   EQ_PDELTA_RESEARCH
  zero lateral/initial state*            reviewed +/−X,+/−Y initial
  no geometric P-Delta effects           geometric nonlinear stiffness
  diagnostic/control only                and well-defined carryover
             \                                 /
        NBC 105:2025 elastic TH §8 or nonlinear TH §9.3
        NBC gravity §5.2, motions §9.3.2, paired XY/YX,
        proper damping/torsion, results checked independently
```

`*` **Critical distinction:** “zero initial condition” must be described as `u(0)=v(0)=0` relative to an explicitly documented reference equilibrium; it does **not** mean omit NBC §5.2 gravity from a final NBC-compliant TH. The no-P-Delta branch is an intentionally noncompliant comparative control (NBC requires P-Delta). If an unconstrained zero-load state is used as a numerical demonstration, label it `DIAGNOSTIC_ONLY`, not NBC-compliant.

**Project requirement:** For an `EQ_PDELTA` case, **initial P-Delta cases must be solved and accepted first**. Reconstruct a fresh solver domain with the same source model/limit state and the intended converged, audited initial state; do not simply copy a postprocessed CSV as solver initial conditions. Preserve the selected sign/axis, initial force/displacement/reaction/stiffness state and history of static loads. Clarify whether each selected state represents *just geometric-stiffness initialization* or *a permanent static lateral bias*.

**Double-counting warning:** Carrying a nonzero static `±1.5 EL` lateral load forward unchanged while also applying a full earthquake acceleration history may unintentionally add the earthquake twice. The documentation must prescribe, test and disclose (a) what static reference loads remain active at `t=0`, (b) which load patterns are held by `loadConst`, (c) what state and tangent stiffness is retained, (d) whether unloading/re-equilibration is needed and permitted for this formulation, (e) how support excitation is introduced, and (f) whether the initial state represents a deliberately biased scenario rather than a universal NBC NLTHA starting state. **No automatic direct transfer of ±EL bias is approved without native verification, equilibrium and physical justification**. The static IS initial cases serve as a compulsory gate, but their exact transfer into every dynamic direction is a model-specific technical design decision, not prescribed by NBC §§8.1.1.3/9.3.1.3.

## 3. Deterministic engineering preflight

A case may start as `NBC105_EQ_PDELTA` **only if**:
1. The project-source EDB SHA256, assembled model SHA256, input weight and ULS/SLS modifier family are verified; no ETABS versus OpenSees source mismatch.
2. Four native `EQ_PD_INIT_{X+,X-,Y+,Y-}` results exist, complete and finite with same source identity, recorded NBC EL coefficient and signed unit actions, reactions, load ratios and P-Delta solver status. Wind variants only when actually required by the project.
3. State transfer policy is signed, initial equilibrium and tangent stiffness are examined; **static lateral load + dynamic acceleration are not accidentally double counted**.
4. NBC §5.2 gravity and mass are independently built, sourced and retained in the dynamic solver; initial combinations are not incorrectly relabelled as seismic-weight or sustained-gravity combinations.
5. NBC §8 / §9.3 requirements (paired motions, scaling, durations, time step, torsion/damping, response checks) are preserved; zero-initial branch stays `CONTROL_NOT_NBC_COMPLIANT` if P-Delta disabled.
6. Any missing result, wrong sign, stale hash, failed convergence, nonfinite response, unsupported state restoration or “only initial case solved” status must **fail closed** with `PDELTA_INITIAL_STATE_UNVERIFIED`.

## 4. Existing implementation dependency audit — actual repository, not conjecture

- `components/model/initial_pdelta.py` already creates four new-domain static X±/Y± initial checks. **Critical review:** it presently infers dead/live classification from `cfg['mass_factors']` (including the 0.3/0.6 seismic occupancy fractions), which is **not logically equivalent** to identifying the 1.2D versus 0.5IL classes. Before claims of a compulsory native initial-state PASS, read explicit ETABS load-pattern categories/assignments and check every source item; no silent D/IL classification through seismic mass percentages.
- `components/validation/eq_pdelta_case_contract.py` explicitly recognizes an ETABS two-stage dependency: nonlinear static P-Delta initial case, followed by **linear lateral EQ using initial-case tangent stiffness while excluding initial-case load actions from the dependent response**. This is a *static load-case dependency*; it must not be represented as proof that a nonlinear dynamic solver has restored the same constitutive state. The no-P-Delta native static EQ comparison starts from zero lateral initialization as a **separate** diagnostic case.
- `components/model/eq_pdelta_initial_tangent.py` is a same-domain **one-step static tangent** diagnostic and does not establish a validated ground-motion NLTHA initial state; it already documents that the second-stage EQ increment acts on the converged initial state. Distinguish *incremental static action* from *time-history ground acceleration* and keep transfer approval OPEN.
- `docs/review/CONFIRMED_GRAVITY_TO_EQX_EQY_PDELTA_HANDOFF_20261109.md` is older and describes initial cases as diagnostics. For this adopted project workflow, the **compulsory prerequisite** supersedes that wording; actual case convergence and model equivalence are still unverified.

**Actionability:** Future code changes must first fix explicit gravity load classification and validate the four native initial cases; then prove exactly what is transferred (stiffness only versus full state) into EQ P-Delta static and dynamic modules. Do not change member/earthquake load factors only to make a readiness flag pass.

## 5. OUTPUT and OWNER — do not scatter across module roots

Proposed evidence layout for a future code patch (not a claim that it already exists):
```text
REVIEW_MAIN/
  00_MODEL/
    20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md
RUN_OUTPUT/<source-model-hash>/<limit-state>/
  00_SOURCE/       <edb/model/record hashes, code input provenance>
  01_PDELTA_INITIAL/JSON/   EQ_PD_INIT_X_PLUS.json ... EQ_PD_INIT_Y_MINUS.json
  01_PDELTA_INITIAL/EXCEL/  EQ_PD_INIT_4_CASES_REACTION_AND_STIFFNESS.xlsx
  01_PDELTA_INITIAL/LOGS/   per-axis native steps and solver warnings
  02_EQ_NO_PDELTA_CONTROL/  CSV/ JSON/ EXCEL/ LOGS/
  03_EQ_PDELTA/             CSV/ JSON/ EXCEL/ LOGS/
  04_PAIRED_COMPARISON/     X/Y drift, displacement, member forces, axial-force and stability differences, timestamps
  05_UPLOAD_ZIP/            manifest + safe redacted evidence
```
**Who:** structural researcher generates initial cases; independent structural reviewer checks combination/force derivation and state-transfer policy; computational reviewer tests numerical reproducibility. **When:** after gravity and modal/stiffness acceptance, before linear TH and nonlinear TH; rerun if mesh, load, material or state changes. **Why:** separate verified NBC compliance from diagnostic P-Delta sensitivity.

## 6. Review findings and open decision

| Finding | Status |
|---|---|
| NBC demands P-Delta in elastic and nonlinear TH | **SOURCE VERIFIED**: §§8.1.1.3 / 9.3.1.3 |
| NBC §5.2 gravity required in those methods | **SOURCE VERIFIED**: §§8.1.1.2 / 9.3.1.2 |
| IS initial combination adopted as **compulsory project prerequisite** | **USER DESIGN-BASIS DECISION**: §7.2(d) |
| IS conventional slab modifiers adopted as **required project input** | **USER DESIGN-BASIS DECISION**: Table 5 |
| Verified ±EL initialization can safely be carried into arbitrary ground motions | **NOT ESTABLISHED**; double-counting / carryover audit required |
| 2025 IS amendment's exact effect on §7.2(d) / Table 5 | **UNKNOWN** pending authentic amendment text |
| Native numerical cases, physical tests, transfer scripts and compliance | **NOT RUN / NOT VERIFIED** |

## 7. Source citations

- Government of Nepal / DUDBC, *NBC 105:2025 Seismic Design of Buildings in Nepal*, 2nd revision, sections 3.4, 5.2, 8.1.1.2–8.1.1.3, 9.3.1.2–9.3.1.3, pp. 42 and 45: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
- BIS, *IS 16700:2023 Criteria for Structural Safety of Tall Concrete Buildings*, 1st rev., 2023, §7.2(d), Table 5; see [amendment watch](../../LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md). Base text also available at https://www.rmcmaindia.org/adminpanel/admin/server/upload/1762423704_IS%2016700%20-%202023.pdf
- [Governing NBC/IS code matrix](../../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md)
