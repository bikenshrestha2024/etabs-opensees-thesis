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

**Restriction:** The provided CSV format is a required trusted source adapter. This module does not parse `.EDB` directly or automatically recover every response node from the OpenSees recorder binary. The current native ETABS COM application and OpenSees recorders still require actual source node/step mapping. It does *not* yet provide a native Windows end-to-end automatically verified ETABS-vs-OpenSees compliance comparison.

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
