# Aw-X engineering validation gates

All items below must be completed **before** promoting Aw-X=2.073174515 m² beyond preferred engineering interpretation.

- [ ] Obtain SHA256 of selected original ULS EDB and original calculation workbook; reconcile with saved export and ULS/SLS model state.
- [ ] Extract source first-storey ETABS wall-area object IDs, polygon vertices, thicknesses, materials, openings, and correct source units. Use read-only API.
- [ ] Establish that there are exactly **two** separate parallel X-direction wall lines, each 12m long, and identify their plane coordinates. Never combine them into 24m by adding parallel lengths.
- [ ] Confirm uninterrupted RC material and reinforcement transfer at the 6m bay/grid interface and opening-head spandrels; distinguish mesh seams from genuine joints.
- [ ] Confirm **two door openings per 12m wall**, each 2m wide x 2.3m tall, and determine their actual minimum horizontal first-storey net concrete area. If the two doors are at different heights, test the minimum section rather than blindly subtracting both.
- [ ] Confirm NBC H=95m from seismic base to roof under basement and story geometry definitions, not an elevation label.
- [ ] Independently check three Y walls, each 6m and no door opening; validate intersections and flanges.
- [ ] Calculate Aw under both 4×6m and 2×12m grouping, record engineer's selected physical grouping, date and justification.
- [ ] Keep legacy `1.930637m²` OpenSees continuous-pier result as diagnostic; no silent source workbook replacement.
- [ ] Compare adopted empirical period ×1.25 with independently obtained Rayleigh and source-matched ETABS/OpenSees mode periods; confirm NBC analysis method eligibility and force scaling.
- [ ] Review coupling-beam and door-edge strength/detailing separately under NBC 105 and relevant RC codes.

**Current status: OPEN_ENGINEERING_REVIEW**; no full EDB / finite-element / experimental validation certified.
