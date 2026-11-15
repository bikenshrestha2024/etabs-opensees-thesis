# src/thesis_core/__init__.py — benchmark schema exports

Source: `src/thesis_core/__init__.py`. Re-exports `validate_model`, `cantilever_example`, and `SCHEMA_VERSION` from `neutral_model.py`. The schema is opt-in and limited to synthetic linear-elastic stand-alone or benchmark cases, not converted ETABS models or full 25-storey thesis structures. Import the package without native ETABS/COM, and use `tests/verify_standalone_neutral_model.py` for source boundary checks.
