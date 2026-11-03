# devices.py — FVD and BRB nonlinear mechanics and demand helpers

**Python source:** [components/sections/devices.py](../../../../components/sections/devices.py)
**Current Git blob SHA:** 288e8ee7cec49f9521dd1d70e9d96789b4df5ba7
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Implements Maxwell ViscousDamper with twoNodeLink (local axis 1, Rayleigh optional), Steel02 BRB core with corotTruss, and experimental-data-only response helpers. The new convert_fvd_cd_mm_to_m(Cd, alpha) returns Cd multiplied by 1000 raised to alpha. summarize_fvd_history returns peak relative force, velocity, displacement, travel and two signed work integrations. brb_cumulative_plastic_ductility requires an ACTUAL plastic deformation history and a separately established positive yield displacement.

## Explicit assumptions and known deficiencies
All parameters must be finite and unit consistent, with FVD K in force/length and Cd in force*(time/length)^alpha. The two signed work integrals are NOT labeled positive dissipated energy until recorder force/velocity sign conventions have been verified. Steel02 corotTruss does not by itself qualify a BRB under cyclic fatigue, fracture, connection eccentricity, casing or brace-core slip.

## Required thesis engineering changes
Validate a full FVD hysteresis curve with test K/Cd/alpha and connection rigidity; verify BRB hysteretic strength, tensile/compressive asymmetry, cumulative plastic ductility, local eccentricity and fatigue against experimental protocols. Add native unit tests for twoNodeLink axis, force sign and multi-step integration before using metrics in the M0–M6 suite.

## Cited scientific context
R05, R06, R07, R08; OpenSees ViscousDamper and Steel02 reference manuals.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
