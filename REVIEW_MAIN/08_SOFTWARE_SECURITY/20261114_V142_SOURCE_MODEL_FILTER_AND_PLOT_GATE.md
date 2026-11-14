# V142 cross-stage source SHA and plot safety gate

Date: 2026-11-14. Status: software integrity implemented; native structural agreement remains unresolved.

**Confirmed source issue:** `components/validation/case_review.py::collect` located gravity, ESM, MRSM, linear and nonlinear saved results across several canonical and legacy folders, and generated one chart without checking that different saved files belonged to the selected serialized model. Historic results could be displayed alongside a different source model's drift/deflection.

**Fix:** `saved_case_identity.py` hashes the current selected `OpenSees_Complete_Model_Data_V118.json` and identifies a response's explicit model hash from the case's `00_INPUT_SOURCE/CASE_MANIFEST.json`, MRSM result JSON or the ESM source META file. When a known mismatch is found, that saved response is **excluded from the V142 graph** and recorded in `issues` with the two full fingerprints and exact file path. A missing digest is retained but marked `NOT_VERIFIED`. Matching serialized hashes say `MATCHED_SERIALIZED_MODEL_SHA_NOT_ETABS_EQUIVALENCE`; this does not prove physical match to original ETABS EDB.

**Reports:** `All_Case_Review_V142.xlsx`, `.json` and plots still save under `09_SOFTWARE_DIAGNOSTICS/CASE_REVIEW_V142`. JSON reports `selected_serialized_model_sha256` and `source_mismatch_excluded_count`. No original model file or response is changed.

**Known limits:** A current single-export comparison cannot automatically combine different ULS/SLS EDB stiffness configurations, even when their site, grid and story count are equal. Unverified historical files still appear for human review but may not be promoted to structural acceptance. Gravity support load-path, slab stiffness, MESH_04/08/16, wall brace connectivity, NLTHA material calibration and P-Delta are unresolved native evidence gates.

**Required tests:** `python -m unittest discover -s tests -p "test_saved_case_identity_v142.py" -v`; run V142 GUI against one source-matched and one old mismatched MRSM/ESM case; verify wrong-model responses show **excluded** in issues rather than plotted as source-correct. Confirm all file hashes unchanged.
