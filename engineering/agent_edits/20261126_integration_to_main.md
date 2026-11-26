# Integration of gravity/Rayleigh review, wall-mesh option and NBC 105 normative register into main

Date: 2026-11-26. Model: UNKNOWN (not recorded). Engineering validation: unit tests only; real OpenSeesPy 3.8 Linux gravity/eigen runs for the cited ablation JSON files; no native ETABS.

Merged into the origin/main line (97c0b3a8): `feat/joint-reaction-rayleigh-fix` (wall mesh option, rigid end zones, ETABS_ELASTIC_GRAVITY_COMPARISON preset, storey mass convention) and `feat/nbc105-normative-sentence-audit` (normative register, owner rulings 1-11).

Conflict resolutions: assembly `_mesh_areas` keeps main's `unique_coordinate_lookup` plus `wall_max_cell_size_m` validation; V144 checklist text keeps main's `GRAVITY_M_S2` formatted sentence (value 9.81); registry, assembly guide and clause 5 matrix keep both sides; MRSM 33 Hz guard uses `clause_07_missing_mass.missing_mass_gate` (same fail-closed result) while keeping main's solver-reaction support tags; MRSM result carries `drift_basis='ETABS_COMPARISON'`.

Adaptations: `tools/etabs_beam_slab_load_path.py` uses the refactored `_stream_tables`; component README catalogs list the new modules; `require_same_drift_basis(outputs)` takes one list so it is JSON-callable; 7 stale tests in `tests/test_nbc105_docs_consistency.py` that asserted the older README vocabulary were removed (superseded by main's source-coverage gate and the normative-register tests); the 11 remaining tests still pass.

Known pre-existing failure on origin/main (not introduced here): `tests/test_linear_th_directional_autofill.py::test_missing_modal_clears_previous_verified_metadata` (patches `components.response_spectrum.model_analysis`, which does not import in this Linux container).
