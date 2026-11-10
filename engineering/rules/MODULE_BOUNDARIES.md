# Integrated today; standalone OpenSees tomorrow
**Architectural policy, not yet implemented.** Preserve current `components/` implementation, legacy launchers and numerical behavior until mapped and tested.

Operating modes (all eventually use ONE canonical OpenSees core):
- integrated: CSI ETABS adapter -> neutral versioned model package -> OpenSees engine -> independent ETABS comparison
- standalone: authored/validated neutral model package -> SAME OpenSees engine; no ETABS import, running process or EDB
- benchmark: literature specimen -> SAME OpenSees engine; independent experimental acceptance

Allowed dependencies: etabs_adapter -> neutral schema; standalone_editor -> neutral schema; neutral schema -> opensees_engine -> recorder/results; CSI results -> comparator.
Forbidden: opensees_engine -> ETABS/comtypes/win32com; numerical core -> GUI; neutral schema -> CSI; standalone -> ETABS runtime; CSI comparator -> source EDB mutation.
Do not create empty placeholder packages as if the architecture is implemented. First inventory current `components/model/`, `components/sections/`, `components/shared/`, `components/gravity/`, and `components/nonlinear_time_history/`. Define versioned neutral schema including node/element tags, shell openings, material/rebar provenance, member offsets/releases, local axes, loads/mass, constraints, limit state and units. No capability substitution when a specialized wall element is missing. Before migrating, require import-cycle detection and ETABS-free standalone benchmark test.

## Actual opt-in milestone (2026-11-10)
A minimal two-node 3D elastic cantilever in `src/thesis_core/neutral_model.py` and `src/opensees_engine/standalone.py` now demonstrates the boundary; ETABS native extraction delegates through `src/etabs_adapter/bridge.py`. These **do not** replace the working `components/` engine, nor support the 25-storey RCC core, frame offsets, shells, PDelta, nonlinear FVD/BRB or M0–M6. A full neutral ETABS converter and native full-building regression remain pending. Keep this limited proof-of-architecture isolated.
