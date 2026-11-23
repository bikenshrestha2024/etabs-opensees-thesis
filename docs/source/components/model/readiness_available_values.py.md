# readiness_available_values.py — direct source inputs without self-approval

**Python source:** `components/model/readiness_available_values.py`

This module implements the request to **take already available model/project/literature values directly** instead of asking for repeated manual transcription. It only reads the **selected nonlinear model's project folder** and local, installed cited literature cards. It never modifies an ETABS EDB, starts a solver, posts private data over a network, modifies production material/FSAM configuration or sets `approved_for_nltha`, `nonlinear_parameters_reviewed` or any of the 16 engineering checks to `True`.

## Direct numeric sources

- `OpenSees_Complete_Model_Config_V118.json`: actual configured dead/live factors for gravity and seismic mass, ULS/SLS slab modifiers, floor subdivisions and existing named frame section mapping. Report these as **configured**, not independently code-verified.
- `OpenSees_Complete_Model_Data_V118.json`: source entity counts, shear-wall property thicknesses, diaphragm count and source gravity load distribution if present. An area/section label is not proof of actual reinforcement or NLTHA constitutive law.
- `OpenSees_Complete_Gravity_Check_V118.json` and load/metadata audits: explicitly present reported scalar fields. A saved elastic 20-step seismic-preload result does not count as a verified fully nonlinear `1D+1L` or signed P-Delta case.
- Model-SHA-matching `04_MODAL/RUNS/<ULS|SLS>/*/*/02_RESULTS/NBC105_Modal_V111.json`: a single uniquely matching serialized-model SHA and consistent state can provide modal periods and cumulative UX/UY screen values. Multiple matching runs, wrong model identity, missing SHA or malformed data remain candidates only (no modal value reused). The modal screen is not the NLTHA initial stiffness verification.
- The existing installed `material_source_sets.peer_single_source()` and `peer_fsam_panel_values()` are the **PEER 2015/12 RW-A15-P10-S78 research material baseline**, not the actual 25-storey project's reinforcement or a production engineering acceptance. Web `rho_x = rho_y = 0.0074`, `nu = 0.8`, `alpha = 0.01`; separate boundary `rho_x = 0.0082`, `rho_y = 0.0587` are NOT assigned absent a source-matched boundary map. The original same-paper ConcreteCM and SteelMPF source values are preserved.

## API and file behavior

`collect_available_project_values(model_script)` returns `NLTHA_DIRECT_AVAILABLE_VALUES_V1`: current builder SHA, direct source paths/SHA-256, available project values, explicit missing production fields, 16 unapproved check evidence candidates, and research-literature provenance. This does not write any file.

`attach_available_values_to_draft(model_script, draft_path)` atomically adds `available_project_values` **only to an existing, exact-model/SHA-bound, unapproved readiness draft**. It refuses approved drafts and wrong/changed model identity; retains all human-entered `checks`, `evidence`, `review_metadata` and other fields unchanged. It does not initialize a production material law from PEER specimen data.

The readiness GUI button **Load existing project + PEER research values (no manual re-entry)** displays the source snapshot; **Use these available values in UNAPPROVED draft** stores it locally with no human approval. An already present separate action can prepare a cited PEER-only **isolated exploratory copy** and material parameters for numerical trials; the production configuration is untouched.

Tests: `tests/test_nltha_direct_available_values_20261123.py` (source values, matching/mismatched modal result, rejection of approved or mismatched manifests, missing material fields).
