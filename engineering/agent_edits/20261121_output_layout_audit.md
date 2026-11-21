# Uniform output-folder standard and read-only layout audit

Editor Claude Code (model label UNKNOWN). Branch `feat/gate-material-blockers-run-analysis`. Plan Task 3.

Edited paths
- `tools/audit_output_layout.py` (new), `tests/test_audit_output_layout.py` (new).
- `docs/OUTPUT_FOLDER_STANDARD.md` (new), `docs/source/tools/audit_output_layout.py.md` (new).
- `docs/00_REPOSITORY_ORGANIZATION.md`, `README.md`: one link each.
- `engineering/registry/CANONICAL_MODULES.csv`: one NEW_WITH_JUSTIFICATION row, NOT_REVIEWED.

Tests (headless): `python -m pytest tests/test_audit_output_layout.py tests/test_literature_code_map.py -q`; `python tests/verify_ref_tags.py`.

Scientific gates: layout evidence only, no solver PASS claimed as engineering acceptance. Producers `building_exploratory.py`, `literature_demo.py`, `full_record_gate.py`, `energy_balance.py` write ad hoc folders and are not migrated. PENDING: native ETABS/OpenSees runs.
