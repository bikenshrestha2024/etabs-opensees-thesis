# soil_c_nltha_suite.py — detailed per-module documentation

**Source code:** [soil_c_nltha_suite.py](../../../../components/nonlinear_time_history/soil_c_nltha_suite.py)

**Role:** Strict read-only eight-pair Soil C source preflight and independent XY/YX/ULS setup. **Does not run the OpenSees model** or approve the ETABS geometry/materials; source input validation is independent of calibrated nonlinear model acceptance.

**Inputs:** Local matched-source directory, registered 16 source filenames + exact SHA-256, dt, PGA and end time in `matched_component_register.csv`. Optional current independently validated modal periods `t1_x_s,t1_y_s,tn90_x_s,tn90_y_s` and proposed analysis dt. `verify_runner_pair` binds a particular X/Y pair to the source register and requires explicit Gorkha/Loma review flags.

**Parameters:** Soil `C`, RC dual wall system `R_mu=3.5,Omega_u=1.4,Z=.35,I=1.0` from the user workbook/code target. Soil C `Ta=.1,Tc=1,Td=4,alpha=2.5`, fitting period `[.05,6]s`, input unit `g`, additional spectral factor `1.0`, conversion to `m/s²` `9.80665`.

**Functions:**
- `register_rows`: exact sixteen manifest rows; unique A/B keys; path and digest restrictions.
- `audit_suite`: source hashes and metadata; 8 pair identities, expected timing; optional actual modal-based dt/period screen. Missing inputs are **UNKNOWN**, not PASS.
- `verify_runner_pair`: SHA mapping to real input without reliance on download suffix and explicit review gate.
- `reconcile_loma_runtime_pair`: strictly one zero sample **only in the shorter runtime array** when opted-in with reviewer; does not alter original waveform file.
- `write_suite_report`: JSON evidence export.

**Output/exit:** `35_SOIL_C_NLTHA_PREFLIGHT.py` writes JSON for all eight pairs; exit code `2` if files do not match and `3` if source timing remains unresolved. The existing exploratory runner writes `Soil_C_Matched_Source_Gate.json` for one case.

**Code clauses:** NBC 105:2025 §§4.1, 4.3, 9.3.1–9.3.3 and Table 5-2. The source files are not sufficient to approve the original SeismoMatch initial 0.33–3 factors nor lower common scale: require session logs. See [full Stage 35 guide](../../../programs/35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md).

**Tests:** `tests/verify_soil_c_nltha_suite.py` (stdlib synthetic source checks, source hash, date/event, period-window, endpoint policy). GitHub CI executes these checks but does NOT simulate nonlinear building response.
