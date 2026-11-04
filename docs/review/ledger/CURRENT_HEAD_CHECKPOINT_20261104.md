# Current-head engineering review ledger — 2026-11-04

**Starting Git commit:** `82080acc44c9b66cc2d2ec6b26e1f283d1dcd831` (`main` when this work began; 2026-11-04 17:08:19 UTC). **Review branch:** `review/current-head-ledger-20261104`.

This is an **incremental, evidence-limited review checkpoint**, not a complete code or engineering verification. The frozen 275-Python-file ledger at `66c5c971ea297dc9d7fb0499b871a6204297913d` remains authoritative **only for that baseline**: [baseline CSV](REVIEW_LEDGER_BASELINE_20261104.csv). It listed 10 files with explicitly bounded source inspection and 265 `NOT_REVIEWED`. The [current-head inventory CSV](REVIEW_LEDGER_HEAD_82080ACC_20261104.csv) records **287 active Python files**: 267 unchanged Git blobs relative to the frozen ledger, 8 changed blobs, and 12 new files. **All 287 have NOT_REVIEWED for this checkpoint**, because Git-tree metadata inspection is not a semantic source review. Historical status and blob equivalence are separately retained in the CSV.

## PR overlap and architecture

[PR #5](https://github.com/bikenshrestha2024/opensees-nbc105-research/pull/5) was **merged** on 2026-11-04 16:38:12 UTC (merge SHA `9f72cd54199dbcf3724b095d7f3bc2bbd29a82f9`). Its `full_record_gate.py` time-step and case-identity changes are already on the default-branch history: **do not cherry-pick or reimplement them blindly**. PRs #1/#2 are separately listed as open at inspection time; their runtime/diagnostic code should not silently be assumed present in `main`.

Read `AGENTS.md`, `docs/review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md`, and `docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md`. The canonical numbered 01–21 launchers and later stage entry points delegate into `components/`, where model assembly, loads, materials, wall topology and transient execution reside. `tests/` and `tools/` provide software-only checks and inventory. Older numbered aliases and archives remain compatibility and historical evidence, **not independently verified current implementations**.

## Actually inspected during this checkpoint

| File | Git blob at checkpoint | Precisely inspected scope | Observation | Executed tests | Status |
|---|---|---|---|---|---|
| `AGENTS.md` | commit `82080acc` source | Full rendered text retrieved from GitHub | Final section wrongly says PR #5 unmerged; stale instruction can cause duplicate edits | NOT RUN | DOCUMENTATION_INSPECTED |
| `docs/review/ledger/README.md` | `e2f49950817456c8c0451ab306188670e3fcfc41` | Full rendered text retrieved | Snapshot explicitly frozen at older commit; wrongly calls PR #5 open | NOT RUN | DOCUMENTATION_INSPECTED |
| `tools/validate_review_ledger.py` | `efa998f2fd4aad61fdcc92e07e8d945e9050ffac` | Entire returned source, including `github_tree_snapshot`, `validate_ledger`, `main` | Correctly checks frozen baseline; does **not** validate current head or automatically certify physical review | NOT RUN | SOURCE_REVIEWED_NOT_EXECUTED |
| `docs/review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md` | `5d6be245b23ed0f987d049d8c88774b5625b45ef` | Displayed introduction, scope, inventory and physical matrix | Earlier engineering findings are a backlog, not current model native tests | NOT RUN | PARTIAL_DOCUMENT_INSPECTION |
| `docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md` | `6b04203f2317f8623c103a6136a54c7e24864d88` | Full returned source | Numbered aliases must be preserved and reviewed against canonical run order | NOT RUN | DOCUMENTATION_INSPECTED |
| `README.md` | `0196a1974cc018d91748913334d38d59f09d634c` | Beginning and engineering-status sections returned by GitHub | Explicit unresolved first-step NLTHA and incomplete experimental validation | NOT RUN | PARTIAL_DOCUMENT_INSPECTION |

**No numerical/physics source module was freshly inspected line-by-line in this checkpoint.** Earlier baseline inspection records are not new current-head inspections. The Git recursive tree was fetched for **automated inventory only**, with 2,736 entries including non-source artifacts; these are not 2,736 reviewed files. The current-head 287-file blob inventory and baseline reconciliation are now captured in the separate CSV; actual line review remains pending.

## Engineering validation matrix

| Requirement | State | Evidence / next action |
|---|---|---|
| Repository starting SHA and PR #5 merge | PASS | GitHub branch and PR API queried |
| Existing frozen ledger and validator source read | PASS | GitHub source retrieved; validator not executed |
| Current-head complete scoped Python blob ledger | PASS | GitHub recursive tree at fixed commit; 287 active Python files inventoried in current CSV (267 unchanged, 8 changed, 12 new), no semantic-review claims |
| Full semantic line review of active source | NOT EVALUATED | Review individual source ranges in batches and include deterministic test evidence |
| Native ZERO/X/Y/XY first-step wall failure | REQUIRES PROJECT EVIDENCE | Exact exported model, paired record, native OpenSeesPy environment, failed-state mapping and logs |
| ETABS gravity/mass/loads/reinforcement equivalence | REQUIRES PROJECT EVIDENCE | Actual ETABS exports and matched load combinations |
| Eight-pair XY/YX full-length M0–M6 ULS/SLS suite | NOT RUN | Complete accepted histories for every case; failed cases excluded from optimum |
| NBC 105:2025 compliance | NOT EVALUATED | Clause-specific independent code audit with project data |
| Experimental FVD/BRB/ConcreteCM/FSAM qualification | REQUIRES PROJECT EVIDENCE | Actual specimen input, protocols, fit error and transfer justification |

## Required additions to each future per-file CSV row

`snapshot_commit,file_path,git_blob_sha,size_bytes,inventory_kind,inspection_scope,inspected_lines_or_functions,review_status,finding_id,severity,evidence_source,tests_executed,test_result,native_model_status,remaining_action,reviewer,review_timestamp_utc`

Use `NOT_REVIEWED` with `NOT_INSPECTED` and `NOT_EVALUATED` for all newly inventoried files; **do not carry a prior review flag to a changed blob**. For unchanged blobs, distinguish **HISTORICAL_INSPECTION** from a fresh current-head review and retain the dated evidence. Record a new immutable snapshot at each audited revision.

## Workflow for the next batches

1. Checkout a fixed SHA, independently recheck [the current-head inventory CSV](REVIEW_LEDGER_HEAD_82080ACC_20261104.csv) against the exact tree, and run `python tools/audit_active_repository.py --output audit/active_inventory.json --fail-on-missing-canonical` followed by `python tools/validate_review_ledger.py` for the *frozen* baseline (requires full Git history).
2. Reconcile current `git ls-tree -r -l HEAD` to the frozen baseline and mark new/modified code `NOT_REVIEWED`; examine `tests/`, `components/model/` and `components/nonlinear_time_history/` first.
3. Review geometry/mass/load-source transfer, then 3D E-SFI wall orientation and material mapping, then isolated native fresh-domain ZERO/X/Y/XY solver diagnostics.
4. Add a failing regression before each verified code fix; report exact input hashes, executed commands, traceback and local environment.
5. Validate real T1/Tn90 and Soil C eight-pair source/dt/scaling provenance. Run complete bidirectional records and ULS/SLS variants only after physical model qualification. Never rank incomplete cases.

No raw ETABS exports, records or private model evidence were uploaded in this checkpoint.
