# NBC 105:2025 source module and native model acceptance checkpoint

**Basis:** user-uploaded official NBC 105:2025 Second Revision, all ten printed main clauses. The source was re-read for clauses 3, 5–10 and Table 10-1; project model EDB and private records were NOT executed or committed.

**Branch:** `feat/nbc105-clauses-02-03-06-10-source-verified-20261121` (PR #130); all code changes remain outside `main` until the full acceptance gates pass.

| Clause | Canonical module | Source-oriented coverage | Outstanding acceptance |
|---|---|---|---|
| 1 | `clause_01_scope_definitions.py` | Existing scope and definitions | Full source/parity and case suitability |
| 2 | `clause_02_general_principles.py` | ULS/SLS, stability/evacuation declarations | Concrete performance, capacity design, SSI |
| 3 | `clause_03_scope_of_analysis.py` | ESM applicability, Table 3-1, LSM/WSM and 30% nonparallel load combos, vertical seismic, bearing upper bound | Complete 3D load-case integration; native stiffness/load combinations |
| 4 | `clause_04_seismic_hazard.py` | Existing spectra, soil and importance references | Vs30, Kirtipur site tests, Annex C |
| 5 | `clause_05_dynamic_characteristics.py` | Rayleigh/empirical, mid-height seismic weight, Table 5-2 rows 1–21, weak/soft/torsion/reentrant/drifts/gap/eccentricity | Exact native centre-of-mass displacement, member coupling, all irregularity evidence |
| 6 | `clause_06_equivalent_static.py` | C_d ULS/SLS, V, k and F_i, Table 6-1; active ESM numerical paths now routed | Full 25-storey direction/±5% and drift parity |
| 7 | `clause_07_modal_response_spectrum.py` | Modal participation/effective load, signed floor force, SRSS and force-only scaling | True CQC/close-mode aggregation, >33 Hz missing mass, mode-shape review |
| 8 | `clause_08_elastic_time_history.py` | 3D/initial state/damping requirements, records selection rule and member-action divisor | Ground-motion input/native XY/YX time histories; exactly-seven-record ambiguity |
| 9 | `clause_09_nonlinear_analysis.py` | Both-sign pushover, 3D hysteresis prerequisites, scale bound, time step and XY/YX count | N2 target solution, element 110280 first-step convergence, all 224 actual runs |
| 10 | `clause_10_parts_and_components.py` | Eq 10.3(1), Table 10-1 a_p, Tables 10-2/10-3, scope cutoff, reduced friction/shutdown | Connection capacity, panel/suspension attachment, protected services, actual component inventory |

## Critical engineering implications

1. The supplied ETABS model is approximately 95 m; NBC §3.2.1 printed p.17 does not allow ULS **ESM-only** primary design for a 95 m structure with T>0.5 s. §7.5 nevertheless requires the MRSM base shear to be checked/scaled against an ESM-derived base shear; this does NOT mean the entire structure is approved for ESM-only design.
2. NBC §5.1 printed p.28 demands the lesser of the Rayleigh and 1.25-amplified empirical periods. The V10.7 ETABS Excel report that only uses amplified empirical is NOT a code-complete period check.
3. The 12 m X-direction wall-envelope interpretation from the provided E2K is a geometry claim, not coupled-wall capacity/stiffness verification. Dual-system row 19 of Table 5-2 must not be adopted without qualifying the RC frame's independent 25% resistance requirement (Clause 1 dual-system definition).
4. NBC §7.5 forbids scaling MRSM drifts and displacements. The new Clause 7 reference helper explicitly preserves those channels, but project ETABS scale-factor workflows must still retain unscaled results.
5. For Table 10-1 printed p.50, the period separation `|T1-Tp| = 0.5 s` is not explicitly covered by an equality row, so `ap=1.0` is the continuous interpolation endpoint. This ruling is documented, not silently assumed.
6. NBC §8.1.3 and §9.3.3 literally provide <7 maximum and >7 mean; exactly seven is unspecified. The reference helper currently fails closed for that case pending formal interpretation.
7. Full native ETABS and OpenSees mass/stiffness/support reactions, Rayleigh periods, nonlinear wall convergence and M0–M6 histories remain NOT_VERIFIED. Synthetic tests or CI compilation cannot close any of these gates.

## Required final gates

- Source table/page footnote review completed and linked for every subclause; no missing machine-checkable requirements.
- One canonical rule source, all active caller adapters migrated with before/after numerical parity.
- Static import cycles, output writer migration and semantic review attestation blockers resolved without relaxing the gate.
- Exact source EDB and config hashes, actual ETABS modal/drift/forces and OpenSees reaction files compared.
- Reproducible full real-model histories and nonlinear wall convergence recorded.
- Full headless, native benchmark, source reference and integrated CI green on exact merge SHA.

Until all gates pass, record status as `REFERENCE_MODULES_PRESENT_PRODUCTION_ENGINEERING_VALIDATION_OPEN`, not 'NBC 105 fully implemented/approved'.

## Production routing update (PR #130)

**Source-integrated active numeric adapters:** ESM §3/§6, MRSM §7, linear history §8, nonlinear seismic input §9 and design drift §5. **User-facing operations:** all Clause 1–10 exported functions are accessible through `components.nbc105.dispatch`, local CLI and the existing settings GUI's isolated calculator.

**Acceptance status:** local source-level numerical regression may pass while native engineering acceptance remains blocked. The latest available V10.7 JSON reads `AMPLIFIED_EMPIRICAL_ONLY__NO_ANALYTICAL_PERIOD_CHECK` and `NOT_TESTED__REQUIRES_REACTION_MASS_MODAL_DRIFT_TORSION_COMPARISON`; it cannot certify the code-required lesser-of periods or physical ETABS–OpenSees equivalence. `components.nbc105.acceptance` explicitly rejects the leap from RS target equality to full NBC compliance. First-step X-wall failure, missing 224 full histories and project-wide semantic audit remain open.
