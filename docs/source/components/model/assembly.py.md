# assembly.py — Model assembly / ETABS source transfer

**Python source:** [components/model/assembly.py](../../../../components/model/assembly.py)
**Current Git blob SHA:** 2ddff7ea2004ef4cacc576be2b8cf387238875c9
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Creates OpenSees basic 3D, 6-DOF nodes, supports, diaphragm masters, frames, walls, floor shells, nodal masses and gravitational loads from assembled ETABS JSON. In the nonlinear branch, ordinary hinged SHS braces are modeled as Steel01 corotTruss, frames as forceBeamColumn with predefined fiber section map and walls as E_SFI_MVLEM_3D with configurable macro-fiber count (default 5).

## Explicit assumptions and known deficiencies
The wall FSAM tags currently track property name rather than proven confined core/boundary subregions. Elastic ShellMITC4 floors do not represent nonlinear slab damage. The hard-coded fiber section mapping must match actual section schedules. An active FVD/BRB assignment is handled through mapping override and must be independently validated.

## Required thesis engineering changes
Validate all source areas and wall opening boundaries against actual ETABS geometry; inspect right-handed wall-node order/local axes; compare source vs solver element tags and load paths; verify frame release semantics, section inertia, torsional response and gravity reactions. Add single-panel cyclic tests before full-building transient.

## Cited scientific context
R01, R02, R03, R12, R13; model formulation references are not a member-level calibration.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
