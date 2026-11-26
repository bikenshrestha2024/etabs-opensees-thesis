# devices.py — FVD and BRB nonlinear mechanics and demand helpers

**Python source:** [components/sections/devices.py](../../../../components/sections/devices.py)
**Current Git blob SHA:** 25567223c27257a7ab0bd3382ef1021bbb571c96
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Implements Maxwell ViscousDamper with twoNodeLink (local axis 1, Rayleigh optional), Steel02 BRB core with corotTruss, and experimental-data-only response helpers. The new convert_fvd_cd_mm_to_m(Cd, alpha) returns Cd multiplied by 1000 raised to alpha. summarize_fvd_history returns peak relative force, velocity, displacement, travel and two signed work integrations. brb_cumulative_plastic_ductility requires an ACTUAL plastic deformation history and a separately established positive yield displacement.

## Explicit assumptions and known deficiencies
All parameters must be finite and unit consistent, with FVD K in force/length and Cd in force*(time/length)^alpha. The two signed work integrals are NOT labeled positive dissipated energy until recorder force/velocity sign conventions have been verified. Steel02 corotTruss does not by itself qualify a BRB under cyclic fatigue, fracture, connection eccentricity, casing or brace-core slip.

## Required thesis engineering changes
Validate a full FVD hysteresis curve with test K/Cd/alpha and connection rigidity; verify BRB hysteretic strength, tensile/compressive asymmetry, cumulative plastic ductility, local eccentricity and fatigue against experimental protocols. Add native unit tests for twoNodeLink axis, force sign and multi-step integration before using metrics in the M0–M6 suite.

## Cited scientific context
- R05 §3 and Eq. (5) describe the signed velocity law and Maxwell model. Table 4 gives the FVD coefficient units. The conversion from millimetres to metres follows from those units. [Korkmaz and Kircil](https://www.mdpi.com/2075-5309/16/4/711)
- R07 Eq. (5) defines cumulative ductility as hysteretic work divided by the product of yield force and yield displacement. This module's diagnostic instead sums absolute increments of isolated core plastic displacement and divides by yield displacement. Fatigue qualification needs independent experimental evidence. [Guerrero Bobadilla et al.](https://doi.org/10.1016/j.soildyn.2025.109700)
- R06 studies damper placement in a composite tower. R08 studies BRB connection eccentricity. Both are stage-specific context listed in the [research source register](../../../00_RESEARCH_REFERENCES.md).

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
