# Agent edit — unified 3D member-prefix filter (15 November 2026)

- Repository: `bikenshrestha2024/etabs-opensees-thesis`; branch `feat/20261115-unified-3d-member-prefix-selector`; base `0813b418a06e7f71efb3d14e7c03d59a74138d3a`.
- Source inspected: `AGENTS.md`, `components/model/id_audit.py` including the complete shared HTML Plotly JS injection and Excel exports, `components/model/display_ids.py`, `tests/verify_3d_zoom_to_node.py`, `tests/test_id_audit_display_labels.py`, `docs/source` guides, and the provided Chrome screenshot.
- User request: compact consistent 3D views; filter by `B/C/CT/CO/BT/FVD/BRB` prefix then exact element number; retain original source/solver IDs and camera/navigation functionality.
- Narrow physical scope: display-only; no source model/EDB, gravity supports, material, stiffness, end-release, P-Delta, wall FSAM or nonlinear behavior modified.
- Changes: source-verified `FVD`/`BRB` labels only if exact category appears; prefix/storey/display-number selection, highlights and element focus in shared Plotly HTML injector; responsive CSS, exact identifiers disclosure and repeat-export de-duplication.
- Native Excel audit retains original 0–9 columns, independent `Display prefix` in column 12, and untouched ETABS source, topology preview and actual solver integer tags. No synthetic source-generated FVD/BRB inferred from plain braces.
- Acceptance: synthetic HTML/Excel/JS parsing integration test under `tests/test_shared_3d_prefix_selector.py`; CI export staging with openpyxl. Windows Chrome visual/interactive acceptance must be separately confirmed.
- Unchanged standalone GUI: `components/sections/mapping_gui.py` Tk/Matplotlib V126; this PR updates all shared Plotly HTML views only.
