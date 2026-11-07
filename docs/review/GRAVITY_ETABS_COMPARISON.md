# Gravity comparison: ETABS and OpenSees

For this project's requested comparison, select `GRAVITY_1.0D_1.0L` in the case-review window. The source patterns classified as dead and live (including assigned roof live) are applied at 1.0. The source self-weight multiplier remains part of the extracted unfactored pattern: do not add self-weight a second time. Unknown pattern types block the profile; review their ETABS load-pattern assignments.

The profile controls the gravity **preload**, not the independently assembled seismic mass. NBC 105:2025 section 5.2, Table 5-1 identifies 0.60 for storage live load, 0.30 for other live load and zero roof live load in seismic weight; applicability and occupancy must be verified. See the [official NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). These mass fractions do not replace the user-selected full-live gravity comparison. The 1.0D+1.0L comparison is a project-selected diagnostic, not a claim about every required design load combination.

## Procedure and limits

1. Export the same ETABS model and verify the load-pattern inventory, slab and wall connectivity, local axes, restraints and self-weight multiplier. Compare the same individual patterns and include roof live in both models only when assigned.
2. Select the comparison profile before a fresh model run. This selection currently affects **subsequent analyses in the application session**, not only gravity; restore `AS_CONFIGURED` before modal or time-history runs unless a different preload has been deliberately reviewed. Seismic mass remains unchanged.
3. Run a matching ETABS static case and OpenSees analysis with matching stiffness modifiers, diaphragm/mesh, releases, P-Delta setting, units and load factors. Compare total applied load, support reactions, nodal vertical displacement and beam end actions with matching axes and sign conventions; compare story and pattern totals separately.
4. The exported source ledger and slab formula workbook are generated at assembly using configured gravity factors. They do not automatically update for a later profile override. Do not compare those applied totals with an overridden run; use the actual `[GRAVITY PROFILE]` and `Gravity_Profile_*` report and reconcile separately. The standalone gravity GUI's manually supplied expected load must also match the selected profile. A global equilibrium pass does not prove identical slab-to-beam distribution.

No project ETABS gravity reactions or matched case results were provided or compared here. The project's live-load factor and roof assumptions, self-weight, actual case identity and beam load-path equivalence remain to be verified. The EDB files in the four ultimate configuration folders and supplied story-drift workbooks do not by themselves establish a matching gravity comparison.


## Upload-ready comparison folder (new gravity GUI action)

In `10_GRAVITY.py` (or `03_GRAVITY.py` compatibility launcher), select the exact OpenSees model script and set **All outputs folder** to a writable analysis-results directory. This is now initially suggested as `OpenSees_Analysis_Results/Gravity_Results` beneath the application working directory, but it remains user-selectable. The new **Comparison bundle output folder** can be left blank (defaults to `<gravity outputs>/Gravity_ETABS_OpenSees_Comparison`) or explicitly selected. Supply **ETABS gravity results JSON** if already extracted for the same 1.0D+1.0L case. After the OpenSees run, click **Bundle gravity evidence ZIP**.

This creates:

```text
<chosen comparison folder>/
  Gravity_ETABS_OpenSees_Evidence.zip          <-- upload this ZIP
  Gravity_ETABS_OpenSees_Evidence/
    EVIDENCE_MANIFEST.json                     <-- SHA256, source paths, missing/oversized files
    README_UPLOAD_FIRST.txt
    source/                                     <-- ETABS-export mapping/load and connectivity evidence, if available
    opensees/Gravity_Result_V110.json          <-- raw solver state
    opensees/nodes.csv                          <-- XYZ, UX/UY/UZ, rotations
    opensees/reactions.csv                      <-- support RX/RY/RZ
    opensees/local_forces.csv                   <-- raw available 12-component frame end actions
    etabs/etabs_gravity.json                    <-- only when an ETABS JSON was supplied
```

The source audit selection also includes actual model configuration and model data, load conversion, diaphragm and wall connection evidence, source load-detail CSV, story load-breakdown CSV, gravity profile files, beam end-action CSV and the V118 gravity check wherever present. The manifest flags each file that is missing or exceeds the user-selectable per-file archive limit (default 40 MiB). Do not interpret an omitted file as an empty load or zero reaction. The bundle **does not generate** unavailable ETABS frame/shell results from the EDB; those must be exported independently from ETABS.

### Optional command-line equivalent

```powershell
python -m components.gravity.comparison_bundle `
  --export-dir "D:/Thesis Opensees/Etabs Nodes Export" `
  --gravity-dir "D:/Thesis Opensees/Etabs Nodes Export/OpenSees_Analysis_Results/Gravity_Results" `
  --etabs-json "D:/Thesis/Gravity/etabs_gravity.json" `
  --output-dir "D:/Thesis/Gravity/Gravity_Comparison_Upload_01"
```

Omit `--etabs-json` when unavailable; the evidence ZIP will explicitly report that comparison-side absence. Never commit project-specific large EDB, raw files or user output bundles to public GitHub.

**Comparison acceptance remains blocked** until the actual source-model identity, gravity case, ETABS mass/weight, support restraints, stiffness modifiers, units, base reactions, common-node deflections, frame end actions and wall force resultants are reconciled. The generated bundle is only an evidence-capture workflow, not automatic verification or an NBC compliance certificate.

## Review ledger

| Area | Evidence reviewed | Status / limitation |
|---|---|---|
| Gravity factors | `components/model/assembly.py`, `components/gravity/storey_loads.py` | Source review and synthetic profile regression; no ETABS run. |
| Mass factors | Assembly maintains `mass_factors` separately | Synthetic test checks the existing mass payload is unchanged; project seismic mass not reconciled. |
| Reports | Assembly-time ledger and standalone gravity GUI source | Profile overrides can make these reports stale; comparison must use matching run evidence. |
| Load path and ETABS agreement | No matching independent pattern/beam results supplied | Not evaluated; no assertion of physical equivalence. |
