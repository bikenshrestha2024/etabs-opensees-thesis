# Audited full-gravity load provenance, not reaction fitting

Source: `components/gravity/source_load_reconciliation.py`.

This module runs after a successful gravity solve and writes four independent evidence files in the **same run output folder**:

* `Gravity_Source_Components_Audit.xlsx` — source type totals (beam, column, brace, slab, shear wall, and distributed/point/area loads), load pattern totals, signed equivalent-nodal source detail, code and evidence limitations.
* `Gravity_Source_Components_Audit.json` — reconciled source total, beam clear-weight hypothesis, optional original ETABS total comparison, and explicit validation status.
* `Gravity_Source_Components_Detail.csv` — all contributing nodal source records, source object, pattern, profile factor and applied signed vertical force.
* `Gravity_Source_Components_Totals.csv` — category totals.

## Engineering meaning

`OpenSees_Complete_Model_Data_V118.json` contains the converted source `unfactored_patterns`, `load_provenance`, and the model-level gravity load totals. The module applies the **selected full gravity or seismic preload profile** using the same source function as the model, sums the unfactored source entries after multiplication by current profile factors, then checks all component and pattern totals against the independently assembled nodal load vectors.

For **1.0DL + 1.0LL**, floor and roof live are included at 100%, separately from independent 0.3 seismic mass factors. Self-weight is generated from source geometric beam/column/brace areas and lengths, shell areas and thicknesses, weight densities, and source pattern multipliers. Source pressures, beam distributed loads, joint loads, floor finishes, wall loads and partitions are included only if present in the ETABS extraction. Missing or unsupported ETABS source load types are **not presumed to be present**.

With the same applied static vertical loads and no omitted support load, `sum(nodeReaction(n,3))` over all restrained nodes must balance this applied total (sign conventions checked). Reducing 76 supports to 32 can strongly affect *individual reactions*, but must **not** reduce the gravity load applied to the model. The 97-node continuous-wall support case is likewise independent.

## ETABS global gap triage

Previously observed ETABS total = 311,367.3139 kN; OpenSees = 320,047.788933 kN. Difference = 8,680.475033 kN. The earlier separate ETABS Material List/offset review reported beam offset weight 8,652.444 kN; residual 28.031 kN.

These numbers are a *prior reported benchmark*, **not a new live ETABS verification**. The current source weight defaults to `GROSS_SECTION_LENGTH`. `ETABS_OpenSees_Beam_Weight_Reconciliation.json` exports source-specific ETABS `GetEndLengthOffset` records and a candidate clear-length weight deduction. This module displays the resulting hypothetical total as **POTENTIAL_ONLY**, not as a performed fix.

Before setting `etabs_beam_weight_policy=ETABS_BEAM_CLEAR_LENGTH` and `etabs_clear_beam_weight_confirmed=true`, verify **per beam** from native ETABS Material List, actual Self Weight Option, source clear-length/end offsets, original weight density, and whether overlapping joint solids/steel corner geometry are counted. Do not also enable `joint_volume_weight_policy=VERIFIED_SINGLE_OWNER`: it would subtract joint weight twice. Compare remaining gaps by material category, floor and support region before changing stiffness or tuning structural parameters. Rigid end zones, shell stiffness factors and wall base restraints redistribute reactions and deformations, not the conservation law for total gravity.

## Validation gates

1. Completed load ledger and consistent source factors.
2. `load_provenance` sums exactly to assembled `gravity_by_pattern_kN` and selected `total_downward_load_kN`, with tolerance.
3. Assembled selected load equals **solver applied load**.
4. Solver restrained reaction sums match applied source load (numerical equilibrium).
5. Original ETABS matching model identity, the exact `1. DL + LL` results, independent base FZ and separate source-material weight by category.
6. Native beam weight option and intersections evidence before changing any physical self-weight.
7. Nodal and foundation-region reactions, vertical displacement, source wall shell modifiers and support assignment checked separately. A small global difference does not prove all these gates pass.

The `SOURCE_LEDGER_RECONCILED_NOT_ETABS_VALIDATED` label deliberately means only (1)–(3) source-level evidence passed. It is NOT an NBC105:2025 code acceptance or completed ETABS/OpenSees model validation.

Related model definitions: `components/model/assembly.py`, `components/model/beam_weight_convention.py`; response reactions: `components/gravity/reaction_case_registry.py`.

Author: ChatGPT GPT-6, 2026-11-09.
