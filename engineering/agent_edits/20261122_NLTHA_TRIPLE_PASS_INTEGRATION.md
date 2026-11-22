# 2026-11-22 — Stage38 triple-pass engineering integration

**Editor:** ChatGPT GPT-6 via installed GitHub connector. **Base:** `4a763af48f871ea4d7793b00075fd2b3d5d3440d`. **Branch:** `fix/nltha-stage38-integration-check-20261122` **PR:** #156. Native ETABS/Windows OpenSeesPy/XARA and actual private waveform/model files **not accessible**; this edit does not imply a physical native run.

Read mandatory project `AGENTS.md`, the 32-foundation/44-wall-mesh source contract, applicable repository read-first skill, CORE_RULES and ENGINEERING_GATES. No physical stiffness, wall material, gravity/live mass, geometry, P-Delta, damping or motion record modified.

- Test-first Stage38 navigation on SHA `dbfa2789`: GitHub Actions 45024194664 correctly reported four missing alias/catalog/index failures.
- Implemented only `38_DIRECT_EXISTING_NLTHA.py` alias to `components/nonlinear_time_history/direct_existing_model.py::main`, registered in canonical index, launcher README, audit inventory and package README. The `tools/run_existing_nltha.py` alternate entry calls the same main.
- Test-first on SHA `1cc559bd`: GitHub Actions 45024435547 correctly reported four missing on-disk XY/YX input-command verification failures.
- Implemented a verifier of `OpenSees_Bidirectional_Input_Commands.json` per case and preserved its SHA in independent success status. Explicit check correct original component/global DOF for each orientation, source paths, dt and g unit factor.
- Documented code/physics/organization findings at `REVIEW_MAIN/06_NONLINEAR_TH/20261122_TRIPLE_PASS_NATIVE_NLTHA_INTEGRATION_AUDIT.md`; updated Stage38 and source guide.
- Current original V118 model config has no verified M0–M6 identity; do not adopt user-provided variant label as a verified physical configuration.

Only final exact-head GitHub CI can establish software tests pass. Native X-wall first-step (Kobe X t≈0.005s), source 32-support pointwise ETABS gravity difference, PEER specimen transfer calibration, and one full building XY/YX record remain unverified.
