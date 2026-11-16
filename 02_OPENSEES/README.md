# 02 — OpenSees/OpenSeesPy solver tasks

The existing working analysis implementations remain in `components/model/`, `components/gravity/`, `components/modal/`, `components/response_spectrum/`, `components/nonlinear_time_history/`, `components/sections/`, and `components/shared/`. These are **canonical source paths today**; editing the pointers here changes no structural behavior.

The new `src/thesis_core/` neutral schema and `src/opensees_engine/` minimal benchmark form an **opt-in standalone prototype**. It does not handle the full RCC core wall, slab mesh, FVD, BRB or 25-storey model, and must not replace working launchers.

Use `python tools/run_standalone_benchmark.py` only for the demonstrated small elastic benchmark. It requires OpenSeesPy but does not need ETABS. Project-scale acceptance remains blocked by the existing engineering gates.

[Beginner guide](../engineering/topics/OPENSEES.md) · [future dependency boundary](../engineering/rules/MODULE_BOUNDARIES.md)

## Standalone OpenSeesPy verification (B01–B12)

[Verification Studio v2 source and Windows launcher](../tools/verification_studio/README.md) · [Thesis acceptance matrix](../tools/verification_studio/THESIS_VALIDATION_MATRIX.md). Run separately from the thesis workflow; offline CI tests are not evidence of native ETABS/OpenSees equivalence. Keep generated run records local and private.

## Completed user-submitted B01–B12 benchmark run (2026-11-16)

The independent Verification Studio v2.1.0 single-file run records **11 native component PASS + 1 analytical-only PASS (B12), 58/58 recorded metrics passed** with OpenSeesPy 3.8.0. [Engineering evidence and open acceptance gates](../REVIEW_MAIN/00_MODEL/20261116_B01_B12_STUDIO_RESULTS_AND_ACCEPTANCE.md).

The **main model-readiness GUI now includes “OpenSees B01–B12 verification”**, launching the standalone Studio in a separate Python process. This does not change model readiness status or the production solver.

To validate your private local report folder without publishing it:

```powershell
python tools/verification_studio/import_verified_runs.py --results "<PRIVATE_RUN>/cases" --out "<PRIVATE_CASE>/REVIEW_MAIN/VERIFICATION_STUDIO/B01_B12_SUMMARY.json"
```

The importer is strict about case/status/metric identity and emits an evidence-consistency report, **not ETABS–OpenSees equivalence**.

### From the main thesis GUI

Open **NLTHA Readiness / Evidence Dashboard**, then use **OpenSees B01–B12 verification** to start a separate standalone benchmark GUI. After completing the run, choose **Import B01–B12 evidence**, select either the run folder or its `cases` subfolder, and inspect the status written under your **selected private project** at `REVIEW_MAIN/VERIFICATION_STUDIO/B01_B12_COMPONENT_EVIDENCE_SUMMARY.json`. The importer process writes its diagnostic log under the project's `OpenSees_Analysis_Results/Readiness_Diagnostics/`. This never changes source geometry, materials, supports, numerical model status, or native ETABS equivalence.
