# Gravity comparison: ETABS and OpenSees

For this project's requested comparison, select `GRAVITY_1.0D_1.0L` in the case-review window. The source patterns classified as dead and live (including assigned roof live) are applied at 1.0. The source self-weight multiplier remains part of the extracted unfactored pattern: do not add self-weight a second time. Unknown pattern types block the profile; review their ETABS load-pattern assignments.

The profile controls the gravity **preload**, not the independently assembled seismic mass. NBC 105:2025 section 5.2, Table 5-1 identifies 0.60 for storage live load, 0.30 for other live load and zero roof live load in seismic weight; applicability and occupancy must be verified. See the [official NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). These mass fractions do not replace the user-selected full-live gravity comparison. The 1.0D+1.0L comparison is a project-selected diagnostic, not a claim about every required design load combination.

## Explicit separation: independent gravity versus earthquake analyses (2026-11-07)

The **standalone Gravity GUI** defaults to `GRAVITY_1.0D_1.0L` and applies **1.0 Dead + 1.0 Live + 1.0 assigned Roof Live**. Roof live is included only when the source ETABS model actually contains that load. The GUI now derives the total from `unfactored_patterns` in the exact model export, not from old generated `GRAVITY_GUI_INPUTS` metadata that might reflect 0.30 live. A mismatch with an entered load total is rejected before the run.

Earthquake workflows (ESM, modal/eigen, MRSM and response-history) **do not use this full-gravity comparison profile**. The default model `mass_factors` retain 1.0 for dead, 0.30 for ordinary live and 0 for roof live, subject to reviewed NBC 105:2025 occupancy/load classifications. Storage live fractions may differ, and independent full-gravity checks must not overwrite those mass factors. The configured gravity preload used with P-Delta/seismic calculations is a separate analysis state, which must also be reviewed for the intended load combination; it is not automatically the full 1.0D+1.0L case.

| Run purpose | Dead gravity | Ordinary floor live gravity | Assigned roof live gravity | Ordinary floor live seismic mass | Roof live seismic mass |
|---|---:|---:|---:|---:|---:|
| Independent ETABS/OpenSees gravity comparison | 1.00 | 1.00 | 1.00 | Separate/not changed | Separate/not changed |
| Default earthquake model `AS_CONFIGURED` | 1.00 | 0.30 | 0.00 | 0.30 | 0.00 |

**Important:** The gravity GUI passes `OPENSEES_GRAVITY_PROFILE` only to its own subprocess. It does not set or persist a process-wide environment override in the parent application. A freshly generated model that preloads gravity is **not preloaded a second time** by the standalone GUI. Inspect `Gravity_Result_V110.json` for `gravity_profile` and the recorded solver report, and compare with a matching ETABS static gravity case. The software does not assert automatic ETABS force/displacement equivalence.

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

## Direct ETABS API comparison in the existing gravity GUI

The integrated `Extract ETABS + compare gravity` button uses the existing
`Gravity_Result_V110.json` and the attached, already analyzed ETABS session.
It first checks that the source EDB in the OpenSees export manifests is
identical to the active ETABS source; checks that the user-selected LINEAR ADD
gravity combination consists of exactly Dead(1.0) and Live(1.0); extracts a
single concurrent global BaseReact FZ; checks source-case additivity; and reads
individual restrained support reactions and displacements. It records missing
supports, local joint axes, and cases without valid result rows as evidence
gaps, never fabricating results.

Results are written under
`<gravity results>/Gravity_ETABS_OpenSees_Direct/` and automatically selected
for the existing `Bundle gravity evidence ZIP` workflow. The comparison is
immediate, but a successful global reaction check does not certify slab-beam-
column-wall load distribution or matched displacement/member stiffness.

No separate gravity API application is needed. See
[gravity_etabs_direct.py](../source/components/validation/gravity_etabs_direct.py.md).

## Diagnostic comparison using a separate `Gravity.EDB` and repeated evidence exports

If ETABS has a deliberately saved gravity-only **copy** open (for example
`Gravity.EDB`) instead of the exact source EDB referenced by the OpenSees export,
the GUI normally refuses to compare their results. To examine this diagnostic
scenario, check **Use a separately saved ETABS gravity-copy EDB** and confirm the
warning. This enables the live OAPI extraction from the **currently open**
ETABS model, without opening, modifying, saving or running it.

The output records the original export EDB path and SHA256 (if accessible),
the active ETABS EDB path and SHA256, and
`model_identity_status=ALTERNATE_EDB_UNVERIFIED`. The comparison can display
a difference in gravity base reactions, but **must not certify structural
equivalence or identical loading/geometry**. A separate review must compare
source model geometry, weight, load patterns, boundary restraints, frame and
wall sections, and stiffness before treating the difference as a model
conversion error. The checkbox defaults OFF each time the GUI is launched.

The gravity evidence button now creates versioned directories and archives
(`Gravity_ETABS_OpenSees_Evidence.zip`, then
`Gravity_ETABS_OpenSees_Evidence_V02.zip`, etc.) in the selected comparison
folder. Previous ZIPs/directories remain unchanged. Upload the latest
archive containing the direct comparison; earlier packages remain auditable.

## Dedicated ETABS instance for gravity comparison (2026-11-07)

The **Extract ETABS + compare gravity** action now defaults to
**Open ETABS in a new dedicated instance; close after comparison WITHOUT saving**.
This resolves the COM `GetActiveObject` attachment error without taking over an
existing ETABS window. The GUI allows an explicit **EDB to open**; leaving it
blank selects the exact EDB recorded in the OpenSees export provenance.
An optional ETABS.exe path can be provided for a specific installed version;
otherwise the registered ETABS API executable is used.

The module calls CSI `CreateObjectProgID` (or `CreateObject` when a path is
provided), `ApplicationStart`, `SapModel.File.OpenFile`, extracts the
already-analyzed exact gravity combination, and calls
`ApplicationExit(False)` in a `finally` block. If the EDB cannot be opened
or the analysis results are unavailable, it reports a failure and still closes
only the instance it created. The source EDB is **never saved**; an unrelated
already-open ETABS instance is **never closed**.

A deliberately different gravity-copy EDB may still be selected using the
explicit diagnostic consent checkbox. That result remains
`ALTERNATE_EDB_UNVERIFIED`. If the EDB is currently open in another ETABS
process, exclusive file locks or licensing may prevent a second instance
from opening it; close the other copy or use a separate already-analyzed
gravity EDB and record that difference.

**Important:** Opening an EDB does not compute new load cases. The case
`1. DL + LL` must already have usable analyzed Dead and Live results; otherwise
the operation stops instead of silently running or saving an analysis.

## Detailed action logging (V03 evidence follow-up)

All direct ETABS extraction steps are recorded in the existing Gravity GUI
**Run log** tab and in
`<gravity output>/Gravity_ETABS_OpenSees_Direct/ETABS_Gravity_Extraction.log`
and `ETABS_Gravity_Extraction_Events.jsonl`. Events record selected source
EDB, launched/attached ETABS mode, original EDB identity, the selected
Dead(1)+Live(1) combination, advisory ETABS analysis case status codes,
saved global base reaction, independent Dead/Live base reactions,
restrained joint inventory counts, missing joint-force/displacement data,
comparison results, export artifacts, failures and owned-instance shutdown.
Traceback is preserved when an API operation fails. The evidence ZIP includes
both log files if they exist.

The **case-status code is advisory**. A case with status other than 4 is not
immediately rejected if actual, finite stored reaction results are available;
on the other hand, a status code alone is not proof of usable results. Missing
`BaseReact` values still block comparison, with the exact case and API
status included in the diagnostic. No ETABS analysis is automatically run and
no source EDB is modified or saved.

For the uploaded `Gravity_ETABS_OpenSees_Evidence_V03.zip`, OpenSees records
320047.788933 kN applied and support reacted, and the archive still lacks
`etabs/etabs_gravity.json`. The model comparison remains pending a successful
ETABS extraction.

## Run missing ETABS gravity results on a verified source-model copy

The user-confirmed **If gravity results are missing, run ETABS on a private COPY**
setting defaults on in the gravity GUI. The selected EDB defaults to the
**original source EDB captured during the ETABS→OpenSees export**, not
`Gravity.EDB` or an unrelated model currently open in ETABS. If that source
file is inaccessible, execution fails closed. Any different EDB still requires
the alternate-model diagnostic consent.

To avoid changing the original EDB, the program creates
`<gravity output>/Gravity_ETABS_OpenSees_Direct/ETABS_Gravity_Working_Copies/run_<id>/<original filename>.EDB`
and verifies its SHA256 matches the selected original before opening.
ETABS is launched as an owned instance, the selected existing `1. DL + LL`
combination is read, and *only if its actual BaseReact result is missing*,
the program calls `SapModel.Analyze.RunAnalysis()` on that working copy.
This may run **all enabled cases**, including expensive histories: it
preserves ETABS case settings rather than silently disabling other cases.
It then attempts the same extraction again, exports direct reactions, and
closes only its owned instance without saving the original. Analysis
sidecars and the analyzed working EDB remain isolated for review.

The analysis of an isolated copy is labelled
`WORKING_COPY_ANALYZED_FROM_SOURCE_EDB`, with original EDB hashes
recorded before/after; this alone does not certify section/geometry/
load-distribution equivalence. If real results are still missing or
RunAnalysis returns nonzero, the log records the exact API error without
fabricating gravity reactions. User must review the original model's analysis
status and any unsupported cases.

For the screenshot supplied 2026-11-07, a *separately analyzed* ETABS model
shows `1. DL + LL` Base Reaction FZ = **311367.3139 kN**, versus OpenSees
320047.788933 kN. That image demonstrates the gravity force discrepancy,
but those files are not yet established as identical source models.
ETABS direct OAPI extraction must preserve explicit model provenance.

## Review ledger

| Area | Evidence reviewed | Status / limitation |
|---|---|---|
| Gravity factors | `components/model/assembly.py`, `components/gravity/storey_loads.py` | Source review and synthetic profile regression; no ETABS run. |
| Mass factors | Assembly maintains `mass_factors` separately | Synthetic test checks the existing mass payload is unchanged; project seismic mass not reconciled. |
| Reports | Assembly-time ledger and standalone gravity GUI source | Profile overrides can make these reports stale; comparison must use matching run evidence. |
| Load path and ETABS agreement | No matching independent pattern/beam results supplied | Not evaluated; no assertion of physical equivalence. |
