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

## Follow-up: ETABS table evidence (assignment export, beam forces)

Editor: Claude Code (model label UNKNOWN). Same branch, on top of 25f76a3. Date 2026-11-21 (UTC).

Edited paths
- `docs/validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md`: new §7 and a pointer in §5. `.json`: new `etabs_table_evidence` block.
- `tools/etabs_beam_slab_load_path.py` (new), `tests/test_etabs_beam_slab_load_path.py` (new), `docs/source/tools/etabs_beam_slab_load_path.py.md` (new). The tool reuses `etabs_assignment_gravity_audit._rows` and `etabs_split_beam_forces._stream_rows` without changing them.
- `engineering/registry/CANONICAL_MODULES.csv`: one NEW_WITH_JUSTIFICATION row. The existing consolidator accepts single-case exports only, and the assignment audit covers weights and offsets only.

Existing-code search: `rg load_workbook components tools`; read `etabs_split_beam_forces.py`, `etabs_assignment_gravity_audit.py`, `assembly.py` (`_mesh_areas`, `surface()`, the elastic frame branch, `rigidDiaphragm`, `export_gravity_beam_actions`) and `elastic_conversion_settings.py` (`end_offsets_m`).

Evidence: the user-uploaded `Assignment_Export_ULS_3_storey_latest.xlsx` and `Beam_Forces_Element_{1,2,3}_latest.xlsx` were read with streaming openpyxl only. The bundles from the previous session were reused from /tmp/rev. The reader run folder is outside the repository (layout audit OK). No OpenSees or ETABS was available or run.

Findings, in brief: the roof +215.463 kN and base −215.463 kN come from ETABS splitting intermediate-joint mass linearly (inferred from an exact fit). The earlier +212 kN includes a 3.16 kN g artefact (ETABS g 9.80665). Floor 1 +195 kN is the V127 allocation of free z = 0 nodes. ETABS floors use `No Auto Mesh`, so no slab load reaches the beam spans (Live V2 constant on all 750 beams). Beam flexure in ETABS moves 3,029.78 kN from the core to the perimeter. The table records 9 mismatches. No repository defect was proven, so no solver, material, damping, load, mass or stiffness numerics were changed.

Tests: `python -m pytest -q` and `python tests/verify_ref_tags.py`; results are in the commit message.

Scientific gates: findings status `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`; tool status `DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE`. PENDING: OpenSees gravity rebuild with elastic settings plus `end_offsets_m` and beam end-action export; ETABS pier, slab-corner and brace forces.
