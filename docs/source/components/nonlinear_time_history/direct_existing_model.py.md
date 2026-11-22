# Existing-model direct NLTHA — input validation, local execution and outcomes

**Source:** [direct_existing_model.py](../../../../components/nonlinear_time_history/direct_existing_model.py); root CLI [tools/run_existing_nltha.py](../../../../tools/run_existing_nltha.py). Full [Stage 38 runbook](../../../programs/38_DIRECT_EXISTING_MODEL_NLTHA.md).

## Direct run entry points

- `make_research_nltha_config(...)` fixes `nonlinear_walls=True`, `PHYSICAL_32`, both `XY`/`YX`, exact existing geometry, `PEER_2015_12_SINGLE_SOURCE` baseline, source scale=1.0, full record by default, research intent (not a fake `THESIS_NLTHA`). It uses `PEER_APPENDIX_EXACT` SteelMPF transition, which converts the paper's absolute `a1=18.5` to `cR1=18.5/20=0.925` per OpenSees law rather than the unstable literal 18.5 parameter (see `research_building_materials.py`).
- `preflight_existing_model(config)` requires original source V118 metadata, source topology, model/config SHA match, exact source frame mapping, distinct local ground acceleration file bytes, 32 source physical support tags and no source assembly errors. Returns a local-only section/provenance ledger. It does not run the native solver or verify accelerogram spectral processing.
- `run_existing_model_nltha(config, check_only=False)` creates per-case JSON status and paper section audit locally; imports OpenSeesPy and launches existing `building_exploratory.run`. Only returns full exploratory numerical screen if **both** XY/YX have complete solver status. A short record is a diagnostic and exceptions write `NATIVE_NLTHA_INCOMPLETE`, not successful fake drifts.
- `main(argv=None)` handles the one-file Spyder/Windows CLI. No additional new source model family, ETABS converter or M0–M6 paper values created.

**Inputs/outputs:** local kN–m–s/OpenSees time series, two horizontal matched accelerograms, 3D nonlinear M0–M6-variant source identity, exact model/material SHA and separate output root. Relevant NBC 105:2025 §9.3.1/9.3.2 and R01/R02; model reinforcements, native P-Delta static initialization, 32 reaction transfer, calibration, all 224 records remain outside automatic numerical acceptance.

**Unit tests:** `tests/test_direct_existing_nltha_20261122.py` for nonlinear-wall XY/YX defaults, full/truncated intent, source hashes, missing motion and unknown section failures. Native Windows test requires actual model+waveform source files and OpenSeesPy/XARA available; CI's syntax/import tests cannot substitute for that.

## 2026-11-22 — strict first-completed-case acceptance screen

The direct native executor now calls `verify_full_duration_pair_outputs(output_dir,config,cases)` **only when its underlying OpenSees runner reports two exploratory full records**. It requires two real on-disk `XY/` and `YX/` histories (`Building_Nonlinear_history.csv`), saved `Case_Summary.json`, and `Accepted_History_Completion_Gate.json`. Every history numeric channel and accepted time is streamed and checked for finiteness, strictly increasing times, exact recorded step count and final physical time. The two case summaries must identify the same 64-hex model and paired-input SHA, original event/variant/state and bidirectional excitation; their on-disk evidence must agree with the returned solver case. It then additionally compares the case model SHA to the source model byte hash collected at preflight.

`DIRECT_EXISTING_NLTHA_STATUS.json` includes byte hashes of both histories, saved completion gates and per-case summaries under `independently_checked_case_histories`. The status remains **`EXPLORATORY_FULL_DURATION_NUMERICAL_SCREEN`**, which explicitly does not certify project detailing, materials, source reactions or NBC compliance. A successful solver return without the files/gates now results in `NATIVE_NLTHA_INCOMPLETE`. An existing nonempty output directory is rejected **before** any status/config file can overwrite a prior run.

**Regression:** `tests/test_nltha_full_duration_result_verification.py`; tests are synthetic file metadata, not the full native building. Verified on connected GitHub's headless pytest for commit `72fff02649dc87cf035dea9482187b8489033670` before output collision guard, with final-head verification separately required.
