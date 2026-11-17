# 2026-11-17 — semantic review of gravity + 04/08/16 formula workbook publication

**Review scope:** Active code and callers: components/gravity/storey_loads.py, components/gravity/load_path_formulas.py, components/gravity/workbook_publishing.py, components/inputs/output_contract.py (atomic_json and symlink checks), components/model/assembly.py (prepare_complete_export and elastic solver-tag allocation), components/gravity/mesh_cases.py (separate mesh-case paths), components/ui/application.py (on-demand post-export action). This is a **targeted, source-inspected review**, not all 573 active Python files or all function-level review units.

**Source baseline:** main commit 2e18dcb57c2522d1398528e8f0f45aa866c6e07b, branch fix/semantic-gravity-workbook-atomic-20261117. Native ETABS v23 source EDB and original model/result XLSX were not available to rerun through Windows. Do not label numerical outputs verified on this review.

## 1. Confirmed defects and evidence

| ID | Level | Source / call path | Reproduction | Correction / limitation |
|---|---|---|---|---|
| GR-XLSX-01 | P1 | storey_loads.export_storey_gravity -> openpyxl Workbook.save(final_file) | Interrupted save overwrote an existing workbook with partial bytes; red GitHub CI in PR #97 | Shared atomic publisher writes temporary XLSX in destination folder; only successful ZIP-valid and hashed bytes replace final file |
| GR-XLSX-02 | P1 | storey_loads.export_storey_gravity -> hashlib.sha256(xlsx.read_bytes()) | Test forbidding whole-file read fails on original code; makes transient full-size XLSX heap allocation | SHA256 now computed in streamed 1-MiB blocks; no second full XLSX heap buffer |
| GR-XLSX-03 | P1 | Workbook.save returns without exception but corrupt/empty ZIP | Synthetic writer returned successfully with non-ZIP bytes; source marked READY | Enforce ZIP central directory and core XLSX parts before READY or any manifest |
| MESH-XLSX-01 | P1 | load_path_formulas.export -> Workbook.save(final timestamped file) | Interrupted write left partial misleading XLSX in EXCEL despite lack of manifest | Shared publisher deletes incomplete temporary file and leaves no XLSX under final filename |
| MESH-XLSX-02 | P1 | load_path_formulas.export -> success JSON manifest | Success manifest lacked final XLSX checksum | Add workbook_sha256 equal to final bytes; JSON publication is atomic and rejects redirected output paths |
| MANIFEST-01 | P1 | previous Gravity_Storey_Workbook_Status_V131.json could still show READY after failed regeneration | Error-path test checks explicit FAILED state | Write GENERATING before full formula work; READY only after final artifact is committed and SHA computed; FAILED on error |

## 2. Functions and cross-boundary assumptions inspected

| Code area | Observed contract | Code-review status | Native engineering status |
|---|---|---|---|
| storey_loads.classify | Classifies source self-weight as dead and pattern/source classes; values counted by load pattern | Scoped semantic inspection performed; no change | Requires original ETABS load pattern type evidence |
| storey_loads.export_storey_gravity | Group source loads by diaphragm; compare applied nodal-source ledger to assembled total; write CSV/JSON; optional XLSX | Targeted publication path fixed; gravity arithmetic unchanged | Reconciliation with native ETABS output and wall-base reactions OPEN |
| storey_loads.main | Requires full export report, config/model SHA match, source load audit before generating Excel | Read source and error gates; no material source change | EDB identity and numerical response still OPEN |
| load_path_formulas.add_formula_audit | Full gravity surface load formulas, seismic-preload copy, loaded node paths, Excel row paging and formula recalc; no solver execution | Inspected formula/output handling; arithmetic untouched | Exact tributary/equivalent force and ETABS comparison OPEN |
| load_path_formulas.export | Requires exact source model/config SHA and FLOOR shell cells, writes selected mesh workbook and manifest | Targeted publication path fixed; source mesh selection unchanged | Full 4/8/16 solved convergence study OPEN |
| workbook_publishing.publish_workbook | Exclusive temporary serialization, ZIP validation, SHA streaming and same-volume replace | New function covered by interrupted/corrupt/success tests | File integrity only; not an engineering response |
| output_contract.atomic_json | Atomic derived JSON; uses fsync and rejects symlinks | Reused unchanged as success manifest writer | Output metadata only |
| assembly.build_complete_model | Initial frame solver tag 100001, then shell tags after frame count | Source allocation inspected, consistent with formula sheet enumeration for unmodified export | Requires actual source mapping/solver source readback |
| GUI and CLI | Workbook is generated from saved export without invoking ETABS or remeshing | Existing UI helper preserved | Windows responsiveness and original ETABS/OpenSees reconciliation OPEN |

## 3. Acceptance gates and evidence classification

- **S1 SOURCE ID:** source EDB/config/source-loaded model fingerprint must match (runtime required).
- **S2 SOFTWARE SOURCE:** tests first red then green; CI includes intentional failed XLSX save, corrupt ZIP, memory-streaming and 04 mesh manifest identity; preserves old XLSX on an aborted write.
- **S3 NUMERICAL:** storey source load totals, original full-gravity Live 1.0, configured seismic preload Live 0.3, unclassified loads and mesh-cell/nodal formulas require source-matched comparison; no modification or acceptance inferred from file integrity.
- **S4 SUPPORTS:** 32/76/97 base strategies still require ETABS native analysis-node restraints and all 6-DOF wall-base section forces; an Excel workbook is not a reaction solver. Keep issue #75 and gravity REVIEW cases OPEN.
- **S5 MESH:** MESH_04, MESH_08, MESH_16 independently assembled and solved; verify beam moments/shear, slab bending and wall-base reactions; no 16x16 large real model was executed here.
- **S6 SECURITY/OUTPUT:** no ETABS EDB, source workbook, confidential folder paths or unredacted run logs committed. XLSX file checksums and output paths are written only to derived case directories.
- **S7 RELEASE:** exact PR SHA tests all green, independent diff review, original physics source unchanged. No bulk file relocation or lifecycle/status promotion from CI-only evidence.

## 4. Structured run ownership

- Gravity on-demand XLSX: selected export root / Gravity_Storey_Load_Breakdown_V131.xlsx; status JSON in same export root and previous workbook preserved if publication fails.
- Mesh workbook: selected case root / 02_MODEL/SLAB_LOAD_PATH/MESH_04 (or 08/16) / EXCEL / timestamped XLSX; JSON / matching atomic manifest with config_sha256 and workbook_sha256.
- Regression evidence: tests/test_deferred_storey_workbook.py, tests/test_mesh_workbook_publication.py; source guide docs/source/components/gravity/workbook_publishing.py.md.
- All original ETABS/OpenSees model geometry, supports, loads, shell mesh/frames, FVD/BRB classifications and M0–M6 physics remain unchanged.

**Disposition:** Confirmed artifact-integrity defects corrected in source pending exact-head CI. Physical model acceptance and full repository function-level semantic audit remain OPEN under issue #75.
