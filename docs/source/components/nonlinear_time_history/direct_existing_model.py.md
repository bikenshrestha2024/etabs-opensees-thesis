# Existing-model direct NLTHA — input validation, local execution and outcomes

**Source:** [direct_existing_model.py](../../../../components/nonlinear_time_history/direct_existing_model.py); root CLI [tools/run_existing_nltha.py](../../../../tools/run_existing_nltha.py). Full [Stage 38 runbook](../../../programs/38_DIRECT_EXISTING_MODEL_NLTHA.md).

## Direct run entry points

- `make_research_nltha_config(...)` fixes `nonlinear_walls=True`, `PHYSICAL_32`, both `XY`/`YX`, exact existing geometry, `PEER_2015_12_SINGLE_SOURCE` baseline, source scale=1.0, full record by default, research intent (not a fake `THESIS_NLTHA`). It uses `PEER_APPENDIX_EXACT` SteelMPF transition, which converts the paper's absolute `a1=18.5` to `cR1=18.5/20=0.925` per OpenSees law rather than the unstable literal 18.5 parameter (see `research_building_materials.py`).
- `preflight_existing_model(config)` requires original source V118 metadata, source topology, model/config SHA match, exact source frame mapping, distinct local ground acceleration file bytes, 32 source physical support tags and no source assembly errors. Returns a local-only section/provenance ledger. It does not run the native solver or verify accelerogram spectral processing.
- `run_existing_model_nltha(config, check_only=False)` creates per-case JSON status and paper section audit locally; imports OpenSeesPy and launches existing `building_exploratory.run`. Only returns full exploratory numerical screen if **both** XY/YX have complete solver status. A short record is a diagnostic and exceptions write `NATIVE_NLTHA_INCOMPLETE`, not successful fake drifts.
- `main(argv=None)` handles the one-file Spyder/Windows CLI. No additional new source model family, ETABS converter or M0–M6 paper values created.

**Inputs/outputs:** local kN–m–s/OpenSees time series, two horizontal matched accelerograms, 3D nonlinear M0–M6-variant source identity, exact model/material SHA and separate output root. Relevant NBC 105:2025 §9.3.1/9.3.2 and R01/R02; model reinforcements, native P-Delta static initialization, 32 reaction transfer, calibration, all 224 records remain outside automatic numerical acceptance.

**Unit tests:** `tests/test_direct_existing_nltha_20261122.py` for nonlinear-wall XY/YX defaults, full/truncated intent, source hashes, missing motion and unknown section failures. Native Windows test requires actual model+waveform source files and OpenSeesPy/XARA available; CI's syntax/import tests cannot substitute for that.
