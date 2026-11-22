# 2026-11-22 — actual ETABS native results and LTHA input source reconciliation

**Software audit:** reviewed source, three MRSM ZIP artifacts, GUI screenshots and two large input logs; **native ETABS 23 Windows EDB or COM execution was NOT performed**. This document contains derived evidence, not private case files or original model uploads.

## Uploaded result evidence

- `MRSM_RUN_Review_UPLOAD.zip`: 68 archive members. No analyzed native ETABS results.
- `MRSM_Review_20261122_160908_508840_UPLOAD.zip`: 140 archive members. No analyzed native ETABS results.
- `MRSM_Review_20261122_161031_843671_UPLOAD.zip`: 140 archive members. No analyzed native ETABS results.
- The two standard MRSM snapshots have **13 byte-identical direct OpenSees JSON objects**. ZIP CRC and parsed JSON/CSV content checks found no format errors. A blank native comparison CSV template exists, but it cannot be treated as an ETABS source.
- MRSM ULS six cases: X_E0/Eplus/Eminus and Y_E0/Eplus/Eminus, **OpenSees-only** scaled reference base shear X=30588.941 kN and Y=26450.735 kN. The saved log explicitly reports `ETABS_SOURCE_SUPPORTS` count **76** (32 actual foundations plus 44 shear-wall mesh points in source restraint records), `LEGACY_GROSS_SHELL`, source seismic gravity preload 1D+0.3 other LL. Saved JSON contains model SHA but **no executed support case/mass operator provenance**. These six historical runs are NOT the user's accepted primary physical 32-foundation model.
- Project input log reports multiple *older 6 m X wall* scaling workbooks (Aw X=1.9582936 m²) whose B4 source EDB is different. Do not import these values as current two 12 m X walls with openings; review current V10.7 source workbook and actual EDB SHA.

## Source-level root causes

1. **Blank ETABS values:** `components/validation/etabs_comparison.py::save` starts from OpenSees source rows and yields no ETABS comparison values unless a native normalized CSV or reviewed direct API `etabs_rows` is supplied. The uploaded ZIPs provide neither. The GUI previously had no simple read-only display of native analyzed case names or signed base reactions. A previous reviewed API CSV could be stranded under a different individual MRSM run's `02_RESULTS/ETABS_Comparison_V148`, so the next comparison could not auto-locate it. `find_verified_etabs_csv` previously required matching EDB SHA and approved map but not the generated model SHA or CSV hash.
2. **LTHA error:** the GUI chose **SLS** but selected EDB is **ULS**; `analysis_autofill` rejected incompatible modal/period inputs and fields were empty. `_run()` called `float(self.p1.get())`, `float(self.p2.get())`, `float(self.t1x.get())` before validating missing data or actual ULS/SLS source state, resulting in the unhelpful popup `could not convert string to float: ''`.
3. **MRSM execution provenance:** old results have `model_sha256` for source *serialized geometry*, not the actual chosen 32/76/97 restraint profile or distributed/lumped seismic mass. Identical geometry hashes can still produce different eigenperiods, reactions, stiffness and response; no physical comparison PASS is permissible from hash alone.

## Implemented source solutions (PR #151)

- `discover_native_base_reactions` is a read-only ETABS COM adapter: checks live EDB identity and SHA, enumerates actually analyzed case/combination names, reads signed Fx/Fy/Fz/Mx/My/Mz in kN-m, preserves original result setup and units. User-facing **Read native ETABS values (live, read-only)** shows a raw results preview and saves a timestamped local JSON/CSV. Selecting one actual native case and an OpenSees MRSM BASE row can **preview-link the raw value with NOT_COMPARABLE**, no automatically fabricated spectrum scaling or percentage. Exact equivalent `etabs_value` requires the separate previously implemented **Direct ETABS API / EDB** reviewed case/story/point mapping, physical basis and approval.
- `verify_native_bundle` checks selected original EDB identity SHA and path, assembled current model SHA, **native normalized CSV SHA**, approved mapping and complete semantic row metadata before reuse. A source-owned `05_COMPARISONS/ETABS_Comparison_V148` mirror makes that small reference bundle available to different MRSM case folders without copying native EDB or other sensitive files.
- `parse_linear_gui_numeric_inputs` rejects mismatched ULS/SLS before parsing numeric fields, lists missing named periods and modes, rejects nonfinite/negative/zero values, duplicate damping periods, damping >5%; the runner starts no output case on invalid GUI input. Periods must still derive from current source-matched Rayleigh and Modal computations; none are auto-invented.
- New MRSM solver stores `support_case`, `seismic_mass_policy` and post-build `support_case_evidence` on each response. The comparison marks legacy unknown 76 or mismatched mass operator `NOT_COMPARABLE` despite numerical coincidence and retains all old files.

## Native acceptance still required

- Open the exact source EDB in ETABS v23 on Windows with completed native analysis and use the new raw observer to identify the real case names. Create and approve exact 32-physical-support compatible ETABS↔OpenSees case/story/point mapping, mass, stiffness, damping, CQC spectrum, §7.5 force normalization and response location. Do NOT use 6 m X wall scaling from old workbooks.
- Rebuild current OpenSees runtime from the same EDB and solve primary 32 foundations with verified 44 wall mesh transfer constraints. Previous best ETABS-elastic joint reaction max 768.045 kN is unresolved; a green Linux unit test does not resolve it.
- Select matching ULS or real SLS source in the LTHA UI and generate matching current state 3D modal Rayleigh inputs and NBC §8 P-Delta initial-state evidence before starting the full record.
- Native ETABS live COM was **not** executed in this task. The actual `etabs_value` column cannot be populated for the uploaded ZIPs without the missing analyzed native ETABS response and verified mapping.
