# Canonical ZIP routing for all analysis modules — 2026-11-22

**Decision:** Every newly generated local evidence ZIP must be written into the **07_EXPORT_ZIP** folder owned by its exact **selected analysis case**, stage or output root. ZIP location does not imply that the solver ran or that the result is correct.

## Writer contract

| Producer | Previous ZIP output behavior | New local ZIP destination |
| --- | --- | --- |
| Gravity review workflow | Already uses named gravity export ownership | Preserve `<gravity-case>/07_EXPORT_ZIP/Gravity_Evidence_Upload/*.zip` |
| Gravity comparison bundle | Named ZIP beside its extracted result | `<selected gravity output>/07_EXPORT_ZIP/<name>*.zip` or existing named subsection |
| Gravity native equivalence preflight | ZIP within audit data root | `<selected audit root>/07_EXPORT_ZIP/GRAVITY_NATIVE_EQUIVALENCE_UPLOAD.zip` |
| Model mesh diagnostics (`MESH_04/08/16`) | `02_MODEL/SLAB_LOAD_PATH/UPLOAD_PACKAGES/` | `02_MODEL/07_EXPORT_ZIP/MESH_nn.zip` |
| ESM consolidated Excel and ZIP | ZIP in ESM `REVIEW_SNAPSHOTS` parent | Exact source-run `07_EXPORT_ZIP/ESM_Combined_Inspection_*.zip` when identifiable; local fallback `<ESM selected root>/07_EXPORT_ZIP` |
| ESM validation evidence | ZIP beside extracted `ESM_Validation_Evidence_*` | Source-run `07_EXPORT_ZIP/ESM_Validation_Evidence_*_UPLOAD.zip` |
| ESM/MRSM automatic and manual seismic package | `02_RESULTS/Seismic_Review_Packages/...` | Source-run `07_EXPORT_ZIP/<ESM or MRSM>_Review_*_UPLOAD.zip` |
| MRSM organized case / multi-module snapshots | `06_REVIEW/Organized_Results/<stamp>/ZIP_Exports` | Exact selected source case `07_EXPORT_ZIP/MRSM_RUN_Review_UPLOAD.zip` or corresponding module ZIP; extracted snapshots/manifests stay under `06_REVIEW/Organized_Results` |
| LTHA/NLTHA manual evidence review | `02_RESULTS/Review_ZIPs` | Source-run `07_EXPORT_ZIP/<Linear or Nonlinear>_Time_History_*.zip` |
| Native ETABS EQX/EQY/P-Delta extractor | ZIP alongside new native result folder | Selected native-result `07_EXPORT_ZIP/<audit-name>_UPLOAD.zip` |

**Modal:** A solved modal report is not automatically compressed. If no export action was invoked, `04_MODAL/.../<run>/07_EXPORT_ZIP` may remain empty **without indicating solver failure**. Its saved eigen CSV/JSON/XLSX should be in `02_RESULTS/03_EXCEL/04_FIGURES`. The shared manual organized exporter may create a Modal ZIP when the user explicitly selects that evidence.

**Legacy outside-case or imported output:** if no `00_INPUT_SOURCE/CASE_MANIFEST.json` exists, the selected folder keeps an isolated `07_EXPORT_ZIP` child. An explicitly selected named subsection *already inside* `07_EXPORT_ZIP` is preserved. A symlinked destination is refused. No archive is written to an unrelated run via filename/model-label guessing.

## Non-destructive migration

- **New archives only:** historical ZIPs inside `Seismic_Review_Packages`, `Organized_Results/ZIP_Exports`, `Review_ZIPs` or `UPLOAD_PACKAGES` remain at their original source paths. Do not move/delete them or rewrite previously signed manifests. Exclude these old dirs from future source packaging to prevent zip-in-zip recursion and evidence contamination.
- **Source files untouched:** EDB/workbook/ground motion and solved `02_RESULTS` are not moved or overwritten; extracted review folders and manifests retain their existing reader paths. The old `Seismic_Review_Packages/LATEST_*_REVIEW.txt` remains a compatibility locator but now points to a ZIP in the seventh folder. A local seventh-folder `LATEST` pointer is also written.
- **Privacy:** local archive manifests and payloads can contain model paths/geometry; there is no automatic online upload. A path-redacted manifest does not scan every payload for private information; users must review before sharing.
- **Different model identities:** do not assemble ESM/Modal/MRSM/LTHA/NLTHA files from different export roots into one package without explicitly checked model SHA, state, stage and support-profile identity. Bundle creation is data packaging, not model equivalence.
- **Failure semantics:** if ZIP compression fails, preserve already completed solver results and report an export failure independently. Empty `07_EXPORT_ZIP` or a ZIP manifest alone cannot prove full analysis case completion.

## Validation

Source owners: `components/inputs/review_zip_paths.py`, `components/validation/seismic_review_bundle.py`, `components/ui/organized_results.py`, `components/ui/history_review_tools.py`, `components/equivalent_static/organized_exports.py`, `components/equivalent_static/evidence_bundle.py`, `components/gravity/comparison_bundle.py`, `components/gravity/mesh_cases.py`, `components/validation/gravity_native_equivalence_preflight.py`, `tools/ETABS_EQX_EQY_PDELTA_EXPORT.py`. Gravity's `components/gravity/output_ownership.py` remains authoritative for its named subsection.

Run `python -m pytest -q tests/test_canonical_review_zip_routes_20261122.py tests/verify_seismic_review_bundle.py tests/test_organized_results.py tests/test_gravity_archive_only_snapshot.py tests/verify_gravity_evidence_workflow.py tests/verify_gravity_comparison_bundle.py tests/verify_esm_validation_bundle.py tests/test_model_mesh_case_workflow.py tests/test_history_review_tools.py` and repository integration/Windows output layout workflows. Passing tests certify source-level route semantics for synthetic cases only; they do not test native Windows ETABS/OpenSees and actual 75+ MB review ZIP compression on the user's system.

Refer also to `REVIEW_MAIN/06_NONLINEAR_TH/20261122_21_BLOCKERS_CLOSURE_PLAN.md` for 21 NLTHA engineering requirements; ZIP folder readiness is **not** among their approval substitutes.
