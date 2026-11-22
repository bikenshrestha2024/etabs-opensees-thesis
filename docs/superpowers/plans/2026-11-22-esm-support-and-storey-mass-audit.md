# ESM export, cross-module foundation profiles and floor seismic mass — implementation plan

> **For agentic workers:** Use Superpowers systematic-debugging, test-driven-development and verification-before-completion. All code changes must have a reproducible failing test first.

**Goal:** Enable default 32 physical foundation-support selection in all OpenSees build paths; offer 76 and 97 as explicit sensitivity variants; fix ESM combined Excel+ZIP discovery without fabricating missing calculation data; audit and optionally assemble NBC-consistent floor-level seismic mass while retaining independent ETABS verification.

**Architecture:** One shared support-profile resolver at the model construction boundary, inherited by all ESM, Rayleigh, modal, MRSM and time-history analyses. Avoid treating 44 shear-wall mesh points as independent physical foundations. Keep optional 97 wall-base extension explicitly diagnostic. ESM combined exporter reads exact state/model-matched calculation sources and can create a **manifest-only** combined workbook if calculations genuinely are missing. A separate floor mass auditor reconciles model nodal weights and source 25-floor CSV while reporting actual solver-mass disposition and source COM/inertia, without secretly changing physics.

**Tech stack:** Python 3.12/OpenSeesPy, tkinter, standard-library CSV/JSON/ZIP, existing project tests, GitHub Actions. Existing spreadsheet writer is unchanged unless needed; uploads stay private.

**Preflight (2026-11-22):** Read AGENTS.md, engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md, .agents/skills/etabs-opensees-read-first/SKILL.md, ENGINEERING_GATES.md; current repo main as branch base; local Windows EDB SHA unavailable; attached two seismic review ZIPs and reaction CSV inspected. Source 32 physical joints + 44 wall mesh points; 76-restraint case gives sum reaction 286419.758231 kN, of which 94063.603041 kN is on the 44 mesh points. Gravity full benchmark must remain 1D+1L; current mass/preload case 1D+0.3L is a different purpose.

## Task 1: Combined ESM output discovery and evidence integrity

**Files:** components/equivalent_static/organized_exports.py, tests/test_esm_combined_case_discovery.py.
- [ ] RED: root has 8 completed saved responses and calculations in source-case 03_ESM/RUNS/ULS/..., fails because _data_rows searches only output_root.
- [ ] GREEN: discover calculations ONLY under exact source-export case name and matching state; verify case result metadata, preserve immutable copy provenance; do not mix older cases.
- [ ] RED: legacy output has eight status rows but no calculation JSON anywhere; combined export should create a clearly marked `MISSING_CALCULATION_JSON` evidence workbook and ZIP instead of raising after building a partial snapshot. No fabricated T, V, Fi or code acceptance.
- [ ] GREEN: manifest-only workbook with status, sources, missing-data reason, provenance and next steps; preserve solver states as reported.
- [ ] Verify: unit tests and full repository CI; retain existing output layout.

## Task 2: Shared 32/76/97 foundation-case selectors

**Files:** components/model/assembly.py, new components/model/support_case_contract.py (if required), selected ESM/modal/MRSM/history GUI callers, tests/test_cross_module_support_profiles.py.
- [ ] RED: default model build uses 32 exact physical support tags rather than all 76 original source restraint IDs, without declaring 44 mesh points new foundations. Fail closed for missing expected tags or unexpected non-matching model source.
- [ ] GREEN: one consistent profile definition `PHYSICAL_32` (default), `SOURCE_76` (diagnostic original assignments), `WALL_BASE_97` (diagnostic source-verified extension, don't invent fixities); always record effective selected profile, exact restrained tags/count and source model/config provenance.
- [ ] Preserve legacy gravity-GUI strategy input and result identity, emit explicit warning for unresolved 44-point native shell-edge/MPC force transfer.
- [ ] Make shared selection accessible in main and specific GUI paths, ensure subprocess environment/CLI propagation; no old GUI duplicate defaults.
- [ ] Verify: tests against baseline 76 source map and empty/missing support metadata, and native full-building tests remain unverified.

## Task 3: Lumped mass and NBC §5.1/§5.2 period audit

**Files:** components/modal/rayleigh_mass_audit.py and existing associated numerical owner, tests/test_story_lumped_mass_contract.py.
- [ ] RED: 25 floor source weights must equal aggregated free horizontal nodal mass under NBC Table5-1, with absolute elevation, mass-centre offsets, polar inertia and intermediate-wall-node shift explicitly reported.
- [ ] GREEN: retain source distributed solver mass by default; only enable a physically different story-lumped case via explicit validated setting that moves horizontal mass to correct floor COM and conserves total/first moments/rotational inertia with a separately recorded stiffness/mass operator fingerprint.
- [ ] Enforce canonical NBC §5.1.1 Rayleigh Wi-Fi-di and empirical `0.075 H^0.75 /sqrt(Aw)`, adopted `min(T_R,1.25 T_emp)`; no reuse of older 6 m X-wall geometry, mixed source, or ETABS eigenperiod as Rayleigh.
- [ ] Verify against attached base ledger: active W=284691.556185 kN, 25 stories, 1571 off-floor active mass nodes, intermediate W=13841.211760 kN; native ETABS equivalence still open.

## Engineering acceptance limits
- All static/unit tests and even clean modal mass >90% are **not** native 25-storey model equivalence.
- 32 real supports; 44 other original source points require actual wall edge/MPC transfer — no artificial spring/fix invented. 76 and 97 are sensitivity only.
- Historical `LEGACY_GROSS_SHELL` vs ETABS-elastic rebuilt 768.045 kN joint discrepancy remains outstanding.
- ESM high-rise §3.2.1 remains comparison-only; Vs30 >40m remains unverified; missing E− cases remain partial.
- Source ZIP reveals two distinct 25-floor ledgers with dead load difference 8652.444352 kN; hash must pin each numerical run.

## Completion contract
Post source-level evidence report, tests with exact conclusions, review PR; merge only after CI verified, no source data/EDB uploaded. If a task cannot be implemented safely, leave code unchanged and document the precise blocker rather than claiming completion.
