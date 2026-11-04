# soil_c_run_matrix.py — per-file source documentation

**Source:** [soil_c_run_matrix.py](../../../../components/nonlinear_time_history/soil_c_run_matrix.py)

**Purpose:** Create a deterministic **config-only** table of M0–M6 × ULS/SLS × eight Soil C matched pairs; 112 configs each with simultaneous XY/YX requested => **224 analysis slots**. This module has no OpenSees imports and NEVER runs a transient analysis.

**Input schema:** `models_json` maps M0..M6 to existing, user-reviewed model export directories; `matched_dir` supplies 16 previously matched `Acc(g)` waveforms with SHA values in the repo register; `output_dir` is a new location; `dt_s` must be positive and <=.005s but is NOT certified from modal results.

**Core functions:** `resolve_sources` computes local waveform hashes and matches A/B to the register; `create_configs` preserves structural variant/state/event isolation, safe no-overwrite defaults, literal `scale=1.0`, and source-review blockers.

**Output:** `00_SOIL_C_M0_M6_RUN_MATRIX.csv`, `00_SOIL_C_RESEARCH_RUN_MATRIX.json`, 112 `configs/M#/state/event.json` documents, with independent output paths. The proposed structural analysis stage remains `RESEARCH_DIAGNOSTIC`.

**NBC source:** [NBC 105:2025 §9.3.2](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). Do not infer original source scale factor or spectral acceptance from these configuration files.

**Tests:** [verify_soil_c_run_matrix.py](../../../../tests/verify_soil_c_run_matrix.py). See [full usage](../../../programs/36_SOIL_C_M0_M6_RUN_MATRIX.md).
