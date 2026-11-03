# area_elements.py — Area-element integration for floor shells and nonlinear walls

**Python source:** [components/sections/area_elements.py](../../../../components/sections/area_elements.py)
**Current Git blob SHA:** b7c79053ac2b8a2a6c33516f07a0ec5894fc6c74
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Provides ETABS area mesh import, ShellMITC4 floor sections and E-SFI wall instantiation with project FSAM materials; also audits seismic mass and uniform area-load transfer.

## Explicit assumptions and known deficiencies
The area adapter's wall macro-fiber discretization path is not necessarily equivalent to the five-macro-fiber-per-quad setting in main components/model/assembly.py. Do not claim two code routes are the same without an element-by-element geometry/response comparison.

## Required thesis engineering changes
Compare geometry, wall fiber widths/thicknesses, actual surface reinforcement, normal directions, areas, opening borders, floor-to-wall joints and density/mass handling. Add small-mesh convergence and isolated panel benchmarks using the same material card in both code paths.

## Cited scientific context
R01, R02 and R13 (R13 is an alternative element family, not identical to E-SFI).
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
