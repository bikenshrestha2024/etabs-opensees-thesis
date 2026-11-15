# V23 — 224 planned Soil-C orientation completion-screen hardening
**Date:** 2026-11-15  
**Status:** RESEARCH_SCREEN_HARDENED / FULL_THESIS_NLTHA_NOT_EXECUTED_OR_VERIFIED

## Real code defect

The previous `tools/audit_soil_c_case_completion.py::inspect_case` accepted a 64-character **nonhexadecimal** string as SHA256 and allowed `RESEARCH_ONLY_FULL_RECORD` with only a boolean `full_record_completed`, a `FULL_DURATION_NUMERIC_SCREEN` status string and finite summary metrics. A 0.1 s exploratory trace could be mislabeled as an entire 45.29 s source if the gate lacked measured timing fields.

V23 now requires syntactically valid 64-hex digests for both model and record, positive finite `full_record_duration_s`, `requested_duration_s`, `achieved_time_s` that coincide within 1e-7 seconds, and at least two accepted states. Mismatches become `INCOMPLETE` rather than full research records. Both record and model *bytes* must still be independently hashed and compared: valid-looking strings are not source verification.

Regression tests: `tests/verify_soil_c_case_completion.py`, including false full-duration and nonhex motion evidence.

## Required native execution and evaluation

The planned matrix is 7 M0–M6 model configurations × 2 limit states × 8 Soil-C earthquake pairs × 2 XY/YX orientations = 224 individual orientation analyses. Cases with `RESEARCH_ONLY_FULL_RECORD` are **not** calibrated research/engineering acceptance until independently verified. Before recording any thesis result, verify the historical first X-wall ~0.005 s localForce issue through fresh-domain zero/X/Y, 1-quad, connected one-bay and building trials; real web/boundary confinement and source reinforcement; correct frame and E-SFI material units; gravity P-Delta and wall-base conditions; time-step refinement; actual paired raw-record SHA, Gorkha/Loma Prieta duration policy, and complete full-time traces.

Files to collect in each case under `07_NONLINEAR_TIME_HISTORY/RUNS/<STATE>/<CASE>/<RUN_ID>/`: input and record hashes, material source and calibration, native stdout/stderr, last accepted response, failure snapshot, accepted-history CSV, completion gate JSON, drift/shear/torsion/device metrics, period/damping preflight, comparison evidence and ZIP. A missing/failed case must not enter a completed optimum.

### Local inspection

```powershell
python tests/verify_soil_c_case_completion.py
python tools/audit_soil_c_case_completion.py --matrix "<PRIVATE_MATRIX.csv>" --output "<LOCAL_EXPORT>/09_SOFTWARE_DIAGNOSTICS/Soil_C_224_Audit.json"
```

No private model or earthquake records should be published on the public GitHub repo.
