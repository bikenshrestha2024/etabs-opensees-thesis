# Stage 02 — source-approved frame reinforcement

The nonlinear research material adapter can now read a **reviewed CSV** (`approved_frame_reinforcement_csv` in the exploratory RunConfig) and apply only its frame reinforcement geometry to the existing three fiber-section templates. The source file is copied into the isolated model; it must declare its original SHA-256 and `review_status=APPROVED_FROM_ETABS_DRAWINGS`. Every defined fiber section must be present, and width/depth must match the current configuration.

Columns: `section_key,width_mm,depth_mm,cover_mm,bar_diameter_mm,bars_per_side,tie_diameter_mm,tie_spacing_mm,source_file_sha256,reviewed_by,review_status`.

**Limitations:** This is not an automatic ETABS design API extraction. The user must export and verify a reinforcement schedule. `bars_per_side` is an equivalent rectangular layer description, not arbitrary actual bar coordinates. Tie spacing is preserved as evidence but **not** turned into fictitious Concrete01/ConcreteCM confinement gain. The wall core/boundary bar schedules, special details and section layout remain outstanding. Existing template behavior remains unchanged unless a valid register is supplied.

PEER 2015/12 supplies the experimental wall-material methodology, not project reinforcement.
