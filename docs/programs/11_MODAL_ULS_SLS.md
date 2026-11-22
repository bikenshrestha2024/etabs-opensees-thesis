# 11 — Modal ULS and SLS analysis

**Current launcher:** [`11_MODAL_ULS_SLS.py`](../../11_MODAL_ULS_SLS.py)  
**Previous launcher:** [`04_MODAL_ULS_SLS.py`](../../04_MODAL_ULS_SLS.py) (compatibility alias)

## Goal
Modal ULS and SLS analysis. Run from the complete repository with a compatible Windows Python/OpenSeesPy environment. This entry point retains the original launcher's numerical implementation unchanged.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
In Spyder open `11_MODAL_ULS_SLS.py` and run. Alternatively from the repository root invoke `python 11_MODAL_ULS_SLS.py`. If the script requires arguments (particularly the two diagnostic scripts), inspect the Python source usage and supply an appropriate export or failed-run folder.

## Validation and results
Review the program's actual run logs, input assumptions, generated files and solver status before interpreting engineering output. Material examples and smoke tests are not experimental calibration, and an incomplete nonlinear earthquake history must not be ranked. The building transient first-step failure remains unresolved.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)


## 2026-11-04 merged modal-stop status fix

The main GUI's case board already exposes **Stop selected batch**. The modal worker has now been corrected to preserve the explicit `CANCELLED` outcome after a terminated subprocess; the nonzero exit code due solely to operator cancellation is not labeled as a numerical eigenanalysis failure. Queued ULS/SLS states remain `NOT COMPLETED`. The current log is preserved; cancelled partial outputs must not be interpreted as a modal participation PASS. The current stop control terminates the active child Python process; it is not a numerical solver convergence solution. Test: `python tests/verify_modal_cancel_status.py`. Native Windows GUI usability remains to be verified locally.


## Mass-operator and modal evidence interpretation

The OpenSees source option `SOURCE_DISTRIBUTED` is multiple **nodal** mass assignments rather than a single floor mass; it is not an element consistent-mass matrix. `STORY_LUMPED_NBC` reallocates the source horizontal nodal mass to one center-of-mass-checked diaphragm master per story and explicitly assigns polar `J_z`, retaining vertical nodal mass. It is an alternate analytical idealization **not automatically approved by NBC 105:2025**. The project default remains distributed until exact ETABS modal/diaphragm equivalence is verified. See the [technical mass operator explanation](../engineering/MASS_SOURCE_DISTRIBUTED_VS_STORY_LUMPED_NBC.md), including equations, implementation owners and sensitivity comparison.

The standardized case creator reserves `07_EXPORT_ZIP` even when no export has been requested. The modal producer writes figures/Excel/results to `04_FIGURES`/`03_EXCEL`/`02_RESULTS`; it does not automatically populate `07_EXPORT_ZIP`. An MRSM review ZIP is from an independently run module and must not be copied to the empty modal folder as if it were modal evidence. A modal result is not missing solely because the ZIP destination is empty.
