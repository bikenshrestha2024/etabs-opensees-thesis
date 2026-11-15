# Source guide — tools/audit_soil_c_case_completion.py

Scope: **read-only** evidence inventory for the 112 planned model-variant/state/earthquake groups and 224 XY/YX orientation results. It does not execute OpenSees, produce earthquake records, validate native wall materials or determine an optimal outrigger design.

## V23 full-record provenance and time checks

For each orientation case, `Case_Summary.json` must identify variant M0–M6, ULS/SLS, exact source pair, XY/YX orientation and `diagnostic_excitation=XY` (paired components). Both `record_sha256` and `model_sha256` must contain exactly 64 hexadecimal characters; their syntactic validity is **not** verification against source file bytes. Response summary fields must contain finite numerical peak roof displacement, drift, base shear and torsional rotation.

`Accepted_History_Completion_Gate.json` must explicitly report `FULL_DURATION_NUMERIC_SCREEN`, `full_record_completed=true`, `accepted_channels_finite=true`, at least two accepted states, and finite positive `full_record_duration_s`, `requested_duration_s` and `achieved_time_s` all matching within 1e-7 seconds. A 0.1-second diagnostic with a 45.29-second source record cannot be marked complete simply by setting a boolean. Missing or inconsistent metadata yields `INCOMPLETE` rather than `RESEARCH_ONLY_FULL_RECORD`. Invalid, failed or truncated orientation cases never count toward 224 completions.

**Still required:** independently compute source file hashes, preserve both paired records and orientation, verify a complete accepted numeric history against the raw trace, confirm native ETABS/OpenSees model provenance, qualify project-specific nonlinear wall/frame/device behavior, compare time-step convergence and engineering drift/damage acceptance. A research-only full-record screen is not proof of NBC 105:2025 compliance.

## Reproduction

```powershell
python tests/verify_soil_c_case_completion.py
python tools/audit_soil_c_case_completion.py --matrix "<LOCAL_RUN_MATRIX.csv>" --output "<LOCAL_EXPORT>/07_NONLINEAR_TIME_HISTORY/06_REVIEW/Soil_C_224_Completion_Audit.json"
```

Output must be a new destination (the command refuses overwrite). Keep private project file paths and actual response records out of public GitHub. Source of truth: `36_SOIL_C_NLTHA_RUN_MATRIX.py`, `components/nonlinear_time_history/full_record_gate.py` and `REVIEW_MAIN/06_NONLINEAR_TH`.
