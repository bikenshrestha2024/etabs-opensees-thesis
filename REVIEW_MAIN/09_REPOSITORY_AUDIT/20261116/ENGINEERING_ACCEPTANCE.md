# Scientific acceptance gates — not automatically promoted by code CI

| Gate | Required evidence | Current position |
| --- | --- | --- |
| S1 tracked-tree discovery | Exact HEAD; all blobs, hashes, archive duplicates, source role ownership | PASS at pinned `19342cb0`; rerun for later HEAD |
| S2 complete semantic inspection | Actual reviewed source per all active symbols, callers and state, source SHA, reviewer, test | **NOT VERIFIED**; 4,561 symbols discovered, not reviewed |
| S3 dependencies and facade/runtime paths | Direct/dynamic imports, ETABS API signatures, CLI/GUI subprocess, external package versions, circular imports | Static import classifications generated; **NOT VERIFIED** at runtime |
| S4 all outputs and readers | Source hash and input contracts, interrupted writes, schema, ZIP, Excel formula correctness and consistent reader locations | IO call-site queue generated; isolated fail-closed fixes; **NOT COMPLETE** |
| S5 CI + security | Source-specific regression gates, Windows smoke, no secrets/private model data, Git history disposition | Targeted static CI passes; full Windows and historical publication review **OPEN** |
| S6 engineering | Matched ETABS model settings, reaction vectors, BCs, mesh effects, mass/damping, NBC 105:2025; no false force parity | **NOT VERIFIED** |
| S7 nonlinear experiment | Verified reference material data, convergence of X-wall first step, completed NLTHA and M0–M6 XY/YX record pairs | **NOT VERIFIED** |

## Unresolved high-priority numerical tasks

- **32 foundation supports:** compare ETABS source and OpenSees 32 true supports, mapping frame-only and shell-only groups. Independently review 76/97 restraint sensitivity, full six-component forces/moments and native ETABS edge constraints. Global vertical sum equality alone is insufficient.
- **MESH_04/08/16:** preserve 6×6 m source panel area and kN–m–s units. Match native ETABS slab–beam–wall interface forces, shell interpolation/edge constraints, deflections, beam end actions and structural responses. B06 simple patch equilibrium is insufficient for deflection convergence.
- **Mass, modal and seismic:** distinguish gravity and seismic mass factors, ETABS beam/internal-joint mass and diaphragm constraints, SLS/ULS modal shapes and period, NBC 105:2025 ground-motion target and spectral scaling, accepted NEC/IS supplementary hierarchy.
- **P-Delta:** NBC 105:2025 governs. Project's explicitly adopted IS 16700 initial cases are supplementary; avoid carried-static-EQ double counting in dynamic response. Use accepted native evidence.
- **Full nonlinear:** source-referenced ConcreteCM/SteelMPF or calibrated alternatives, first-step X-wall element diagnostic, proper beam hinges and wall openings, FVD Cd/alpha units, completed bidirectional histories, accepted IO/LF/CP metrics.

Do **not** label `NATIVE_OPENSEES_BENCHMARK_PASS` as `ETABS_OPENSEES_EQUIVALENCE_VERIFIED`, or a short accepted time-history as a full duration passed experiment. Preserve source EDB and private model geometry outside public Git.

Owner-level issue #75 is intentionally open until the actual tests and reviewer evidence are complete. Closing issue #75 because an AST queue or spreadsheet was generated is prohibited.
