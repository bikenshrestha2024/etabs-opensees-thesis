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
