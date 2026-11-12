# Nonlinear analysis readiness — evidence-based dashboard

Open the existing GUI and select **OpenSees nonlinear readiness / calibration status**. The old nine-item hard-coded warning was replaced by a model-and-project-specific table.

### What the dashboard does

- Inventories current ETABS source data, loads/mass, RC frame section evidence, core wall geometry, research materials, FVD/BRB devices, gravity/modal/P-Delta, first-step diagnostics and ground-motion history evidence.
- Distinguishes `MISSING_EVIDENCE`, `EVIDENCE_FOUND_REVIEW_REQUIRED` and `REVIEWED_SIGNOFF_CLAIM`.
- Hashes evidence with SHA256 and lists exact candidate file paths; file existence **never** becomes a numerical PASS.
- Uses the existing `OpenSees_Model_Readiness_Draft_*_V134.json` review mechanism. A changed model source hash or path invalidates signoff; even valid reviewer signoff is **not** a building-level physical validation pass.
- Exports `OpenSees_Analysis_Results/Readiness_Audit/Nonlinear_Readiness_Audit.json` and `.md`.
- Buttons: choose project, choose exact model-builder script, refresh, open model-bound review, inspect dependency preflight, export evidence and open project folder.

### Separation of analysis levels

`DIAGNOSTIC_ONLY` permits isolated smoke tests and is not a full building analysis approval. `MODEL_BOUND_SIGNOFF_RECORDED_NOT_AUTOMATICALLY_VERIFIED` reports a human claim, not a self-certified solver or experimental result. The native first-step X-only failure is not fixed by the dashboard. In addition to a successful numerical run, thesis-level model verification requires independently checked ETABS geometry/mass and reinforcement, cyclic RC wall benchmarks and device qualifications.

### Implementation and regression

- GUI: [readiness_dashboard_gui.py](../source/components/model/readiness_dashboard_gui.py.md).
- Backend: [readiness_dashboard.py](../source/components/model/readiness_dashboard.py.md).
- Test: `python tests/verify_readiness_dashboard.py`.
- Launch through the existing root application button; no separate window program is required.
- Official NBC seismic context: https://dudbc.gov.np/pages/24231978/ ; paper wall basis PEER 2015/12 and Kolozvari et al. (2023) DOI 10.1016/j.engstruct.2023.116700. No paper source is treated as project approval.

### Direct diagnostic tools

The dashboard includes action buttons to launch the eight-material visual validation interface, generate separate ZERO/X/Y/XY wall diagnostic RunConfig files, and execute an isolated native FVD/BRB recorder test. Child-process console logs go to `OpenSees_Analysis_Results/Readiness_Diagnostics`; case outputs are written to distinct diagnostic directories. These buttons never run the building's full nonlinear time history automatically and never promote a case to thesis-qualified status.

NBC 105:2025 screening now appears as a distinct dashboard workstream; the presence of a spectrum-screen JSON remains **available for review only**, never a code pass. See docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md.

### 2026-11-12 usability and material-source clarification

- When the chosen project folder contains the standard `OpenSees_Complete_Nonlinear_Model.py` in its root, the dashboard preselects that exact file **for inspection only** and computes its source SHA in the regular audit. If absent, the user must choose a model explicitly. A gravity-only builder is never substituted.
- Changing project folders refreshes the model field so a selected model from an unrelated project is not silently retained.
- The dependency preflight separately reports whether an **external project nonlinear material definition file** is configured and exists, versus whether `Material_Catalog/` research cards and `material_source_sets.py` exist. The research cards do **not** discharge material/reinforcement calibration requirements or set `approval=True`.
- Readiness review claims remain model-bound and SHA-checked; automatic file discovery never checks reviewer boxes.
- Regression tests: `python -m unittest tests.verify_readiness_dashboard -v`. This does not run native OpenSees/ETABS and does not resolve the first-step X wall failure.

See [the 2026-11-12 thesis workboard](../review/20261112_THESIS_DELIVERY_WORKBOARD.md) for ordered structural verification and research completion gates.
