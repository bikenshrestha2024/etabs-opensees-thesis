# 2026-11-22 — Three-pass existing-model NLTHA integration audit

**Purpose:** verify that the first existing-model nonlinear time-history run is both technically runnable and accurately reported. **Current engineering result:** NO COMPLETE NATIVE 25-STOREY RECORD PROVEN. This is a checked source/software path with pending native solver/model inputs; it is not engineering acceptance.

**Read-first:** `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/ENGINEERING_GATES.md`. Baseline `main=4a763af48f871ea4d7793b00075fd2b3d5d3440d`, PR #156 on `fix/nltha-stage38-integration-check-20261122`. All file edits routed via the connected GitHub integration. Full native source model, EDB and 16 matched horizontal records are not available within this ChatGPT execution environment; OpenSeesPy/XARA are not installed here.

## Pass 1 — Code data flow, preserved source and terminal conditions

`38_DIRECT_EXISTING_NLTHA.py` is ONLY a root alias to `components/nonlinear_time_history/direct_existing_model.py::main`; `tools/run_existing_nltha.py` is a compatible alternate CLI entry point calling the SAME function. There is one backend: `building_exploratory.py::run`. No new physical model builder. Sequence:

1. Explicit model folder plus real matched horizontal A/B files; six SHA-verified export files and the original 32 physical source support tags. Original model/config byte SHA and section property lookup. Preflight has no solver execution.
2. Exact registered Soil-C matched waveforms verified by SHA256, original A then B (not renamed based on global axis), no added spectral scale. Loma Prieta/Gorkha require existing source-policy review. The original SeismoMatch 0.33–3 scaling logs, fit-window and actual two-component selection remain independent gates.
3. Isolated source byte copy including `OpenSees_Element_Connectivity.json`; source cannot be overwritten. Original ETABS section names and 12m X-wall opening geometry remain the declared source intent; per-model original geometry/EDB SHA still needs native comparison.
4. Build fresh source nonlinear domain, apply as-configured gravity and verify 32 actual model reaction joints (44 other points are shear-wall mesh transfer, NOT 44 foundations); modes, Rayleigh damping and XY/YX UniformExcitation; native time integration and accepted-step recorders.
5. Stage full only if *both* saved `XY/` and `YX/` histories have full-duration gates, finite numeric channels, strictly monotone accepted times, original end time, correct count and source SHA identity. Verify saved `OpenSees_Bidirectional_Input_Commands.json` in each direction for actual global DOF1/DOF2, A/B rotation, model-requested file paths, `Path '-factor'` in model m/s² (g converted once), matching sampled dt and pair factor.
6. Preserve original native `First_Step_Failure_Evidence.json`, `FAILED.json` and `INCOMPLETE.json` on failure; use a new empty output directory every rerun. Success status stays `EXPLORATORY_FULL_DURATION_NUMERICAL_SCREEN` and explicit thesis-design/material acceptance is FALSE.

**Software test evidence:**
- Stage38 missing canonical navigation: test-only `dbfa2789`, GitHub Actions run `45024194664`, RED with **4 expected failures** (root alias, inventory, registry, indices).
- Actual XY/YX UniformExcitation command provenance: test-only `1cc559bd`, GitHub Actions run `45024435547`, RED with **4 expected failures** (manifest absent, YX mistakenly identical to XY, source path substituted, factor changed from g once).
- On the fix branch, `tests/test_nltha_stage38_navigation.py` and `tests/test_nltha_full_duration_result_verification.py` are required, together with FULL repository pytest, static inventory/navigation and data boundary jobs. Final head CI is reported separately and must be green before merge.

## Pass 2 — Physics and literature applicability

**Literature R01:** Kolozvari, Orakcal & Wallace (2015), PEER Report 2015/12, `https://peer.berkeley.edu/publications/2015-12`; the actual paper's web-panel ConcreteCM + SteelMPF + FSAM parameters may be used as **research transferred specimen cards**, never as the as-built M45 concrete or verified actual Fe500 confinement / bar schedule.

**Literature R02:** Kolozvari, López & Massone (2023), *Efficient three-dimensional shear-flexure interaction model for reinforced concrete walls*, Engineering Structures 294, 116700, `https://doi.org/10.1016/j.engstruct.2023.116700`. Official author/command documentation `https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html`: 4-node/24-DOF E-SFI_MVLEM_3D, m FSAM macrofibers with `-thick`/`-width`/`-mat` and optional `-CoR`/`-ThickMod`/`-Poisson`/`-Density`. Building builder syntax is consistent with documented mandatory syntax; parameter transfer, local panel response, mesh refinement and connected 3D forces remain separate validations.

**Response-history and earthquake sources:** official OpenSees UniformExcitation `https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html`; Nepal NBC 105:2025 `https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf`, particularly §§5.2,9.3; NIST GCR 17-917-46v1 (2017) `https://nvlpubs.nist.gov/nistpubs/gcr/2017/NIST.GCR.17-917-46v1.pdf` for nonlinear modeling/response-history research considerations. Any specific NBC threshold must be traced to its applicable clause and independently validated; these citations alone certify no output.

**Blocking physical qualifications:** unresolved historical first real X-motion step at t≈0.005 s with postfailed force clues at solver tags 110280/112778 (source areas 354/482), no demonstrated initiating FSAM/ConcreteCM/SteelMPF fault; 32-support ETABS/OpenSees pointwise shear-wall reaction transfer mismatch; unsupplied project wall/web/boundary/column/beam reinforcement and validation; source M0–M6 variant identification absent from archived `OpenSees_Complete_Model_Config_V118.json`; actual gravity vs seismic mass, damping modes, PDelta initial combinations, original SeismoMatch source logs, vertical acceleration §4.3 applicability, FVD/BRB test cards and response drift/IO–LS–CP, model timestep and energy checks are NOT ACCEPTED.

**Do not mark M0 just because the CLI's `--variant-id` says M0.** The archived source model config lacks a verified physical variant identifier. Use `--variant-id UNVERIFIED` for a diagnostic until a source-EDB/override device-and-outrigger fingerprint establishes a specific M0–M6 state.

## Pass 3 — Navigation, ownership, test gates and evidence organization

- `components/nonlinear_time_history/direct_existing_model.py` is the sole direct existing-source orchestration owner; `building_exploratory.py` is the native nonlinear solver. No rival solver, second model conversion or duplicate engine from closed PR #154 is installed.
- Stage 38 is exposed by thin root `38_DIRECT_EXISTING_NLTHA.py`; synchronized with `tools/audit_active_repository.py::CANONICAL`, `docs/programs/00_PROGRAM_INDEX.md`, `launchers/README.md`, `engineering/registry/CANONICAL_MODULES.csv`, and package README.
- Root shell-specific and study papers in `docs/programs/38_DIRECT_EXISTING_MODEL_NLTHA.md`, per-source guide in `docs/source/components/nonlinear_time_history/direct_existing_model.py.md`; test files under `tests/`; issues and historical failures under `REVIEW_MAIN/06_NONLINEAR_TH/`.
- Local solver results belong in one new `07_NONLINEAR_TIME_HISTORY/<event>/<limit_state>/<unambiguous run id>/` directory, within isolated `XY/` and `YX/` case outputs, never as random repository root JSON or workbook files. Do not upload the user-owned private native EDB, model JSON or waveform bytes as a CI convenience.

## Acceptance state

| Gate | Status |
|---|---|
| Current-source Python and test integration | Must show final exact-head CI and relevant output tests |
| Native OpenSees installed and input A/B present locally | NOT AVAILABLE IN THIS SESSION |
| ONE full real M0–M6 source-specific 25-storey XY/YX earthquake pair | NOT VERIFIED |
| X-wall first-step nonlinear material/element cause corrected | NOT VERIFIED |
| ETABS/OpenSees 32-support pointwise reaction equality | NOT VERIFIED |
| Actual RC, FVD, BRB materials and original SeismoMatch matching evidence | NOT VERIFIED |
| NBC105:2025 whole-code model and response-history approval | NOT VERIFIED |

**Required engineering next action:** with the exact private export and source-registered real matched Kobe A/B files on the user's Windows OpenSeesPy installation, run Stage 38 in a new directory. If the first step fails, preserve ZERO/X/Y/XY new-domain diagnostic and material element snapshots; do not tune reinforcement strengths or alter real geometry merely to force convergence. Only source-attested full XY/YX evidence followed by code/physics checks can advance the status.
