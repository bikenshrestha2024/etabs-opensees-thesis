# Source model handoff — original OpenSees export and literature sections

**Source:** [source_model_handoff.py](../../../../components/nonlinear_time_history/source_model_handoff.py). **Owner:** existing-model NLTHA inputs, SHA provenance, physical-support recorder identity. **User data:** original ETABS-derived JSONs remain on the user's local drive; no private files committed.

## `stage_existing_model_sources(source, destination)`

Before writing anything, checks all six mandatory V118 source files including `OpenSees_Element_Connectivity.json`. Then copies exact source bytes into one isolated run model folder and returns SHA256 for each. Refuses to overwrite an existing staged file whose bytes differ. Optional source story masters, overrides, element maps are carried by the same source set. This repairs the missing topology file in the prior exploratory nonlinear run when `assembly.py` calls `select_support_case(... PHYSICAL_32)`. Source EDB/model data are not mutated.

## `solver_reaction_support_tags(model_report, support_case)`

Derives foundation recorder node IDs from the actual returned `build_complete_model` report, never the static `data['supports']` export of 76 mixed records. Calls the shared `require_runtime_support_case` so `PHYSICAL_32` enforces the precise 32 user-confirmed foundation tags; 44 mesh points are not independent ground supports. The returned tag count reflects the **solved** local OpenSees support set. Matching IDs is not proof of source ETABS shell/MPC reaction equivalence.

## `literature_section_inventory(data, config)`

Source section names, counts, wall concrete class and wall thickness come from the actual local model. Solver section tags and current illustrative RC fiber cards come from `components.sections.definitions`. Unmapped frame sections or inconsistent wall property dimensions fail, rather than silently mapping all to one nominal card. Returns `RESEARCH_TEMPLATE_UNCALIBRATED` for incomplete actual material/rebar/FSAM mappings. Reference R01: PEER 2015/12 ConcreteCM/SteelMPF/FSAM specimen formulation; R02: E-SFI-MVLEM-3D 2023 doi:10.1016/j.engstruct.2023.116700. These are formulation sources only. Original source concrete M45 vs illustrative fiber concrete M35 is a documented unresolved transfer, not a verified material conversion.

**Tests:** `tests/test_direct_existing_nltha_20261122.py` stages exact topology bytes, rejects missing topology/mapping, verifies geometry counts, uses active 32 supports even when raw export has 76 and rejects mismatched solver support case. No live ETABS/OpenSees solver is represented by these unit tests.
