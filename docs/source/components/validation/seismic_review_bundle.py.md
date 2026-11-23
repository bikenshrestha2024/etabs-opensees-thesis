# Consolidated seismic evidence review package

**Canonical source:** [`components/validation/seismic_review_bundle.py`](../../../../components/validation/seismic_review_bundle.py)

## Purpose

The `bundle_seismic_review` function creates one timestamped editable review folder and one ZIP under the selected ESM or MRSM analysis directory's `Seismic_Review_Packages/` folder. An immutable SHA256 manifest accounts for each unique file. Same-byte files are preserved once and listed with exact source/target paths under `duplicates`. A standalone `RESTORE_DUPLICATES.py` reconstructs those paths after extraction without changing original sources. Never package earlier ZIPs recursively.

Subfolders: `Source_Provenance`, `OpenSees_Direct`, `ETABS_Linked`, `ETABS_Native` (only user-supplied genuine independent ETABS result files), and `Comparisons` (the normalized Excel case / story / node comparison input template).

The auto-packaging triggers after generating ESM loads, after creating the ETABS-linked original Excel reference copy, after finishing ESM solver cases, and after the MRSM batch completes. All actual present outputs in the method-specific analysis output root are scanned, rather than inferred from a fixed filename list.

## Engineering data contract and limitations

An original ETABS-linked calculation workbook (source Aw and adopted period) is not a response result from ETABS analysis. The separate ETABS Native tab remains blank absent native ETABS results, and must not be represented as validated. The code does not read or alter source EDBs.

The ESM solver now exports original-point crosswalk plus all-node displacement increments, plus a model-hashed metadata sidecar. The normalized collector includes only current-state/model-verified ESM records and differentiates cumulative *applied* floor forces from section-cut *recovered* story shear. OpenSees CQC envelopes are peak modal combinations; they are not simultaneous signed responses. Source `etabs_comparison.save` and `etabs_direct_api.extract_from_sap` remain the explicit native comparison route, after case, location, and response basis review.

**Validation gate:** no source model/EDB/hash/case/spectrum/scale/mass/stiffness equivalence is established merely because an archive exists. ESM eligibility (NBC105:2025 §3.2.1), site Vs30, and Excel Aw openings remain separate mandatory review gates. MRSM native ETABS comparisons require verified mapping, and unsolved/missing native results are not replaced with zero.

## Test

`python tests/verify_seismic_review_bundle.py`; the CI quality workflow executes this regression, source-guide inventory, gravity audit and broader controls. The native Windows ETABS integration is still a project-specific manual verification step.

## Security and packaging

No cloud upload occurs. The ZIP is created locally, not automatically published. Original source data, EDB and users' other private folders are not mutated. The reconstruction helper verifies SHA256 before copying content. Exclude previous evidence bundles and long-recursive scanner paths to avoid runaway copies and incorrectly inflated uploads.


## 2026-11-23 — Stage-owned new review files from legacy selections

The selected native/legacy analysis-output folder remains a **read-only source** for historical case evidence. `stage_review_owner(export_dir, selected_output, stage)` maps new review publication under the owning `03_ESM` or `05_MRSM` stage when the GUI selected an old `OpenSees_Analysis_Results` location or another stage within the same export. Existing canonical run folders preserve their own local `07_EXPORT_ZIP`; explicit outside-export custom locations remain opt-in overrides. The ESM legacy route comparison writes to `03_ESM/COMPARISONS`, and seismic review ZIPs to `<stage>/07_EXPORT_ZIP` with snapshots in `<stage>/REVIEW_SNAPSHOTS`. No existing files are moved or invalidated; see `tests/test_stage_owned_seismic_legacy_routing.py`. This is **folder provenance only**, not native structural acceptance.
