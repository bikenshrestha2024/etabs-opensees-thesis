# Components — current source navigation

The current active component modules are inventoried below. **These are module ownership links, not structural compliance approvals.**

- [equivalent_static](equivalent_static/README.md) — Equivalent static method (ESM) and source-linked Aw calculation
- [gravity](gravity/README.md) — Gravity solver, 32/76/97 supports and native reaction evidence
- [inputs](inputs/README.md) — Source files, project provenance and output contracts
- [linear_time_history](linear_time_history/README.md) — Linear time-history analysis
- [modal](modal/README.md) — Modal/Rayleigh analysis and directional periods
- [model](model/README.md) — Structural model and physical load assembly
- [nbc105](nbc105/README.md) — NBC 105:2025 reference rules (Clauses 1–10, Annex A/B)
- [nonlinear_time_history](nonlinear_time_history/README.md) — Nonlinear time-history analysis and M0–M6 investigations
- [response_spectrum](response_spectrum/README.md) — Modal response spectrum method (MRSM)
- [sections](sections/README.md) — Section/material/element mapping and device definitions
- [shared](shared/README.md) — Solver-independent shared utilities and runtime conventions
- [ui](ui/README.md) — Desktop application and results navigation
- [validation](validation/README.md) — ETABS/OpenSees independent comparison and engineering review

Authoritative integration policy: [Active module integration and source authority](../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md). Output layout: [Uniform source-owned stages](../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Current module coverage is checked by `tools/audit_component_readmes.py` in CI; the old V134 index is historical only.
