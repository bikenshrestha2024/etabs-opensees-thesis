# 02 — OpenSees/OpenSeesPy solver tasks

The existing working analysis implementations remain in `components/model/`, `components/gravity/`, `components/modal/`, `components/response_spectrum/`, `components/nonlinear_time_history/`, `components/sections/`, and `components/shared/`. These are **canonical source paths today**; editing the pointers here changes no structural behavior.

The new `src/thesis_core/` neutral schema and `src/opensees_engine/` minimal benchmark form an **opt-in standalone prototype**. It does not handle the full RCC core wall, slab mesh, FVD, BRB or 25-storey model, and must not replace working launchers.

Use `python tools/run_standalone_benchmark.py` only for the demonstrated small elastic benchmark. It requires OpenSeesPy but does not need ETABS. Project-scale acceptance remains blocked by the existing engineering gates.

[Beginner guide](../engineering/topics/OPENSEES.md) · [future dependency boundary](../engineering/rules/MODULE_BOUNDARIES.md)
