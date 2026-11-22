# 2026-11-22 — Priority P0: exactly one complete existing-building NLTHA case

**Editor actually used:** ChatGPT GPT-6, via the connected GitHub tool (not Codex/Claude). **Base main:** `80f96b323e7d7c3c5400ab77d08a60c006f26fe3`. **Working branch:** `fix/nltha-physical-32-source-staging-20261122`; **PR:** #155. **Native Windows OpenSeesPy:** NOT AVAILABLE IN THIS SESSION. **Actual model EDB/JSON and matched waveform bytes for the current live source:** NOT AVAILABLE HERE, hence no genuine 25-storey full-record transient was executed. No claim that first-step wall nonconvergence was solved.

## Preflight sources and physics

Read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/CORE_RULES.md`, `ENGINEERING_GATES.md`, Stage 38 source/guide, current `building_exploratory.py`, `source_model_handoff.py`, `direct_existing_model.py`, `runner_and_gui.py`, and X-wall 0.005 s diagnostic evidence. The active 32 foundation joints and 44 analytical shell-mesh transfer points remain distinct; X source wall geometry stays two 12 m walls with real openings; source configs/reinforcement/physical material laws are not changed. Full comparative gravity is 1D+1L, while NBC Table 5-1 seismic mass is separately defined.

The current main already uses `stage_existing_model_sources` to transfer the essential 6 source files including `OpenSees_Element_Connectivity.json`. An older source snapshot had omitted this topology, but that defect was ALREADY FIXED IN MAIN before this branch; **no duplicate source-handoff fix** is claimed.

## Exact new correction and interfaces

- `direct_existing_model.verify_full_duration_pair_outputs(output_dir, config, cases)` checks two independent XY and YX saved full-duration case summaries, independent completion-gate files and every recorded finite numerical history row. Must reach requested record end and matching accepted time/count, identical model/record source SHA, proper XY/YX, expected variant/event/state, and match preflight source model hash.
- Native saved case histories/case summary/gate SHA256 are included in `DIRECT_EXISTING_NLTHA_STATUS.json.independently_checked_case_histories`. Failure leaves `NATIVE_NLTHA_INCOMPLETE` rather than a false positive.
- Reject reusing nonempty output folders before any prior success or failure evidence is overwritten.
- Default direct research case `soil_c_primary_nltha=True`. Preflight now verifies registered exact Soil-C pair waveform SHA and original A/B order before expensive model load; preserves explicit Gorkha/Loma review guards. Registered source identity is not original SeismoMatch session validation.

**No changes:** FE mesh, 32 foundation supports/44 shell transfer, RC member materials, E-SFI/FSAM properties, FVD/BRB, gravity loads, source accelerograms, EDB, stiffness, modal periods, time-step integrator, Newton fallback, P-Delta cases, damping or IO/LS/CP demand limits.

## Test-first evidence

- First test commit `87be5868` targeted missing full-duration verifier; GitHub Actions headless pytest failed as expected.
- Implementation commit `72fff026`: exact-head suite CI `45022694520` **passed** with five accompanying static/disclosure workflows passing.
- Test-only commit `233d529f`: CI `45022875419` **failed specifically** because a previous nonempty output folder could be reused; code fix `05c86f0` added file-existence gate.
- Test-only commit `286f7aa6`: required default registered Soil-C config; code fix `1648bedd` activated exact A/B SHA preflight.
- Require final-head full CI before merging or marking software complete.

## Native first-complete-case acceptance (STILL OPEN)

Run source-specific **M0/Kobe/ULS** using BOTH fresh-domain XY and YX full original matched components on the user's own Windows OpenSeesPy environment, with no source file upload. Preserve exact executable SHA and motion/model hashes, nonzero finite accepted steps from t=0 to source record end, complete native log, meaningful physical demands, no unresolved E-SFI constitutive failure and numerical dt/energy refinement. The same-source 32-support ETABS/OpenSees pointwise gravity residual and source M45/steel/boundary reinforcement calibration are separate required model/code gates; passing software history checks alone does NOT complete thesis engineering acceptance.

Scientific authorities: Nepal NBC 105:2025 §§5.2, 9.3.1–9.3.3; NIST GCR 17-917-46v1 (2017); Kolozvari, Orakcal and Wallace PEER 2015/12; Kolozvari, Lopez and Massone, Engineering Structures 294 (2023) 116700; OpenSees E-SFI-MVLEM-3D element and UniformExcitation official guides.
