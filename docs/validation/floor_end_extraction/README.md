# NBC 105:2025 — Floor-end torsion extraction and ETABS/OpenSees comparison

**Read first:** [Government of Nepal NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf), **printed page 34**, §§5.4.2.1–5.4.2.2 and Figure 5-3.

## What this implementation does

The standalone `extract_torsion_data.py` uses **independently exported, already-matched nodal geometry and signed displacement CSVs** from either ETABS or OpenSees. The existing `torsion_check.py` is retained. The converter:

1. Requires a single named ULS or SLS source model.
2. Uses **actual story labels**, not approximate Z rounding alone.
3. Requires `is_perimeter=true` evidence for the physical exterior floor edge; outrigger/core connection nodes are not automatically floor ends.
4. For **X** excitation, finds min/max **Y** perimeter ends, with matched along-building **X** coordinate; for **Y** excitation it uses min/max **X** ends with matched **Y** coordinate. All matching opposite-end pairs are checked, not one arbitrary corner.
5. Uses only **signed Ux for X** or **signed Uy for Y**, at the **same analysis step and centered-CM load case**. It never uses `sqrt(Ux²+Uy²)` and never combines independent X/Y maxima or unrelated peak times.
6. Rejects inputs labelled time history/CQC envelopes/±5% eccentricity as automatic §5.4.2 evidence. These are relevant separate checks, but cannot substitute for the centered-CM code screening case.
7. Produces `Floor_End_Pairs.csv`, `Floor_End_Governing.csv`, `Floor_End_Provenance.json`, with source hashes, input node IDs, actual coordinates, pair offset, ratio and verdict. Missing opposite-end matches become `NOT EVALUATED`, never PASS.

**Current status:** The ETABS direct API adapter can obtain **signed joint displacements for an explicitly reviewed centered-CM static case and single ETABS step**, using an already-open source .EDB. It still requires reviewed physical perimeter geometry and actual ETABS point identifiers; it does **not** parse EDB binaries, automatically identify every physical floor edge from the EDB, or run analysis. OpenSees results can be read from exported/signed CSV (not raw recorder binary unless first mapped to the specified schema). The ETABS API adapter has **mocked CI tests**, not native Windows ETABS v23 tests. This is not a completed ETABS/OpenSees physical equivalence certification.

**Excel:** The local extractor also writes `Floor_End_Torsion_Review.xlsx`, including status, every valid opposite-end pair, governing per-floor ratios, provenance and a plotted profile showing thresholds 1.5 and 2.5.

### Input CSV formats

Geometry must contain **exactly the required named columns**, with one row per node at a named floor:

```csv
node_id,storey,x_m,y_m,z_m,is_perimeter
A,25,0,0,95,true
B,25,0,20,95,true
C,25,10,0,95,true
D,25,10,10,95,true
```

For X-centered static perturbation, displacement CSV:

```csv
node_id,storey,limit_state,case,axis,step,ux_m,uy_m,centered_cm_load,response_basis
A,25,ULS,X_CENTERED,X,FINAL,0.010,0.0,true,signed_centered_linear_increment
B,25,ULS,X_CENTERED,X,FINAL,0.030,0.0,true,signed_centered_linear_increment
C,25,ULS,X_CENTERED,X,FINAL,0.003,0.0,true,signed_centered_linear_increment
D,25,ULS,X_CENTERED,X,FINAL,0.002,0.0,true,signed_centered_linear_increment
```

**All numbers above are synthetic.** A single story named `25` is illustrative. Different ETABS and OpenSees node tags are allowed; run the extraction separately with each software's *own* geometry CSV and node-response CSV. Independent matching between ETABS/OpenSees spatial locations still requires a separate coordinate-matching audit. Local source EDB remains read-only.

### Directly read an already-open ETABS EDB (optional Windows mode)

1. Open the **identical original model** in ETABS v23 and run the **signed centered centre-of-mass static case**, without accidental eccentricity. Verify its actual load case and select **one real result step**.
2. Use a reviewed ETABS geometry CSV (same `node_id` values as ETABS PointObj, with `is_perimeter=true` only for verified exterior floor-end nodes).
3. Run from the repository root in Windows:
```powershell
python extract_torsion_data.py --geometry "D:\\YourData\\ETABS_Floor_Nodes.csv" --source ETABS --state ULS --etabs-api --edb "D:\\YourModels\\ULTIMATE_MODEL.EDB" --case "ACTUAL_CENTERED_STATIC_CASE" --axis X --step-type Step --step-number 1 --reviewed-centered-cm --output "D:\\YourData\\Torsion_ETABS_ULS"
```

**The `--reviewed-centered-cm` argument is a documented engineering assertion, not automatic verification** of the load's actual application through the center of mass. No results are accepted if a point is missing, a step differs, or the selected ETABS file differs from the active model. Initial static API `StepType`/step number should be checked from ETABS first; the example `Step/1` is not guaranteed to match your specific case. The script restores display units and ETABS result-selection settings, and never opens, saves or unlocks the source EDB.

`ETABS_Signed_Source_Results.csv` is generated automatically for the chosen point set; use it and its SHA256 in the subsequent torsion review. For Service, use your *actual* SLS source EDB and `--state SLS`, not ULS results.

### Run locally, Python 3.12 / Spyder-compatible

```powershell
python extract_torsion_data.py --geometry "D:\\YourData\\ETABS_Floor_Nodes.csv" --responses "D:\\YourData\\ETABS_Centered_Results.csv" --source ETABS --state ULS --output "D:\\YourData\\Torsion_ETABS_ULS"
python extract_torsion_data.py --geometry "D:\\YourData\\OpenSees_Floor_Nodes.csv" --responses "D:\\YourData\\OpenSees_Centered_Results.csv" --source OPENSEES --state ULS --output "D:\\YourData\\Torsion_OpenSees_ULS"
```

Use SLS only with a genuine Service/SLS model and SLS results.

### Geometric interpretation for your asymmetric re-entrant plan

- Use actual slab/diaphragm exterior polygons and edge nodes, **not** every core, wall, outrigger, belt or internal analytical node; one remote projection should not be paired with an unrelated node from another bay.
- Default tolerance for identifying near-end perimeter nodes is `0.05 m`; along-building pairing tolerance is `0.10 m`. These are geometric **matching choices**, not NBC code tolerances. Changing either requires a documented source mesh review.
- A re-entrant gap may leave no corresponding pair. That case is `NOT EVALUATED`; don't create synthetic interpolation without geometry/element interpolation evidence.
- The extreme torsion threshold of 2.5 is a *design configuration gate*. Preserve saved analysis results for diagnosis rather than halting the solver and hiding the source of trouble.
- For genuine **simultaneous bidirectional dynamic XY/YX**, use the full same-time Ux and Uy histories for response envelopes and physical edge checks; do not misuse the §5.4.2 centered static torsion test or compose the maximum of unrelated records/times.

### Known limitations and validation

- Real ETABS v23 native result return-array ordering, floor metadata and OpenSees recorder node mapping must be tested on your Windows installation; the current CSV reader assumes the named schema.
- The perimeter boolean must be certified from source geometry or a reviewed floor polygon. Coordinate extrema in an L-shaped building alone are not sufficient for arbitrary opposite-end selection; the algorithm rejects unaligned edges rather than inventing a line.
- ETABS SLS and ULS geometry may be similar but cracked stiffness and response cases differ; do not mix their displacements or comparison targets.
- The extractor checks all eligible physical pairs but **does not compute a full floor continuum displacement field**. Extra edge points or interpolation may be needed for conclusive design acceptance.
- Passing synthetic tests does not establish project code compliance.

**Unit tests:** `python tests/verify_floor_end_extraction.py`.

**Main components:** `components/validation/floor_end_extraction.py`, `components/validation/torsion_check.py`, and `extract_torsion_data.py`.
