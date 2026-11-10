---
applyTo: "components/model/**/*.py,components/gravity/**/*.py,components/modal/**/*.py,components/nonlinear_time_history/**/*.py,src/opensees_engine/**/*.py"
---
See `engineering/rules/MODULE_BOUNDARIES.md` and `engineering/rules/ENGINEERING_GATES.md`. Preserve full load path, mass, constraints, solver result integrity, wall/material capabilities; do not add ETABS/COM dependencies to an ETABS-free solver. Test gravity and nonlinear first-step stability with source-matched evidence.
