# src/thesis_core/neutral_model.py — strict minimal benchmark schema

**Version:** `SCHEMA_VERSION=0.1.0`. Supported input is an explicit `kN-m-s` dictionary in `standalone` or `benchmark` mode, with positive unique node tags, six-DOF fixities, one three-dimensional `elasticBeamColumn3D` element, explicit local-axis `vecxz`, exact section keys `A,E,G,J,Iy,Iz`, finite nodal load vectors and source description. `validate_model(data)` rejects unknown fields, invalid units, unsupported elements or degenerate geometry. `model_sha256(data)` fingerprints sorted canonical JSON, while `cantilever_example()` creates a two-node axial-gravity reference case.

**Limitations:** Not a neutral representation of the thesis core walls, floor diaphragms, complex material behavior, staged gravity, nonlinear joints, FVD/BRB or M0–M6 ground motions. Conversion and structural equivalence remain **NOT_VERIFIED**. Source-only regressions: `tests/verify_standalone_neutral_model.py`, `tests/verify_etabs_adapter_boundary.py`.


## Prototype contract robustness (2026-11-15)

Exactly **two** node records are supported because the opt-in solver builds exactly one two-node elastic member. Disconnected extras are rejected even if the records happen to be fully fixed. Six fixity entries require **integer** zeros/ones; Python booleans are intentionally refused. Element tags and endpoint/load node tags require valid actual integers, and nonmapping element/load records are rejected with explicit `ValueError`. Source `description` must be a nonempty string. None of this is a migration of the production `components/` model schema or an assertion that nonlinear shells, mass, walls, offsets or full M0–M6 support is available.
