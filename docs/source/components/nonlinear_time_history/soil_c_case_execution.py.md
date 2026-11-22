# soil_c_case_execution.py — direct, evidence-bound NLTHA launch

**Owner:** `components/nonlinear_time_history/soil_c_case_execution.py` (Stage 38 CLI facade).
**Status:** Native launch workflow; not a material model or independent nonlinear solver.
**Units:** Input matched Acc(g), modeled acceleration conversion 9.81 m/s² per g; time seconds; forces kN, lengths m.

## Inputs and behavior
- Existing Stage 36 JSON for an actual M0–M6 export folder and verified matched Soil-C A/B pair; no geometry is constructed here.
- Validates NBC 105:2025 Soil-C configuration using `soil_c_physics_preflight.audit_soil_c_analysis_config` and both waveform SHA256 using `soil_c_nltha_suite.verify_runner_pair`. Gorkha original/matched provenance and Loma one-sample endpoint remain explicit reviewer gates.
- Rejects new output within source and refuses all existing output folders; normalizes absolute paths; persists frozen input config.
- **Default:** preflight only, no writes. **With --run:** uses the existing `building_exploratory` implementation in an independent Python process. Child source/solver output and traceback go to the local case directory; no original EDB, workbook, source seismic record or mesh is modified.
- The original solver alone constructs gravity-preloaded nonlinear domains, records response and writes `XY/Case_Summary.json` and `YX/Case_Summary.json`. A successful process return is insufficient: the facade reads both completion gates before classifying full duration.
- Every case has `Execution_Status.json`, `Executed_RunConfig.json` and `Native_NLTHA_Console.log` (the last when the real child launcher starts). `engineering_accepted` is always false; source, numerical, code, modal, damping and experimental acceptance are separate.
- Diagnostic matrix jobs require `--allow-research-diagnostic`. Thesis intent requires explicit source evidence and is still blocked by the downstream `check_project_material_qualification` and physical readiness tests.

## Scientific and governing basis
- R01: Kolozvari et al. (2015), PEER 2015/12: component cyclic shear/flexure benchmark evidence, not transferable numerical reinforcement.
- R02: Kolozvari, Lopez and Massone (2023), DOI 10.1016/j.engstruct.2023.116700: E-SFI-MVLEM-3D formulation and model suitability checks.
- R10: DUDBC NBC 105:2025 §§5.2, 9.3.1–9.3.3: governing seismic loading, nonlinear material/geometry and paired-history assessment.
- NIST GCR 17-917-46v1 (2017), DOI 10.6028/NIST.GCR.17-917-46v1: independent modeling, motion, integration, and quality considerations.

**No thesis acceptance from synthetic tests.** Current 32-foundation/44-mesh connectivity and X-wall nonfinite 0.005-s issue are unresolved until native source-reconciled runs. The module introduces no solver tolerance, damping, material card or accepted performance threshold.

## Regression contract
`python -m unittest tests.test_soil_c_direct_execution` exercises input, output-isolation, pair-SHA handoff, incomplete orientation, two full-duration software screens, and nonzero child return using a fake launcher. A fake process is NOT OpenSees numerical verification.
