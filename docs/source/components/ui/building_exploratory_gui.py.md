# building_exploratory_gui.py — Building NLTHA graphical control and research-run safety

**Python source:** [components/ui/building_exploratory_gui.py](../../../../components/ui/building_exploratory_gui.py)
**Current Git blob SHA:** 6bf4179a76cfc1597309807715693f74205a93e0
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Controls research building material selection, wall configuration, transient system, output folder, diagnostic toggles and presentation of logs/results through GUI execution.

## Explicit assumptions and known deficiencies
Provide visible grouping for assumed versus calibrated inputs and for short probe versus full record. UI can display analysis outcomes but cannot independently establish solver convergence or specimen calibration.

## Required thesis engineering changes
Add explicit preview of input model/record hashes, ULS/SLS, XY/YX and damping; provide cancel, safe run folder selection, progress updates, selected test evidence and links to file-specific validation reports. Avoid silent exceptions.

## Cited scientific context
R01, R02, R05, R10; documents for literature-based controls, not a GUI physics benchmark.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)



## 2026-11-15 one-storey probe process working directory

The 1-wall-quadrilateral diagnostic worker launches `python -m components.nonlinear_time_history.one_storey_wall_probe`. The historical root facade changes `__file__`, which previously made the derived subprocess `cwd` point outside the actual runtime. The new `_runtime_repo_root()` uses the facade's `_component_source` when present and the direct component path otherwise. This only corrects the module-search directory, not wall topology, loads, material values, condensation or nonlinear solver behavior. The isolated element probe is **not** full-building NLTHA.

## 2026-11-25 exploratory convergence settings
The convergence recovery panel exposes the research-only final 1e-6 tolerance as an unchecked option and maximum iterations per attempt (default 40). The shared engine validates both before launch. The saved configuration records the choice, and completed/truncated case messages report the number of relaxed steps. No relaxation is enabled by default. GUI rendering and native convergence remain unverified.
