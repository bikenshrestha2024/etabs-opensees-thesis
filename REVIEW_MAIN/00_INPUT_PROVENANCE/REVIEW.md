# RV-PROV-001 — EDB and workbook source identity
**Priority:** P0 | **Status:** OPEN_HIGH

**Observed:** Source workbook `SCALING SUMMARY!B14/B15` carries Aw-X≈1.9582936 m² and Aw-Y≈2.2030803 m², but `B4` refers in several runs to a different saved SERVICE model while the selected EDB is ULTIMATE. A later ETABS Linked output said SAME_EDB_PATH_REFERENCE; a path match alone does not prove identical bytes or analysis state. Git LFS pointers surfaced when ZIP exports omitted the original workbook.

**Engineering judgment:** Matching an EDB pathname, nominal wall thickness or a copied Excel calculation is not validation of the loaded model. A ULS/SLS comparison is invalid if gravity, mass, diaphragm, material modifiers, case settings or geometric state differ.

**Required evidence:** EDB and workbook SHA256 before/after, export manifest and source-cell references; actual ETABS OAPI current model path, saved file hash, material sections, load patterns, mass source, end offsets, support DOFs, case settings and timestamp; generated OpenSees model and script revision; precise ULS/SLS distinction.

**Acceptance:** independent identity and configuration checks, zero silent substitutions, explicit mapping for each model state. Preserve original sources read-only.
