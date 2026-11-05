# Gravity comparison: ETABS and OpenSees

For this project's requested comparison, select `GRAVITY_1.0D_1.0L` in the case-review window. The source patterns classified as dead and live (including assigned roof live) are applied at 1.0. The source self-weight multiplier remains part of the extracted unfactored pattern: do not add self-weight a second time. Unknown pattern types block the profile; review their ETABS load-pattern assignments.

The profile controls the gravity **preload**, not the independently assembled seismic mass. NBC 105:2025 section 5.2, Table 5-1 identifies 0.60 for storage live load, 0.30 for other live load and zero roof live load in seismic weight; applicability and occupancy must be verified. See the [official NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). These mass fractions do not replace the user-selected full-live gravity comparison. The 1.0D+1.0L comparison is a project-selected diagnostic, not a claim about every required design load combination.

## Procedure and limits

1. Export the same ETABS model and verify the load-pattern inventory, slab and wall connectivity, local axes, restraints and self-weight multiplier. Compare the same individual patterns and include roof live in both models only when assigned.
2. Select the comparison profile before a fresh model run. This selection currently affects **subsequent analyses in the application session**, not only gravity; restore `AS_CONFIGURED` before modal or time-history runs unless a different preload has been deliberately reviewed. Seismic mass remains unchanged.
3. Run a matching ETABS static case and OpenSees analysis with matching stiffness modifiers, diaphragm/mesh, releases, P-Delta setting, units and load factors. Compare total applied load, support reactions, nodal vertical displacement and beam end actions with matching axes and sign conventions; compare story and pattern totals separately.
4. The exported source ledger and slab formula workbook are generated at assembly using configured gravity factors. They do not automatically update for a later profile override. Do not compare those applied totals with an overridden run; use the actual `[GRAVITY PROFILE]` and `Gravity_Profile_*` report and reconcile separately. The standalone gravity GUI's manually supplied expected load must also match the selected profile. A global equilibrium pass does not prove identical slab-to-beam distribution.

No project ETABS gravity reactions or matched case results were provided or compared here. The project's live-load factor and roof assumptions, self-weight, actual case identity and beam load-path equivalence remain to be verified. The EDB files in the four ultimate configuration folders and supplied story-drift workbooks do not by themselves establish a matching gravity comparison.

## Review ledger

| Area | Evidence reviewed | Status / limitation |
|---|---|---|
| Gravity factors | `components/model/assembly.py`, `components/gravity/storey_loads.py` | Source review and synthetic profile regression; no ETABS run. |
| Mass factors | Assembly maintains `mass_factors` separately | Synthetic test checks the existing mass payload is unchanged; project seismic mass not reconciled. |
| Reports | Assembly-time ledger and standalone gravity GUI source | Profile overrides can make these reports stale; comparison must use matching run evidence. |
| Load path and ETABS agreement | No matching independent pattern/beam results supplied | Not evaluated; no assertion of physical equivalence. |
