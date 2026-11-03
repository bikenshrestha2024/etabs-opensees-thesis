# research_building_materials.py — Source-grade, wall FSAM and material-card adapter

**Python source:** [components/nonlinear_time_history/research_building_materials.py](../../../../components/nonlinear_time_history/research_building_materials.py)
**Current Git blob SHA:** 1a18ad3db702afa027d60565207e0cbf7745b736
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Builds frame Concrete01/Steel02 templates and web FSAM using ConcreteCM/SteelMPF; loads published PEER or nominal M30/Fe500 card; allows bounded research material overrides and exports the selected material assignment.

## Explicit assumptions and known deficiencies
Source code explicitly retains existing bar-layout TEMPLATE values, nominal Fe500 reinforcement, unconfined wall web throughout and a two-curtain wall steel assumption. Its SteelMPF transition profiles include a documented default and a distinct PEER appendix value. These are not approved project reinforcement/confinement.

## Required thesis engineering changes
Require actual longitudinal/transverse bar schedules, cover/core confinement and section-by-section wall boundary assignments; preserve signed compressive concrete conventions, unit conversions exactly once and recorded calibration specimen/protocol. Reject unexpected materials and independently compare cyclic panels.

## Cited scientific context
R01, R02, R03, R04. Never treat paper specimen parameters as the building strength.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
