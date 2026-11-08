# load_path_formulas.py — source documentation

**Python source:** [components/gravity/load_path_formulas.py](../../../../components/gravity/load_path_formulas.py)
**Git baseline content SHA:** 245bd43de57522753fe561a705ccd742d75de851
**Subsystem:** Gravity-load and support equilibration
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the gravity implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-08 correction: full gravity vs seismic preload formula tabs

The `Slab_Load_Path_Formulas_V141.xlsx` generator formerly populated
the visible `Surface load formulas` Gravity factor (column G) directly
from `cfg.gravity_factors` (typically Live 0.3), even when the native
gravity GUI used the runtime `GRAVITY_1.0D_1.0L` profile (Live 1.0).
That was an evidence labeling/calculation-view defect, **not** a
confirmed error in the OpenSees gravity solver.

The exported workbook now contains two separate sheets:
- `Surface load formulas`: **FULL GRAVITY 1.0D+1.0L**. All included
  dead and live source patterns, including assigned roof live, use
  gravity factor 1.0. For an area of 2.25 m² with 4 kN/m² live,
  applied load is 9.0 kN, not 2.7 kN.
- `Surface seismic preload`: the model configuration's
  `gravity_factors`, typically 0.3 for Live.
Both retain the independent original `mass_factors` column; seismic
mass is not multiplied by the gravity full-load override. Other
source-detail formulas continue to use unfactored source loads and
their own analysis-context settings.

Workbook sheets are diagnostic arithmetic, not replacement for
independently executed, case-specific solver reactions and
displacements. A previously saved workbook does **not** update itself
from GitHub. Refresh using the existing **Export / open current
load-path formulas** action after updating the application, then
check the full-gravity factor and configured seismic-preload factor.

Regression: `python tests/verify_slab_full_gravity_factors.py`.
