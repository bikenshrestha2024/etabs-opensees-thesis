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
