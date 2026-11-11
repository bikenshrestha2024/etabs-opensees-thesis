# Source guide — grouped_wall_aw.py

## Purpose
Distinguish *minimum first-storey horizontal solid wall area* (net of the door opening) from *whole connected structural wall length* in NBC 105:2025 §5.1.2. The current OpenSees continuous-through-storey pier diagnostic treats each pier separately and is retained as a **separate** geometry diagnostic, never silently overwritten.

## Normative code and historical explanation
- Government of Nepal DUDBC, **NBC 105:2025** §5.1.2, pp. 29–30: `Aw = Σ Awi[0.2 + (min(Lwi/H, 0.9))²]`; area described as effective wall cross section in the first storey, length as the structural wall length in the earthquake direction. This code does **not** independently prescribe how to group two piers around door openings.
  Official listing: https://dudbc.gov.np/pages/24231978/
- ICBO, **1997 Uniform Building Code**, §1628 definition of `Ae` as minimum cross-sectional area at any horizontal first-storey plane; `De` as overall first-storey lateral-wall length, §1630.2.2 Equation (30-9). Historical interpretive precedent, **not** an additional Nepalese design mandate.
  Original reference: https://peshtaz.com/wp-content/uploads/2019/10/UBC-1997-Volume-2.pdf
- **SEAOC Seismic Design Manual, Vol. I (1997 UBC)**, Example 19, §1630.2.2: front-wall example with four 10 ft openings in a 60 ft wall; `Ae=(60-4×10)×(7.63/12)` ft² but `De=60 ft` (with 0.9 ratio cap). The example is a **masonry wall**, not experimental proof of concrete coupling, and the opening geometry/building differ from this thesis.
  Example: https://www.scribd.com/document/819936779/SEAOC-Seismic-Design-Manual-Vol-1-Code-Application-Examples
- IS 1893 (Part 1):2016 §7.6.2 contains related empirical wall-area formula. IS 456/13920 and ACI 318 address detailed structural modeling and design; ASCE 7's later approximate-period rules are not interchangeable with NBC 105.
- Do not claim there is a Nepal-specific accepted commentary approving the precise door grouping. Engineer judgment is required.

## User illustrative dimensions and numerical reconciliation
- Assumed four separate *connected* 6.0 m long X wall groups, each 0.6 m thick and with a 2.0 m **floor-to-spandrel door opening** (height 2.3 m, assumed lower critical section), building `H=95 m`.
- `Awi,X=(6-2)*0.6=2.4 m²`; `Lwi,X=6.0 m`; sum `Aw,X=1.9582936288 m²`.
- Assumed three unperforated 6.0 m long Y walls, 0.6 m thick: `Aw,Y=2.2030803324 m²`.
- Continuous-pier diagnostic `Aw,X≈1.9306371 m²` is from the actual user's saved export; its exact value need not match a synthetic rectangular doorway test. It is not the adopted `Aw`.
- Doorway head/spandrel/coupling behavior must be modeled in the finite-element system; do not add wall above door as separate `Awi` in this formula.

## API & units
- `wall_aw_example(...)` returns explicitly *illustrative* X/Y areas in m², never approved source evidence.
- `grouped_wall_aw(profile, H_m, groups)` uses source first-storey elevation slices from `_wall_aw_profile`, and explicit groups with id, X/Y axis, wall plane in m, thickness in m, and absolute along-wall start/end coordinates in m. It merges shell intervals, computes the **minimum** source horizontal area per group across first-storey slices and weights by the overall group length. It rejects overlapping groups, any unmapped source wall material, nonfinite geometry, and groups with zero first-storey concrete sections. Returns a traceable engineering-review candidate, **not** an accepted NBC input.
- `source_matched_grouping(...)` reads **only** optional local `NBC105_Wall_Grouping_Review.json` in the ETABS export directory. Require exact original EDB byte SHA256, generated model byte SHA256, source limit state and seismic height. The program does **not** invent 4 X/3 Y groups from source labels. Example schema:
```json
{
  "source_edb_sha256": "<actual SHA256 of original native EDB>",
  "assembled_model_sha256": "<actual SHA256 of OpenSees_Complete_Model_Data_V118.json>",
  "limit_state": "ULS",
  "height_m": 95.0,
  "wall_groups": [
    {"id": "X1", "axis": "X", "plane_m": 0.0,
     "thickness_m": 0.6, "start_m": 0.0, "end_m": 6.0}
  ]
}
```
The wall groups above are **schema illustration only**: do not reuse coordinate values without checking the actual ETABS export. The reviewed manifest must include **every** relevant first-storey wall group, including Y walls. The source profile is compared slice-by-slice, and missing wall segments prevent adoption of the candidate. Missing, mismatched or invalid manifests leave pre-existing continuous-pier diagnostic untouched and record the problem.

## New ESM GUI workflow
In the ESM module click **Create doorway wall Aw grouping REVIEW template**. The program writes `<selected ETABS export>/REVIEW_MAIN/02_ESM/NBC105_Wall_Grouping_TEMPLATE.json` containing the current EDB and assembled-model SHA256, NBC seismic wall height, all first-storey source shell slices, and an **empty** `wall_groups` array. It cannot be consumed as an adopted candidate. After independently reviewing the native ETABS wall IDs, planes, exact first-storey spans and connection above each door, create `<selected ETABS export>/NBC105_Wall_Grouping_Review.json` with only `source_edb_sha256`, `assembled_model_sha256`, `limit_state`, `height_m` and the **complete** reviewed `wall_groups` list. Re-run **Sync from OpenSees model**. Check new candidate and legacy pier values separately in the generated sync JSON/Excel and the ESM log; none is a code PASS without engineering sign-off. If the original ULS or SLS EDB has been modified, regenerate the export and grouping evidence; never copy a manifest across different source SHA hashes.

## Safety / side effects
Pure computation and optional local file read. No EDB modifications, no Excel edits, no OpenSees frame/wall stiffness changes, no native dynamic solver operations, no approval. The source-matched grouped result is surfaced under `grouped_wall_aw_review` in sync JSON. It may be shown as a reviewed candidate; downstream code may NOT promote its status to physical equivalence or code acceptance. Original Excel-linked adopted value remains authoritative only where **same EDB/limit state and workbook provenance** have independently been verified.

## Tests
`python -m unittest discover -s tests -p 'test_grouped_wall_aw_ubc_seaoc.py' -v`; synthetic test includes 4 X doorway bays, 3 Y solid walls, overlap/unassigned source material, stale EDB/model source fingerprints and old continuous-pier diagnostic preservation. Native ETABS source geometry/spandrel and ULS/SLS acceptance remain unverified until the user's Windows source audit.
