# Solved gravity case-reaction registry

Source: `components/gravity/reaction_case_registry.py`.

## Purpose

Display **two separate physical quantities** in the gravity GUI:
1. `Applied downward gravity load (kN)`, independent of the number of support nodes, obtained from the current complete load-pattern and self-weight ledger (`GRAVITY_1.0D_1.0L` or `AS_CONFIGURED`). It is never overwritten by a reaction.
2. `Solved vertical support reaction (kN)`, which is the independently calculated **sum of OpenSees `nodeReaction(tag,3)` over the actually restrained nodes of a completed gravity analysis**. Its display switches with the 32, 76, or 97 node strategy, provided that case has been solved for the same model and load profile.

`checked_reaction_result` checks success, exact scenario, profile, model path, unique node count, complete finite reaction rows, nodal-versus-report reaction summation and finite total load. `register_case` records SHA256 of the selected model script and a result path in `Gravity_Case_Reaction_Index.json` under the selected output root. `current_case` re-verifies the saved run and model SHA256 each time the GUI selection changes and returns no result if missing, changed, stale or invalid. Older unindexed results are not assumed valid.

## Three support modes

* `ETABS_NONZERO_REACTION_DIAGNOSTIC` — user-confirmed 32 OpenSees nodes; this is a **diagnostic FZ-filtered assumption**, not verified native ETABS support equivalence.
* `ETABS_SOURCE_SUPPORTS` — original 76 mapped supports.
* `CONTINUOUS_WALL_BASE_FIXED` — independent 97-node continuous wall base strategy.

The same applied gravity loads are used for all three modes, assuming identical full-gravity profile and source model. The support reaction changes between modes because force distribution changes; if complete converged static gravity runs are in global equilibrium, **their summed vertical reactions should each equal their applied gravitational load within numerical tolerance**. The selection of reaction-bearing support nodes cannot be used to change mass, self-weight or applied loads.

## Safety and verification

* Never use the last run's total when switching to an unrun case; show `Not analyzed for this case`.
* Never reuse reactions from another model, gravity profile, support strategy, number of supports or modified model script.
* Show explicit equilibrium screening but never upgrade it to ETABS validation, even if total reactions agree.
* Full source-load agreement, wall-region forces, displacement, source support restraints, beam-weight conventions and wall stiffness modifiers remain separate engineering gates.
* Keep each native per-node reaction in `Gravity_Result_V110.json`; the registry only indexes its verified sum, it does not modify model data.
* The single 32-node result uses `Gravity_Reaction_Diagnostic/<timestamp>`. Both 76/97 cases retain their isolated `Gravity_Wall_Base_Comparison/<timestamp>/<mode>` output folders.

## Sources

* [OpenSeesPy reactions command](https://openseespydoc.readthedocs.io/en/latest/src/reactions.html)
* [OpenSeesPy nodeReaction](https://openseespydoc.readthedocs.io/en/latest/src/nodeReaction.html)
* [Gravity reaction filter policy](../../../review/GRAVITY_REACTION_FILTER_DIAGNOSTIC.md)

Changes authored by ChatGPT GPT-6; do not infer provenance for historical commits.
