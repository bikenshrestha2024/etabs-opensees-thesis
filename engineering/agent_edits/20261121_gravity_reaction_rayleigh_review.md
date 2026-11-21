# Gravity support-reaction distribution and Rayleigh period review

Editor: Claude Code (model label UNKNOWN). Branch `feat/gravity-reaction-rayleigh-review`, created from `feat/nbc105-clauses-1-3-annexc` at 99d3cfa. Date 2026-11-21 (UTC).

Edited paths
- `components/modal/rayleigh_mass_audit.py`: floor allocation now uses `storey_index_for_elevation` (§5.2 mid-height rule), the same rule as the assembly ledger, and reports `maximum_downward_lump_m`. Ported verbatim from origin/main 891843e.
- `tests/test_rayleigh_mass_audit.py`: lower-half node test, ported verbatim from origin/main 891843e. It failed before the change with "Mass audit floor weights fail source seismic ledger reconciliation" and passes after it.
- `docs/source/components/modal/rayleigh_mass_audit.py.md`: contract text updated.
- `tools/gravity_reaction_attribution.py` (new), `tests/test_gravity_reaction_attribution.py` (new), `docs/source/tools/gravity_reaction_attribution.py.md` (new).
- `engineering/registry/CANONICAL_MODULES.csv`: one NEW_WITH_JUSTIFICATION row.
- `docs/validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md` and `.json` (new).

Existing-code search: `rg` for tributary, reaction ranking (`components/validation/gravity_node_comparison.py`), `audit_shell_gravity_transfer.py`, `elastic_conversion_settings.py` and output_contract. No solver, material, damping, load, mass or stiffness numerics were changed.

Evidence: uploaded gravity, comparison, ESM and MESH_04/08/16 bundles (read-only, unzipped outside the repository). No OpenSees or ETABS available or run.

Tests: `python -m pytest -q` and `python tests/verify_ref_tags.py`; results are in the commit message.

Scientific gates: findings status `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`; the tool status is `DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE`. PENDING: Windows rebuild with ETABS elastic settings, Rayleigh/ESM re-run on the clear-beam export, and native ETABS Dead/Live joint reactions.
