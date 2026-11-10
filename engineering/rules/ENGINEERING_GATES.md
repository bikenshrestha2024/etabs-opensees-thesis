# Engineering evidence and acceptance gates
Every claim carries independent flags: SOURCE_CHECKED, NUMERICALLY_CONVERGED, ETABS_OPENSEES_MATCHED, EXPERIMENT_VALIDATED, CODE_ACCEPTED. Missing evidence is NOT_VERIFIED, not PASS.

- Gravity: prior source gross-beam run ETABS 311367.314 kN versus OpenSees 320019.758 kN (~8652.444 kN difference). A code correction is NOT proof of rerun. Primary comparison uses original 32 reaction-bearing joints; 76/97-point schemes are mesh/support sensitivity only.
- Beam volume/weight: native ETABS object material-list weights, end offsets, length and self-weight factor must be reconciled without overlapping column, wall and slab volumes. No double counting or missing quantity; check each source individually.
- NBC105 ESM: project-matched original Excel Aw/T1 values and workbook/EDB SHA have priority as **adopted research inputs**, not unquestioned code compliance. Do not replace with provisional continuous-pier geometry.
- Modal/RSA/EQX/EQY/PDelta: record source EDB, ULS/SLS, case naming, stiffness, source mass, gravity preload, signed direction, +/− eccentricity, equation definitions, base/story shears, displacements/drift, support reactions, code acceptance separately. Applied floor-force accumulation != independently recovered section-cut story shear.
- NLTHA: first-step nonfinite X response around wall element 110280 remains unresolved until actual mapping and ZERO/X/Y/XY run evidence supports the cause. Planned 112 configurations / 224 XY/YX runs must never be labeled solved.
- Ground motions: preserve original SeismoMatch scaling, units, time-step, pair mapping and duration. Never double-scale matched accelerograms; confirm vertical-acceleration applicability independently.
- Materials/FVD/BRB/walls: source actual laboratory data and verified OpenSees build; smoke tests do not validate full 3D material behavior.
Retain detailed preexisting gates in `docs/00_THESIS_ACCEPTANCE_GATES.md`.
